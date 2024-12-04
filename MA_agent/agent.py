import os
import uuid
import pathway as pw
from fastapi import FastAPI, File, UploadFile
from pathlib import Path
import time
import asyncio
from typing import List
from common.plan_rag import plan_rag_query, single_plan_rag_step_query

# from rag.client import retrieve_documents
from MA_agent.constants import (
    LIST_OF_DOCUMENTS_INPUT,
    LIST_OF_DOCUMENTS_OUTPUT,
    DOCUMENT_PROMPT_MAPPING,
)
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
import MA_agent.prompts as prompts
from langchain_openai import ChatOpenAI
import uvicorn
import pymongo

uri = "mongodb://localhost:27017/"
client = pymongo.MongoClient(uri)

from pathway.xpacks.llm.vector_store import VectorStoreClient

VECTOR_PORT = 8765
PATHWAY_HOST = "127.0.0.1"

vector_client = VectorStoreClient(
    host=PATHWAY_HOST,
    port=VECTOR_PORT,
)


async def retrieve_documents(query: str):
    results = vector_client.query(query, 10)
    return results


llm = ChatOpenAI(model="gpt-4o-mini")
import json

app = FastAPI()
with open("./MA_agent/definitive_agreement_outline.txt", "r") as f:
    definitive_agreement_outline = f.read()
with open("./MA_agent/term_sheet_outline.txt", "r") as f:
    term_sheet_outline = f.read()
with open("./MA_agent/letter_of_intent_outline.txt", "r") as f:
    letter_of_intent_outline = f.read()
with open("./MA_agent/nda_outline.txt", "r") as f:
    nda_outline = f.read()
with open("./MA_agent/due_diligence_outline.txt", "r") as f:
    due_diligence_outline = f.read()


DOCUMENT_OUTLINE_MAPPING = {
    "Definitive Agreement": definitive_agreement_outline,
    "Term Sheet": term_sheet_outline,
    "Letter of Intent": letter_of_intent_outline,
    "NDA": nda_outline,
    "Due Diligence Report": due_diligence_outline,
}

os.makedirs("MA", exist_ok=True)


def plan_to_queries(plan):
    queries = []
    for step in plan.split("\n"):
        if len(step) > 0:
            query = single_plan_rag_step_query(step)
            queries.append(query)
    return queries


async def generate_agreement(company1, company2, id):
    async def create_queries(output_doc):
        plan = plan_rag_query(
            query=None,
            agent="M&A",
            companies=(company1, company2),
            input_docs=LIST_OF_DOCUMENTS_INPUT,
            output_doc=output_doc,
        )
        queries: list[str] = plan_to_queries(plan)
        return queries

    tasks = [create_queries(output_doc) for output_doc in LIST_OF_DOCUMENTS_OUTPUT]

    # Wait for all tasks to complete in parallel and collect queries
    all_docs_queries: list[list[str]] = await asyncio.gather(*tasks)

    POOL_SIZE = 8
    with ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:
        # Flatten the nested list of queries
        all_queries = list(chain.from_iterable(all_docs_queries))
        futures = [executor.submit(retrieve_documents, query) for query in all_queries]

        all_results = [future.result() for future in futures]

    start_idx = 0
    final_results: list[list[any]] = []
    for query_group in all_docs_queries:
        count = len(query_group)
        final_results.append(all_results[start_idx : start_idx + count])
        start_idx += count

    async def create_summaries(documents, doc_type, company_name):
        summary = await generate_summary(documents, doc_type, company_name)
        return summary

    tasks = []
    for idx, output_doc in enumerate(LIST_OF_DOCUMENTS_OUTPUT):
        for company, company_name in zip(final_results, [company1, company2]):
            tasks.append(create_summaries(company[idx], output_doc, company_name))

    summaries: list[str] = await asyncio.gather(*tasks)

    # Generate the final documents based on the summaries parallely
    tasks = []
    for idx in range(0, len(summaries), 2):
        output_doc = LIST_OF_DOCUMENTS_OUTPUT[idx // 2]
        tasks.append(
            generate_document(
                output_doc, company1, company2, summaries[idx], summaries[idx + 1]
            )
        )

    documents: list[str] = await asyncio.gather(*tasks)
    output_to_document: dict[str, str] = {
        output_doc: document
        for output_doc, document in zip(LIST_OF_DOCUMENTS_OUTPUT, documents)
    }
    insights = await generate_insights(summaries, company1, company2)
    send_documents(output_to_document, insights, id)


@app.post("/submit")
async def ingest(company1: str, company2: str, files: List[UploadFile] = File(...)):
    id = str(uuid.uuid4())
    for file in files:
        file_location = f"MA/{id}_{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

    asyncio.create_task(generate_agreement(company1, company2, id))

    return {
        "message": "Files uploaded successfully, agreement generation in progress.",
        "conversation_id": id,
    }


async def generate_document(
    type, company1, company2, company1_details, company2_details
):
    prompt = DOCUMENT_PROMPT_MAPPING[type].format(
        company_a=company1,
        company_b=company2,
        company_a_details=company1_details,
        company_b_details=company2_details,
        document_outline=DOCUMENT_OUTLINE_MAPPING[type],
    )
    document = llm.invoke(prompt).content
    return document


async def generate_summary(documents, doc_type, company_name):
    prompt = prompts.SUMMARY_PROMPT.format(
        company_name=company_name,
        document_type=doc_type,
        context=" ".join(doc.text for doc in documents),
    )
    summary = llm.invoke(prompt).content
    return summary


# Function to generate insights based on document headings
async def generate_insights(summaries, company1, company2):
    company1_summary = " ".join(summary for summary in summaries[::2])
    company2_summary = " ".join(summary for summary in summaries[1::2])
    prompt = prompts.INSIGHTS_PROMPT.format(
        company_a=company1,
        company_b=company2,
        a_summary=company1_summary,
        b_summary=company2_summary,
    )
    insights = llm.invoke(prompt).content
    insights = json.loads(insights)
    return insights


async def send_documents(output_to_document, insights, conversation_id):
    # store the documents in the database using the mongo client and conversation_id
    db = client["MA"]
    collection = db["documents"]
    output_to_document["insights"] = insights
    output_to_document["conversation_id"] = conversation_id

    collection.insert_one(output_to_document)
    return


# Run the FastAPI application
if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)

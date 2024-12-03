import os
import uuid
import pathway as pw
from fastapi import FastAPI, File, UploadFile
from pathlib import Path
import time
import asyncio
from typing import List
from common.plan_rag import plan_rag_query
from constants import LIST_OF_DOCUMENTS_INPUT, LIST_OF_DOCUMENTS_OUTPUT
from concurrent.futures import ThreadPoolExecutor

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

os.makedirs("MA", exist_ok=True)

data_sources = [
    pw.io.fs.read(
        "./MA",
        format="binary",
        mode="streaming",
        with_metadata=True,
    )
]


async def generate_agreement(company1, company2):
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

    # Use asyncio.gather to run the plan generation tasks concurrently
    tasks = [create_queries(output_doc) for output_doc in LIST_OF_DOCUMENTS_OUTPUT]

    # Wait for all tasks to complete in parallel and collect queries
    all_docs_queries: list[list[str]] = await asyncio.gather(*tasks)
    


    


@app.post("/submit")
async def ingest(company1: str, company2: str, files: List[UploadFile] = File(...)):
    for file in files:
        file_location = f"MA/{uuid.uuid4()}_{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

    asyncio.create_task(generate_agreement(company1, company2))

    return {"message": "Files uploaded successfully, agreement generation in progress."}


async def generate_documents():
    # This function will eventually generate the documents using LLM
    pass


# Function to generate insights based on document headings
async def generate_insights():
    # This will generate insights based on document headings and other logic
    pass


# Function to send the final documents to the user
async def send_documents():
    # This will send the generated documents to the user
    pass


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

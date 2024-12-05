from fastapi import FastAPI, WebSocket,Form
import uvicorn
import pymongo
import uuid
from common.reranker import rerank_docs
from langchain_openai import ChatOpenAI
from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.plan_rag import plan_rag_query
from common.metrag import metrag_filter
import asyncio

check_event = asyncio.Event()
uri = "mongodb://localhost:27017/"
client = pymongo.MongoClient(uri)
db = client["macro"]
db = db["results"]
app = FastAPI()
def single_retriever_macro_agent(query):
    """For simple queries, run them through HyDe and then retrieve the documents"""

    modified_query = hyde_query(query)
    documents = retrieve_documents(modified_query)

    result = rerank_docs(modified_query, documents)

    documentlist = [doc.document.text for doc in result.results]
    context = "\n\n".join(documentlist)
    prompt = f"""You are a helpful chat assistant that helps create a summary of the following context: '{context}', in light of the query: '{query}'.
                You must keep in mind that you are an expert in market analysis, and that the response you generate should be tailored accordingly.
            """
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content
    documents = metrag_filter(documents, query, "macro")

    return documents, response

async def multi_retrieval_macro_agent(query,id):
    """Answer complex queries by running them through a multi-retrieval process based on PlanRAG"""
    global check_event
    plan = plan_rag_query(query, "macro")
    documents = []
    response = []
    print(f"Plan:\n{plan}")
    for step in plan.split("\n"):
        if len(step) > 0:
            query_llm = ChatOpenAI(model="gpt-4o-mini")
            query_prompt = f"""You are a helpful prompt engineering assistant that must generate a query to feed to an LLM based on the given step in a multi-step plan.
                The step you must generate a query for is: {step}
                The query you generate should be clear and concise, and should be designed to retrieve the most relevant documents and information for the given step.
                It should be a query and not a statement, and must be no longer than 2 sentences.
                You must keep in mind that you are an expert in market analysis, and that the query you generate should be tailored accordingly.
                """
            query = query_llm.invoke(query_prompt).content
            print(f"Step:\n{step}")
            print(f"Query:\n{query}")
            docs, resp = single_retriever_macro_agent(query)
            for i, doc in enumerate(docs):
                print(f"\nDocument {i}:")
                for key, value in doc.items():
                    print(f"{key}: {value}")
            documents.extend(docs)
            response.append(resp)
  
    # modified_query = hyde_query(query) # For the complex query, do we need HyDE?


    result = rerank_docs(query, documents) 

    documents = [doc.document.text for doc in result.results]
    context_response = "\n\n".join(response)
    context_documents = "\n\n".join(documents)
    prompt = f"""You are a helpful chat assistant that helps answer query based on the given context.
            Currently, you had given a step-by-step plan to generate the answer and the plan is as follows:
            {plan}
            The responses to the queries generated from the plan are as follows:
            {context_response}
            Supplementary information to the responses is as follows:
            {context_documents}
            Do not use outside knowledge to answer the query. If the answer is not contained in the provided information, just say that you don't know, don't try to make up an answer.
            You must keep in mind that you are an expert in market analysis, and that the response you generate should be tailored accordingly.
            """

    print("Prompt:\n", prompt)
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content
    db.update_one({"id" : id}, {"$set" : response},upsert=True)
    print("Done")
    check_event.set()
@app.post("/submit")
async def submit(query : str = Form(...)):
    id = str(uuid.uuid4())
    asyncio.create_task(multi_retrieval_macro_agent(query,id))
    return {
        "message": "Files uploaded successfully, agreement generation in progress.",
        "conversation_id": id,
    }

@app.websocket("/ws/check")
async def check(ws: WebSocket):
    await ws.accept()
    global check_event
    while True:
        await check_event.wait()  
        await ws.send_json({"result": "OK"})  
        check_event.clear()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8230)
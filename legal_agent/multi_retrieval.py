from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.reranker import rerank_docs
from langchain_openai import ChatOpenAI
from common.plan_rag import plan_rag_query

def single_retriever_legal_agent(query):
    """For simple finance related queries, run them through HyDe and then retrieve the documents"""

    modified_query = hyde_query(query)
    documents = retrieve_documents(modified_query)

    result = rerank_docs(modified_query, documents)

    documentlist = [doc.document.text for doc in result.results]
    context = "\n\n".join(documentlist)
    prompt = f"""You are a helpful chat assistant that helps create a summary of the following context: '{context}', in light of the query: '{query}'.
                You must keep in mind that you are a legal expert, and that the response you generate should be tailored accordingly.
            """
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content

    return documents, response

def multi_retrieval_legal_agent(query):
    """Answer complex finance related queries by running them through a multi-retrieval process based on PlanRAG"""
    plan = plan_rag_query(query, "legal")
    documents = []
    response = []
    for step in plan.split("\n"):
        if len(step) > 0:
            query_llm = ChatOpenAI(model="gpt-4o-mini")
            query_prompt = f"""You are a helpful prompt engineering assistant that must generate a query to feed to an LLM based on the given step in a multi-step plan.
                The step you must generate a query for is: {step}
                The query you generate should be clear and concise, and should be designed to retrieve the most relevant documents and information for the given step.
                It should be a query and not a statement, and must be no longer than 2 sentences.
                You must keep in mind that you are a legal expert, and that the query you generate should be tailored accordingly.
                """
            query = query_llm.invoke(query_prompt).content
            docs, resp = single_retriever_legal_agent(query)
            documents.extend(docs)
            response.append(resp)
            print(len(documents))

    result = rerank_docs(query, documents) 

    documents = [doc.document.text for doc in result.results]
    response.extend(documents)
    context = "\n\n".join(response)
    prompt = f"""You are a helpful chat assistant that helps answer query based on the given context.
            You will answer queries only on the basis of the following information: {context}
            Do not use outside knowledge to answer the query. If the answer is not contained in the provided information, just say that you don't know, don't try to make up an answer.
            You must keep in mind that you are a legal expert, and that the response you generate should be tailored accordingly.
            """

    print("Multi Retrieval")
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content

    return response

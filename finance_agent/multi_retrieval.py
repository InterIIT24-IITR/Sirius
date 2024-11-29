from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.reranker import rerank_docs
from langchain_openai import ChatOpenAI
from common.planrag import planrag_query
from finance_agent.single_retrieval import single_retriever_finance_agent

def multi_retrieval_finance_agent(query):
    """Answer complex finance related queries by running them through a multi-retrieval process based on PlanRAG"""
    plan = planrag_query(query, "finance")
    documents = []
    response = []
    for step in plan.split("\n"):
        if len(step) > 0:
            query_llm = ChatOpenAI(model="gpt-4o-mini")
            query_prompt = f"""You are a helpful prompt engineering assistant that must generate a query to feed to an LLM based on the given step in a multi-step plan.
                The step you must generate a query for is: {step}
                The query you generate should be clear and concise, and should be designed to retrieve the most relevant documents and information for the given step.
                It should be a query and not a statement, and must be no longer than 2 sentences.
                You must keep in mind that you are an expert in the field of finance, and that the query you generate should be tailored accordingly.
                """
            query = query_llm.invoke(query_prompt).content
            print(f"Step: {step}")
            print(f"Query: {query}")
            docs, resp = single_retriever_finance_agent(query)
            documents.extend(docs)
            response.append(resp)
            print(len(documents))
    
    # modified_query = hyde_query(query) # For the complex query, do we need HyDE?

    result = rerank_docs(query, documents) 

    documents = [doc.document.text for doc in result.results]
    response.extend(documents)
    context = "\n\n".join(response)
    prompt = f"""You are a helpful chat assistant that helps answer query based on the given context.
            You will answer queries only on the basis of the following information: {context}
            Do not use outside knowledge to answer the query. If the answer is not contained in the provided information, just say that you don't know, don't try to make up an answer.
            You must keep in mind that you are an expert in the field of finance, and that the response you generate should be tailored accordingly.
            """

    print("Multi Retrieval")
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content

    return response

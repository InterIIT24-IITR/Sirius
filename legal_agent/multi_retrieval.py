from common.reranker import rerank_docs
from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.metrag import metrag_filter
from langchain_openai import ChatOpenAI
from common.plan_rag import plan_rag_query

def single_retriever_legal_agent(query):
    """For simple legal related queries, run them through HyDe and then retrieve the documents and return the response and documents"""

    modified_query = hyde_query(query)
    documents = retrieve_documents(modified_query)

    result = rerank_docs(modified_query, documents)

    documentlist = [doc.document.text for doc in result.results]
    context = "\n\n".join(documentlist)
    prompt = f"""You are a helpful chat assistant that helps create a summary of the following context: '{context}', in light of the query: '{query}'.
                You must keep in mind that you are a legal expert in the field of finance, and that the response you generate should be tailored accordingly.
                You should ensure that the summary is clear and contains data relevant to the query.
                """
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content

    documents = metrag_filter(documents, query, "finance")

    return documents, response
  
def multi_retrieval_legal_agent(query):
    """Answer complex legal related queries by running them through a multi-retrieval process based on PlanRAG"""
    plan = plan_rag_query(query, "legal")

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
                You must keep in mind that you are a legal expert, and that the query you generate should be tailored accordingly.
                """
            query = query_llm.invoke(query_prompt).content
            
            docs, resp = single_retriever_legal_agent(query)
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
            You must keep in mind that you are a legal expert, and that the response you generate should be tailored accordingly.
            """

    print("Prompt:\n", prompt)
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content
    return response

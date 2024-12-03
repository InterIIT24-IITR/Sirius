from common.reranker import rerank_docs
from langchain_openai import ChatOpenAI
from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.plan_rag import plan_rag_query
from common.metrag import metrag_filter
from concurrent.futures import ThreadPoolExecutor, as_completed

def single_retriever_finance_agent(query):
    """For simple finance related queries, run them through HyDe and then retrieve the documents"""
    mod_query = hyde_query(query)
    #print(f"Query:\n{query}")
    #print(f"Modified Query:\n{mod_query}")
    documents = retrieve_documents(mod_query)
    documents = metrag_filter(documents, query, "finance")
    #print(f"Documents:\n{documents}")
    #result = rerank_docs(mod_query, documents)

    #documentlist = [doc.document.text for doc in result.results]
    documentlist = [doc['text'] for doc in documents]
    context = "\n\n".join(documentlist)
    prompt = f"""You are a helpful chat assistant that helps create a summary of the following context: '{context}', in light of the query: '{query}'.
                You must keep in mind that you are an expert in the field of finance, and that the response you generate should be tailored accordingly.
            """
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content
    return documents, response

def single_plan_rag_step_query(step):
    query_llm = ChatOpenAI(model="gpt-4o-mini")
    query_prompt = f"""You are a helpful prompt engineering assistant that must generate a query to feed to an LLM based on the given step in a multi-step plan.
        The step you must generate a query for is: {step}
        The query you generate should be clear and concise, and should be designed to retrieve the most relevant documents and information for the given step.
        It should be a query and not a statement, and must be no longer than 2 sentences.
        You must keep in mind that you are an expert in the field of finance, and that the query you generate should be tailored accordingly.
        """
    query_ = query_llm.invoke(query_prompt).content
    return query_

def step_executor(step):
    query_ = single_plan_rag_step_query(step)
    documents, response = single_retriever_finance_agent(query_)
    return documents, response


def multi_retrieval_finance_agent(query):
    """Answer complex finance related queries by running them through a multi-retrieval process based on PlanRAG"""
    plan = plan_rag_query(query, "finance")
    dict_store = {}
    resp_dict = {}
    documents = []
    response = []
    print(f"Plan:\n{plan}")
    
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(step_executor, step): i for i, step in enumerate(plan.split("\n")) if step
        }
        for future in as_completed(futures):
            i = futures[future]
            docs, resp = future.result()
            dict_store[i] = docs
            resp_dict[i] = resp
    for i in sorted(dict_store.keys()):
        documents.extend(dict_store[i])
        response.extend(resp_dict[i])
    modified_query = hyde_query(query) # For the complex query, do we need HyDE?

    result = rerank_docs(query, documents) 

    documents = [doc.document.text for doc in result.results]
    #documents = [doc['text'] for doc in documents]
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
            You must keep in mind that you are an expert in the field of finance, and that the response you generate should be tailored accordingly.
            """

    #print("Prompt:\n", prompt)
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content
    return response
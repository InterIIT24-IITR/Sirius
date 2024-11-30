from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.reranker import rerank_docs
from langchain_openai import ChatOpenAI


def single_retrieval_legal_agent(query):
    """Answer simple legal related queries by running them through HyDe and then retrieve the documents"""

    modified_query = hyde_query(query)
    documents = retrieve_documents(modified_query)

    result = rerank_docs(modified_query, documents)
    documents = [doc.document.text for doc in result.results]
    context = "\n\n".join(documents)

    prompt = f"""You are a helpful chat assistant that helps answer query based on the given context.
            You will answer queries only on the basis of the following information: {context}
            Do not use outside knowledge to answer the query. If the answer is not contained in the provided information, just say that you don't know, don't try to make up an answer.
            You must keep in mind that you are a legal expert, and that the response you generate should be tailored accordingly.
            """

    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content

    return response

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

    return documents, response
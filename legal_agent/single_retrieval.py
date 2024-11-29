from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.reranker import rerank_docs
from langchain_openai import ChatOpenAI


def single_retrieval_legal_agent(query):
    """Answer simple finance related queries by running them through HyDe and then Retrieving the documents"""

    modified_query = hyde_query(query)
    documents = retrieve_documents(modified_query)
    # print(documents)

    result = rerank_docs(modified_query, documents)
    # print("asdfasdf >>>>> ", result.results[0].document.text)
    documents = [doc.document.text for doc in result.results]
    context = "\n\n".join(documents)
    #     retrieved_contexts = [doc["text"] for doc in documents]
    #     context = "\n\n".join(retrieved_contexts)
    #     print("context >>>>> ", context)
    prompt = f"""You are a helpful chat assistant that helps answer query based on the given context.
            You will answer queries only on the basis of the following information: {context}
            Do not use outside knowledge to answer the query. If the answer is not contained in the provided information, just say that you don't know, don't try to make up an answer.
            You must keep in mind that you are a legal expert, and that the response you generate should be tailored accordingly.
            """

    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content

    return response

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
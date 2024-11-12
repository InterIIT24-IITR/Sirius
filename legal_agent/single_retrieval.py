from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.reranker import rerank_docs
from langchain_openai import ChatOpenAI


def single_retrieval_legal_agent(query):
    """Answer simple finance related queries by running them through HyDe and then Retrieving the documents"""

    modified_query = hyde_query(query)
    documents = retrieve_documents(modified_query)
    documents = rerank_docs(modified_query, documents)

    context = "\n\n".join(documents)
    prompt = f"""You are a helpful chat assistant that helps answer query based on the given context.
            You will answer queries only on the basis of the following information: {context}
            Do not use outside knowledge to answer the query. If the answer is not contained in the provided information, just say that you don't know, don't try to make up an answer.
            """

    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt).content

    return response

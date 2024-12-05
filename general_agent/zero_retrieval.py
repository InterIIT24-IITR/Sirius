from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.reranker import rerank_docs
from common.metrag import metrag_filter
from langchain_openai import ChatOpenAI

def zero_retrieval_agent(query):
    """Answer extremely simple queries without any RAG-retrieval"""

    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(query).content

    return response
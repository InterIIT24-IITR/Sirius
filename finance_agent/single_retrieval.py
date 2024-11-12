from common.hyde import hyde_query
from rag.client import retrieve_documents
from common.reranker import rerank_docs
import openai

def single_retrieval_finance_agent(query):
    """Answer simple finance related queries by running them through HyDe and then Retrieving the documents"""

    modified_query = hyde_query(query) 
    documents = retrieve_documents(modified_query)
    documents = rerank_docs(modified_query, documents)
    
    prompt = ""

    response = openai.Completion.create(
        model="gpt-4o",
        prompt=prompt,
        max_tokens=150
    )

    return response.choices[0].text.strip()
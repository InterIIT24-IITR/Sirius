from rag.client import retrieve_documents
from langchain_openai import ChatOpenAI

from common.websearch import tavily_search

CORRECT_THRESHOLD=0.8
AMBIGUOUS_THRESHOLD=0.5

def corrective_rag(query, documents):
    total_score = 0
    doc_length = len(documents)
    for doc in documents:
        total_score += score_document_relevance(query, doc)
    total_score /= doc_length
    if total_score > CORRECT_THRESHOLD:
        return documents
    elif total_score > AMBIGUOUS_THRESHOLD:
        external_knowledge = tavily_search(query)
        return documents + external_knowledge
    else:
        return tavily_search(query)
    

def score_document_relevance(query, document):
    """Evaluate and return relevance of documents on a scale of 0-1"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    score = llm.invoke(
        f"""
        For the query: '{query}'
        
        Evaluate the relevance of the following document on a scale of 0-1 for answering the above query.
        
        Document: '{document}'
        
        Only output the score, up to 2 decimal places
        """
    ).content

    return score
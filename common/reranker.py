import os
import cohere

co = cohere.ClientV2(api_key=os.environ["COHERE_API_KEY"])

def rerank_docs(query, dat_arr):
    results = co.rerank(model="rerank-english-v3.0", query=query, documents=dat_arr, rank_fields=['name','info'],top_n=10, return_documents=True)
    return results    
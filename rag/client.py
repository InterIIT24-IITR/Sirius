from pathway.xpacks.llm.vector_store import VectorStoreClient
from rag.rrf import rerank_results

VECTOR_PORT = 8000
BM25_PORT = 7000
SPLADE_PORT = 9000
PATHWAY_HOST = "127.0.0.1"

vector_client = VectorStoreClient(
    host=PATHWAY_HOST,
    port=VECTOR_PORT,
)
bm25_client = VectorStoreClient(
    host=PATHWAY_HOST,
    port=BM25_PORT,
)
splade_client = VectorStoreClient(
    host=PATHWAY_HOST,
    port=SPLADE_PORT,
)
from concurrent.futures import ThreadPoolExecutor


def retrieve_documents(query: str):
    with ThreadPoolExecutor() as executor:
        vector_future = executor.submit(vector_client.query, query, 10)
        bm25_future = executor.submit(bm25_client.query, query, 10)
        splade_future = executor.submit(splade_client.query, query, 10)

        vector_results = vector_future.result()
        bm25_results = bm25_future.result()
        splade_results = splade_future.result()

    #  make single list of results
    results = []
    results.append(vector_results)
    results.append(bm25_results)
    results.append(splade_results)

    #  rerank results
    reranked_results = rerank_results(results)

    return reranked_results

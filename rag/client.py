from pathway.xpacks.llm.vector_store import VectorStoreClient

PATHWAY_PORT = 8000
PATHWAY_HOST = "127.0.0.1"

client = VectorStoreClient(
    host=PATHWAY_HOST,
    port=PATHWAY_PORT,
)

def retrieve_documents(query: str):
    """Retrieves the documents from the VectorStoreClient"""
    documents = client.query(query, k=5)
    return documents

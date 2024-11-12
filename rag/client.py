from pathway.xpacks.llm.vector_store import VectorStoreClient

PATHWAY_PORT = 8765
PATHWAY_HOST = "ed69-15-206-68-41.ngrok-free.app"
PATHWAY_HOST = "3.6.115.182"

client = VectorStoreClient(
    host=PATHWAY_HOST,
    port=PATHWAY_PORT,
)

def retrieve_documents(query: str):
    documents = client.query(query)
    return documents
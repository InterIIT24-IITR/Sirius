from swarm import Agent
from legal_agent.single_retrieval import single_retrieval_legal_agent
from legal_agent.multi_retrieval import multi_retrieval_legal_agent

def transfer_to_legal_agent() -> Agent:
    """Transfer legal related queries to expert agent"""
    return Agent(
        name="Legal Agent",
        instructions="You are an expert at routing legal queries to a single or multi-retrieval agent based on the complexity of the query",
        functions=[single_retrieval_legal_agent, multi_retrieval_legal_agent],
    )

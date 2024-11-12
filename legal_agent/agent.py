from swarm import Agent
from common.general_agent import transfer_to_general_agent
from legal_agent.single_retrieval import single_retrieval_legal_agent

def transfer_to_legal_agent() -> Agent:
    """Transfer finance related queries to expert agent"""
    return Agent(
        name="Legal Agent",
        instructions="You are an expert at answering legal queries",
        functions=[transfer_to_general_agent, single_retrieval_legal_agent]
    )   
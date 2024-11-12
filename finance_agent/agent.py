from swarm import Agent
from common.general_agent import transfer_to_general_agent
from finance_agent.single_retrieval import single_retrieval_finance_agent


def transfer_to_finance_agent() -> Agent:
    """Transfer finance related queries to expert agent"""
    return Agent(
        name="Finance Agent",
        instructions="You are an expert at answering financial queries",
        functions=[single_retrieval_finance_agent],
    )

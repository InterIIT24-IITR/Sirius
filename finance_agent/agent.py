from swarm import Agent
from finance_agent.single_retrieval import single_retrieval_finance_agent
from finance_agent.multi_retrieval import multi_retrieval_finance_agent


def transfer_to_finance_agent() -> Agent:
    """Transfer finance related queries to expert agent"""
    return Agent(
        name="Finance Agent",
        instructions="You are an expert at routing financial queries to a single or multi-retrieval agent based on the complexity of the query",
        functions=[single_retrieval_finance_agent, multi_retrieval_finance_agent],
    )

from swarm import Agent
# from finance_agent.single_retrieval import single_retrieval_finance_agent
from macro_agent.multi_retrieval import multi_retrieval_macro_agent

def transfer_to_macro_agent() -> Agent:
    """Transfer macro analysis queries to expert agent"""
    return Agent(
        name="Macro Agent",
        instructions="You are an expert at analyzing a particular product domain.",
        functions=[ multi_retrieval_macro_agent],
    )

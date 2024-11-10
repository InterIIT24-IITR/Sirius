from swarm import Agent

def transfer_to_finance_agent() -> Agent:
    """Transfer finance related queries to expert agent"""
    return Agent(
        name="Finance Agent",
        instructions="You are an expert at answering financial queries",
    )   
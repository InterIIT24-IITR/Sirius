from swarm import Agent

def transfer_to_legal_agent() -> Agent:
    """Transfer finance related queries to expert agent"""
    return Agent(
        name="Legal Agent",
        instructions="You are an expert at answering legal queries",
    )   
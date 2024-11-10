from swarm import Agent

def transfer_to_general_agent():
    """Transfer to agent which answers general queries"""
    return Agent(
        name="General Agent", 
        instructions="You are a helpful bot who only answers queries to the best of your knowledge while never hallucinating or lying."
        )
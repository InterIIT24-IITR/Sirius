from swarm import Agent

def answer_general_queries(messages) -> str:
    """
    Broad, open-ended questions that don’t require specific technical or detailed responses. 
    Example: What is machine learning?
    """
    return "General Agent called"

def answer_simple_queries(messages) -> str:
    """
    imple and specific questions with a clear, concise answer, often factual. 
    Example: "What is the capital of France?"
    """
    return "Simple Agent called"

def answer_complex_queries(messages) -> str:
    """
    In-depth questions that require layered or nuanced responses, sometimes involving multiple steps or considerations. 
    Example: "How does reinforcement learning differ from supervised learning, and what are some practical use cases?"
    """
    return "Complex Agent called"

def transfer_to_classifier() -> Agent:
    """Transfer to """
    return Agent(
        name="Classifier",
        instructions="You are an expert in routing auser question to agents which can answer general queries or finance specific queries or legal specific queries",
        functions=[answer_simple_queries, answer_simple_queries, answer_complex_queries],
)
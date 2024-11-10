from dotenv import load_dotenv
load_dotenv()

from swarm import Swarm, Agent
import swarm

from finance_agent.agent import finance_agent

client = Swarm()

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

def transfer_to_finance_agent():
    """Transfer finance related queries to expert agent"""
    return finance_agent


agent = Agent(
    name="AdaRAG",
    instructions="You are an expert in routing auser question to agents which can answer general queries or finance specific queries",
    functions=[answer_simple_queries,transfer_to_finance_agent],
)


messages = [{"role": "user", "content": "What were the best performing stocks in 2019?"}]

response = client.run(agent=agent, messages=messages, debug=True)
print(response.messages[-1]["content"])
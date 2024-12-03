from swarm import Agent
from finance_agent.agent import transfer_to_finance_agent
from sasuke.legal_agent.agent import transfer_to_legal_agent
from common.general_agent import transfer_to_general_agent

def adarag_agent():
    return Agent(
        name="AdaRAG",
        instructions="You are an expert in routing auser question to agents which can answer general queries or finance specific queries or legal specific queries",
        functions=[
            transfer_to_general_agent,
            transfer_to_finance_agent,
            transfer_to_legal_agent,
        ]
    )
from dotenv import load_dotenv

load_dotenv()

from swarm import Swarm, Agent

from finance_agent.agent import transfer_to_finance_agent
from legal_agent.agent import transfer_to_legal_agent
from common.general_agent import transfer_to_general_agent

client = Swarm()


agent = Agent(
    name="AdaRAG",
    instructions="You are an expert in routing auser question to agents which can answer general queries or finance specific queries or legal specific queries",
    functions=[
        transfer_to_general_agent,
        transfer_to_finance_agent,
        transfer_to_legal_agent,
    ],
)

input_prompt = input("Ask a question: ")

messages = [
    {
        "role": "user",
        "content": input_prompt,
    }
]

response = client.run(agent=agent, messages=messages, debug=True)
print(response.messages[-1]["content"])

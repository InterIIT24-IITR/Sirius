from dotenv import load_dotenv
from swarm import Swarm
from adarag import adarag_agent

load_dotenv()
client = Swarm()

input_prompt = input("Ask a question: ")

messages = [
    {
        "role": "user",
        "content": input_prompt,
    }
]

response = client.run(agent=adarag_agent, messages=messages, debug=True)
print(response.messages[-1]["content"])

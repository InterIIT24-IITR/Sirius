from dotenv import load_dotenv
from swarm import Swarm
from adarag import adarag_agent
from guardrail.guard import guardrail

load_dotenv()
client = Swarm()

def run_pipeline(query):
    messages = [
        {
            "role": "user",
            "content": query,
        }
    ]

    safe, unsafe_category = guardrail(messages)
    if not safe:
        print(unsafe_category)
        return

    response = client.run(agent=adarag_agent, messages=messages, debug=True)

    safe, unsafe_category = guardrail(response.messages)
    if not safe:
        print(unsafe_category)
        return

    print(response.messages[-1]["content"])

input_prompt = input("Ask a question: ")
run_pipeline(input_prompt)
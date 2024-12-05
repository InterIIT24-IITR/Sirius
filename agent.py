from dotenv import load_dotenv
from swarm import Swarm
from common.adarag import adarag_agent
from guardrail.guard import guardrail
import logging
import os

load_dotenv()

logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
)
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
        return "Sorry we can't answer the request"

    response = client.run(agent=adarag_agent(), messages=messages, debug=True)
    answer = response.messages[-1]["content"]

    messages += [
        {
            "role": "assistant",
            "content": answer,
        }
    ]

    safe, unsafe_category = guardrail(messages)
    if not safe:
        print(unsafe_category)
        return "Sorry we can't answer the request"
    
    print(answer)
    return answer


if __name__ == "__main__":
    input_prompt = input("Enter your prompt: ")
    run_pipeline(input_prompt)

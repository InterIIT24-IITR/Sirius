from langchain_openai import ChatOpenAI
import requests


def call_llm(prompt):
    try:
        return call_openai_4o_mini(prompt)
    except:
        try:
            return call_llama_7b(prompt)
        except:
            return "Error: No LLM model available."


def call_llama_7b(prompt):
    response = requests.post(
        "https://8003-01jdya9bpnhj5dqyfzh17zdghv.cloudspaces.litng.ai/predict",
        json={"input": prompt},
    )
    return response.json()["output"]["content"]


def call_openai_4o_mini(prompt):
    llm = ChatOpenAI(model="gpt-4o-mini")
    return llm.invoke(prompt).content

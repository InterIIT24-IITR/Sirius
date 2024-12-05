from langchain_openai import ChatOpenAI

def call_llm(prompt):
    try:
        return call_openai_4o_mini(prompt)
    except:
        try:
            return call_llama_7b(prompt)
        except:
            return "Error: No LLM model available."

def call_llama_7b(prompt):
    pass

def call_openai_4o_mini(prompt):
    llm = ChatOpenAI(model="gpt-4o-mini")
    return llm.invoke(prompt).content

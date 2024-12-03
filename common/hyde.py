from langchain_openai import ChatOpenAI

def hyde_query(query):
    llm = ChatOpenAI(model="gpt-4o-mini")
    hypothetical_doc = llm.invoke(
        f"Write a detailed explanation or passage on: '{query}'"
    ).content

    return hypothetical_doc

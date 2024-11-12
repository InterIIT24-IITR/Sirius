import openai
from rag.client import retrieve_documents

def hyde_query(query):
    hypothetical_doc = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Write a detailed explanation or passage on: '{query}'",
        max_tokens=150
    ).choices[0].text.strip()

    return hypothetical_doc
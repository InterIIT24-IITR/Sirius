from rag.client import retrieve_documents
from langchain_openai import ChatOpenAI


def planrag_query(query, agent="finance"):
    llm = ChatOpenAI(model="gpt-4o-mini")
    planquery = llm.invoke(
        f"""
        You are a helpful AI agent.
        You are tasked with writing a detailed step-by-step plan to answer the complex query given to you, which is: '{query}'.
        Your plan should include steps as to process each part of the query.
        This is done by breaking down the query into sub-parts, then determining retrieval points for each sub-part, followed by finally retrieving the documents for each sub-part along with a description of how the parts should be combined to form the final answer.
        Answer this question as a RAG planning agent and assume you have access to the appropriate documents and data as is needed.
        The steps you generate need to be clear, and should be written in a way that they can be input to another RAG model as queries for retrieval and step-by-step processing.
        Ensure each step of the plan is a separate line in the message and that can also be used a query for retrieval by another RAG agent.
        Put primary focus on the quality of the query for the RAG agent.
        Do NOT output a plan with more than 5 steps."""
    ).content

    # Add agent-specific prompts?

    return planquery

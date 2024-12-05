from rag.client import retrieve_documents
from langchain_openai import ChatOpenAI


def plan_rag_query(query, agent = "finance"):
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    if agent=="macro":
        plan_query = llm.invoke(
            f"""
            You are a helpful AI agent.
            You are tasked with writing a detailed step-by-step plan to answer the complex query given to you, which is: '{query}'.
            Your plan should focus specifically on conducting a domain analysis of the product and providing market insights about trends, opportunities, and competitors.
            Break down the query into sub-parts, determine retrieval points for each sub-part, and specify how to retrieve the relevant documents for each sub-part.
            Answer this question as a RAG planning agent and assume you have access to the appropriate documents and data as needed.
            The steps you generate need to be clear and should be written in a way that they can be input to another RAG model as queries for retrieval and step-by-step processing.
            Ensure each step of the plan is a separate line in the message and can also be used as a query for retrieval by another RAG agent.
            Put primary focus on the quality of the query for the RAG agent.
            Do NOT output a plan with more than 5 steps and try to minimize the number of steps to as low as possible, preferably 2 or 3.
            Do NOT include a final step to synthesize the information, only steps for retrieval as that will be done separately.

            Here is the step-by-step plan to conduct a domain analysis of the product and provide market insights:
            1. Identify the specific product field from the query (e.g., smartphones) and list all major companies in that field (e.g., Apple, Samsung, Xiaomi).
            2. Retrieve comprehensive data on each identified company, including market share, product offerings, recent innovations, financial performance, and customer demographics.
            3. Analyze the competitive landscape by identifying key competitors, their strengths and weaknesses, and their market strategies.
            4. Investigate current market trends related to the product field, focusing on consumer preferences, technological advancements, and regulatory influences.
            5. Identify potential opportunities for growth and innovation within the product field, considering emerging markets and shifts in consumer behavior.
            """
        ).content
        return plan_query

    plan_query = llm.invoke(
        f"""
        You are a helpful AI agent.
        You are tasked with writing a detailed step-by-step plan to answer the complex query given to you, which is: '{query}'.
        Your plan should include steps as to process each part of the query.
        This is done by breaking down the query into sub-parts, then determining retrieval points for each sub-part, followed by finally retrieving the documents for each sub-part along with a description of how the parts should be combined to form the final answer.
        Answer this question as a RAG planning agent and assume you have access to the appropriate documents and data as is needed.
        The steps you generate need to be clear, and should be written in a way that they can be input to another RAG model as queries for retrieval and step-by-step processing.
        Ensure each step of the plan is a separate line in the message and that can also be used a query for retrieval by another RAG agent.
        Put primary focus on the quality of the query for the RAG agent.
        Do NOT output a plan with more than 3 steps and try to minimise the number of steps to as low as possible, preferrably 2 or 3.
        Do NOT include a final step to synthesize the information, only steps for retrieval as that will be done separately.
        """
    ).content

    # TODO: Add agent-specific prompts

    return plan_query

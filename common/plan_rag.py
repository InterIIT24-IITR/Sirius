from langchain_openai import ChatOpenAI

def plan_rag_query(query, agent = "finance", **kwargs):
    llm = ChatOpenAI(model="gpt-4o-mini")

    if agent == "M&A":
        companies = kwargs.get("companies")
        input_docs = kwargs.get("input_docs")
        output_doc = kwargs.get("output_doc")
        if companies is None or len(companies) != 2:
            raise ValueError("The 'companies' argument is required for the M&A agent.")
        if input_docs is None:
            raise ValueError("The 'input_docs' argument is required for the M&A agent.")
        if output_doc is None:
            raise ValueError("The 'output_doc' argument is required for the M&A agent.")

        prompt = f"""
        You are a helpful AI agent.
        You are tasked with writing a detailed step-by-step plan to formulate a merger and acquisition agreement between two companies, {companies[0]} and {companies[1]}.
        Currently, you are in the process of drafting the {output_doc} document.
        For this, you will break down the process into multiple steps, each of which will involve retrieving relevant information from the following documents: {', '.join(input_docs)}.
        Your plan should include steps to retrieve information from each document and how to combine them to form the final agreement.
        Answer this question as a RAG planning agent and assume you have access to the appropriate documents and data as is needed.
        The steps you generate need to be clear, and should be written in a way that they can be input to another RAG model as queries for retrieval and step-by-step processing.
        Ensure each step of the plan is a separate line in the message and that can also be used a query for retrieval by another RAG agent.
        Put primary focus on the quality of the query for the RAG agent.
        Output a plan with a minimal number of steps, preferrably 3-4.
        """

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

    return plan_query

def single_plan_rag_step_query(step):
    query_llm = ChatOpenAI(model="gpt-4o-mini")
    query_prompt = f"""You are a helpful prompt engineering assistant that must generate a query to feed to an LLM based on the given step in a multi-step plan.
        The step you must generate a query for is: {step}
        The query you generate should be clear and concise, and should be designed to retrieve the most relevant documents and information for the given step.
        It should be a query and not a statement, and must be no longer than 2 sentences.
        You must keep in mind that you are an expert in the field of finance, and that the query you generate should be tailored accordingly.
        """
    query_ = query_llm.invoke(query_prompt).content
    return query_
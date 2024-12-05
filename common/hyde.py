from common.llm import call_llm
from swarm.util import debug_print


def hyde_query(query):
    debug_print(True, f"Processing tool call: {hyde_query.__name__}")

    hypothetical_doc = call_llm(
        f"""Write a detailed explanation or passage on: '{query}'
        Make sure the document is not too long, two paragraphs at max, less than 200 words overall.
        Do NOT output in markdown format, remove all special characters and formatting.
        If you do not have access to the information, you are allowed to hallucinate facts and figures.
        """
    )
    # print("HyDE Doc\n",hypothetical_doc)
    return hypothetical_doc

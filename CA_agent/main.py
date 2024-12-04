import os, uuid, time
from langchain_openai import ChatOpenAI
from pathway.xpacks.llm.parsers import ParseUnstructured
from pathway.xpacks.llm.vector_store import VectorStoreClient
from common.plan_rag import plan_rag_query, single_plan_rag_step_query
from CA_agent.multi_retrieval import multi_retrieval_CA_agent


VECTOR_PORT = 8100
PATHWAY_HOST = "127.0.0.1"

vector_client = VectorStoreClient(
    host=PATHWAY_HOST,
    port=VECTOR_PORT,
)

def retrieve_documents(query: str):
    return vector_client.query(query, 10)

def parse_document(docpath):
    with open(docpath) as f:
        paraphrase = f.read()
        parser = ParseUnstructured(mode='single')
        parsed = parser.__call__(paraphrase)
        parsed_ = parser.__call__(paraphrase)
        parsed_ = str(parsed_)
        parsed_ = parsed_[28:-2]
        return parsed_

def add_user_document(documentpath):
    # Apart from this make sure the document is added to the vector store
    parsed_doc = parse_document(documentpath)
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = f"""
    You are a helpful AI agent.
    You are a knowledgeable agent aware of the field of chartered accountancy and finance. Particularly, you are
    aware of the income tax laws and regulations in India.
    You are tasked with adding the following document to your database: '{parsed_doc}'.
    The document is a document input by a user and is a statement of their income and expenses for the year.
    Your job is to parse the document and extract the relevant information from it, such as the income, expenses, and any other relevant information.
    You should return the extracted information in a structured format that is easy to understand and is descriptive of the document's content.
    """
    summarised_doc = llm.invoke(prompt).content
    prompt = f"""
    You are a helpful AI agent.
    Return a small one-line descriptor of the content of this document: '{parsed_doc}'.
    You have generated a summary of the document: '{summarised_doc}'
    Now you need to return a one-line descriptor for the same document.sum
    """
    point_doc = llm.invoke(prompt).content
    return summarised_doc, point_doc

def add_to_info(documentpath, info_dict):
    summ_doc, point_doc = add_user_document(documentpath)
    info_dict[point_doc] = summ_doc
    return info_dict

RELEVANT_SECTIONS = [["80C", "80CC", "80CCA", "80CCB", "80CCC", "80CCD", "80CCE"], ["80CCF", "80CCG", "80CCH"], ["80D", "80DD", "80DDB"], ["80E", "80EE", "80EEA", "80EEB"], ["80G", "80GG", "80GGA", "80GGB", "80GGC"]]

def single_section_handler(info_dict, section):
    response = multi_retrieval_CA_agent(section, info_dict)
    query = f"""
    Identify and classify the sections of the income tax act that are applicable for tax deduction in context of a user who has given you documents related to the same.
    The sections that are relevant are: {", ".join(section)}
    The documents that are input by the user are as follows:{'\n\n'.join(info_dict.keys())}
    """
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = multi_retrieval_CA_agent(query, section, info_dict)
    prompt_new = f"""
    {query}
    You also have the following response based on a multi-retrieval RAG-based process which has been crafted to assist you in this task:
    {response}
    Output a response that clearly mentions which sections of tax deduction are applicable to the user, and which sections aren't, and those which are ambiguous.
    The response should be structured as a JSON input with the following format as an example:
    {{
        "applicable_sections": ["80C", "80CC", "80CCA"],
        "non_applicable_sections": ["80CCF", "80CCG"],
        "probable_sections": ["80D", "80DD"]
    }}
    """
    response = llm.invoke(prompt_new).content
    return response

def overall_handler(info_dict):
    responses = []
    for section in RELEVANT_SECTIONS:
        response = single_section_handler(info_dict, section)
        responses.append(response)
    prompt_new = f"""
    You are a helpful AI agent.
    You were tasked with identifying which sections of the income tax act are applicable for tax deduction in context of a user who has given you documents related to the same.
    You have successfully identified the sections that are applicable and those that are not.
    You have also identified the sections that are ambiguous and require further clarification.
    You have generated the following responses for different groups of related sections:
    {"\n\n".join(responses)}
    The last step is to combine all the responses into a single JSON output that clearly mentions which sections of tax deduction are applicable to the user, and which sections aren't, and those which are ambiguous.
    The response should be structured as a JSON input with the following format as an example:
    {{
        "applicable_sections": ["80C", "80CC", "80CCA"],
        "non_applicable_sections": ["80CCF", "80CCG"],
        "probable_sections": ["80D", "80DD"]
    }}
    """
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(prompt_new).content
    return response

### For the developers
# Doc input hoga, usko vectorstore mein daalna, and ensure I have a path to pass to add to info
# Maintain an info_dict for the user
# Uske baad simply call the overall_handler with the info_dict and it will return the response
# Based on the response, display on the user interface
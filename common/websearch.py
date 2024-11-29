from tavily import TavilyClient
from langchain_community.document_loaders import BraveSearchLoader
from linkup import LinkupClient
import os

def tavily_search(query):
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_KEY"])
    response = tavily_client.search(query=query)
    docs = [result['content'] for result in response['results']]
    return docs

def brave_search(query):
    loader = BraveSearchLoader(
        query=query, api_key=os.environ["BRAVE_KEY"], search_kwargs={"count": 5}
    )
    docs = loader.load()
    return docs

def linkup_search(query):
    client = LinkupClient(api_key=os.environ["LINKUP_KEY"])
    response = client.search(
        query=query,
        depth="deep",
        output_type="sourcedAnswer"
    )
    return response.answer

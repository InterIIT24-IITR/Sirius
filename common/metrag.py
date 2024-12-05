from langchain_openai import ChatOpenAI
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np
from swarm.util import debug_print


def metrag_score(document, query, agent):
    debug_print(True, f"Processing tool call: {metrag_score.__name__}")
    llm_utility = ChatOpenAI(model="gpt-4o-mini")
    good_utility = "The document is absolutely outstanding and exceeds expectations in addressing the query. It is exceptionally relevant, brilliantly complete, impeccably accurate, and presented with crystal-clear clarity. Its consistency is flawless, making it an invaluable and extraordinary resource of immense utility!"
    bad_utility = "The document is utterly disappointing and fails to meet even basic expectations in addressing the query. It lacks relevance, is incomplete, riddled with inaccuracies, and confusingly presented. Its inconsistency undermines any potential value, making it a frustrating and entirely unhelpful resource."
    prompt = f"""
    You are a helpful AI agent.
    You are tasked with evaluating the utility of a document in answering a query.
    Certain criteria for utility are defined as follows:
    - Relevance: How relevant is the document to the query?
    - Completeness: How complete is the information in the document?
    - Accuracy: How accurate is the information in the document?
    - Clarity: How clear and concise is the information in the document?
    - Consistency: How consistent is the information in the document?
    Point to Note: A document may not be semantically similar to the query but may still be useful in answering the query.
    A query which has high utility will be able to answer the query effectively and for such a query a possible output could be:
    '{good_utility}'
    A query which has low utility will not be able to answer the query effectively and for such a query a possible output could be:
    '{bad_utility}'
    Evaluate the utility of the following document in answering the query:
    '{query}'.
    The document is as follows:
    '{document}'
    """
    if agent == "finance":
        added_info = """
        You must keep in mind that you are an expert in the field of finance, and that the response you generate should be tailored accordingly.
        For instance, for relevancy you also need to consider whether the document contains the relevant terms and whether it is focused on the company which is the same as the query.
        If there is no reference to the company of the query in the document, it is not relevant, then output the same output as that for a low utility document.
        """
        prompt = prompt + added_info

    response = llm_utility.invoke(prompt).content
    return SentimentIntensityAnalyzer().polarity_scores(response).get("compound")


def metrag_filter(documents, query, agent):
    debug_print(True, f"Processing tool call: {metrag_filter.__name__}")
    score_dict = [(doc, metrag_score(doc, query, agent)) for doc in documents]
    metrag_threshold = np.percentile(list([b for (a, b) in score_dict]), 25)
    return [doc for (doc, score) in score_dict if score > metrag_threshold]

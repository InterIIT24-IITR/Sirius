from typing import Dict, Any, Tuple
import json

class EvaluationCriteria:
    relevance_threshold: float = 0.7
    quality_threshold: float = 0.7
    evaluation_aspects = [
        "relevance",
        "factual_accuracy",
        "completeness",
        "coherence",
        "context_usage"
    ]

class LLMEvaluatorAgent:
    def __init__(
        self,
        llm_client,
        criteria
    ):
        self.llm = llm_client
        self.criteria = criteria

    def create_evaluation_prompt(
        self, 
        query: str, 
        response: str, 
        context: str = None
    ) -> str:
        """Create a structured prompt for LLM evaluation."""
        return f"""You are an expert evaluator for RAG systems. Evaluate the following response based on these criteria:

Query: {query}

Response to evaluate: {response}

Retrieved Context: {context if context else 'No context provided'}

For each aspect below, provide:
1. A score between 0.0 and 1.0
2. A brief justification

Evaluate these aspects:
- Relevance: How well does the response address the query?
- Factual Accuracy: Are the facts consistent with the context?
- Completeness: Does the response fully address all aspects of the query?
- Coherence: Is the response well-structured and logical?
- Context Usage: How effectively is the provided context utilized?

Provide your evaluation in JSON format:
{
    "aspect_name": {
        "score": float,
        "justification": "string"
    }
}"""

    def evaluate_response(
        self, 
        query: str, 
        response: str, 
        context: str = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate response using LLM-based analysis.
        Returns (is_acceptable, detailed_metrics)
        """
        evaluation_prompt = self.create_evaluation_prompt(query, response, context)

        llm_response = self.llm.generate(evaluation_prompt)

        try:
            evaluation_results = json.loads(llm_response)

            metrics = {
                aspect: {
                    "score": evaluation_results[aspect]["score"],
                    "justification": evaluation_results[aspect]["justification"]
                }
                for aspect in self.criteria.evaluation_aspects
            }

            overall_score = sum(
                metrics[aspect]["score"] 
                for aspect in self.criteria.evaluation_aspects
            ) / len(self.criteria.evaluation_aspects)

            relevance_score = metrics["relevance"]["score"]

            is_acceptable = (
                relevance_score >= self.criteria.relevance_threshold and
                overall_score >= self.criteria.quality_threshold
            )

            metrics["overall_score"] = overall_score

            return is_acceptable, metrics

        except json.JSONDecodeError:
            return False, {"error": "Failed to parse LLM evaluation"}
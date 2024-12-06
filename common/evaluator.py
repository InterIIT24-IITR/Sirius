from typing import Dict, Any, Tuple
from dataclasses import dataclass
import json

@dataclass
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
        llm_client,  # Your preferred LLM client (e.g., OpenAI, Anthropic)
        criteria: EvaluationCriteria = EvaluationCriteria()
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

        # Get LLM evaluation
        llm_response = self.llm.generate(evaluation_prompt)

        try:
            evaluation_results = json.loads(llm_response)

            # Calculate overall metrics
            metrics = {
                aspect: {
                    "score": evaluation_results[aspect]["score"],
                    "justification": evaluation_results[aspect]["justification"]
                }
                for aspect in self.criteria.evaluation_aspects
            }

            # Calculate aggregate scores
            overall_score = sum(
                metrics[aspect]["score"] 
                for aspect in self.criteria.evaluation_aspects
            ) / len(self.criteria.evaluation_aspects)

            relevance_score = metrics["relevance"]["score"]

            # Determine if response meets thresholds
            is_acceptable = (
                relevance_score >= self.criteria.relevance_threshold and
                overall_score >= self.criteria.quality_threshold
            )

            metrics["overall_score"] = overall_score

            return is_acceptable, metrics

        except json.JSONDecodeError:
            return False, {"error": "Failed to parse LLM evaluation"}

class EnhancedRAGPipeline:
    def __init__(self, llm_client):
        self.evaluator = LLMEvaluatorAgent(llm_client)

    def generate_response(self, query: str, max_retries: int = 2) -> Dict[str, Any]:
        """Enhanced pipeline with LLM evaluation and detailed feedback."""
        attempts = []

        for attempt in range(max_retries):
            # Initial response generation
            response = self._generate_initial_response(query)
            context = self._get_context(query)

            # Evaluate response
            is_acceptable, metrics = self.evaluator.evaluate_response(
                query, response, context
            )

            attempts.append({
                "attempt": attempt + 1,
                "response": response,
                "metrics": metrics
            })

            if is_acceptable:
                return {
                    "final_response": response,
                    "evaluation_metrics": metrics,
                    "attempts": attempts
                }

            # Apply fallback strategies based on specific failures
            if metrics.get("relevance", {}).get("score", 0) < self.evaluator.criteria.relevance_threshold:
                response = self._call_crag_agent(query)
            else:
                response = self._call_llm_fallback(query, context)

        # Return best attempt if all retries fail
        best_attempt = max(attempts, key=lambda x: x["metrics"].get("overall_score", 0))
        return {
            "final_response": best_attempt["response"],
            "evaluation_metrics": best_attempt["metrics"],
            "attempts": attempts,
            "warning": "Max retries reached without meeting quality thresholds"
        }
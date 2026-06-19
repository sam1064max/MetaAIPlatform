import logging
from typing import Any
from datetime import datetime, timezone

logger = logging.getLogger("metaai.gateway")


MODEL_PRICING = {
    "gpt-5": {"input": 15.0, "output": 60.0},
    "gpt-4o": {"input": 2.50, "output": 10.0},
    "claude-sonnet-4": {"input": 3.0, "output": 15.0},
    "claude-3.5": {"input": 3.0, "output": 15.0},
    "gemini-2": {"input": 1.25, "output": 5.0},
    "deepseek-v3": {"input": 0.50, "output": 2.0},
    "ollama": {"input": 0.0, "output": 0.0},
}

MODEL_COMPLEXITY_SCORES = {
    "gpt-5": 10,
    "gpt-4o": 8,
    "claude-sonnet-4": 9,
    "claude-3.5": 7,
    "gemini-2": 6,
    "deepseek-v3": 7,
    "ollama": 4,
}

FALLBACK_CHAINS = {
    "gpt-5": ["claude-sonnet-4", "gpt-4o"],
    "gpt-4o": ["claude-3.5", "deepseek-v3"],
    "claude-sonnet-4": ["gpt-4o", "deepseek-v3"],
    "deepseek-v3": ["gemini-2", "ollama"],
}


class ModelGateway:
    def __init__(self):
        self.cost_tracker: dict[str, dict] = {}

    async def chat_completion(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> dict[str, Any]:
        original_model = model
        last_error = None

        models_to_try = [model] + FALLBACK_CHAINS.get(model, [])

        for attempt_model in models_to_try:
            try:
                logger.info("Attempting chat completion with model: %s", attempt_model)
                result = await self._call_model(attempt_model, messages, temperature, max_tokens, **kwargs)
                self._track_cost(attempt_model, result)
                result["model_used"] = attempt_model
                result["fallback_used"] = attempt_model != original_model
                result["timestamp"] = datetime.now(timezone.utc).isoformat()
                return result
            except Exception as e:
                last_error = e
                logger.warning("Model %s failed: %s. Trying fallback...", attempt_model, str(e))
                continue

        logger.error("All models failed for original request '%s'", original_model)
        return await self._mock_response(original_model, messages, error=str(last_error))

    async def _call_model(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> dict[str, Any]:
        if model.startswith("gpt"):
            return await self._mock_call(model, messages, temperature, max_tokens)
        elif model.startswith("claude"):
            return await self._mock_call(model, messages, temperature, max_tokens)
        elif model.startswith("gemini"):
            return await self._mock_call(model, messages, temperature, max_tokens)
        elif model.startswith("deepseek"):
            return await self._mock_call(model, messages, temperature, max_tokens)
        elif model == "ollama":
            return await self._mock_call(model, messages, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported model: {model}")

    async def _mock_call(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "Hello")
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")

        input_tokens = len(user_msg) + len(system_msg)
        output_tokens = min(max(50, len(user_msg) * 2), max_tokens)

        pricing = MODEL_PRICING.get(model, {"input": 1.0, "output": 4.0})
        cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])

        return {
            "content": (
                f"Based on analysis using {model}: "
                f"I've processed your request regarding '{user_msg[:100]}'. "
                f"The market indicators suggest a positive outlook with moderate volatility. "
                f"Recommended allocation: 60% equities, 30% fixed income, 10% alternatives."
            ),
            "model": model,
            "total_tokens": input_tokens + output_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(cost, 6),
            "finish_reason": "stop",
        }

    async def _mock_response(
        self,
        model: str,
        messages: list[dict],
        error: str | None = None,
    ) -> dict[str, Any]:
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        return {
            "content": f"Mock response for '{user_msg[:100]}' (model: {model})",
            "model": model,
            "total_tokens": 50,
            "input_tokens": 25,
            "output_tokens": 25,
            "cost": 0.001,
            "finish_reason": "stop",
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _track_cost(self, model: str, result: dict):
        if model not in self.cost_tracker:
            self.cost_tracker[model] = {"total_cost": 0.0, "total_tokens": 0, "call_count": 0}
        self.cost_tracker[model]["total_cost"] += result.get("cost", 0)
        self.cost_tracker[model]["total_tokens"] += result.get("total_tokens", 0)
        self.cost_tracker[model]["call_count"] += 1

    def get_cost_summary(self) -> dict[str, Any]:
        total_cost = sum(v["total_cost"] for v in self.cost_tracker.values())
        total_tokens = sum(v["total_tokens"] for v in self.cost_tracker.values())
        total_calls = sum(v["call_count"] for v in self.cost_tracker.values())
        return {
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_calls": total_calls,
            "per_model": self.cost_tracker,
        }

    @staticmethod
    def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = MODEL_PRICING.get(model, {"input": 1.0, "output": 4.0})
        return (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])

    @staticmethod
    def score_complexity(query: str) -> int:
        complexity = 1
        financial_terms = ["portfolio", "derivative", "option", "swap", "risk", "compliance",
                          "regulatory", "merger", "acquisition", "valuation", "forecast"]
        for term in financial_terms:
            if term in query.lower():
                complexity += 1

        if len(query) > 200:
            complexity += 1
        if "?" in query:
            complexity += 1

        return min(complexity, 10)

    @staticmethod
    def select_model(query: str, preferred_model: str = "gpt-4o") -> str:
        complexity = ModelGateway.score_complexity(query)
        if complexity >= 8:
            return "gpt-5"
        elif complexity >= 6:
            return "claude-sonnet-4"
        elif complexity >= 4:
            return "gpt-4o"
        elif complexity >= 2:
            return "deepseek-v3"
        return "ollama"


model_gateway = ModelGateway()

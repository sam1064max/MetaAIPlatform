import logging
from typing import Any

logger = logging.getLogger("metaai.workflows")


def plan_and_execute_pattern() -> dict[str, Any]:
    return {
        "name": "plan_and_execute",
        "description": "Agent plans steps first, then executes them sequentially",
        "config": {
            "planner": {"model": "gpt-4o", "temperature": 0.3},
            "executor": {"model": "gpt-4o", "temperature": 0.5, "max_retries": 3},
            "reviewer": {"model": "gpt-4o-mini", "temperature": 0.2},
            "max_steps": 10,
            "stop_on_error": True,
        },
        "nodes": {
            "planner": {
                "type": "llm",
                "system_prompt": "You are a financial planning agent. Break down the user request into a sequence of steps.",
                "output_key": "plan",
            },
            "executor": {
                "type": "tool_executor",
                "tools": ["MarketDataServer", "PortfolioServer", "ResearchServer"],
            },
            "reviewer": {
                "type": "llm",
                "system_prompt": "Review the execution results for quality and correctness.",
                "output_key": "review",
            },
        },
        "edges": [
            {"from": "planner", "to": "executor"},
            {"from": "executor", "to": "reviewer"},
        ],
    }


def react_pattern() -> dict[str, Any]:
    return {
        "name": "react",
        "description": "Reasoning + Acting loop: think, act, observe, repeat",
        "config": {
            "model": "gpt-4o",
            "temperature": 0.5,
            "max_iterations": 15,
            "max_tokens": 4096,
        },
        "system_prompt": (
            "You are a ReAct financial agent. You have access to financial tools. "
            "Reason about the user's request, decide which tool to call, "
            "observe the result, and continue until you can provide a final answer. "
            "Always verify market data before making recommendations."
        ),
        "tools": ["MarketDataServer", "PortfolioServer", "ResearchServer", "CRMServer"],
        "stop_conditions": ["final_answer", "max_iterations_reached", "error"],
    }


def supervisor_pattern() -> dict[str, Any]:
    return {
        "name": "supervisor",
        "description": "Supervisor delegates tasks to specialist sub-agents",
        "config": {
            "supervisor": {"model": "gpt-4o", "temperature": 0.3},
            "specialists": {
                "market_analyst": {
                    "model": "gpt-4o",
                    "temperature": 0.4,
                    "tools": ["MarketDataServer"],
                    "description": "Analyzes market trends and conditions",
                },
                "portfolio_manager": {
                    "model": "gpt-4o",
                    "temperature": 0.5,
                    "tools": ["PortfolioServer"],
                    "description": "Manages and optimizes portfolios",
                },
                "risk_analyst": {
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "tools": ["ResearchServer"],
                    "description": "Assesses risk and compliance",
                },
                "client_advisor": {
                    "model": "gpt-4o",
                    "temperature": 0.6,
                    "tools": ["CRMServer", "PortfolioServer"],
                    "description": "Handles client relationships and reporting",
                },
            },
            "max_delegations": 5,
            "require_approval_for": ["trade", "large_transfer"],
        },
        "supervisor_prompt": (
            "You are a supervisor agent for a financial advisory firm. "
            "Delegating tasks to specialist sub-agents. "
            "Ensure compliance with regulations before any action."
        ),
    }


def get_pattern(name: str) -> dict[str, Any] | None:
    patterns = {
        "plan_and_execute": plan_and_execute_pattern,
        "react": react_pattern,
        "supervisor": supervisor_pattern,
    }
    factory = patterns.get(name)
    if factory:
        return factory()
    logger.warning("Workflow pattern '%s' not found", name)
    return None


def list_patterns() -> list[dict[str, Any]]:
    return [
        plan_and_execute_pattern(),
        react_pattern(),
        supervisor_pattern(),
    ]

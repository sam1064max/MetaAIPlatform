import json
import logging
from typing import TypedDict, Any, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("metaai.graph")


class AgentState(TypedDict):
    input: str
    plan: list[str]
    current_step: int
    executed_steps: list[dict]
    tool_results: list[dict]
    output: str
    status: str
    error: Optional[str]
    requires_human_approval: bool
    human_feedback: Optional[str]
    trace: list[dict]


def create_initial_state(user_input: str) -> AgentState:
    return {
        "input": user_input,
        "plan": [],
        "current_step": 0,
        "executed_steps": [],
        "tool_results": [],
        "output": "",
        "status": "pending",
        "error": None,
        "requires_human_approval": False,
        "human_feedback": None,
        "trace": [],
    }


class StateGraph:
    def __init__(self):
        self.nodes: dict[str, Any] = {}
        self.edges: list[tuple[str, str, Optional[Any]]] = []
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, func: Any):
        self.nodes[name] = func
        if self.entry_point is None:
            self.entry_point = name

    def add_edge(self, source: str, target: str, condition: Optional[Any] = None):
        self.edges.append((source, target, condition))

    def set_entry_point(self, name: str):
        self.entry_point = name

    async def run(self, state: AgentState) -> AgentState:
        current = self.entry_point
        visited = set()
        max_steps = 50

        while current and len(visited) < max_steps:
            visited.add(current)
            node_fn = self.nodes.get(current)
            if not node_fn:
                state["error"] = f"Node '{current}' not found"
                state["status"] = "failed"
                break

            logger.info("Executing node: %s", current)
            try:
                state = await node_fn(state)
                state["trace"].append({"node": current, "status": state["status"]})
            except Exception as e:
                state["error"] = f"Node '{current}' failed: {str(e)}"
                state["status"] = "failed"
                break

            if state["status"] in ("failed", "completed", "awaiting_human"):
                break

            next_node = None
            for src, tgt, cond in self.edges:
                if src == current:
                    if cond is None:
                        next_node = tgt
                        break
                    elif callable(cond):
                        result = cond(state)
                        if result:
                            next_node = tgt
                            break
            current = next_node

        return state


def create_financial_agent_graph() -> StateGraph:
    graph = StateGraph()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def planner_node(state: AgentState) -> AgentState:
        input_text = state["input"].lower()

        if "portfolio" in input_text or "investment" in input_text:
            plan = [
                "retrieve_portfolio_data",
                "analyze_market_conditions",
                "generate_investment_recommendations",
                "review_recommendations",
            ]
        elif "risk" in input_text or "compliance" in input_text:
            plan = [
                "assess_risk_profile",
                "check_compliance_rules",
                "generate_risk_report",
            ]
        elif "research" in input_text or "analyze" in input_text:
            plan = [
                "gather_research_data",
                "synthesize_findings",
                "generate_analysis_report",
            ]
        elif "trade" in input_text or "order" in input_text:
            plan = [
                "validate_trade_parameters",
                "check_market_conditions",
                "request_human_approval",
                "execute_trade",
            ]
            state["requires_human_approval"] = True
        elif "customer" in input_text or "client" in input_text:
            plan = [
                "lookup_client_profile",
                "check_client_portfolio",
                "generate_client_report",
            ]
        else:
            plan = [
                "understand_request",
                "gather_information",
                "formulate_response",
            ]

        state["plan"] = plan
        state["current_step"] = 0
        state["status"] = "planning_complete"
        return state

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def executor_node(state: AgentState) -> AgentState:
        if state["current_step"] >= len(state["plan"]):
            state["status"] = "completed"
            return state

        step = state["plan"][state["current_step"]]
        logger.info("Executing step %d: %s", state["current_step"], step)

        from backend.tools.registry import ToolRegistry
        registry = ToolRegistry()

        step_result = {"step": step, "index": state["current_step"], "result": None, "status": "executing"}

        try:
            if step == "retrieve_portfolio_data":
                result = await registry.invoke_tool("PortfolioServer", action="get_portfolio")
            elif step == "analyze_market_conditions":
                result = await registry.invoke_tool("MarketDataServer", action="get_market_overview")
            elif step == "generate_investment_recommendations":
                result = {"recommendations": ["Buy AAPL", "Hold MSFT", "Sell TSLA"], "confidence": 0.85}
            elif step == "review_recommendations":
                result = {"review": "Recommendations align with portfolio strategy", "approved": True}
            elif step == "assess_risk_profile":
                result = {"risk_score": 72, "risk_level": "moderate", "max_drawdown": 0.15}
            elif step == "check_compliance_rules":
                result = {"compliant": True, "rules_checked": ["KYC", "AML", "Suitability"]}
            elif step == "generate_risk_report":
                result = {"summary": "Portfolio risk within acceptable parameters", "var_95": 0.032}
            elif step == "gather_research_data":
                result = await registry.invoke_tool("ResearchServer", action="get_research")
            elif step == "synthesize_findings":
                result = {"key_findings": ["Market trending bullish", "Tech sector leading"], "sources": 5}
            elif step == "generate_analysis_report":
                result = {"report": "Analysis complete", "recommendations": ["Increase tech allocation"]}
            elif step == "validate_trade_parameters":
                result = {"valid": True, "estimated_slippage": 0.001}
            elif step == "check_market_conditions":
                result = {"market_open": True, "volatility": "normal", "liquidity": "high"}
            elif step == "request_human_approval":
                state["requires_human_approval"] = True
                state["status"] = "awaiting_human"
                result = {"message": "Awaiting human approval for trade execution"}
            elif step == "execute_trade":
                result = {"order_id": "ORD-2024-001", "status": "filled", "price": 185.50, "quantity": 100}
            elif step == "lookup_client_profile":
                result = {"client_id": "CLT-001", "tier": "premium", "acv": 500000}
            elif step == "check_client_portfolio":
                result = {"holdings": ["AAPL", "MSFT", "GOOGL"], "total_value": 1250000}
            elif step == "generate_client_report":
                result = {"report_url": "/reports/client_CLT-001.pdf", "generated": True}
            elif step == "understand_request":
                result = {"interpretation": "General inquiry", "intent": "information"}
            elif step == "gather_information":
                result = {"data_points": 15, "relevance_score": 0.92}
            elif step == "formulate_response":
                result = {"response": "Based on available information, here is what I found..."}
            else:
                result = {"message": f"Executed step: {step}"}

            step_result["result"] = result
            step_result["status"] = "completed"
            state["executed_steps"].append(step_result)
            state["current_step"] += 1

            if not state["requires_human_approval"]:
                state["status"] = "executing"
            else:
                state["status"] = "awaiting_human"

        except Exception as e:
            step_result["status"] = "failed"
            step_result["error"] = str(e)
            state["executed_steps"].append(step_result)
            state["error"] = f"Step '{step}' failed: {str(e)}"
            state["status"] = "failed"

        return state

    async def reviewer_node(state: AgentState) -> AgentState:
        if state["status"] == "failed":
            return state

        steps_completed = len(state["executed_steps"])
        steps_total = len(state["plan"])
        completion_rate = steps_completed / max(steps_total, 1)

        if completion_rate < 0.5 and steps_completed > 0:
            state["output"] = (
                f"Partially completed. Completed {steps_completed}/{steps_total} steps. "
                f"Errors: {state.get('error', 'none')}"
            )
        elif state.get("requires_human_approval") and state["human_feedback"]:
            state["output"] = f"Human approved. Final output: {json.dumps(state['executed_steps'])}"
            state["status"] = "completed"
        elif state["status"] == "awaiting_human":
            state["output"] = "Awaiting human input to proceed."
        else:
            state["output"] = json.dumps(
                {"completed_steps": steps_completed, "results": state["executed_steps"]},
                indent=2,
            )
            state["status"] = "completed"

        return state

    async def human_approval_node(state: AgentState) -> AgentState:
        if state["requires_human_approval"] and state["human_feedback"]:
            feedback = state["human_feedback"].lower()
            if feedback in ("approve", "yes", "approved"):
                state["status"] = "executing"
                state["requires_human_approval"] = False
            else:
                state["status"] = "completed"
                state["output"] = "Human declined the action."
        return state

    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("human_approval", human_approval_node)
    graph.set_entry_point("planner")

    graph.add_edge("planner", "executor",
                    condition=lambda s: s["status"] == "planning_complete")
    graph.add_edge("executor", "human_approval",
                    condition=lambda s: s.get("requires_human_approval") and s["status"] != "failed")
    graph.add_edge("executor", "executor",
                    condition=lambda s: s["status"] == "executing" and not s.get("requires_human_approval"))
    graph.add_edge("human_approval", "executor",
                    condition=lambda s: s["status"] == "executing")
    graph.add_edge("executor", "reviewer",
                    condition=lambda s: s["status"] in ("completed", "failed", "awaiting_human"))

    return graph


async def run_agent_graph(input_text: str, human_feedback: str | None = None) -> AgentState:
    graph = create_financial_agent_graph()
    state = create_initial_state(input_text)
    if human_feedback:
        state["human_feedback"] = human_feedback
    return await graph.run(state)

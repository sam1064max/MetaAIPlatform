import streamlit as st
import json
import requests
from components.metrics import tool_card, status_badge

import os; API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")

MCP_SERVERS = ["market-data-server", "portfolio-server", "crm-server", "research-server", "news-server"]

TOOL_TYPES = ["function", "webhook", "database", "api", "custom"]

SAMPLE_TOOLS = [
    {
        "id": "market-data",
        "name": "Market Data Tool",
        "description": "Real-time market data and quotes. Retrieves live stock prices, indices, forex rates, and commodity prices from multiple exchanges.",
        "status": "published",
        "tool_type": "api",
        "mcp_server": "market-data-server",
        "parameters": {"symbol": {"type": "string", "required": True}, "exchange": {"type": "string", "default": "NYSE"}},
    },
    {
        "id": "portfolio-analyzer",
        "name": "Portfolio Analyzer",
        "description": "Portfolio performance analytics. Calculates returns, volatility, Sharpe ratio, and generates performance attribution reports.",
        "status": "published",
        "tool_type": "function",
        "mcp_server": "portfolio-server",
        "parameters": {"portfolio_id": {"type": "string", "required": True}, "benchmark": {"type": "string", "default": "S&P500"}},
    },
    {
        "id": "crm-tool",
        "name": "CRM Tool",
        "description": "Customer relationship management. Queries customer data, transaction history, interaction logs, and segment information.",
        "status": "published",
        "tool_type": "database",
        "mcp_server": "crm-server",
        "parameters": {"customer_id": {"type": "string", "required": True}, "include_history": {"type": "boolean", "default": True}},
    },
    {
        "id": "research-tool",
        "name": "Research Tool",
        "description": "Financial research and reports. Searches and retrieves analyst reports, SEC filings, earnings transcripts, and market commentary.",
        "status": "draft",
        "tool_type": "api",
        "mcp_server": "research-server",
        "parameters": {"query": {"type": "string", "required": True}, "max_results": {"type": "integer", "default": 10}},
    },
    {
        "id": "news-tool",
        "name": "News Tool",
        "description": "Real-time financial news. Aggregates news from major financial publishers with sentiment analysis and relevance scoring.",
        "status": "draft",
        "tool_type": "api",
        "mcp_server": "news-server",
        "parameters": {"topics": {"type": "array", "required": True}, "timeframe": {"type": "string", "default": "24h"}},
    },
]


def fetch_tools():
    try:
        r = requests.get(f"{API_BASE}/api/v1/tools", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return SAMPLE_TOOLS


def register_tool(data):
    try:
        r = requests.post(f"{API_BASE}/api/v1/tools", json=data, timeout=5)
        if r.status_code == 201:
            return r.json()
    except Exception:
        pass
    return {"id": f"tool_{len(SAMPLE_TOOLS) + 1}", "status": "registered"}


def show():
    st.markdown('<div class="main-header">🔧 Tool Registry</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94a3b8; margin-bottom: 1.5rem;">Register, manage, and publish tools for your agents</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ Register New Tool", expanded=False):
        st.markdown("### New Tool Registration")
        reg_col1, reg_col2 = st.columns(2)
        with reg_col1:
            tool_name = st.text_input("Tool Name", placeholder="e.g., sentiment-analyzer")
            tool_desc = st.text_area("Description", placeholder="Describe what this tool does", height=100)
            mcp_server = st.selectbox("MCP Server", options=[""] + MCP_SERVERS)
        with reg_col2:
            tool_type = st.selectbox("Tool Type", options=TOOL_TYPES)
            st.markdown("**Parameters (JSON)**")
            params_json = st.text_area(
                "",
                value='{\n  "param1": {\n    "type": "string",\n    "required": true\n  }\n}',
                height=150,
                label_visibility="collapsed",
            )

        if st.button("📦 Register Tool", type="primary", use_container_width=True):
            if not tool_name:
                st.error("Tool name is required.")
            else:
                try:
                    params = json.loads(params_json) if params_json.strip() else {}
                except json.JSONDecodeError:
                    st.error("Invalid JSON in parameters field.")
                    params = {}
                payload = {
                    "name": tool_name,
                    "description": tool_desc,
                    "mcp_server": mcp_server,
                    "tool_type": tool_type,
                    "parameters": params,
                }
                with st.spinner("Registering tool..."):
                    result = register_tool(payload)
                st.success(f"Tool '{tool_name}' registered! ID: {result.get('id', 'unknown')}")

    st.markdown("---")
    st.markdown('<div class="sub-header">Available Tools</div>', unsafe_allow_html=True)

    search_query = st.text_input(
        "",
        placeholder="🔍  Search tools by name or description...",
        label_visibility="collapsed",
    )

    tools = fetch_tools()

    if search_query:
        q = search_query.lower()
        tools = [t for t in tools if q in t.get("name", "").lower() or q in t.get("description", "").lower()]

    if not tools:
        st.info("No tools found.")
        return

    st.markdown(
        f'<div style="color: #64748b; margin-bottom: 1rem;">{len(tools)} tool{"s" if len(tools) != 1 else ""} registered</div>',
        unsafe_allow_html=True,
    )

    for i in range(0, len(tools), 3):
        row = tools[i : i + 3]
        cols = st.columns(3)
        for j, tool in enumerate(row):
            with cols[j]:
                tool_card(tool)
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("🧪 Test", key=f"test_{tool['id']}", use_container_width=True):
                        st.info(f"Testing '{tool['name']}'... (mock execution)")
                        st.code(f"Tool: {tool['name']}\nParams: {json.dumps(tool.get('parameters', {}), indent=2)}")
                with b_col2:
                    is_published = tool.get("status") == "published"
                    if st.button(
                        "📢 Publish" if not is_published else "✅ Published",
                        key=f"publish_{tool['id']}",
                        use_container_width=True,
                        disabled=is_published,
                    ):
                        tool["status"] = "published"
                        st.success(f"'{tool['name']}' published!")
                        st.rerun()

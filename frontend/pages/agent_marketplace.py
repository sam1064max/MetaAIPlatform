import streamlit as st
import requests
from components.metrics import agent_card

import os; API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")

SAMPLE_AGENTS = [
    {
        "id": "wealth-advisor",
        "name": "Wealth Advisor Agent",
        "description": "Personalized wealth management and portfolio advisory. Analyzes market trends, assesses risk tolerance, and provides tailored investment strategies for high-net-worth individuals.",
        "version": "2.3.1",
        "status": "deployed",
        "tags": ["finance", "portfolio", "advisory"],
    },
    {
        "id": "customer-service",
        "name": "Customer Service Agent",
        "description": "24/7 customer support for banking products. Handles account inquiries, transaction disputes, product recommendations, and escalates complex issues to human agents.",
        "version": "1.8.0",
        "status": "active",
        "tags": ["support", "banking", "chat"],
    },
    {
        "id": "research-agent",
        "name": "Research Agent",
        "description": "Automated financial research and report generation. Synthesizes earnings calls, SEC filings, and market data into comprehensive research reports with actionable insights.",
        "version": "3.0.2",
        "status": "deployed",
        "tags": ["research", "reports", "nlp"],
    },
    {
        "id": "compliance-agent",
        "name": "Compliance Agent",
        "description": "Regulatory compliance checking and monitoring. Scans transactions, communications, and operations for regulatory breaches and generates compliance reports.",
        "version": "1.5.1",
        "status": "active",
        "tags": ["compliance", "risk", "monitoring"],
    },
    {
        "id": "portfolio-risk",
        "name": "Portfolio Risk Agent",
        "description": "Real-time portfolio risk assessment. Calculates VaR, stress tests portfolios, monitors concentration risk, and provides hedging recommendations.",
        "version": "2.1.0",
        "status": "draft",
        "tags": ["risk", "portfolio", "analytics"],
    },
]


def fetch_agents():
    try:
        r = requests.get(f"{API_BASE}/api/v1/agents", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return SAMPLE_AGENTS


def show():
    st.markdown('<div class="main-header">🏪 Agent Marketplace</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94a3b8; margin-bottom: 1.5rem;">Browse, clone, and deploy pre-built agents</div>',
        unsafe_allow_html=True,
    )

    search_query = st.text_input(
        "",
        placeholder="🔍  Search agents by name, description, or tags...",
        label_visibility="collapsed",
    )

    agents = fetch_agents()

    if search_query:
        q = search_query.lower()
        agents = [
            a
            for a in agents
            if q in a.get("name", "").lower()
            or q in a.get("description", "").lower()
            or any(q in t.lower() for t in a.get("tags", []))
        ]

    if not agents:
        st.info("No agents found matching your search.")
        return

    st.markdown(
        f'<div style="color: #64748b; margin-bottom: 1rem;">{len(agents)} agent{"s" if len(agents) != 1 else ""} available</div>',
        unsafe_allow_html=True,
    )

    if "expanded_agent" not in st.session_state:
        st.session_state.expanded_agent = None

    for i in range(0, len(agents), 3):
        row = agents[i : i + 3]
        cols = st.columns(3)
        for j, agent in enumerate(row):
            with cols[j]:
                agent_card(agent)
                b_col1, b_col2, b_col3 = st.columns(3)
                with b_col1:
                    if st.button(
                        "👁️ View",
                        key=f"view_{agent['id']}",
                        use_container_width=True,
                    ):
                        st.session_state.expanded_agent = (
                            agent["id"]
                            if st.session_state.expanded_agent != agent["id"]
                            else None
                        )
                        st.rerun()
                with b_col2:
                    if st.button(
                        "📋 Clone",
                        key=f"clone_{agent['id']}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_agent = agent
                        st.session_state.current_page = "Agent Studio"
                        st.success(f"Cloned '{agent['name']}' to Agent Studio!")
                        st.rerun()
                with b_col3:
                    is_deployed = agent.get("status") == "deployed"
                    if st.button(
                        "✅ Deploy" if not is_deployed else "✔️ Deployed",
                        key=f"deploy_{agent['id']}",
                        use_container_width=True,
                        disabled=is_deployed,
                    ):
                        agent["status"] = "deployed"
                        st.success(f"'{agent['name']}' deployed successfully!")
                        st.rerun()

                if st.session_state.expanded_agent == agent["id"]:
                    with st.expander("Agent Details", expanded=True):
                        det = st.columns(2)
                        with det[0]:
                            st.markdown(f"**ID:** `{agent['id']}`")
                            st.markdown(f"**Version:** v{agent['version']}")
                            st.markdown(f"**Status:** {agent['status'].title()}")
                        with det[1]:
                            st.markdown("**Tags:**")
                            for tag in agent.get("tags", []):
                                st.markdown(f"- `{tag}`")
                        st.markdown(f"**Description:** {agent['description']}")
                        st.markdown("---")
                        st.markdown(
                            "**Configuration:**\n```yaml\n"
                            f"agent:\n  name: {agent['name']}\n"
                            f"  version: {agent['version']}\n"
                            f"  status: {agent['status']}\n"
                            f"  tags: {agent.get('tags', [])}\n```"
                        )

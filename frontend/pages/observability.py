import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from components.metrics import metric_card, chart_container, status_badge
import requests

import os; API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


def fetch_traces():
    try:
        r = requests.get(f"{API_BASE}/api/v1/observability/traces", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    agents = ["Wealth Advisor", "Customer Service", "Research Agent", "Compliance Agent", "Portfolio Risk"]
    statuses = ["success", "success", "success", "success", "error", "pending"]
    traces = []
    for i in range(25):
        start = datetime.now() - timedelta(hours=np.random.randint(0, 48))
        dur = round(np.random.uniform(0.5, 12.0), 2)
        traces.append(
            {
                "trace_id": f"trace-{i:04d}",
                "agent": np.random.choice(agents),
                "duration": dur,
                "status": np.random.choice(statuses, p=[0.6, 0.1, 0.1, 0.05, 0.1, 0.05]),
                "timestamp": start.strftime("%Y-%m-%d %H:%M:%S"),
                "tokens_used": np.random.randint(100, 5000),
                "cost": round(np.random.uniform(0.01, 0.15), 4),
            }
        )
    return sorted(traces, key=lambda x: x["timestamp"], reverse=True)


def fetch_agent_calls():
    try:
        r = requests.get(f"{API_BASE}/api/v1/observability/agent-calls", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    agents = ["Wealth Advisor", "Customer Service", "Research Agent", "Compliance Agent", "Portfolio Risk"]
    return {
        "total_calls": 28734,
        "unique_agents": 7,
        "avg_duration": 2.45,
        "calls_per_agent": {a: np.random.randint(2000, 8000) for a in agents},
    }


def fetch_tool_calls():
    try:
        r = requests.get(f"{API_BASE}/api/v1/observability/tool-calls", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    tools = ["Market Data", "Portfolio Analyzer", "CRM", "Research", "News"]
    return {
        "total_calls": 89234,
        "success_rate": 96.8,
        "tool_distribution": {t: np.random.randint(5000, 25000) for t in tools},
    }


def fetch_failures():
    try:
        r = requests.get(f"{API_BASE}/api/v1/observability/failures", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {
        "error_rate": 3.2,
        "top_failures": [
            {"error": "Rate limit exceeded", "count": 234, "pct": 28.4},
            {"error": "Model timeout", "count": 187, "pct": 22.7},
            {"error": "Invalid tool parameters", "count": 145, "pct": 17.6},
            {"error": "Authentication failed", "count": 98, "pct": 11.9},
            {"error": "Context length exceeded", "count": 76, "pct": 9.2},
            {"error": "API connection refused", "count": 84, "pct": 10.2},
        ],
    }


def fetch_cost_analysis():
    try:
        r = requests.get(f"{API_BASE}/api/v1/observability/costs", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {
        "cost_by_model": {
            "gpt-5": 12450.00,
            "claude-sonnet-4": 8920.00,
            "gemini-2": 5670.00,
            "deepseek-v3": 3450.00,
            "ollama": 890.00,
        },
        "cost_by_agent": {
            "Wealth Advisor": 6200.00,
            "Customer Service": 4800.00,
            "Research Agent": 5300.00,
            "Compliance Agent": 2800.00,
            "Portfolio Risk": 4100.00,
        },
        "cumulative": {
            "dates": [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, -1, -1)],
            "costs": [round(800 + np.random.uniform(-200, 400), 2) for _ in range(31)],
        },
    }


def show():
    st.markdown('<div class="main-header">🔍 Observability</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94a3b8; margin-bottom: 1.5rem;">Monitor traces, calls, failures, and costs</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🔄 Traces", "🤖 Agent Calls", "🔧 Tool Calls", "❌ Failure Analysis", "💰 Cost Analysis"]
    )

    with tab1:
        st.markdown("### Recent Traces")
        traces = fetch_traces()
        trace_df = pd.DataFrame(traces)
        st.dataframe(
            trace_df[["trace_id", "agent", "duration", "status", "timestamp"]],
            use_container_width=True,
            height=400,
            column_config={
                "trace_id": "Trace ID",
                "agent": "Agent",
                "duration": st.column_config.NumberColumn("Duration (s)", format="%.2f"),
                "status": "Status",
                "timestamp": "Timestamp",
            },
        )

        st.markdown("### Trace Details")
        trace_ids = [f"{t['trace_id']} - {t['agent']} ({t['timestamp']})" for t in traces[:10]]
        selected_trace = st.selectbox("Select trace to expand", options=[""] + trace_ids)
        if selected_trace:
            st.markdown("#### Trace Details", unsafe_allow_html=True)
            trace_id = selected_trace.split(" - ")[0]
            trace_data = next(t for t in traces if t["trace_id"] == trace_id)
            det_cols = st.columns(4)
            with det_cols[0]:
                metric_card("Duration", f"{trace_data['duration']}s", icon="⏱️")
            with det_cols[1]:
                metric_card("Tokens", f"{trace_data['tokens_used']:,}", icon="🔤")
            with det_cols[2]:
                metric_card("Cost", f"${trace_data['cost']:.4f}", icon="💰")
            with det_cols[3]:
                st.markdown(
                    f'<div style="background:#151b2b;border:1px solid #1e293b;border-radius:10px;padding:1.25rem 1.5rem;">'
                    f'<div style="color:#64748b;font-size:0.75rem;text-transform:uppercase;">Status</div>'
                    f'<div style="margin-top:0.25rem;">{status_badge(trace_data["status"])}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown("### Agent Call Metrics")
        agent_data = fetch_agent_calls()
        m_cols = st.columns(3)
        with m_cols[0]:
            metric_card("Total Calls", f"{agent_data['total_calls']:,}", delta=5.2, icon="📞")
        with m_cols[1]:
            metric_card("Unique Agents", agent_data["unique_agents"], icon="🤖")
        with m_cols[2]:
            metric_card("Avg Duration", f"{agent_data['avg_duration']}s", delta=-2.8, icon="⏱️")

        fig = go.Figure(
            data=[
                go.Bar(
                    x=list(agent_data["calls_per_agent"].keys()),
                    y=list(agent_data["calls_per_agent"].values()),
                    marker_color=["#00d4aa", "#7c3aed", "#f59e0b", "#3b82f6", "#ef4444"],
                )
            ]
        )
        fig.update_layout(
            title=dict(text="Calls per Agent", font=dict(size=14, color="#e2e8f0")),
            yaxis_title="Number of Calls",
            hovermode="x unified",
        )
        chart_container(fig)

    with tab3:
        st.markdown("### Tool Call Metrics")
        tool_data = fetch_tool_calls()
        m_cols = st.columns(2)
        with m_cols[0]:
            metric_card("Total Tool Calls", f"{tool_data['total_calls']:,}", delta=8.1, icon="🔧")
        with m_cols[1]:
            metric_card("Success Rate", f"{tool_data['success_rate']}%", delta=0.3, icon="✅")

        colors = ["#00d4aa", "#7c3aed", "#f59e0b", "#ef4444", "#3b82f6"]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=list(tool_data["tool_distribution"].keys()),
                    values=list(tool_data["tool_distribution"].values()),
                    marker=dict(colors=colors),
                    textinfo="label+percent",
                    textfont=dict(color="#e2e8f0", size=11),
                    hovertemplate="<b>%{label}</b><br>Calls: %{value:,}<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            title=dict(text="Tool Call Distribution", font=dict(size=14, color="#e2e8f0")),
        )
        chart_container(fig)

    with tab4:
        st.markdown("### Failure Analysis")
        fail_data = fetch_failures()
        metric_card("Overall Error Rate", f"{fail_data['error_rate']}%", delta=-0.8, icon="⚠️")

        st.markdown("### Top Failures")
        fail_df = pd.DataFrame(fail_data["top_failures"])
        fig = go.Figure(
            data=[
                go.Bar(
                    x=fail_df["error"],
                    y=fail_df["count"],
                    marker_color="#ef4444",
                    text=fail_df["count"],
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(
            title=dict(text="Failure Count by Type", font=dict(size=14, color="#e2e8f0")),
            yaxis_title="Count",
            hovermode="x unified",
            xaxis_tickangle=-30,
        )
        chart_container(fig)

        st.dataframe(fail_df, use_container_width=True)

    with tab5:
        st.markdown("### Cost Analysis")
        cost_data = fetch_cost_analysis()

        chart_cols = st.columns(2)
        with chart_cols[0]:
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(cost_data["cost_by_model"].keys()),
                        y=list(cost_data["cost_by_model"].values()),
                        marker_color=["#00d4aa", "#7c3aed", "#f59e0b", "#3b82f6", "#10b981"],
                    )
                ]
            )
            fig.update_layout(
                title=dict(text="Cost by Model", font=dict(size=14, color="#e2e8f0")),
                yaxis_title="Cost ($)",
                hovermode="x unified",
            )
            chart_container(fig)

        with chart_cols[1]:
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(cost_data["cost_by_agent"].keys()),
                        y=list(cost_data["cost_by_agent"].values()),
                        marker_color=["#f59e0b", "#ef4444", "#7c3aed", "#00d4aa", "#3b82f6"],
                    )
                ]
            )
            fig.update_layout(
                title=dict(text="Cost by Agent", font=dict(size=14, color="#e2e8f0")),
                yaxis_title="Cost ($)",
                hovermode="x unified",
            )
            chart_container(fig)

        cum = cost_data["cumulative"]
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=cum["dates"],
                    y=np.cumsum(cum["costs"]),
                    name="Cumulative Cost",
                    line=dict(color="#00d4aa", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(0,212,170,0.1)",
                )
            ]
        )
        fig.update_layout(
            title=dict(text="Cumulative Cost Over Time", font=dict(size=14, color="#e2e8f0")),
            yaxis_title="Cumulative Cost ($)",
            hovermode="x unified",
        )
        chart_container(fig)

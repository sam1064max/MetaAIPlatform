import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from components.metrics import metric_card, chart_container
import requests

import os; API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


def fetch_metrics():
    try:
        r = requests.get(f"{API_BASE}/api/v1/dashboard/stats", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {
        "total_agents": 12,
        "total_executions": 8453,
        "total_llm_calls": 124890,
        "monthly_cost": 28450.75,
        "avg_latency": 1.87,
        "success_rate": 97.3,
    }


def fetch_cost_trends():
    try:
        r = requests.get(f"{API_BASE}/api/v1/dashboard/cost-trends", timeout=3)
        if r.status_code == 200:
            data = r.json()
            trends = data.get("trends", [])
            return {
                "dates": [t["date"] for t in trends],
                "llm_cost": [t["total_cost"] for t in trends],
                "infra_cost": [0 for _ in trends],
                "total_cost": None,
            }
    except Exception:
        pass
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, -1, -1)]
    return {
        "dates": dates,
        "llm_cost": [round(200 + np.random.uniform(-50, 80), 2) for _ in dates],
        "infra_cost": [round(50 + np.random.uniform(-10, 30), 2) for _ in dates],
        "total_cost": None,
    }


def fetch_token_usage():
    try:
        r = requests.get(f"{API_BASE}/api/v1/dashboard/token-usage", timeout=3)
        if r.status_code == 200:
            data = r.json()
            usage = data.get("usage", [])
            if usage:
                return {
                    "models": ["gpt-5", "claude-sonnet-4", "gemini-2", "deepseek-v3", "ollama"],
                    "input_tokens": [u["input_tokens"] for u in usage[-5:]],
                    "output_tokens": [u["output_tokens"] for u in usage[-5:]],
                }
    except Exception:
        pass
    models = ["gpt-5", "claude-sonnet-4", "gemini-2", "deepseek-v3", "ollama"]
    return {
        "models": models,
        "input_tokens": [450000, 320000, 280000, 190000, 85000],
        "output_tokens": [180000, 140000, 95000, 72000, 38000],
    }


def fetch_agent_activity():
    try:
        r = requests.get(f"{API_BASE}/api/v1/dashboard/agent-activity", timeout=3)
        if r.status_code == 200:
            data = r.json()
            activity = data.get("activity", [])
            return {
                "dates": [a["date"] for a in activity],
                "executions": [a["executions"] for a in activity],
            }
    except Exception:
        pass
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
    return {
        "dates": dates,
        "executions": [np.random.randint(150, 400) for _ in dates],
    }


def fetch_model_usage():
    try:
        r = requests.get(f"{API_BASE}/api/v1/dashboard/model-usage", timeout=3)
        if r.status_code == 200:
            data = r.json()
            models = data.get("models", [])
            return {
                "models": [m["model"] for m in models],
                "calls": [m["percentage"] for m in models],
            }
    except Exception:
        pass
    return {
        "models": ["gpt-5", "claude-sonnet-4", "gemini-2", "deepseek-v3", "ollama"],
        "calls": [38, 27, 18, 12, 5],
    }


def show():
    st.markdown('<div class="main-header">📊 Platform Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94a3b8; margin-bottom: 1.5rem;">Real-time overview of your AI platform</div>',
        unsafe_allow_html=True,
    )

    metrics = fetch_metrics()

    cols = st.columns(6)
    with cols[0]:
        metric_card("Total Agents", metrics["total_agents"], delta=2, icon="🤖")
    with cols[1]:
        metric_card("Total Executions", f"{metrics['total_executions']:,}", delta=12.4, icon="⚡")
    with cols[2]:
        metric_card("Total Tokens", f"{metrics.get('total_tokens_used', 0):,}", delta=8.7, icon="🧠")
    with cols[3]:
        metric_card("Total Cost", f"${metrics.get('total_cost_usd', 0):,.2f}", delta=-3.2, icon="💰")
    with cols[4]:
        metric_card("Avg Latency", f"{metrics.get('avg_latency_ms', 0)}ms", delta=-5.1, icon="⏱️")
    with cols[5]:
        metric_card("Success Rate", f"{metrics.get('success_rate_pct', 0)}%", delta=1.8, icon="✅")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Cost Trends", "🔤 Token Usage", "📊 Agent Activity", "🎯 Model Usage"]
    )

    with tab1:
        cost_data = fetch_cost_trends()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=cost_data["dates"],
                y=cost_data["llm_cost"],
                name="LLM Cost",
                line=dict(color="#00d4aa", width=2),
                fill="tozeroy",
                fillcolor="rgba(0,212,170,0.1)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=cost_data["dates"],
                y=cost_data["infra_cost"],
                name="Infrastructure Cost",
                line=dict(color="#7c3aed", width=2),
                fill="tozeroy",
                fillcolor="rgba(124,58,237,0.1)",
            )
        )
        fig.update_layout(
            title=dict(text="Daily Cost Trends (Last 31 Days)", font=dict(size=14, color="#e2e8f0")),
            yaxis_title="Cost (USD)",
            hovermode="x unified",
        )
        chart_container(fig)

    with tab2:
        token_data = fetch_token_usage()
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=token_data["models"],
                y=token_data["input_tokens"],
                name="Input Tokens",
                marker_color="#00d4aa",
            )
        )
        fig.add_trace(
            go.Bar(
                x=token_data["models"],
                y=token_data["output_tokens"],
                name="Output Tokens",
                marker_color="#7c3aed",
            )
        )
        fig.update_layout(
            title=dict(text="Token Usage by Model", font=dict(size=14, color="#e2e8f0")),
            yaxis_title="Tokens",
            barmode="stack",
            hovermode="x unified",
        )
        chart_container(fig)

    with tab3:
        activity = fetch_agent_activity()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=activity["dates"],
                y=activity["executions"],
                name="Executions",
                line=dict(color="#f59e0b", width=2),
                fill="tozeroy",
                fillcolor="rgba(245,158,11,0.1)",
            )
        )
        fig.update_layout(
            title=dict(text="Agent Executions (Last 30 Days)", font=dict(size=14, color="#e2e8f0")),
            yaxis_title="Executions",
            hovermode="x unified",
        )
        chart_container(fig)

    with tab4:
        model_data = fetch_model_usage()
        colors = ["#00d4aa", "#7c3aed", "#f59e0b", "#ef4444", "#3b82f6"]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=model_data["models"],
                    values=model_data["calls"],
                    hole=0.5,
                    marker=dict(colors=colors),
                    textinfo="label+percent",
                    textfont=dict(color="#e2e8f0", size=12),
                    hovertemplate="<b>%{label}</b><br>Calls: %{value}%<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            title=dict(text="Model Usage Distribution", font=dict(size=14, color="#e2e8f0")),
            annotations=[
                dict(
                    text=f"Total<br>{sum(model_data['calls'])}%",
                    x=0.5,
                    y=0.5,
                    font=dict(size=14, color="#e2e8f0"),
                    showarrow=False,
                )
            ],
        )
        chart_container(fig)

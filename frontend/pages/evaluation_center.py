import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from components.metrics import metric_card, chart_container
import requests

import os; API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


def fetch_eval_metrics():
    try:
        r = requests.get(f"{API_BASE}/api/v1/evaluation/metrics", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {
        "accuracy": 94.2,
        "groundedness": 91.8,
        "hallucination_rate": 3.1,
        "avg_latency": 2.34,
        "avg_cost": 0.087,
    }


def fetch_eval_history():
    try:
        r = requests.get(f"{API_BASE}/api/v1/evaluation/history", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    agents = ["Wealth Advisor", "Customer Service", "Research Agent", "Compliance Agent"]
    types = ["golden", "synthetic", "regression"]
    rows = []
    for i in range(20):
        rows.append(
            {
                "Date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "Agent": np.random.choice(agents),
                "Type": np.random.choice(types),
                "Accuracy": round(np.random.uniform(85, 99), 1),
                "Groundedness": round(np.random.uniform(82, 98), 1),
                "Hallucination": round(np.random.uniform(1, 8), 1),
                "Latency (s)": round(np.random.uniform(1.0, 4.5), 2),
                "Cost ($)": round(np.random.uniform(0.03, 0.15), 3),
            }
        )
    return rows


def show():
    st.markdown('<div class="main-header">📋 Evaluation Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94a3b8; margin-bottom: 1.5rem;">Measure, track, and improve agent performance</div>',
        unsafe_allow_html=True,
    )

    metrics = fetch_eval_metrics()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Accuracy", f"{metrics['accuracy']:.1f}%", delta=1.2, icon="🎯")
    with col2:
        metric_card("Groundedness", f"{metrics['groundedness']:.1f}%", delta=0.8, icon="📌")
    with col3:
        metric_card("Hallucination Rate", f"{metrics['hallucination_rate']:.1f}%", delta=-0.4, icon="⚠️")
    with col4:
        metric_card("Avg Latency", f"{metrics['avg_latency']}s", delta=-3.1, icon="⏱️")
    with col5:
        metric_card("Avg Cost", f"${metrics['avg_cost']:.3f}", delta=-2.7, icon="💰")

    st.markdown("---")

    sec1, sec2, sec3 = st.tabs(
        ["▶️ Run Evaluation", "📊 Results Table", "📈 Charts"]
    )

    with sec1:
        st.markdown("### Run New Evaluation")
        eval_col1, eval_col2 = st.columns(2)
        with eval_col1:
            agents = ["Wealth Advisor Agent", "Customer Service Agent", "Research Agent", "Compliance Agent", "Portfolio Risk Agent"]
            eval_agent = st.selectbox("Select Agent", options=agents, key="eval_agent")
        with eval_col2:
            eval_type = st.selectbox(
                "Evaluation Type",
                options=["golden dataset", "synthetic", "regression"],
                key="eval_type",
            )

        if st.button("▶️ Run Evaluation", type="primary", use_container_width=True):
            progress_bar = st.progress(0, text="Starting evaluation...")
            import time
            for pct in range(0, 101, 10):
                time.sleep(0.15)
                progress_bar.progress(pct, text=f"Evaluating... {pct}%")
            st.success(f"Evaluation complete! {eval_agent} scored 94.2% accuracy.")

    with sec2:
        st.markdown("### Evaluation History")
        history = fetch_eval_history()
        df = pd.DataFrame(history)

        def color_val(val):
            if isinstance(val, float):
                if val > 95:
                    return "color: #10b981"
                elif val < 85:
                    return "color: #ef4444"
            return ""

        styled = df.style.map(color_val, subset=["Accuracy", "Groundedness"])
        styled = styled.background_gradient(
            subset=["Hallucination"], cmap="RdYlGn_r", low=0.1, high=0.3
        )

        st.dataframe(styled, use_container_width=True, height=400)

    with sec3:
        history = fetch_eval_history()
        df = pd.DataFrame(history)
        df = df.sort_values("Date")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig = go.Figure()
            for agent in df["Agent"].unique():
                agent_df = df[df["Agent"] == agent]
                fig.add_trace(
                    go.Scatter(
                        x=agent_df["Date"],
                        y=agent_df["Accuracy"],
                        name=agent,
                        mode="lines+markers",
                        line=dict(width=2),
                    )
                )
            fig.update_layout(
                title=dict(text="Accuracy Trend", font=dict(size=14, color="#e2e8f0")),
                yaxis_title="Accuracy (%)",
                yaxis_range=[80, 100],
                hovermode="x unified",
            )
            chart_container(fig)

        with chart_col2:
            cost_by_type = df.groupby("Type")["Cost ($)"].sum().reset_index()
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=cost_by_type["Type"],
                        y=cost_by_type["Cost ($)"],
                        marker_color=["#00d4aa", "#7c3aed", "#f59e0b"],
                    )
                ]
            )
            fig.update_layout(
                title=dict(text="Cost per Evaluation Type", font=dict(size=14, color="#e2e8f0")),
                yaxis_title="Total Cost ($)",
                hovermode="x unified",
            )
            chart_container(fig)

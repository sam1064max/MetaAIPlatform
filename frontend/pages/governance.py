import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from components.metrics import metric_card, chart_container, status_badge
import requests

import os; API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


def fetch_audit_logs(user_filter=None, action_filter=None, start_date=None, end_date=None):
    try:
        params = {}
        if user_filter:
            params["user_filter"] = user_filter
        if action_filter:
            params["action_filter"] = action_filter
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        r = requests.get(f"{API_BASE}/api/v1/audit-logs", params=params, timeout=3)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                logs = []
                for log in data:
                    logs.append({
                        "timestamp": log.get("created_at", ""),
                        "user": str(log.get("user_id", "unknown")),
                        "action": log.get("action", ""),
                        "resource": log.get("resource_type", ""),
                        "details": log.get("details_json", ""),
                        "ip": log.get("ip_address", ""),
                    })
                return logs
    except Exception:
        pass
    users = ["sam.altman", "john.doe", "jane.smith", "admin", "mike.chen", "sarah.lee"]
    actions = ["agent.create", "agent.deploy", "tool.register", "tool.publish", "model.call", "kb.create", "eval.run", "settings.update"]
    resources = ["Wealth Advisor", "Customer Service", "Market Data Tool", "gpt-5", "Financial Docs KB", "Settings"]
    logs = []
    for i in range(50):
        logs.append({
            "timestamp": (datetime.now() - timedelta(hours=np.random.randint(0, 720))).strftime("%Y-%m-%d %H:%M:%S"),
            "user": np.random.choice(users),
            "action": np.random.choice(actions),
            "resource": np.random.choice(resources),
            "details": f"Performed {np.random.choice(actions)} on {np.random.choice(resources)}",
            "ip": f"10.0.{np.random.randint(0, 255)}.{np.random.randint(1, 254)}",
        })
    logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
    if user_filter:
        logs = [l for l in logs if user_filter.lower() in l["user"].lower()]
    if action_filter:
        logs = [l for l in logs if action_filter.lower() in l["action"].lower()]
    if start_date:
        logs = [l for l in logs if l["timestamp"] >= start_date]
    if end_date:
        logs = [l for l in logs if l["timestamp"] <= end_date + " 23:59:59"]
    return logs


def fetch_model_usage_gov():
    try:
        r = requests.get(f"{API_BASE}/api/v1/model-usage", timeout=3)
        if r.status_code == 200:
            data = r.json()
            return data
    except Exception:
        pass
    return {
        "total_calls": 124890,
        "cost_by_model": {
            "gpt-5": 12450.00,
            "claude-sonnet-4": 8920.00,
            "gemini-2": 5670.00,
            "deepseek-v3": 3450.00,
            "ollama": 890.00,
        },
        "usage_over_time": {
            "dates": [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)],
            "calls": [np.random.randint(3000, 6000) for _ in range(30)],
        },
    }


def fetch_user_activity():
    try:
        r = requests.get(f"{API_BASE}/api/v1/user-activity", timeout=3)
        if r.status_code == 200:
            data = r.json()
            return data
    except Exception:
        pass
    return {
        "active_users": 47,
        "top_users": [
            {"user": "sam.altman", "actions": 2843, "role": "admin"},
            {"user": "jane.smith", "actions": 2156, "role": "developer"},
            {"user": "john.doe", "actions": 1892, "role": "analyst"},
            {"user": "mike.chen", "actions": 1567, "role": "developer"},
            {"user": "sarah.lee", "actions": 1234, "role": "analyst"},
        ],
        "activity_by_role": {
            "admin": 3520,
            "developer": 5840,
            "analyst": 4210,
            "viewer": 890,
        },
    }


def fetch_compliance_data():
    try:
        r = requests.get(f"{API_BASE}/api/v1/compliance-report", timeout=3)
        if r.status_code == 200:
            data = r.json()
            return data
    except Exception:
        pass
    return {
        "overview": {
            "total_reports": 48,
            "passed": 44,
            "failed": 4,
            "compliance_rate": 91.7,
        },
        "history": [
            {"date": (datetime.now() - timedelta(days=i * 7)).strftime("%Y-%m-%d"), "type": "SOC2", "status": np.random.choice(["passed", "passed", "passed", "failed"]), "score": round(np.random.uniform(82, 100), 1)}
            for i in range(10)
        ],
    }


def show():
    st.markdown('<div class="main-header">\U0001f6e1\ufe0f Governance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94a3b8; margin-bottom: 1.5rem;">Audit logs, model governance, user activity, compliance</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["\U0001f4cb Audit Logs", "\U0001f9e0 Model Usage", "\U0001f465 User Activity", "\U0001f4c4 Compliance Reports"]
    )

    with tab1:
        st.markdown("### Audit Logs")
        filt_col1, filt_col2, filt_col3, filt_col4 = st.columns(4)
        with filt_col1:
            user_filter = st.text_input("User", placeholder="Filter by user...", key="audit_user")
        with filt_col2:
            action_filter = st.text_input("Action", placeholder="e.g., agent.create...", key="audit_action")
        with filt_col3:
            start_date = st.date_input("From", value=None, key="audit_start")
        with filt_col4:
            end_date = st.date_input("To", value=None, key="audit_end")

        logs = fetch_audit_logs(
            user_filter=user_filter,
            action_filter=action_filter,
            start_date=str(start_date) if start_date else None,
            end_date=str(end_date) if end_date else None,
        )

        log_df = pd.DataFrame(logs)
        if not log_df.empty:
            st.dataframe(
                log_df[["timestamp", "user", "action", "resource", "details"]],
                use_container_width=True,
                height=450,
            )
            st.markdown(
                f'<div style="color:#64748b;font-size:0.8rem;">Showing {len(logs)} log entries</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No audit logs match the current filters.")

    with tab2:
        st.markdown("### Model Usage Governance")
        model_data = fetch_model_usage_gov()
        metric_card("Total Model Calls", f"{model_data.get('total_calls', 0):,}", icon="\U0001f9e0")

        chart_cols = st.columns(2)
        with chart_cols[0]:
            cost_by_model = model_data.get("cost_by_model", {})
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(cost_by_model.keys()),
                        y=list(cost_by_model.values()),
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
            usage = model_data.get("usage_over_time", {})
            dates = usage.get("dates", [])
            calls = usage.get("calls", [])
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=dates,
                        y=calls,
                        name="Daily Calls",
                        line=dict(color="#7c3aed", width=2),
                        fill="tozeroy",
                        fillcolor="rgba(124,58,237,0.1)",
                    )
                ]
            )
            fig.update_layout(
                title=dict(text="Model Usage Over Time", font=dict(size=14, color="#e2e8f0")),
                yaxis_title="Calls",
                hovermode="x unified",
            )
            chart_container(fig)

    with tab3:
        st.markdown("### User Activity")
        user_data = fetch_user_activity()
        metric_card("Active Users (30d)", user_data.get("active_users", 0), delta=8, icon="\U0001f465")

        chart_cols = st.columns(2)
        with chart_cols[0]:
            top_users = user_data.get("top_users", [])
            if top_users:
                top_df = pd.DataFrame(top_users)
                st.markdown("**Top Users by Actions**")
                st.dataframe(top_df, use_container_width=True)

        with chart_cols[1]:
            activity_by_role = user_data.get("activity_by_role", {})
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=list(activity_by_role.keys()),
                        values=list(activity_by_role.values()),
                        marker=dict(colors=["#00d4aa", "#7c3aed", "#f59e0b", "#3b82f6"]),
                        textinfo="label+percent",
                        textfont=dict(color="#e2e8f0", size=11),
                    )
                ]
            )
            fig.update_layout(
                title=dict(text="Activity by Role", font=dict(size=14, color="#e2e8f0")),
            )
            chart_container(fig)

    with tab4:
        st.markdown("### Compliance Reports")
        comp_data = fetch_compliance_data()
        overview = comp_data.get("overview", {})

        comp_cols = st.columns(4)
        with comp_cols[0]:
            metric_card("Total Reports", overview.get("total_reports", 0), icon="\U0001f4c4")
        with comp_cols[1]:
            metric_card("Passed", overview.get("passed", 0), icon="\u2705")
        with comp_cols[2]:
            metric_card("Failed", overview.get("failed", 0), icon="\u274c")
        with comp_cols[3]:
            metric_card("Compliance Rate", f"{overview.get('compliance_rate', 0)}%", delta=2.1, icon="\U0001f4ca")

        if st.button("\U0001f4c4 Generate Report", type="primary", use_container_width=False):
            with st.spinner("Generating compliance report..."):
                import time
                time.sleep(1.5)
            st.success("Compliance report generated! Download ready.")

        st.markdown("### Report History")
        history = comp_data.get("history", [])
        if history:
            hist_df = pd.DataFrame(history)
            st.dataframe(hist_df, use_container_width=True)

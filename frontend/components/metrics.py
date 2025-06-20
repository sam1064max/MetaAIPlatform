import streamlit as st


def metric_card(title, value, delta=None, icon=None, delta_suffix=None):
    delta_html = ""
    if delta is not None:
        cls = "positive" if delta > 0 else "negative"
        arrow = "▲" if delta > 0 else "▼"
        suffix = delta_suffix or "%"
        delta_html = f'<div class="metric-delta {cls}">{arrow} {abs(delta)}{suffix}</div>'
    icon_html = f'<div class="metric-icon">{icon}</div>' if icon else ""
    st.markdown(
        f"""
        <div class="metric-card">
            {icon_html}
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def agent_card(agent_data):
    name = agent_data.get("name", "Unnamed Agent")
    desc = agent_data.get("description", "")
    version = agent_data.get("version", "1.0.0")
    status = agent_data.get("status", "draft")
    tags = agent_data.get("tags", [])
    if len(desc) > 120:
        desc = desc[:117] + "..."
    tag_html = "".join(
        f'<span class="tag tag-{t.split("-")[0] if "-" in t else "primary"}">{t}</span>'
        for t in tags
    )
    badge = status_badge(status)
    st.markdown(
        f"""
        <div class="agent-card">
            <div class="agent-name">{name}</div>
            <div class="agent-desc">{desc}</div>
            <div class="agent-tags">{tag_html}</div>
            <div class="agent-footer">
                <span class="agent-version">v{version}</span>
                {badge}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tool_card(tool_data):
    name = tool_data.get("name", "Unnamed Tool")
    desc = tool_data.get("description", "")
    status = tool_data.get("status", "draft")
    tool_type = tool_data.get("tool_type", "function")
    badge = status_badge(status)
    if len(desc) > 100:
        desc = desc[:97] + "..."
    st.markdown(
        f"""
        <div class="tool-card">
            <div class="tool-name">{name}</div>
            <div class="tool-desc">{desc}</div>
            <div class="tool-meta">
                <span>{tool_type}</span>
                {badge}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_container(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=11),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="#1e293b", zerolinecolor="#1e293b")
    fig.update_yaxes(gridcolor="#1e293b", zerolinecolor="#1e293b")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


def status_badge(status):
    status = status.lower()
    color_map = {
        "active": "active",
        "deployed": "deployed",
        "published": "published",
        "draft": "draft",
        "inactive": "inactive",
        "failed": "failed",
        "error": "error",
        "pending": "pending",
    }
    cls = color_map.get(status, "draft")
    return f'<span class="status-badge {cls}">{status}</span>'

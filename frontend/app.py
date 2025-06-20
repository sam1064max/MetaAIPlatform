import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Meta AI Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS_PATH = Path(__file__).parent / "assets" / "css" / "style.css"
if CSS_PATH.exists():
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

NAV_ITEMS = [
    ("📊", "Dashboard"),
    ("⚡", "Agent Studio"),
    ("🏪", "Agent Marketplace"),
    ("🔧", "Tool Registry"),
    ("📚", "RAG Studio"),
    ("📋", "Evaluation Center"),
    ("🔍", "Observability"),
    ("🛡️", "Governance"),
    ("⚙️", "Settings"),
]

NAV_ICONS = {name: icon for icon, name in NAV_ITEMS}

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "auth_token" not in st.session_state:
    st.session_state.auth_token = "mock-token-abc123"
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None
if "selected_kb" not in st.session_state:
    st.session_state.selected_kb = None

st.markdown(
    """
    <div class="sidebar-user">
        <div class="avatar">SA</div>
        <div class="user-info">
            <div class="user-name">Sam Altman</div>
            <div class="user-role">Platform Admin</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
for icon, name in NAV_ITEMS:
    active_class = "active" if st.session_state.current_page == name else ""
    if st.sidebar.button(
        f"{icon}  {name}",
        key=f"nav_{name}",
        use_container_width=True,
    ):
        st.session_state.current_page = name
        st.rerun()
st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f'<div style="padding: 0.5rem 1rem; color: #64748b; font-size: 0.75rem;">'
    f'Meta AI Platform v2.1.0<br>'
    f'Build 2026.06.19<br>'
    f'API: backend:8000</div>',
    unsafe_allow_html=True,
)

page = st.session_state.current_page

if page == "Dashboard":
    from pages.dashboard import show
elif page == "Agent Studio":
    from pages.agent_studio import show
elif page == "Agent Marketplace":
    from pages.agent_marketplace import show
elif page == "Tool Registry":
    from pages.tool_registry import show
elif page == "RAG Studio":
    from pages.rag_studio import show
elif page == "Evaluation Center":
    from pages.evaluation_center import show
elif page == "Observability":
    from pages.observability import show
elif page == "Governance":
    from pages.governance import show
elif page == "Settings":
    from pages.settings import show

show()

st.markdown(
    '<div class="app-footer">Meta AI Platform v2.1.0 &mdash; '
    '&copy; 2026 Meta AI &mdash; All rights reserved</div>',
    unsafe_allow_html=True,
)

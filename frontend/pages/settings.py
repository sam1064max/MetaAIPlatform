import streamlit as st
from components.metrics import status_badge

API_BASE = "http://localhost:8000"


def show():
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94a3b8; margin-bottom: 1.5rem;">Manage your platform configuration</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["👤 Profile", "🔑 API Keys", "🔔 Notifications", "ℹ️ About"]
    )

    with tab1:
        st.markdown("### Profile Settings")
        prof_col1, prof_col2 = st.columns(2)
        with prof_col1:
            st.text_input("Name", value="Sam Altman", key="settings_name")
            st.text_input("Email", value="sam.altman@meta-ai.com", key="settings_email")
            st.text_input("Organization", value="Meta AI Corp", key="settings_org")
        with prof_col2:
            st.text_input("Title", value="Platform Administrator", key="settings_title")
            st.selectbox(
                "Timezone",
                options=["UTC", "America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"],
                index=0,
                key="settings_tz",
            )
            st.selectbox(
                "Language",
                options=["English", "Spanish", "French", "German", "Chinese", "Japanese"],
                index=0,
                key="settings_lang",
            )

        if st.button("💾 Save Profile", type="primary"):
            st.success("Profile updated successfully!")

        st.markdown("---")
        st.markdown("### Theme")
        theme = st.select_slider(
            "Interface Theme",
            options=["Dark", "Light"],
            value="Dark",
            key="settings_theme",
            disabled=True,
        )
        st.caption("Theme switching is currently in preview. Dark mode is the default.")

    with tab2:
        st.markdown("### API Keys")
        st.markdown(
            '<div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">'
            "Manage API keys for platform access. Keys are masked for security.</div>",
            unsafe_allow_html=True,
        )

        api_keys = [
            {"name": "Production", "key": "sk-prod-***a1b2", "created": "2026-01-15", "status": "active"},
            {"name": "Development", "key": "sk-dev-***c3d4", "created": "2026-03-22", "status": "active"},
            {"name": "Staging", "key": "sk-stage-***e5f6", "created": "2026-04-10", "status": "revoked"},
        ]

        for k in api_keys:
            badge = status_badge(k["status"])
            cols = st.columns([2, 3, 1.5, 1.5, 1])
            with cols[0]:
                st.markdown(f"**{k['name']}**")
            with cols[1]:
                st.markdown(f"<code>{k['key']}</code>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<span style='color:#64748b;font-size:0.8rem;'>{k['created']}</span>", unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f"{badge}", unsafe_allow_html=True)
            with cols[4]:
                if k["status"] == "active":
                    if st.button("Revoke", key=f"revoke_{k['name']}"):
                        k["status"] = "revoked"
                        st.rerun()

        st.markdown("---")
        st.markdown("### Generate New Key")
        key_col1, key_col2 = st.columns(2)
        with key_col1:
            key_name = st.text_input("Key Name", placeholder="e.g., ci-cd-pipeline")
        with key_col2:
            key_role = st.selectbox("Role", options=["admin", "developer", "analyst", "viewer"])
        if st.button("🔑 Generate Key", type="primary"):
            st.success(f"API key generated: sk-{key_name or 'new'}-{st.session_state.get('auth_token', 'xxxx')[:8]}")

    with tab3:
        st.markdown("### Notification Preferences")
        st.markdown(
            '<div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">'
            "Configure which events trigger notifications.</div>",
            unsafe_allow_html=True,
        )

        notif_options = [
            ("Agent Deployment", "When agents are deployed or updated", True),
            ("Evaluation Complete", "When agent evaluations finish", True),
            ("Cost Alerts", "When monthly cost exceeds threshold", True),
            ("Error Alerts", "When error rate exceeds 5%", True),
            ("Model Updates", "When new models become available", False),
            ("Compliance Reports", "When compliance reports are generated", True),
            ("User Activity", "When new users join or roles change", False),
            ("System Updates", "Platform version updates and maintenance", True),
        ]

        for name, desc, default in notif_options:
            cols = st.columns([2, 3, 1])
            with cols[0]:
                st.markdown(f"**{name}**")
            with cols[1]:
                st.markdown(f"<span style='color:#64748b;font-size:0.8rem;'>{desc}</span>", unsafe_allow_html=True)
            with cols[2]:
                st.toggle("", value=default, key=f"notif_{name.replace(' ', '_')}")

        if st.button("💾 Save Preferences", type="primary"):
            st.success("Notification preferences saved!")

    with tab4:
        st.markdown("### About Meta AI Platform")

        about_items = [
            ("Platform Version", "2.1.0"),
            ("Build", "2026.06.19-1842"),
            ("API Endpoint", "http://localhost:8000"),
            ("Streamlit Version", "1.41.1"),
            ("Python Runtime", "3.11+"),
            ("License", "Enterprise License"),
            ("Support", "support@meta-ai.com"),
        ]

        for label, value in about_items:
            cols = st.columns([2, 4])
            with cols[0]:
                st.markdown(f"**{label}**")
            with cols[1]:
                st.markdown(f"<span style='color:#94a3b8;'>{value}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(
            '<div style="text-align:center;color:#64748b;font-size:0.8rem;">'
            "Meta AI Platform &copy; 2026 Meta AI Corporation. All rights reserved.<br>"
            "Built with Streamlit &middot; Powered by FastAPI &middot; Secured by Enterprise Grade Security</div>",
            unsafe_allow_html=True,
        )

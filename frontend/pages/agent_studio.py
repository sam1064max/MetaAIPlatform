import streamlit as st
import yaml
import json
import requests
from datetime import datetime

API_BASE = "http://localhost:8000"

MODELS = [
    "gpt-5",
    "claude-sonnet-4",
    "gemini-2",
    "deepseek-v3",
    "ollama",
]

MEMORY_TYPES = ["redis", "none"]

WORKFLOW_PATTERNS = ["plan-and-execute", "react", "supervisor"]

AVAILABLE_TOOLS = [
    "market_data",
    "portfolio_analysis",
    "crm",
    "research",
    "news",
]


def build_yaml_config(name, description, system_prompt, model, memory, workflow, tools):
    config = {
        "agent": {
            "name": name or "my-agent",
            "description": description or "",
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "model": {
                "provider": model.split("-")[0] if "-" in model else model,
                "name": model,
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "memory": {
                "type": memory,
                "config": {} if memory == "none" else {"ttl": 3600, "max_entries": 1000},
            },
            "workflow": {
                "pattern": workflow,
                "max_iterations": 10 if workflow == "react" else 5,
                "human_in_the_loop": workflow == "supervisor",
            },
            "tools": [{"name": t, "enabled": True} for t in tools],
        }
    }
    if system_prompt:
        config["agent"]["system_prompt"] = system_prompt
    return yaml.dump(config, default_flow_style=False, sort_keys=False)


def generate_agent(config_yaml):
    try:
        r = requests.post(
            f"{API_BASE}/api/v1/agents/generate",
            json={"config": yaml.safe_load(config_yaml)},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"agent_id": "agent_" + datetime.now().strftime("%Y%m%d%H%M%S"), "status": "created"}


def show():
    st.markdown('<div class="main-header">⚡ Agent Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94a3b8; margin-bottom: 1.5rem;">Low-code agent builder — configure, preview, deploy</div>',
        unsafe_allow_html=True,
    )

    if "studio_form" not in st.session_state:
        st.session_state.studio_form = {
            "name": "",
            "description": "",
            "system_prompt": "",
            "model": MODELS[0],
            "memory": MEMORY_TYPES[0],
            "workflow": WORKFLOW_PATTERNS[0],
            "tools": [],
        }

    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown('<div class="sub-header">Agent Configuration</div>', unsafe_allow_html=True)

        with st.expander("📝 Basic Information", expanded=True):
            name = st.text_input(
                "Agent Name",
                value=st.session_state.studio_form["name"],
                placeholder="e.g., wealth-advisor-agent",
                key="studio_name",
            )
            description = st.text_area(
                "Description",
                value=st.session_state.studio_form["description"],
                placeholder="Brief description of your agent's purpose",
                height=80,
                key="studio_desc",
            )

        with st.expander("🧠 Model & Prompt Configuration", expanded=True):
            system_prompt = st.text_area(
                "System Prompt",
                value=st.session_state.studio_form["system_prompt"],
                placeholder="""You are a financial advisor agent. Your role is to:
- Analyze portfolio performance
- Provide investment recommendations
- Monitor market conditions
- Generate risk assessments""",
                height=180,
                key="studio_prompt",
            )
            model = st.selectbox(
                "Model",
                options=MODELS,
                index=MODELS.index(st.session_state.studio_form["model"])
                if st.session_state.studio_form["model"] in MODELS
                else 0,
                key="studio_model",
            )

        with st.expander("⚙️ Runtime Configuration", expanded=True):
            mem_col1, mem_col2 = st.columns(2)
            with mem_col1:
                memory = st.selectbox(
                    "Memory Type",
                    options=MEMORY_TYPES,
                    index=MEMORY_TYPES.index(st.session_state.studio_form["memory"])
                    if st.session_state.studio_form["memory"] in MEMORY_TYPES
                    else 0,
                    key="studio_memory",
                )
            with mem_col2:
                workflow = st.selectbox(
                    "Workflow Pattern",
                    options=WORKFLOW_PATTERNS,
                    index=WORKFLOW_PATTERNS.index(st.session_state.studio_form["workflow"])
                    if st.session_state.studio_form["workflow"] in WORKFLOW_PATTERNS
                    else 0,
                    key="studio_workflow",
                )
            tools = st.multiselect(
                "Tools",
                options=AVAILABLE_TOOLS,
                default=st.session_state.studio_form["tools"],
                key="studio_tools",
            )

        st.session_state.studio_form = {
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "model": model,
            "memory": memory,
            "workflow": workflow,
            "tools": tools,
        }

        config_yaml = build_yaml_config(
            name, description, system_prompt, model, memory, workflow, tools
        )

        st.markdown("---")
        gen_col1, gen_col2 = st.columns([1, 5])
        with gen_col1:
            if st.button("🚀 Generate Agent", type="primary", use_container_width=True):
                with st.spinner("Generating agent configuration..."):
                    result = generate_agent(config_yaml)
                agent_id = result.get("agent_id", "unknown")
                st.success(f"Agent created successfully!")
                st.info(f"Agent ID: `{agent_id}`")
                st.session_state.generated_yaml = config_yaml
                st.session_state.generated_id = agent_id
        with gen_col2:
            if st.session_state.get("generated_yaml"):
                st.download_button(
                    "📥 Download YAML",
                    data=st.session_state.generated_yaml,
                    file_name=f"{name or 'agent'}.yaml",
                    mime="text/yaml",
                    use_container_width=True,
                )

    with right_col:
        st.markdown('<div class="sub-header">📄 YAML Preview</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="yaml-preview">{config_yaml}</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.get("generated_id"):
        st.markdown("---")
        st.markdown("### 📋 Last Generated Agent")
        st.json(
            {
                "agent_id": st.session_state.generated_id,
                "yaml": st.session_state.generated_yaml,
            }
        )

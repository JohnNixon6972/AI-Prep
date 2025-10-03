# frontend/app.py
import streamlit as st
import requests
from urllib.parse import urljoin

API_BASE = st.sidebar.text_input("Backend URL", value="http://localhost:8000")

st.set_page_config(page_title="Multi-Agent Risk Forecaster", layout="wide")
st.title("🏗️ Multi-Agent Risk Forecaster (Practice)")

with st.sidebar:
    st.header("Models")
    models = ["gpt-4.1-mini", "gpt-4.1-mini"]
    model_a = st.selectbox("Model A (primary)", models, index=0)
    model_b = st.selectbox("Model B (compare)", models, index=1)
    st.markdown("---")
    st.header("Project")
    projects = {
        "None": None, "River Bridge Expansion (proj_A)": "proj_A", "City Mall Renovation (proj_B)": "proj_B"}
    project_choice = st.selectbox(
        "Select project to ground on", list(projects.keys()))

prompt = st.text_area(
    "Ask a question (e.g., 'What risks could delay Project A?')", height=140)

if st.button("Run multi-agent pipeline"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        payload = {"model_a": model_a, "model_b": model_b,
                   "prompt": prompt, "project_id": projects[project_choice]}
        try:
            resp = requests.post(urljoin(API_BASE, "/ask"),
                                 json=payload, timeout=120)
        except Exception as e:
            st.error(f"Failed to contact backend: {e}")
            raise

        if resp.status_code != 200:
            st.error(f"Backend error: {resp.text}")
        else:
            res = resp.json()
            st.subheader("🧭 Planner decision")
            st.json(res["plan"])
            st.subheader("📂 Retrieved docs (RAG)")
            st.json(res["docs"])
            st.subheader("📉 Forecaster (primary model output)")
            st.json(res["forecast"])
            st.subheader("⚖️ Evaluator (compare models)")
            st.json(res["evaluation"])
            st.write(f"Pipeline latency: {res.get('latency_ms')} ms")
            st.info(
                "Logs are written to backend/logs/query_logs.csv — fetch and download from backend if needed.")

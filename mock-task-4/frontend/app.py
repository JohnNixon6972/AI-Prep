# frontend/app.py
import streamlit as st
import requests
import pandas as pd
from io import StringIO

API = "http://localhost:8000"

st.set_page_config(page_title="nPlan Practice UI", layout="wide")
st.title("nPlan-style LLM Practice Sandbox")

# Simple sidebar config
st.sidebar.header("Config")
models = ["gpt-4.1-mini","gpt-4.1-mini"]
project_choices = {
    "None": None,
    "River Bridge Expansion (proj_A)": "proj_A",
    "City Mall Renovation (proj_B)": "proj_B"
}

tab = st.tabs(["Chat", "Compare & Eval", "Agent (RAG)", "Logs & Export"])[0]  # we'll use manual sections below

# Chat section
st.header("💬 Chat (single model)")
col1, col2 = st.columns([1, 1])
with col1:
    model_choice = st.selectbox("Select model", models, index=0)
    project_choice = st.selectbox("Ground answers on project", list(project_choices.keys()))
    user_prompt = st.text_area("Prompt", height=150)
    if st.button("Run Chat"):
        if not user_prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            payload = {"model": model_choice, "prompt": user_prompt, "project_id": project_choices[project_choice]}
            r = requests.post(f"{API}/query", json=payload)
            if r.status_code == 200:
                data = r.json()
                st.success("Response:")
                st.write(data["response"])
                st.write(f"Latency: {data.get('latency_ms', 'n/a')} ms")
            else:
                st.error(r.text)

# Compare & Eval
st.markdown("---")
st.header("📊 Compare & Eval (side-by-side)")
eval_col1, eval_col2 = st.columns(2)
with eval_col1:
    eval_model_a = st.selectbox("Model A", models, index=0, key="ma")
with eval_col2:
    eval_model_b = st.selectbox("Model B", models, index=1, key="mb")

eval_prompt = st.text_area("Prompt to compare", height=120, key="eval_prompt")
eval_project_choice = st.selectbox("Ground on project (compare)", list(project_choices.keys()), key="eval_proj")

if st.button("Run Compare"):
    if not eval_prompt.strip():
        st.warning("Enter a prompt.")
    else:
        payload = {"model_a": eval_model_a, "model_b": eval_model_b, "prompt": eval_prompt, "project_id": project_choices[eval_project_choice]}
        r = requests.post(f"{API}/eval", json=payload)
        if r.status_code == 200:
            res = r.json()
            a = res["responses"][eval_model_a]["response"]
            b = res["responses"][eval_model_b]["response"]
            colA, colB = st.columns(2)
            with colA:
                st.subheader(f"{eval_model_a}")
                st.write(a)
                st.write(f"Latency: {res['responses'][eval_model_a]['latency_ms']} ms")
            with colB:
                st.subheader(f"{eval_model_b}")
                st.write(b)
                st.write(f"Latency: {res['responses'][eval_model_b]['latency_ms']} ms")
            st.write("### Your preference")
            pref = st.radio("Which response is better?", [eval_model_a, eval_model_b, "Tie"], index=0)
            st.success(f"You picked: {pref}")
        else:
            st.error(r.text)

# Agent (RAG) section
st.markdown("---")
st.header("🕵️ Agent (RAG-enabled)")
agent_model = st.selectbox("Agent model", models, index=0, key="agent_model")
agent_project = st.selectbox("Ground agent on project", list(project_choices.keys()), key="agent_proj")
agent_task = st.text_input("Agent task (e.g., 'Assess critical path risk for Project A')", key="agent_task")
if st.button("Run Agent"):
    payload = {"model": agent_model, "task": agent_task, "project_id": project_choices[agent_project]}
    r = requests.post(f"{API}/agent", json=payload)
    if r.status_code == 200:
        d = r.json()
        st.subheader("Tool outputs")
        st.json(d.get("tool_outputs", []))
        st.subheader("Agent response")
        st.write(d.get("response", ""))
        st.write(f"Latency: {d.get('latency_ms')} ms")
    else:
        st.error(r.text)

# Logs & export
st.markdown("---")
st.header("📥 Logs & Export")
if st.button("Fetch logs"):
    r = requests.get(f"{API}/logs")
    if r.status_code == 200:
        csv_text = r.json().get("csv", "")
        st.text_area("Raw CSV", csv_text, height=200)
        try:
            df = pd.read_csv(StringIO(csv_text))
            st.dataframe(df)
            csv_bytes = csv_text.encode("utf-8")
            st.download_button("Download logs CSV", csv_bytes, file_name="query_logs.csv")
        except Exception as e:
            st.error(f"Failed to parse CSV: {e}")
    else:
        st.error(r.text)

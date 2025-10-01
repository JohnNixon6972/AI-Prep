import streamlit as st
import requests

st.set_page_config(page_title="LiteLLM Playground", layout="wide")

st.title("🦾 LiteLLM Playground")

tab1, tab2, tab3 = st.tabs(["Chatbot", "Agent", "Evals"])

# --- Chatbot Tab ---
with tab1:
    st.header("Chatbot")
    models = ["gpt-4.1-mini"]
    prompt = st.text_area("Enter your prompt:")
    model_choice = st.selectbox("Choose a model:", models)

    if st.button("Run Chatbot"):
        response = requests.post(
            "http://localhost:8000/query",
            json={"model": model_choice, "prompt": prompt}
        )
        st.write(response.json())

# --- Agent Tab ---
with tab2:
    st.header("Agent Mode")
    agent_query = st.text_input("Ask the agent (e.g., 'What is 5*12?'):")
    agent_model = st.selectbox("Choose a model for agent:", ["gpt-4.1-mini"])

    if st.button("Run Agent"):
        response = requests.post(
            "http://localhost:8000/agent",
            json={"model": agent_model, "query": agent_query}
        )
        st.write(response.json())

# --- Evals Tab ---
with tab3:
    st.header("LLM Evaluations")
    if st.button("Run Evals"):
        response = requests.get("http://localhost:8000/evals")
        results = response.json()["results"]
        for r in results:
            st.write(r)

import streamlit as st
from datetime import datetime
import os
import time
import json
from llm_utils import call_model

st.set_page_config(page_title="nPlan Mock LLM Task", layout="wide")

st.title("🔍 Model Comparison Playground")
st.write("Compare outputs from multiple LLM providers using LiteLLM")

# User input
prompt = st.text_area("Enter your question or prompt:", height=120)

# Model choices
models = [
    "gpt-4.1-mini",
    "anthropic/claude-3-haiku",
]
selected_models = st.multiselect(
    "Select models to compare:", models, default=models)

if st.button("Run Comparison"):
    if not prompt:
        st.warning("Please enter a prompt first!")
    else:
        cols = st.columns(len(selected_models))
        results = {}
        for i, m in enumerate(selected_models):
            with cols[i]:
                st.subheader(m)
                start = time.time()
                output = call_model(m, prompt)
                latency = round(time.time() - start, 2)
                word_count = len(output.split())
                st.write(output)
                st.caption(f" {latency}s | {word_count} words")
                results[m] = output

        # Simple evaluation feedback
        st.write("### 👍 Rate the best output")
        best = st.radio("Which model performed better?",
                        options=selected_models)

        if st.button("Submit Feedback"):
            os.makedirs("logs", exist_ok=True)
            feedback = {
                "timestamp": str(datetime.now()),
                "prompt": prompt,
                "best": best,
                "results": results
            }
            with open("logs/feedback.log", "a") as f:
                f.write(
                    json.dumps(feedback) + "\n"
                )
            st.success("Feedback saved!")

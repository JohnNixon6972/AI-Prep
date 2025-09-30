import streamlit as st
from rag_agent import extract_pdf_text, chunk_text, build_index, retrieve, run_agent

st.set_page_config(page_title="📄 RAG Agent", layout="wide")

st.title("📄 RAG Agent with PDF Upload + Streaming")

uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_pdf:
    with st.spinner("Extracting text..."):
        text = extract_pdf_text(uploaded_pdf)
        chunks = chunk_text(text)
        index, chunks = build_index(chunks)
    st.success("Index built!")

    query = st.text_area("Ask a question about the PDF:")
    model = st.selectbox("Choose model", ["gpt-4.1-mini", "anthropic/claude-3-haiku"])

    if st.button("Ask"):
        with st.spinner("Thinking..."):
            context_chunks = retrieve(query, index, chunks)
            response_stream = run_agent(query, context_chunks, model)

            st.write("### Answer:")
            placeholder = st.empty()
            answer = ""
            for chunk in response_stream:
                delta = chunk["choices"][0]["delta"].get("content", "")
                if not delta:
                    break
                answer += delta
                placeholder.write(answer)

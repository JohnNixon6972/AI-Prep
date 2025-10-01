# 📋 New Task: RAG + Agent Prototype

**Scenario:**

We want to evolve the comparison playground into a  **document QA agent** .

* Users should  **upload a PDF** .
* The app should extract and chunk text.
* Build a **retrieval index** (vector store).
* Allow users to  **ask questions about the PDF** .
* An **agent** uses retrieval + LLM to answer.
* Outputs should **stream token by token** for better UX.

**Stretch goal:** Keep model choice flexible (LiteLLM providers).

---

# 🛠️ Implementation Plan

1. **File upload + PDF text extraction**
   * Use `pypdf` or `pdfplumber`.
   * Chunk text into manageable segments.
2. **Embed & store**
   * Use LiteLLM-compatible embeddings (`openai/text-embedding-ada-002` or similar).
   * Store in in-memory FAISS vector store (fast for prototypes).
3. **Retriever**
   * For each question, find top-k relevant chunks.
4. **Agent orchestration**
   * Pass context (retrieved chunks) + user query into chosen model.
   * Format: “Answer using only the context below.”
5. **Streaming output**
   * Stream responses token by token in Streamlit.

import os
import faiss
import numpy as np
from litellm import completion, embedding
from pypdf import PdfReader
from dotenv import load_dotenv
load_dotenv()


def extract_pdf_text(pdf_file) -> str:
    """Extract raw text from PDF file."""
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text: str, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def build_index(chunks, embed_model="text-embedding-ada-002"):
    """Embed chunks and store in FAISS index."""
    vectors = []
    for chunk in chunks:
        vec = embedding(model=embed_model, input=chunk, api_base="http://localhost:4000", api_key=os.getenv(
            "LITELLM_API_KEY"))["data"][0]["embedding"]

        vectors.append(vec)

    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype("float32"))
    return index, chunks


def retrieve(query, index, chunks, embed_model="text-embedding-ada-002", k=3):
    """Return top-k relevant chunkls for query."""

    q_vec = embedding(model=embed_model, input=query, api_base="http://localhost:4000", api_key=os.getenv(
        "LITELLM_API_KEY"))["data"][0]["embedding"]

    D, I = index.search(np.array([q_vec]).astype("float32"), k)
    return [chunks[i] for i in I[0]]


def run_agent(query, context_chunks, model="gpt-4.1-mini"):
    """Use LiteLLM to answer based on retrieved chunks."""
    context = "\n\n".join(context_chunks)
    system_prompt = (
        "You are a helpful assistant. Answer the question using ONLY the context below.\n\n"
        f"Context:\n{context}\n\n"
        "If the answer is not in the context, say 'I don’t know based on the document.'"
    )
    return completion(
        model=model,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": query}],
        api_base="http://localhost:4000",
        api_key=os.getenv("LITELLM_API_KEY"),
        stream=True,  # enable streaming
    )

# backend/rag_utils.py
import json
from typing import List, Dict
import os

# Very small prompt templates; keep modular for quick changes
PROMPT_TEMPLATES = {
    "system": "You are an expert construction project analyst. Answer concisely and reference project facts provided in context when relevant.",
    "agent_system": "You are an agent that should use available tools and project context to perform multi-step reasoning. Be explicit about steps and final answer."
}

def load_projects(path: str):
    """
    Loads a small JSON file of projects. Each project has id, name, and a list of events/milestones
    """
    if not os.path.exists(path):
        # Try relative to this file
        here = os.path.dirname(__file__)
        alt = os.path.join(here, path)
        if os.path.exists(alt):
            path = alt
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalize into list of docs
    projects = {p["id"]: p for p in data.get("projects", [])}
    return projects

def retrieve_relevant_docs(projects: Dict[str, Dict], project_id: str, query: str, top_k: int = 3) -> List[Dict]:
    """
    Very simple retriever: scores milestone text by overlap with query tokens.
    For the practice task this is sufficient; in real life you'd use embeddings + vector DB.
    """
    project = projects.get(project_id)
    if not project:
        return []
    items = project.get("milestones", [])
    qtokens = set(query.lower().split())
    scored = []
    for m in items:
        text = f"{m.get('date','')}: {m.get('title','')} - {m.get('notes','')}"
        tokens = set(text.lower().split())
        score = len(qtokens.intersection(tokens))
        scored.append({"text": text, "score": score})
    # sort by score desc, fallback to chronological
    scored_sorted = sorted(scored, key=lambda x: (-x["score"], x["text"]))[:top_k]
    return scored_sorted

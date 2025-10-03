import json, os
from typing import Dict, List

PROMPT_TEMPLATES = {
    "system": "You are an expert construction project analyst. Answer clearly.",
    "forecaster": "You are a risk forecaster. Identify possible delays or risks in project milestones and estimate impacts."
}

def load_projects(path: str):
    if not os.path.exists(path):
        here = os.path.dirname(__file__)
        alt = os.path.join(here, path)
        if os.path.exists(alt):
            path = alt
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {p["id"]: p for p in data.get("projects", [])}

def retrieve_relevant_docs(projects: Dict, pid: str, query: str, top_k: int = 3) -> List[Dict]:
    proj = projects.get(pid)
    if not proj:
        return []
    q = set(query.lower().split())
    scored = []
    for m in proj["milestones"]:
        text = f"{m['date']}: {m['title']} - {m['notes']}"
        score = len(set(text.lower().split()) & q)
        scored.append({"text": text, "score": score})
    return sorted(scored, key=lambda x: -x["score"])[:top_k]

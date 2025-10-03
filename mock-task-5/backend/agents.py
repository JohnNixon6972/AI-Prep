import litellm
import logging
from rag_utils import PROMPT_TEMPLATES
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import time

load_dotenv()

logger = logging.getLogger("agents")
logging.basicConfig(level=logging.INFO)


def call_model(model_name: str, messages: List[Dict[str, str]], timeout: int = 60, max_retries: int = 2) -> Dict[str, Any]:
    attempt = 0
    while True:
        attempt += 1
        start = time.time()
        try:
            resp = litellm.completion(
                model=model_name, messages=messages, timeout=timeout, api_base="http://localhost:4000",
                api_key=os.getenv("LITELLM_API_KEY"))
            latency = int((time.time() - start) * 1000)
            return {"resp": resp, "latency": latency, "error": None}
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            logger.exception(f"call_model error on {model_name}: {e}")
            if attempt > max_retries:
                return {"resp": None, "latency": latency, "error": str(e)}
            time.sleep(0.5 * attempt)


def extract_text(resp: Any) -> str:
    if not resp:
        return ""
    try:
        if isinstance(resp, dict) and "choices" in resp and len(resp["choices"]) > 0:
            ch = resp["choices"][0]
            if isinstance(ch, dict) and "message" in ch and "content" in ch["message"]:
                return ch["message"]["content"]

        if isinstance(resp, dict) and "content" in resp:
            return resp["content"]
        if isinstance(resp, dict) and "text" in resp:
            return resp["text"]

    except Exception:
        pass

    try:
        return str(resp)
    except:
        return ""

# --- Planner ---


def planner_agent(prompt: str) -> Dict:
    """Very simple routing: classify task type."""
    if "risk" in prompt.lower() or "delay" in prompt.lower():
        return {"action": "risk_forecast", "confidence": 0.8}
    elif "what" in prompt.lower() or "list" in prompt.lower():
        return {"action": "lookup", "confidence": 0.6}
    else:
        return {"action": "general", "confidence": 0.5}

# --- Retriever ---


def retriever_agent(projects: Dict, project_id: str, query: str, top_k: int = 3) -> List[Dict]:
    from rag_utils import retrieve_relevant_docs
    docs = retrieve_relevant_docs(projects, project_id, query, top_k=top_k)
    return docs

# --- Forecaster ---


def forecaster_agent(docs: List[Dict], query: str, model: str) -> Dict:
    context = "\n".join([d["text"] for d in docs])
    messages = [
        {"role": "system", "content": PROMPT_TEMPLATES["forecaster"]},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
    ]
    resp = litellm.completion(model=model, messages=messages, api_base="http://localhost:4000",
                              api_key=os.getenv("LITELLM_API_KEY"))
    answer = resp["choices"][0]["message"]["content"]
    return {"model": model, "forecast": answer}

# --- Evaluator ---


def evaluator_agent(query: str, docs: List[Dict], model_a: str, model_b: str) -> Dict:
    context = "\n".join([d["text"] for d in docs])
    responses = {}
    for m in [model_a, model_b]:
        msgs = [
            {"role": "system", "content": PROMPT_TEMPLATES["system"]},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
        ]
        called = call_model(m, msgs)
        text = extract_text(called["resp"])
        responses[m] = {"text": text, "latency_ms":
                        called["latency"], "error": called["error"]}

    def score_response(text: str) -> float:
        if not text:
            return 0.0
        s = 0.0

        low = text.lower()
        if "delay" in low or "delayed" in low:
            s += 0.4
        if "week" in low or "weeks" in low:
            s += 0.3
        if "confidence" in low or "%" in low:
            s += 0.2

        L = len(text.split())
        if 30 <= L <= 300:
            s += 0.2
        elif L < 30:
            s += 0.1
        else:
            s += 0.0

        return min(s, 1.0)

    scores = {m: score_response(responses[m]["text"]) for m in responses}

    winner = max(scores, key=scores.get)

    return {"responses": responses, "scores": scores, "winner": winner}

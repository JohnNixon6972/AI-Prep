# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import time
import csv
import os
from typing import List, Dict, Any
import litellm
from rag_utils import load_projects, retrieve_relevant_docs, PROMPT_TEMPLATES
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Basic config
LOG_FILE = "query_logs.csv"
os.makedirs("logs", exist_ok=True)
LOG_FILEPATH = os.path.join("logs", LOG_FILE)

# Initialize app
app = FastAPI(title="nPlan Practice LLM API")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

# Load sample project data
# expects relative path when running from backend/
PROJECTS = load_projects("../data/projects.json")

# Ensure a CSV log header exists
if not os.path.exists(LOG_FILEPATH):
    with open(LOG_FILEPATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "model", "endpoint",
                        "prompt", "response_len", "latency_ms", "error"])

# Pydantic models


class QueryRequest(BaseModel):
    model: str
    prompt: str
    project_id: str = None  # optional: which project to ground on


class EvalRequest(BaseModel):
    model_a: str
    model_b: str
    prompt: str
    project_id: str = None


class AgentRequest(BaseModel):
    model: str
    task: str
    project_id: str = None

# Helper: call liteLLM with retries and basic observability


def call_model(model_name: str, messages: List[Dict[str, str]], max_retries: int = 2) -> Dict[str, Any]:
    attempt = 0
    while True:
        attempt += 1
        start = time.time()
        try:
            # Example using litellm.completion (API may differ by version)
            # This code assumes litellm.completion returns a dict similar to OpenAI responses.
            resp = litellm.completion(model=model_name, messages=messages, timeout=60,  api_base="http://localhost:4000",
                                      api_key=os.getenv("LITELLM_API_KEY"),)
            latency_ms = int((time.time() - start) * 1000)
            return {"resp": resp, "latency_ms": latency_ms, "error": None}
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            logger.exception(f"Model call error (model={model_name}): {e}")
            if attempt > max_retries:
                return {"resp": None, "latency_ms": latency_ms, "error": str(e)}
            time.sleep(0.5 * attempt)


def log_query(model: str, endpoint: str, prompt: str, response_len: int, latency_ms: int, error: str = ""):
    ts = int(time.time())
    with open(LOG_FILEPATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([ts, model, endpoint, prompt.replace(
            "\n", " "), response_len, latency_ms, error])


def extract_content_from_completion(resp: Dict[str, Any]) -> str:
    """
    Try common response shapes to extract text content.
    Keep defensive since different providers have different response shapes.
    """
    if resp is None:
        return ""
    # Try common shape used earlier in examples
    try:
        # litellm may return {'choices': [{'message': {'content': '...'}}]}
        if "choices" in resp and len(resp["choices"]) > 0:
            ch = resp["choices"][0]
            if isinstance(ch, dict) and "message" in ch and "content" in ch["message"]:
                return ch["message"]["content"]
        # Some providers return 'content' at top level
        if "content" in resp:
            return resp["content"]
        # Or 'text' field
        if "text" in resp:
            return resp["text"]
    except Exception:
        pass
    # Fallback: stringify
    try:
        return str(resp)
    except Exception:
        return ""


@app.post("/query")
async def query_model(request: QueryRequest):
    """
    Basic model query endpoint. If project_id is provided, we use RAG to add context.
    """
    model = request.model
    prompt = request.prompt
    project_id = request.project_id

    # Construct system + user messages using prompt template
    system_prompt = PROMPT_TEMPLATES["system"]
    user_prompt = prompt

    # If grounding to a project, retrieve docs and add to context
    context_snippet = ""
    if project_id:
        docs = retrieve_relevant_docs(PROJECTS, project_id, prompt, top_k=3)
        context_snippet = "\n\n".join([d["text"] for d in docs])
        user_prompt = f"Project context:\n{context_snippet}\n\nUser question:\n{prompt}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    called = call_model(model, messages)
    resp, latency_ms, error = called["resp"], called["latency_ms"], called["error"]
    content = extract_content_from_completion(resp)
    response_len = len(content)

    # logging / observability
    log_query(model=model, endpoint="/query", prompt=prompt,
              response_len=response_len, latency_ms=latency_ms, error=error or "")

    if error:
        raise HTTPException(status_code=500, detail={"error": error})

    return {"model": model, "response": content, "latency_ms": latency_ms, "grounding": bool(project_id), "context_snippet": context_snippet}


@app.post("/eval")
async def eval_models(request: EvalRequest):
    """
    Compare outputs of two models for the same prompt and return both responses.
    """
    prompt = request.prompt
    model_a = request.model_a
    model_b = request.model_b
    project_id = request.project_id

    # Optionally retrieve context
    context_snippet = ""
    if project_id:
        docs = retrieve_relevant_docs(PROJECTS, project_id, prompt, top_k=3)
        context_snippet = "\n\n".join([d["text"] for d in docs])
        prompt = f"Project context:\n{context_snippet}\n\nUser question:\n{prompt}"

    messages = [{"role": "system", "content": PROMPT_TEMPLATES["system"]},
                {"role": "user", "content": prompt}]

    # Run both models (sequentially for now)
    result = {}
    for m in [model_a, model_b]:
        called = call_model(m, messages)
        resp, latency_ms, error = called["resp"], called["latency_ms"], called["error"]
        content = extract_content_from_completion(resp)
        result[m] = {"response": content,
                     "latency_ms": latency_ms, "error": error}
        log_query(model=m, endpoint="/eval", prompt=request.prompt,
                  response_len=len(content), latency_ms=latency_ms, error=error or "")

    return {"prompt": request.prompt, "project_id": project_id, "responses": result, "context_snippet": context_snippet}


@app.post("/agent")
async def agent(request: AgentRequest):
    """
    Simple agent that can use a small set of tools:
    - retrieve project context (RAG)
    - run a number-fact tool (via numbersapi)
    - perform a small internal calc tool (eval)
    The agent will be asked to plan steps and produce a final answer.
    """
    model = request.model
    task = request.task
    project_id = request.project_id

    # Simple tool outputs
    tool_outputs = []
    # RAG tool
    if project_id:
        docs = retrieve_relevant_docs(PROJECTS, project_id, task, top_k=3)
        rag_text = "\n\n".join([d["text"] for d in docs])
        tool_outputs.append({"tool": "rag", "output": rag_text})
    # number tool
    import re
    import requests
    nums = re.findall(r"\b\d+\b", task)
    if nums:
        n = nums[0]
        try:
            fact = requests.get(
                f"http://numbersapi.com/{n}/math", timeout=5).text
            tool_outputs.append({"tool": "numbersapi", "output": fact})
        except Exception:
            tool_outputs.append(
                {"tool": "numbersapi", "output": "numbersapi unavailable"})

    # calc tool (unsafe eval guarded)
    if "calculate" in task.lower() or "what is" in task.lower():
        # keep it very simple and safe:
        safe_expr = "".join([c for c in task if c in "0123456789+-*/(). "])
        if safe_expr.strip():
            try:
                calc_res = eval(safe_expr)
                tool_outputs.append({"tool": "calc", "output": str(calc_res)})
            except Exception:
                pass

    # Build prompt for the agent model
    tool_desc = "\n".join(
        [f"[{t['tool']}]: {t['output']}" for t in tool_outputs]) or "No tools used."
    agent_input = f"You are an agent with tools. Task: {task}\n\nTool outputs:\n{tool_desc}\n\nPlease plan steps, use the tool outputs where relevant, and give a final concise answer."

    messages = [{"role": "system", "content": PROMPT_TEMPLATES["agent_system"]},
                {"role": "user", "content": agent_input}]

    called = call_model(model, messages)
    resp, latency_ms, error = called["resp"], called["latency_ms"], called["error"]
    content = extract_content_from_completion(resp)

    log_query(model=model, endpoint="/agent", prompt=task,
              response_len=len(content), latency_ms=latency_ms, error=error or "")

    if error:
        raise HTTPException(status_code=500, detail={"error": error})

    return {"model": model, "response": content, "tool_outputs": tool_outputs, "latency_ms": latency_ms}


@app.get("/logs")
async def get_logs():
    """
    Return CSV logs as text (small scale). In production, you'd expose via a secure storage.
    """
    if not os.path.exists(LOG_FILEPATH):
        raise HTTPException(status_code=404, detail="No logs found.")
    with open(LOG_FILEPATH, "r", encoding="utf-8") as f:
        data = f.read()
    return {"csv": data}

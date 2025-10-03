from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import time

from agents import planner_agent, retriever_agent, forecaster_agent, evaluator_agent
from rag_utils import load_projects
from utils import log_event

# FastAPI app
app = FastAPI(title="Multi-Agent Risk Forecaster API")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

PROJECTS = load_projects("../data/projects.json")

# Schemas
class AskRequest(BaseModel):
    model_a: str
    model_b: str
    prompt: str
    project_id: str | None = None


@app.post("/ask")
async def ask(req: AskRequest):
    start = time.time()

    # Step 1: Planner decides route
    plan = planner_agent(req.prompt)
    log_event(endpoint="/ask", agent="planner", model=str(req.model_a)+","+str(req.model_b),prompt=req.prompt,response=str(plan),latency_ms=0)

    # Step 2: Retriever fetches docs if needed
    docs = []
    if plan["action"] in ["lookup", "risk_forecast"] and req.project_id:
        docs = retriever_agent(PROJECTS, req.project_id, req.prompt)
        log_event(endpoint="/ask", agent="retriever", model="",prompt=req.prompt, response=str(docs), latency_ms=0)


    # Step 3: Forecaster if risk analysis
    forecast = None
    if plan["action"] == "risk_forecast":
        forecast = forecaster_agent(docs, req.prompt, req.model_a)

    # Step 4: Evaluator compares outputs
    evaluation = evaluator_agent(req.prompt, docs, req.model_a, req.model_b)
    latency = int((time.time() - start) * 1000)

    
    result =  {
        "plan": plan,
        "docs": docs,
        "forecast": forecast,
        "evaluation": evaluation,
        "latency_ms": latency,
    }

    log_event(endpoint="/ask",agent="orchestrator", model=f"{req.model_a},{req.model_b}",prompt=req.prompt,response="completed",latency_ms=latency)
    return result

@app.get("/health")
async def health():
    return {"status":"ok"}

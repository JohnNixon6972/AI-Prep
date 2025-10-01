from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import litellm
import logging
from agent import run_agent
from dotenv import load_dotenv
import os
from evals import run_evals


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(title="LiteLLM Chatbot API")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    model: str
    prompt: str


@app.post("/query")
async def query_model(request: QueryRequest):
    try:
        response = litellm.completion(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            api_base="http://localhost:4000",
            api_key=os.getenv("LITELLM_API_KEY"),
        )
        return {"model": request.model, "response": response["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AgentRequest(BaseModel):
    model: str
    query: str


@app.post("/agent")
async def run_agent_endpoint(request: AgentRequest):
    try:
        response = run_agent(request.query, request.model)
        return {"model": request.model, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evals")
async def run_eval_endpoint():
    try:
        results = run_evals()
        print(results)
        return {"results": results}
    except Exception as e:
        logger.exception("Error while running evals")
        raise HTTPException(status_code=500, detail=str(e))

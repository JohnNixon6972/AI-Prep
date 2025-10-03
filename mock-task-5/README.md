# Multi-Agent Risk Forecaster (Practice Repo)

## Features

- Planner Agent: routes question → lookup / risk forecast / general
- Retriever Agent: fetches project milestones (RAG-style)
- Forecaster Agent: predicts risks/delays using LLM
- Evaluator Agent: compares outputs of 2 models
- Streamlit UI to view all steps

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

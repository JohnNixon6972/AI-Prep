# practice-nplan-task

Advanced practice repo for an nPlan-style on-site AI Engineer task.

## Overview

This repo contains a FastAPI backend and a Streamlit frontend that:

- Calls multiple LLMs via LiteLLM (you provide API keys in env).
- Implements a tiny RAG (retrieval over a small JSON dataset).
- Provides an agent endpoint that can use simple tools.
- Logs queries to CSV for basic observability.
- Provides an evaluation flow (compare 2 models + record preference).

## Setup

### 1) Python environment

Create a virtualenv and install dependencies for backend and frontend.

```bash
# from repo root
python -m venv venv
source venv/bin/activate

# backend deps
cd backend
pip install -r requirements.txt

# frontend deps
cd ../frontend
pip install -r requirements.txt
```

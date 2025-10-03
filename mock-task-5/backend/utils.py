import time
import csv
import os
import logging
from typing import Dict, Any


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "query_logs.csv")
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger("backend_utils")
logging.basicConfig(level=logging.INFO)


if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ts", "endpoint", "agent", "model",
                        "prompt", "response_len", "error"])


def log_event(endpoint: str, agent: str, model: str, prompt: str, response: str, latency_ms: int, error: str = ""):
    ts = int(time.time())
    row = [ts, endpoint, agent, model, prompt.replace("\n", " "),len(response),latency_ms, error]
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)
    logger.info(f"LOG [{endpoint}] agent={agent} model={model} latency={latency_ms}ms error={error}")


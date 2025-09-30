import os
import time
import logging
from litellm import completion
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(filename="logs/app.log", level=logging.INFO)
load_dotenv()

# Retry decorator for robustness


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_model(provider: str, prompt: str) -> str:
    start = time.time()
    try:
        response = completion(
            model=provider,
            messages=[{"role": "user", "content": prompt}],
            api_base="http://localhost:4000",
            api_key=os.getenv("LITELLM_API_KEY"),
        )
        latency = round(time.time() - start, 2)
        result = response["choices"][0]["message"]["content"]
        logging.info(f"SUCCESS | model = {provider} | latency = {latency}s")
        return result
    except Exception as e:
        logging.error(f"FAIL | model={provider} | error = {str(e)}")
        return f"❌ Error calling {provider}: {str(e)}"

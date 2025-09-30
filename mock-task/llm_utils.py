import os
from litellm import completion
from tenacity import retry, stop_after_attempt, wait_fixed

# Retry decorator for robustness
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_model(provider: str, prompt: str) -> str:
    """
    Call an LLM provider via LiteLLM.
    provider: e.g. "openai/gpt-3.5-turbo" or "anthropic/claude-3-haiku"
    """
    try:
        response = completion(
            model=provider,
            messages=[{"role": "user", "content": prompt}],
            api_key=os.getenv("LITELLM_API_KEY"),
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error calling {provider}: {str(e)}"

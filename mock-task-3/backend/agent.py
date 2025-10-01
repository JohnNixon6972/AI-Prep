import litellm
from dotenv import load_dotenv
import os

load_dotenv()

# Simple tools


def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


TOOLS = {
    "calculator": calculator,
}


def run_agent(query: str, model="gpt-4.1-mini"):
    """
    A simple ReAct-style agent using LiteLLM.
    Supports tool use (calculator).
    """
    system_prompt = """
    You are a helpful assistant. 
    You can use tools when needed. 
    Available tools: calculator(expression).
    If using a tool, output in format: TOOL: <tool_name> <input>.
    Otherwise, just answer directly.
    """

    history = [{"role": "system", "content": system_prompt}]
    history.append({"role": "user", "content": query})

    # Step 1: Get LLM response
    response = litellm.completion(
        model=model,
        messages=history,
        api_base="http://localhost:4000",
        api_key=os.getenv("LITELLM_API_KEY"),
    )
    content = response["choices"][0]["message"]["content"]

    # Step 2: If it wants to use a tool
    if content.startswith("TOOL:"):
        _, tool_call = content.split(":", 1)
        tool_name, tool_input = tool_call.strip().split(" ", 1)
        if tool_name in TOOLS:
            tool_result = TOOLS[tool_name](tool_input)
            # Feed back to LLM
            history.append({"role": "assistant", "content": content})
            history.append(
                {"role": "user", "content": f"Tool result: {tool_result}"})
            response = litellm.completion(
                model=model,
                messages=history,
                api_base="http://localhost:4000",
                api_key=os.getenv("LITELLM_API_KEY"),
            )
            return response["choices"][0]["message"]["content"]
    return content

from utils import LiteLLM
from dotenv import load_dotenv
import litellm
from langchain.evaluation.criteria import Criteria, CriteriaEvalChain
from langchain.prompts import ChatPromptTemplate
import os
import logging
logger = logging.getLogger(__name__)


load_dotenv()

# Define test cases
TEST_CASES = [
    {"input": "What is 2+2?", "expected": "4"},
    {"input": "Summarize: The Eiffel Tower is in Paris",
        "expected": "Eiffel Tower is in Paris"},
]

prompt = ChatPromptTemplate.from_template(
    "You are an evaluator. Evaluate the model output below for {criteria}.\n"
    "Input: {input}\n"
    "Output: {output}\n"
    "Respond with a score (0-1) or a short comment."
)


def run_evals(models=["gpt-4.1-mini"]):
    eval_llm = LiteLLM()
    results = []
    evaluator = CriteriaEvalChain.from_llm(
        llm=eval_llm,
        criteria_name="correctness",
        prompt=prompt
    )

    for case in TEST_CASES:
        for model in models:
            try:
                response = litellm.completion(
                    model=model,
                    messages=[{"role": "user", "content": case["input"]}],
                    api_base="http://localhost:4000",
                    api_key=os.getenv("LITELLM_API_KEY"),
                )
                output = response["choices"][0]["message"]["content"]

                score = evaluator.evaluate_strings(
                    output=output,
                    input=case["input"],
                    prediction=output
                )
                results.append({
                    "model": model,
                    "input": case["input"],
                    "output": output,
                    "expected": case["expected"],
                    "score": score
                })
            except Exception as e:
                logger.error(
                    f"Eval failed for model={model}, input={case['input']}, error={e}")
                results.append({
                    "model": model,
                    "input": case["input"],
                    "error": str(e)
                })

    return results

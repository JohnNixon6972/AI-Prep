
import os
from dotenv import load_dotenv
from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs.llm_result import LLMResult
from langchain_core.outputs.generation import Generation
from typing import List, Optional, Mapping, Any
import litellm


load_dotenv()
class LiteLLM(BaseLLM):
    model_name: str = "gpt-4.1-mini"

    def _generate(
        self, prompts: List[str], stop: Optional[List[str]] = None
    ) -> LLMResult:
        generations = []
        for prompt in prompts:
            response = litellm.completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                api_base="http://localhost:4000",
                api_key=os.getenv("LITELLM_API_KEY"),
            )
            text = response["choices"][0]["message"]["content"]
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        return "litellm"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name}
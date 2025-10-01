# 📝 Mock Problem Statement (Practice)

**Context**

nPlan is experimenting with AI assistants to help construction planners. The current prototype is a simple chatbot that queries a single LLM (GPT-3.5) and returns responses.

**Problem**

While useful, the prototype has several limitations:

1. It only supports **one model** (GPT-3.5). We want flexibility to try **multiple providers** (OpenAI, Anthropic, Google).
2. It has **no agentic capabilities** (e.g., cannot use tools like calculator or fetch structured results).
3. It has  **no evaluation framework** , so we cannot measure whether one model’s output is “better” than another’s.
4. It lacks **observability** (no logging of latency, cost, or errors).

**Your Task (4h, with team)**

* **Part A: Multi-model support**
  * Extend the chatbot to use **LiteLLM** so it can call multiple providers.
  * Allow users to **select models** or  **compare outputs side-by-side** .
* **Part B: Agent Mode**
  * Add a simple **agent framework** (e.g., tool use for calculator).
  * Let users test queries that require reasoning + tool use.
* **Part C: LLM Evaluations**
  * Implement a small **evaluation harness** with test cases.
  * Log and score outputs (e.g., correctness, faithfulness).
  * Present insights (e.g., “Claude gave more accurate math, GPT was faster”).

**Deliverables**

1. A working app with three modes:
   * **Chatbot** (multi-model)
   * **Agent** (tool use)
   * **Evals** (scoring test cases)
2. A **short presentation (15 min)** covering:
   * What you inherited (the old GPT-only chatbot).
   * What you built/improved.
   * A live demo of each mode.
   * What you learned (tradeoffs, bugs, surprises).
   * Next steps if you had more time (e.g., adding construction-specific RAG).

**Scenario (refined):**

You start with a minimal LLM-based prototype that answers questions (e.g. “What are risks in this construction schedule?”). It uses a single OpenAI model and lacks robustness, evaluation, or switching.

Your mission (within ~4 hours) is to:

1. **Integrate LiteLLM / abstraction layer**
   * Make it possible to switch between at least two providers (e.g. OpenAI + Anthropic or OpenAI + a fine-tuned model).
   * Ensure consistent handling of response formats.
2. **Model comparison / evaluation UI / metrics**
   * Let the user submit a question, then show side-by-side results from two models.
   * Additionally, allow a quick human evaluation metric (e.g. a “which is better?” button or score 1–5).
   * Log all queries + responses + selected best (for future analysis).
3. **Robustness & observability**
   * Add error handling, retries, timeouts.
   * Instrument basic metrics: response times, success/failure counts, logging.
   * Optionally, expose a simple health-check or metrics endpoint.
4. **Light Web front-end**
   * Build a simple web UI (could be Streamlit, Flask, or minimal React) so a non-technical user can try it.
   * Show model selection, a compare view, evaluation input.
5. **Demo + plan next steps**
   * Present what works, show gaps, propose further enhancements (e.g. caching, cost control, real-time streaming, model fine-tuning, deployment).

This aligns better with shipping prototypes, managing multiple LLM pipelines, evaluation, and front-end / API design.

# Advanced Mock On-Site Task (Practice)

### Scenario

nPlan helps forecast risks and delays in large construction projects. You’re given a **prototype LLM app** that can answer questions about project schedules (milestones, risks, timelines).

**Current Limitations:**

1. Only queries one LLM (GPT-3.5).
2. Answers are generic and don’t use project data.
3. No way to compare outputs across models.
4. No evaluation of answer quality.
5. No logging/observability (you don’t know which model was called, latency, or errors).

---

### Your Task

Improve this prototype so it’s closer to something nPlan could actually use in production:

1. **Multi-Model Support**
   * Integrate **LiteLLM** to support GPT-4, Claude, Gemini, etc.
   * Allow switching models or running comparisons side-by-side.
2. **Domain-Aware Agent**
   * Add a simple **RAG (Retrieval-Augmented Generation)** layer over a provided mini dataset (e.g., JSON/CSV of project milestones).
   * Example:
     * User: *“What’s the critical path risk in Project A?”*
     * Agent should retrieve schedule data → LLM reasons over it → returns grounded answer.
3. **Evaluation Mode**
   * Implement a way to evaluate responses:
     * Automatic metrics (latency, token usage, cost).
     * Human preference logging (let user pick which model’s answer was better).
4. **Observability**
   * Log each query with:
     * Model used
     * Latency
     * Response length
     * Errors (if any)
5. **Presentation**
   * At the end, prepare a 15-minute presentation covering:
     * What the app could/couldn’t do before.
     * What you added (demo).
     * Tradeoffs (speed vs. accuracy, complexity vs. reliability).
     * Next steps if you had more time (e.g., fine-tuning domain models, advanced eval pipelines).

---

### Stretch Goals (if time permits)

* Build a simple **FastAPI backend** +  **Streamlit frontend** .
* Allow exporting evaluation logs to CSV.
* Implement a lightweight **prompt template system** for construction questions.

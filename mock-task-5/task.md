🏗️ Advanced Prep Task: Multi-Agent Construction Risk Forecaster

### **Scenario**

nPlan wants to explore how **multi-agent systems** could help project managers identify  **risks in construction schedules** . You’re given a dataset of milestones for two projects (like the earlier `projects.json`).

Right now, there’s only a **basic chatbot** that answers “What is happening in Project A?” using a single LLM.

---

### **Your Task**

Build a **multi-agent prototype** that improves this app:

#### 1. **Planner Agent**

* Takes the user’s question.
* Decides if it’s:
  * a **data lookup** (needs retrieval from schedule),
  * a **risk forecast** (requires reasoning over delays, dependencies),
  * or a **general explanation** (just use the LLM).
* Routes task accordingly.

#### 2. **Retriever Agent**

* Uses a **RAG pipeline** to fetch project milestones from `projects.json`.
* Summarizes the relevant schedule facts.

#### 3. **Forecaster Agent**

* Uses reasoning + retrieved facts to identify possible **risks** (e.g., steel delivery delayed → critical path at risk).
* Outputs structured JSON:
  ```json
  {
    "risk": "Steel delivery delay",
    "impact": "3 weeks late on pier construction",
    "confidence": 0.7
  }
  ```

#### 4. **Evaluator Agent**

* Compares responses from **two models** (e.g., GPT-4 vs Claude).
* Rates them on  **clarity, correctness, and risk relevance** .
* Logs evaluation scores.

---

### **Requirements**

1. **Multi-agent orchestration** : basic planner → retriever/forecaster → evaluator.
2. **Observability** : log each agent’s step, latency, and model used.
3. **UI** (Streamlit):
   * User enters a question.
   * Shows each agent’s contribution (planner decision, retriever docs, forecaster risks, evaluator scores).
4. **Export logs** : to CSV for later analysis.

---

### **Stretch Goals**

* Add  **voting mechanism** : if evaluator disagrees strongly, fallback to a different model.
* Add **timeout + retry** if an agent fails.
* Add **confidence scoring** (planner agent outputs confidence in its routing decision).

---

### **Example Interaction**

 **User** : *“What risks could delay Project A?”*

* **Planner Agent** : “This is a risk forecast task → route to retriever + forecaster.”
* **Retriever Agent** : Finds “Steel delivery delayed by 3 weeks.”
* **Forecaster Agent** : Predicts:

> “Steel delivery delay may push back pier construction → overall delay ~3 weeks. Risk confidence 0.7.”

* **Evaluator Agent** : Compares GPT-4 vs Claude’s forecast. GPT-4 is clearer → assigns higher score.
* **UI Output** : Shows retrieved facts, risks identified, evaluator scores.

---

✅ This task directly tests:

* **Multi-agent orchestration** (role separation, planner-executor-evaluator).
* **LLM app prototyping** (LiteLLM + multiple models).
* **RAG grounding** (domain-specific).
* **Evaluation lifecycle** (structured scoring).
* **Observability** (logs + latency).

# Skynet R2 — AI Logistics Control Tower

An agentic AI system that autonomously monitors shipments, predicts delays, and takes corrective action across a simulated supply-chain network. Built around a LangGraph-orchestrated reasoning loop, a local Llama 3 LLM, classical ML risk models, and a FAISS-backed long-term memory — with industry-style guardrails and human-in-the-loop escalation on top.

---

## Why this exists

Real logistics control towers are reactive — operators stare at dashboards and put out fires. Skynet R2 explores the next step: an agent that **observes** events, **reasons** about root cause using both ML predictions and similar past situations, **decides** an action, and only acts after passing a strict guardrail layer. Anything risky, expensive, or low-confidence gets escalated to a human.

---

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────┐     ┌──────────────┐
│  Simulator  │ ──▶ │              LangGraph Agent                  │ ──▶ │  Dashboard   │
│  (events)   │     │                                               │     │ (React + TS) │
└─────────────┘     │  Perception → Predict → Memory → Reason →     │     └──────────────┘
                    │             Guardrails → Action               │
                    │                                               │
                    │  ML Models   │  FAISS    │  Llama 3 (Ollama)  │
                    │  (sklearn)   │  (vector  │  + Tool Calling    │
                    │              │   memory) │                    │
                    └──────────────────────────────────────────────┘
                                          │
                                          ▼
                                  ┌───────────────┐
                                  │ SQLite Audit  │
                                  │     Log       │
                                  └───────────────┘
```

**Flow per shipment event**

1. **Perception** — raw shipment dict is normalized into a `ShipmentContext` (distance, weather risk, traffic risk, queue time, carrier reliability, mode, priority, cost cap).
2. **Predict** — two scikit-learn RandomForest pipelines run in parallel: a classifier for delay probability and a regressor for ETA in minutes.
3. **Memory** — the context is embedded into a 128-dim vector and queried against a FAISS index of historical shipments to retrieve the top-k similar past situations.
4. **Reason** — Llama 3 (via Ollama) receives the context, ML predictions, and retrieved memory, then proposes a decision (`reroute`, `prioritize`, `expedite`, `escalate_to_human`, `none`) with a confidence and root-cause analysis.
5. **Guardrails** — the proposed decision is rewritten if it violates any policy:
   - Confidence below 0.65 → escalate
   - Estimated cost impact above the shipment's cost cap → escalate
   - Reroute requested on a SEA-mode shipment → escalate (vessels are not autonomously rerouted)
6. **Act + Audit** — autonomous decisions are executed against the simulator; every decision (including human overrides) is logged to SQLite for replay and analysis.

---

## Tech stack

**Backend:** Python, FastAPI, LangGraph, Ollama (Llama 3), scikit-learn, FAISS, SQLite, Pydantic
**Frontend:** React 18, TypeScript, Tailwind CSS, Vite, lucide-react, framer-motion
**Other:** REST API, CORS, joblib model serialization

---

## Project structure

```
Skynet_R2/
├── backend/
│   ├── api/                 # FastAPI app + endpoints
│   ├── agent/               # LangGraph workflow, LLM client, tools, short-term memory
│   ├── perception/          # Raw event → ShipmentContext
│   ├── predictive/          # Delay classifier + ETA regressor (training + saved models)
│   ├── memory/              # FAISS long-term vector memory
│   ├── reasoning/           # LLM reasoning engine
│   ├── decision/            # Decision engine
│   ├── guardrails/          # Confidence / cost / safety policy checks
│   ├── actions/             # LangChain tools (reroute, prioritize, escalate, no-op)
│   ├── simulator/           # Synthetic shipment + event generator
│   ├── learning/            # SQLite audit logger
│   └── models/              # delay_model + eta_model wrappers
└── frontend/
    ├── src/                 # Control-tower dashboard
    ├── index.html
    └── vite.config.ts
```

---

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com/) running locally with the Llama 3 model pulled:
  ```bash
  ollama pull llama3
  ollama serve
  ```

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn scikit-learn faiss-cpu joblib pandas numpy requests langgraph langchain pydantic

# Train the ML models once (generates synthetic dataset + saves .pkl files)
python -m backend.predictive.train_models

# Run the API
uvicorn backend.api.main:app --reload
```

Backend will be live at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard will be live at `http://localhost:5173`.

---

## API

| Method | Endpoint            | Purpose                                                     |
|--------|---------------------|-------------------------------------------------------------|
| GET    | `/simulate`         | Generate a random shipment event and run the full agent loop |
| POST   | `/custom_simulate`  | Submit a user-defined shipment from the UI                   |
| POST   | `/operator_action`  | Human-in-the-loop override for an escalated shipment         |

Example response (truncated):

```json
{
  "shipment": { "shipment_id": 42, "origin": "Mumbai", "destination": "Singapore", ... },
  "result": {
    "decision": "reroute",
    "risk_score": 0.83,
    "reasoning": {
      "root_cause": "High port queue time combined with low carrier reliability",
      "confidence": 0.78
    }
  }
}
```

---

## Guardrails

| # | Rule                                | Trigger                                         | Action                |
|---|-------------------------------------|-------------------------------------------------|-----------------------|
| 1 | Confidence floor                    | LLM confidence < 0.65                           | Escalate to human     |
| 2 | Cost cap                            | Estimated cost > shipment's cost constraint      | Escalate to human     |
| 3 | SEA-mode safety policy              | Decision is `reroute` on a SEA shipment          | Escalate to human     |

Guardrails run *after* reasoning and *before* action — the LLM never executes anything directly.

---

## What's intentionally not production-grade

This is a hackathon/exploration project. A few honest caveats:

- Training data is synthetic, generated by hand-tuned heuristics in `train_models.py`.
- FAISS embeddings are deterministic hash-based vectors, not real text embeddings (would swap in `sentence-transformers` or OpenAI embeddings for production).
- Actions are simulated against an in-memory simulator, not a real TMS / WMS.
- No tests, CI, or container deployment yet.

---

## Roadmap

- Replace mock embeddings with `sentence-transformers/all-MiniLM-L6-v2`
- Add reinforcement-style learning loop that updates the agent's prompt/memory based on logged outcomes
- Replace synthetic training data with a public logistics dataset
- Dockerize backend + frontend, add CI
- Add unit tests for guardrails and decision engine
- Stream agent thoughts to the dashboard via WebSocket

---

## License

MIT

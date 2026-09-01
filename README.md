# AI Customer Support Intelligence & RAG Assistant

A portfolio-grade full-stack application that turns a raw customer complaint into a
structured, grounded response:

1. A user submits a complaint.
2. The backend classifies **intent** (fine-tuned DistilBERT), **sentiment**, and
   **priority**.
3. A **RAG pipeline** (LangChain + PostgreSQL/pgvector) retrieves relevant knowledge
   base passages.
4. **Groq** generates a response grounded in the retrieved context — never inventing
   policy when context is insufficient.
5. The complaint, analysis, retrieved sources, and generated response are persisted
   and shown in a Next.js frontend (Dashboard, New Complaint, Analysis Results,
   History, Knowledge Base).

## Tech stack

| Layer      | Stack |
|------------|-------|
| Frontend   | Next.js, TypeScript, Tailwind CSS, shadcn/ui, Motion, Recharts |
| Backend    | FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, Uvicorn |
| Database   | PostgreSQL + pgvector |
| ML/NLP     | PyTorch, Hugging Face Transformers, scikit-learn (TF-IDF baseline, BiLSTM, DistilBERT) |
| RAG        | LangChain, langchain-postgres, langchain-huggingface |
| LLM        | Groq API, behind a provider abstraction |

See [TECH_STACK.md](TECH_STACK.md) for the full list and dependency rules.

## Repository layout

```
project-root/
├── backend/        FastAPI service (app/, alembic/, tests/)
├── frontend/        Next.js app (src/app, src/features, src/components)
├── ml/              Dataset pipeline + TF-IDF / BiLSTM / DistilBERT training & evaluation
├── data/            Knowledge base markdown docs + processed dataset splits (raw data is gitignored)
├── docs/            Full specification set (per-component specs + acceptance criteria)
├── deploy/nginx/    Reverse proxy config for a single-VPS deployment
├── docker-compose.yml         Local Postgres + pgvector
├── docker-compose.prod.yml    Production stack (Postgres, backend, frontend, Nginx)
└── requirements.txt            Backend + ML Python dependencies
```

## Getting started (local development)

### Prerequisites

- Python 3.11
- Node.js 20+
- Docker (for PostgreSQL + pgvector)
- A [Groq API key](https://console.groq.com) — only required to generate the final
  grounded response; classification, retrieval, and the rest of the app work without
  one, and the automated test suite never calls the real Groq API.

### 1. Configure environment variables

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

Edit `.env` and set `GROQ_API_KEY` and `GROQ_MODEL` (e.g. `llama-3.1-8b-instant`).
Adjust `POSTGRES_*` values if you don't want the defaults. Never commit `.env` —
it's already covered by `.gitignore`.

### 2. Start PostgreSQL + pgvector

```bash
docker compose up -d
```

### 3. Install backend/ML Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
cd backend
alembic upgrade head
cd ..
```

### 5. Build the ML models

Runs the full dataset pipeline once, then trains and evaluates all three intent
classifiers on the same split:

```bash
python -m ml.data.pipeline          # download (Hugging Face), validate, clean, dedupe, split
python -m ml.baseline.train         # TF-IDF + Logistic Regression
python -m ml.bilstm.train           # BiLSTM
python -m ml.distilbert.train full  # DistilBERT fine-tune (use `smoke` for a fast CPU sanity run)
python -m ml.evaluation.run         # compares all three and selects the production model
```

The comparison and the model-selection rationale are written to
`ml/evaluation/artifacts/COMPARISON_REPORT.md` (see [below](#ml-model-comparison) for
the current results). The backend always loads the currently-selected DistilBERT
artifact automatically — no manual wiring needed.

### 6. Ingest the knowledge base

```bash
cd backend
python -m app.services.ingestion.pipeline   # loads data/knowledge_base/*.md, chunks, embeds, stores in pgvector
```

### 7. Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

### 8. Run the frontend

```bash
cd ../frontend
npm install
npm run dev
```

Visit `http://localhost:3000`.

## Testing

```bash
cd backend && python -m pytest -q      # backend suite — Groq is mocked, no live API key needed
cd ml && python -m pytest -q            # ML pipeline/model suite
cd frontend && npm run lint && npx tsc --noEmit && npm test
```

## ML model comparison

All three models are trained on the same seed-42 stratified train/validation/test
split and scored once, after freezing, on the same held-out test set (2,699
examples). Full detail (per-class confusion pairs, latency percentiles, selection
rationale) is in `ml/evaluation/artifacts/COMPARISON_REPORT.md`.

| Model | Accuracy | Macro F1 | Weighted F1 | Size | Mean latency |
|---|---|---|---|---|---|
| TF-IDF + Logistic Regression | 0.9918 | 0.9918 | 0.9919 | 1.22 MB | 2.06 ms |
| BiLSTM | 0.9926 | 0.9926 | 0.9926 | 1.61 MB | 2.84 ms |
| **DistilBERT (production)** | **0.9978** | **0.9979** | **0.9978** | 256.21 MB | 86.81 ms |

**Selected for production: DistilBERT.** It has the highest macro F1 among all
candidates (primary selection metric); weighted F1, accuracy, and latency are
tracked as secondary/tie-break metrics but did not require a tie-break here.

## Architecture & specifications

- [REQUIREMENTS.md](REQUIREMENTS.md) — functional and non-functional requirements
- [ARCHITECTURE.md](ARCHITECTURE.md) — request flow, RAG flow, ML flow, layering rules
- [DATABASE.md](DATABASE.md) / [API_SPEC.md](API_SPEC.md) — schema and API contract
- [docs/](docs/) — per-component specs (ML, RAG, LangChain, LLM, backend, database,
  frontend, testing, security, deployment) and
  [docs/project/MASTER_ACCEPTANCE_CRITERIA.md](docs/project/MASTER_ACCEPTANCE_CRITERIA.md)

## Deployment

See [docs/deployment/DEPLOYMENT_SPEC.md](docs/deployment/DEPLOYMENT_SPEC.md).
`docker-compose.prod.yml` provisions PostgreSQL + pgvector, the backend, and the
frontend, fronted by the Nginx config in `deploy/nginx/ai-customer-support.conf`, for
a single Docker-compatible VPS. All production secrets are injected through the
hosting environment, never bundled into the frontend build.

## Important notes

- The documents under `data/knowledge_base/` are **fictional demo content**, not real
  company policy.
- The raw Bitext dataset is downloaded programmatically (`ml/data/download.py`) and
  is not committed to the repository.
- If retrieval doesn't find relevant context, the system says so explicitly instead
  of inventing an answer.

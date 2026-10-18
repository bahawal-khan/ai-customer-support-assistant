<div align="center">

# 🤖 AI Customer Support Intelligence & RAG Assistant

**A portfolio-grade full-stack application that turns a raw customer complaint into a structured, grounded response — automatically.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-customer--support.khanova.tech-6D28D9?style=for-the-badge&logo=vercel&logoColor=white)](https://customer-support.khanova.tech)

[![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL%20%2B%20pgvector-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=flat-square&logo=groq&logoColor=white)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](#license)

</div>

---

## ✨ Overview

Submit a customer complaint and get **intent, sentiment, and priority classification**, **relevant knowledge-base sources**, and an **AI-generated response grounded in your own documentation** — never invented.

1. A user submits a complaint.
2. The backend classifies **intent** (fine-tuned DistilBERT), **sentiment**, and **priority**.
3. A **RAG pipeline** (LangChain + PostgreSQL/pgvector) retrieves relevant knowledge base passages.
4. **Groq** generates a response grounded in the retrieved context — never inventing policy when context is insufficient.
5. The complaint, analysis, retrieved sources, and generated response are persisted and shown in a Next.js frontend (Dashboard, New Complaint, Analysis Results, History, Knowledge Base).

---

## 📸 Screenshots

<img width="1312" height="633" alt="image" src="https://github.com/user-attachments/assets/b4cc7f96-8397-48d5-8dfc-acb4ad934439" />


<img width="1356" height="635" alt="image" src="https://github.com/user-attachments/assets/98f4f1d4-7210-4db9-8e9a-42bcd59bbed6" />


<img width="1215" height="617" alt="image" src="https://github.com/user-attachments/assets/7e0058b9-1c82-4a01-b22f-0212df85534d" />


---

## 🧱 Tech Stack

| Layer      | Stack |
|------------|-------|
| **Frontend**   | Next.js, TypeScript, Tailwind CSS, shadcn/ui, Motion, Recharts |
| **Backend**    | FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, Uvicorn |
| **Database**   | PostgreSQL + pgvector |
| **ML / NLP**   | PyTorch, Hugging Face Transformers, scikit-learn (TF-IDF baseline, BiLSTM, DistilBERT) |
| **RAG**        | LangChain, langchain-postgres, langchain-huggingface |
| **LLM**        | Groq API, behind a provider abstraction |

See [TECH_STACK.md](TECH_STACK.md) for the full list and dependency rules.

---

## 📂 Repository Layout

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

---

## 🚀 Getting Started (Local Development)

### Prerequisites

- Python 3.11
- Node.js 20+
- Docker (for PostgreSQL + pgvector)
- A [Groq API key](https://console.groq.com) — only required to generate the final grounded response; classification, retrieval, and the rest of the app work without one, and the automated test suite never calls the real Groq API.

### 1. Configure environment variables

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

Edit `.env` and set `GROQ_API_KEY` and `GROQ_MODEL` (e.g. `llama-3.1-8b-instant`). Adjust `POSTGRES_*` values if you don't want the defaults. Never commit `.env` — it's already covered by `.gitignore`.

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

Runs the full dataset pipeline once, then trains and evaluates all three intent classifiers on the same split:

```bash
python -m ml.data.pipeline          # download (Hugging Face), validate, clean, dedupe, split
python -m ml.baseline.train         # TF-IDF + Logistic Regression
python -m ml.bilstm.train           # BiLSTM
python -m ml.distilbert.train full  # DistilBERT fine-tune (use `smoke` for a fast CPU sanity run)
python -m ml.evaluation.run         # compares all three and selects the production model
```

The comparison and the model-selection rationale are written to `ml/evaluation/artifacts/COMPARISON_REPORT.md` (see [below](#-ml-model-comparison) for the current results). The backend always loads the currently-selected DistilBERT artifact automatically — no manual wiring needed.

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

---

## 🧪 Testing

```bash
cd backend && python -m pytest -q      # backend suite — Groq is mocked, no live API key needed
cd ml && python -m pytest -q            # ML pipeline/model suite
cd frontend && npm run lint && npx tsc --noEmit && npm test
```

---

## 📊 ML Model Comparison

All three models are trained on the same seed-42 stratified train/validation/test split and scored once, after freezing, on the same held-out test set (2,699 examples). Full detail (per-class confusion pairs, latency percentiles, selection rationale) is in `ml/evaluation/artifacts/COMPARISON_REPORT.md`.

| Model | Accuracy | Macro F1 | Weighted F1 | Size | Mean latency |
|---|---|---|---|---|---|
| TF-IDF + Logistic Regression | 0.9918 | 0.9918 | 0.9919 | 1.22 MB | 2.06 ms |
| BiLSTM | 0.9926 | 0.9926 | 0.9926 | 1.61 MB | 2.84 ms |
| **DistilBERT (production)** | **0.9978** | **0.9979** | **0.9978** | 256.21 MB | 86.81 ms |

**Selected for production: DistilBERT.** It has the highest macro F1 among all candidates (primary selection metric); weighted F1, accuracy, and latency are tracked as secondary/tie-break metrics but did not require a tie-break here.

---

## 🏗️ Architecture & Specifications

- [REQUIREMENTS.md](REQUIREMENTS.md) — functional and non-functional requirements
- [ARCHITECTURE.md](ARCHITECTURE.md) — request flow, RAG flow, ML flow, layering rules
- [DATABASE.md](DATABASE.md) / [API_SPEC.md](API_SPEC.md) — schema and API contract
- [docs/](docs/) — per-component specs (ML, RAG, LangChain, LLM, backend, database, frontend, testing, security, deployment) and [docs/project/MASTER_ACCEPTANCE_CRITERIA.md](docs/project/MASTER_ACCEPTANCE_CRITERIA.md)

---

## 🌐 Deployment

**Live at: [customer-support.khanova.tech](https://customer-support.khanova.tech)**

See [docs/deployment/DEPLOYMENT_SPEC.md](docs/deployment/DEPLOYMENT_SPEC.md) for the full guide. `docker-compose.prod.yml` provisions PostgreSQL + pgvector, the backend, and the frontend, fronted by the Nginx config in `deploy/nginx/ai-customer-support.conf`, for a single Docker-compatible VPS with HTTPS via Let's Encrypt. All production secrets are injected through the hosting environment, never bundled into the frontend build.

---

## 📝 Important Notes

- The documents under `data/knowledge_base/` are **fictional demo content**, not real company policy.
- The raw Bitext dataset is downloaded programmatically (`ml/data/download.py`) and is not committed to the repository.
- If retrieval doesn't find relevant context, the system says so explicitly instead of inventing an answer.

---

<div align="center">
<sub>Built as a portfolio project demonstrating full-stack ML/AI engineering — classification, RAG, and grounded generation, end to end.</sub>
</div>

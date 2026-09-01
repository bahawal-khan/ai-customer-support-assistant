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

> 🔗 **Try it live:** [customer-support.khanova.tech](https://customer-support.khanova.tech)

---

## 📸 Screenshots

<img width="1312" height="633" alt="image" src="https://github.com/user-attachments/assets/c7555bae-acd9-47c9-872d-91e5c7af97b6" />


<img width="1356" height="635" alt="image" src="https://github.com/user-attachments/assets/5e7578dd-6ec3-4cd5-9433-40cba7a844a8" />


<img width="1215" height="617" alt="image" src="https://github.com/user-attachments/assets/e314f4ac-053b-48a1-b931-6e8d064bafbd" />


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

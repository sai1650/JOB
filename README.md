# AI-Powered Role-Based Candidate Screening System

A production-minded starter implementation of an AI-driven, role-aware candidate
screening system. This project demonstrates an end-to-end pipeline for
automatically ingesting resumes, building candidate profiles, retrieving role-
relevant knowledge, generating grounded interview questions, running adaptive
interviews, evaluating free-text answers with an LLM + rule-based fallback, and
persisting a structured candidate assessment report.

---

## Project Overview

This system automates early-stage technical screening by combining:
- Resume parsing and structured candidate profiles
- A retrieval-augmented generation (RAG) pipeline against role-specific
  knowledge bases
- An LLM-driven question generator that only cites retrieved chunks
- An adaptive interview strategy that drives question selection
- An answer evaluator with LLM parsing and deterministic rule-based fallback
- Persisted, auditable interview reports and per-question evaluations

The codebase is organized as a monorepo with a `frontend/` React UI and a
`backend/` FastAPI service that holds models, services, and API routes.

## Problem Statement

Hiring teams need a reliable, reproducible, and auditable way to screen
technical candidates at scale. Manual phone screens are time-consuming and
inconsistent. This system aims to reduce bias and variability by producing
structured interview artifacts (questions, evaluations, and reports) that are
grounded in explicit role knowledge and the candidate's submitted materials.

## Features

- Resume upload and automated parsing (TXT/PDF, PyMuPDF optional)
- Candidate profile extraction (skills, technologies, domains)
- Role-specific knowledge base ingestion and fallback vectors
- RAG retrieval with traceable chunks and scoring
- LLM-based question generation with strict citation validation
- Adaptive interview strategy tracking session state and difficulty
- Per-answer evaluation: LLM attempted parse -> Pydantic-validated JSON ->
  rule-based fallback
- Persisted interview sessions, questions, answers, and full generated reports
- React frontend for candidate flow, interview UI, and results dashboard

## Architecture

ASCII architecture diagram (high-level):

Candidate

React Frontend

FastAPI Backend

Resume Parser

Candidate Profile

Query Builder

RAG Retriever

Role Knowledge Base

Question Generator

Interview Session

Answer Evaluator

Final Report

Each arrow denotes a flow of data (uploads, retrievals, generated outputs,
and persisted entities). The system keeps provenance: questions cite the
retrieved chunks they were derived from and the report stores the original
generated content.

## Technology Stack

- Backend: FastAPI — fast, lightweight ASGI framework with Pydantic schema
  validation and excellent testing support.
- Database: PostgreSQL recommended for production, SQLite fallback for local
  testing and CI convenience.
- ORM: SQLAlchemy — robust, battle-tested ORM with good migration tooling
  (Alembic recommended for real deployments).
- LLMs: OpenAI-compatible calls (configurable). Deterministic rule-based
  fallbacks are included for tests and resilience.
- Retrieval/RAG: Lightweight vector store scaffold with JSON fallback and a
  ranker; pluggable to FAISS / Milvus / cloud vector DBs.
- Frontend: React + Vite — modern, fast developer experience for an
  interactive interview UI.

Why these choices:
- FastAPI provides fast development with automatic OpenAPI docs and tight
  integration with Pydantic for request/response validation.
- SQLAlchemy + Postgres give production-grade transactional guarantees. A
  SQLite fallback ensures tests run without external dependencies.
- Pluggable retrieval/embedding layers allow experimentation with local
  fallbacks during development and high-performance vector DBs in production.

## Project Structure (top-level)

- backend/
  - app/
    - api/            # FastAPI route modules
    - models/         # SQLAlchemy models
    - repositories/   # DB CRUD abstractions
    - services/       # LLM, retrieval, evaluator, report generator
    - core/           # config, security helpers
    - db/             # database init and session
    - middleware/     # rate limiting, CORS, etc.
    - main.py         # FastAPI app entrypoint
- frontend/          # React application (Vite)
- knowledge_base/    # Role-specific ingestion artifacts
- tests/             # pytest suite (backend)
- docker-compose.yml
- README.md

## Database Schema (high level)

- Candidate: id, name, email, resume_filename, resume_text (optional),
  extracted_skills, extracted_technologies, extracted_domains
- InterviewSession: id, candidate_id, selected_role, status,
  strategy_state (JSON), current_question_index, started_at, completed_at
- InterviewQuestion: id, session_id, question_text, difficulty, topic,
  retrieved_context (JSON), source_reference
- InterviewAnswer: id, question_id, session_id, answer_text,
  evaluation_score, evaluation_feedback, evaluation (JSON)
- InterviewReport: id, session_id, overall_score, strengths, weaknesses,
  topic_scores (JSON), recommendation, report (full generated JSON)

All JSON columns are validated at the service boundary using Pydantic schemas
before persisting.

## RAG Pipeline (conceptual)

1. Document ingestion
   - Role knowledge bases are loaded from `knowledge_base/<role>/`.
   - Documents may be PDFs, text, or preprocessed JSON with chunked vectors.

2. Chunking
   - Text is split into semantically-sized chunks (configurable). A fallback
     JSON file with pre-chunked vectors is used when heavy dependencies are
     unavailable.

3. Embeddings
   - A pluggable embedding service produces vectors for chunks and queries.
   - In local/dev mode, a deterministic hashing-based vector is used.

4. Vector database
   - A pluggable vector store interface. Default development path uses a
     JSON-backed fallback. Swap in FAISS, Milvus, or managed vector DBs for
     production.

5. Retrieval
   - QueryBuilder constructs a retrieval query from the candidate profile,
     role, and interview history.
   - Assembler and VectorStore return candidate chunks.
   - ContextRanker boosts relevance using keyword overlap and filters low-
     relevance results.

6. Context construction
   - The final retrieval returns traceable chunks (text, source, page, score)
     used to ground question generation and evaluation. All chunks include a
     `trace_id` for auditability.

7. Question generation
   - The LLM is prompted to produce a strict JSON array of question objects
     with citations to retrieved chunks. The service validates citations —
     questions that reference unknown chunks are rejected.

## Resume Processing

- TXT resumes are decoded and cleaned.
- PDF parsing uses PyMuPDF (`fitz`) when available; otherwise PDF upload
  extraction raises a clear error and tests use monkeypatched behavior.
- The parser extracts sections, naive skill matching, technologies, and
  domain seeds. This produces a compact candidate profile used by retrieval
  and question generation.

## Adaptive Interview Logic

- `InterviewStrategy` tracks asked topics, difficulty history, scores, and
  weak/strong areas in `session.strategy_state`.
- `next` uses previous answers and strategy heuristics to pick the next topic
  and difficulty, then triggers retrieval and question generation.

## API Documentation (key endpoints)

- POST `/api/resume/upload` — upload resume (PDF or TXT) and create Candidate
- POST `/api/interviews` — create interview session and generate first
  question
- GET `/api/interviews/{session_id}` — read session with questions
- GET `/api/interviews/{session_id}/current-question` — current active question
- POST `/api/interviews/{session_id}/answer` — submit answer (evaluated)
- POST `/api/interviews/{session_id}/next` — advance to next question
- POST `/api/interviews/{session_id}/complete` — finalize interview and
  persist generated report
- GET `/api/interviews/{session_id}/report` — retrieve stored structured report

Routes use Pydantic schemas for request/response validation. The backend also
exposes OpenAPI docs when running locally via FastAPI's auto-generated UI.

## Environment Variables

- `DATABASE_URL` — primary DB (Postgres) connection string
- `OPENAI_API_KEY` — key for calling OpenAI or compatible LLM providers
- `BACKEND_HOST`, `BACKEND_PORT` — server bind settings
- Additional settings in `app/core/config.py` (CORS, rate limits, LLM retry)

## Local Setup

Prerequisites: Python 3.11+, Node 18+, and optionally Docker for containers.

Backend (quick start):

1. Create a Python virtual environment and install deps (or use `requirements.txt`):

```bash
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
```

2. Copy `.env.example` to `.env` and set `DATABASE_URL` (or use default
   sqlite fallback for testing).

3. Start the backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend in the browser and follow the upload -> interview flow.

## Docker Setup

The repository includes `docker-compose.yml` to start a Postgres instance,
the backend (Uvicorn), and the frontend dev server. For production, build
container images and enable environment secrets via your orchestrator.

Example:

```bash
docker-compose up --build
```

## Testing

- Backend tests use `pytest` and FastAPI `TestClient`.
- A test SQLite database is used in CI/local runs so tests do not require a
  Postgres container.
- LLM calls are mocked in tests; deterministic rule-based fallbacks ensure
  tests remain stable even without external LLM access.

Run tests:

```bash
cd backend
python -m pytest -q
```

## Deployment

- Use Postgres in production (set `DATABASE_URL`) and a managed vector DB or
  FAISS for retrieval scale.
- Configure a secrets manager for `OPENAI_API_KEY` and other credentials.
- Add an application-managed worker or background task queue for expensive
  ingestion and batch-report generation.

## Design Decisions

- FastAPI + Pydantic: clear schema validation and auto-documentation reduce
  runtime contract errors between frontend and backend.
- SQLAlchemy + Postgres: production-grade data integrity and migration support.
- Pluggable RAG stack: developers can start with deterministic local
  fallbacks, then migrate to FAISS / managed vector DBs without changing
  higher-level business logic.
- LLM + Rule-based evaluation: LLMs provide rich, human-like evaluations, but
  a deterministic rule-based fallback guarantees consistent output when the
  model is unavailable or returns malformed JSON.

## Limitations

- The parser is heuristic and not guaranteed to extract all skills perfectly.
- The in-memory rate limiter is not suitable for multi-process production.
- The JSON fallback vector store is not suitable for large-scale retrieval.

## Future Improvements

- Integrate FAISS or managed vector DB for scalable retrieval.
- Add Alembic migrations and a production-ready deployment manifest.
- Improve resume parsing with a dedicated parser (NLP models) and robust
  PDF OCR handling.
- Add authentication, RBAC, and per-tenant isolation for multi-company use.

## Demo Instructions

1. Start the backend (see Local Setup). If you don't have a Postgres
   instance, the app uses a local SQLite fallback for development and tests.
2. Start the frontend and open the UI in a browser.
3. Upload a resume (TXT or a simple PDF). The app extracts skills and creates
   a Candidate.
4. Create an interview for the candidate and step through the questions.
5. Submit answers to see evaluator feedback and the final persisted report on
   the Results Dashboard.

---

If you'd like, I can:
- Add a `requirements.txt` and `frontend/package.json` snippets to this
  README,
- Add CI config that runs tests and lints on push,
- Or generate a short demo script that exercises the API end-to-end.
# Candidate Screening AI

Monorepo scaffold for an AI-powered Role-Based Candidate Screening System.

Overview
- Frontend: React + TypeScript + Vite + Tailwind
- Backend: FastAPI + SQLAlchemy + Alembic + PostgreSQL
- AI: planned (LangChain, Sentence Transformers, PyMuPDF)

Quickstart (Docker)

1. Copy `.env.example` to `.env` and adjust values.

```powershell
cd candidate-screening-ai
docker-compose up --build
```

2. Frontend: http://localhost:5173
3. Backend health: http://localhost:8000/api/health

Development (local)
- Backend: run `uvicorn app.main:app --reload --port 8000 --host 0.0.0.0` inside `backend` virtualenv
- Frontend: run `npm install` then `npm run dev` inside `frontend`

Notes
- Authentication, RAG pipeline, and interview generation are intentionally deferred.
- All secrets come from environment variables.

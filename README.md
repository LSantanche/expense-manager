# Expense Manager + AI (DS-first, end-to-end)

Local-first, free, reproducible project to manage expenses with an AI pipeline:
OCR → field extraction → human-in-the-loop (confidence + evidence) → DB quality (dedup) → chat (DB-first) → analytics (forecasting/anomaly) → evaluation suite → minimal MLOps.

> Current status: **DB + Expenses CRUD API + Streamlit v1 (manual entry + list) + basic tests**.

---

## Features (now)

- ✅ Expenses CRUD API (FastAPI)
  - Create, list (filters + pagination), get by id, patch (partial update), delete
- ✅ DB layer (SQLAlchemy) + migrations (Alembic)
- ✅ Integration tests (pytest) using SQLite in-memory (fast, reproducible)
- ✅ Streamlit v1 UI (API-first): manual entry + list

---

## Tech stack

- OS: Windows (but should work on any OS)
- Python: 3.12
- Backend: FastAPI
- UI v1: Streamlit
- DB: Postgres (Docker) **or** SQLite fallback
- ORM/Migrations: SQLAlchemy + Alembic
- Quality: Ruff, Pytest, MyPy
- Dependency management: Poetry

License: MIT

---

## Repository structure

- `backend/` — FastAPI app, DB models, migrations, tests
- `ui_streamlit/` — Streamlit UI (API-first, calls the backend only)
- `ops/` — docker-compose for Postgres (dev/local)
- `ml/` — ML pipeline (OCR/extraction/forecast/anomaly) (WIP)
- `eval/` — evaluation suite (WIP)

---

## Prerequisites

- Python 3.12
- Poetry
- (Optional) Docker Desktop — only if you want Postgres locally

---

## Environment variables

The backend loads environment variables from:

- `backend/.env`

Template files:

- `.env.example` (root)
- (Recommended) `backend/.env.example` (copy the same content here)

Minimum required:

- `DATABASE_URL`

Examples:

- Postgres (Docker): `DATABASE_URL=postgresql+psycopg://expense:expense@127.0.0.1:5432/expense_db`
- SQLite fallback: `DATABASE_URL=sqlite:///./expense_manager.db`

---

## Quickstart (recommended): Postgres via Docker

### 1) Start Postgres
From repo root:

```powershell
cd ops
docker compose up -d
```

### 2) Create `backend/.env`
From repo root:

```powershell
Copy-Item .env.example backend\.env
```

### 3) Install backend dependencies

```powershell
cd backend
poetry install
```

### 4) Apply migrations

```powershell
poetry run alembic upgrade head
```

### 5) Run the API

```powershell
poetry run uvicorn app.main:app --reload
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

---

## Quickstart (no Docker): SQLite fallback

### 1) Create `backend/.env`

```powershell
Copy-Item .env.example backend\.env
```

### 2) Edit `backend/.env` and set:

```env
DATABASE_URL=sqlite:///./expense_manager.db
```

### 3) Install + migrate + run

```powershell
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

---

## Run Streamlit UI (v1)

Open a second terminal:

```powershell
cd backend
poetry run streamlit run ..\ui_streamlit\app.py
```

Streamlit will print the URL (usually http://localhost:8501).

> UI is **API-first**: it never connects to the DB directly, it only calls the backend.

---

## Run tests / lint / type-check

From `backend/`:

### Tests

```powershell
poetry run pytest
```

### Lint (Ruff)

```powershell
poetry run ruff check .
```

### Type-check (MyPy)

```powershell
poetry run mypy .
```

---

## Notes on “production-minded” choices

- **Service layer** (`app/services/...`) keeps business logic out of routes.
- **PATCH for updates** enables HITL workflows (field-by-field corrections).
- **List endpoints return `total`** for pagination + analytics.
- **Integration tests run on SQLite in-memory**: fast + no external dependencies.

---

## Roadmap (high level)

1) ✅ DB + CRUD + Streamlit v1  
2) OCR ingestion (image/PDF) → text + bbox evidence  
3) Field extraction with confidence per field + needs_review  
4) Data quality: dedup + normalization  
5) Chat: DB-first tool calling (SQL) + optional RAG on OCR text/notes  
6) Analytics: dashboard + forecasting + anomaly detection  
7) Evaluation suite: extraction F1, category F1, forecast MAE/MAPE, chatbot golden queries  
8) Minimal MLOps: Docker, CI, tracking, logging

---

## Contributing

PRs are welcome. Please keep commits small and focused.

---

## License

MIT

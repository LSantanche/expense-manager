# Expense Manager + AI (DS-first, end-to-end)

Local-first, free, reproducible project to manage expenses with an AI pipeline:  
OCR → field extraction → human-in-the-loop (confidence + evidence) → DB quality (dedup) → chat (DB-first) → analytics (forecasting/anomaly) → evaluation suite → minimal MLOps.

> Current status: **Expenses CRUD API + Streamlit v1 + Documents upload + OCR (Tesseract) for images/PDF + basic tests**.

---

## Features (now)

- ✅ Expenses CRUD API (FastAPI)
  - Create, list (filters + pagination), get by id, patch (partial update), delete
- ✅ DB layer (SQLAlchemy) + migrations (Alembic)
- ✅ Integration tests (pytest) using SQLite in-memory (fast, reproducible)
- ✅ Streamlit v1 UI (API-first): manual entry + list + filters
- ✅ Documents API
  - Upload receipts (image/PDF) to local storage
  - Persist document metadata + status in DB (`uploaded/processed/failed`)
- ✅ OCR (local, free)
  - Engine: **Tesseract** via `pytesseract`
  - Output: plain text in DB + raw JSON on disk (bbox + confidence)

---

## Tech stack

- OS: Windows (but should work on any OS)
- Python: 3.12
- Backend: FastAPI
- UI v1: Streamlit
- DB: Postgres (Docker) **or** SQLite fallback
- OCR: Tesseract (local) + PDF rendering via `pypdfium2`
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
- OCR (Windows): install **Tesseract OCR**
  - Either add it to PATH, or set `TESSERACT_CMD` in `backend/.env` (recommended for reproducibility)

---

## Environment variables

The backend loads environment variables from:

- `backend/.env`

Template files:

- `.env.example` (root)
- `backend/.env.example`

### Required
- `DATABASE_URL`

Examples:

- Postgres (Docker):  
  `DATABASE_URL=postgresql+psycopg://expense:expense@127.0.0.1:5432/expense_db?connect_timeout=3`
- SQLite fallback:  
  `DATABASE_URL=sqlite:///./expense_manager.db`

### OCR (recommended on Windows)
If `tesseract.exe` is not in PATH:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSERACT_LANG=eng
```

Optional:
- `TESSERACT_LANG=ita+eng` (only if you installed Italian language data)

---

## Local data & persistence (DB vs disk)

This project stores information in two places:

1) **Database (Postgres/SQLite)**  
   - Expenses records
   - Documents metadata and status
   - OCR plain text (`documents.ocr_text_plain`) and path to raw JSON (`documents.ocr_json_path`)

2) **Disk (local files)**  
   - Uploaded documents and OCR artifacts live under: `backend/data/`
   - This folder is **ignored by git** (local-only)

Folder layout example:
- `backend/data/documents/<document_id>/original.pdf`
- `backend/data/documents/<document_id>/ocr_result.json`

---

## Quickstart (recommended): Postgres via Docker

### 1) Start Postgres
From repo root:

```powershell
cd ops
docker compose up -d
docker compose ps
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

## OCR usage (via API)

### 1) Upload a receipt (image or PDF)
Use Swagger UI at:
- http://127.0.0.1:8000/docs

Endpoint:
- `POST /documents/upload`

You will receive a `document_id`.

### 2) Process OCR
Endpoint:
- `POST /documents/{document_id}/process-ocr`

Expected results:
- `status="processed"`
- `ocr_text_plain` populated (plain text OCR)
- `ocr_json_path` populated (path to raw JSON with bbox/confidence)

### 3) Read document status
Endpoint:
- `GET /documents/{document_id}`

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
- **OCR output storage (hybrid)**:
  - raw JSON on disk (bbox/conf + full structured output)
  - plain text in DB (easy search + future chat/RAG)

---

## Roadmap (high level)

1) ✅ DB + CRUD + Streamlit v1  
2) ✅ OCR ingestion (image/PDF) → text + bbox evidence  
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

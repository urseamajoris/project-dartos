---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.
<!--
Guidance for AI coding agents working on the Dartos repository.
Keep this file short (20–50 lines). Be specific about patterns, tools, and where to look.
-->

# Copilot instructions for project-dartos

Quick orientation (why): Dartos is a React frontend + FastAPI backend for PDF upload, OCR, embedding (ChromaDB) and LLM-driven RAG. The important code lives in `backend/` (FastAPI services and modular services) and `frontend/` (React UI). The repo includes an enhanced bootstrap (`run.py`) and Docker Compose for reproducible runs.

What to change / how to be productive:
- Prefer editing backend logic under `backend/services/*` for features like PDF extraction (`pdf_processor.py`), LLM calls (`llm_service.py`) and RAG (`rag_service.py`). API surface is in `backend/main.py` (endpoints: `/api/upload`, `/api/documents`, `/api/process`).
- Frontend changes belong in `frontend/src/` and use `src/services/api.js` to call the backend. Keep payload shapes compatible with `schemas.py` (e.g., `ProcessingRequest`).

Key developer commands (reproducible):
- Run everything with Docker (recommended): `docker compose up` from repository root. This brings up backend, Postgres, and (optionally) frontend.
- Local backend dev (requires Python env + deps):
  - `cd backend`
  - `python -m venv venv && source venv/bin/activate`
  - `pip install -r requirements.txt`
  - `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Quick Bootstrap helper: `python run.py` (installs deps, starts postgres container, sets DATABASE_URL, and launches uvicorn).

Project-specific patterns and gotchas:
- The bootstrap `run.py` manipulates `sys.path` so imports from `backend` succeed when run from repo root; tests and scripts also insert `backend` to sys.path. Prefer absolute imports inside `backend/` (e.g., `from services.pdf_processor import PDFProcessor`).
- RAG storage uses `backend/chroma_db` (Chroma PersistentClient). Tests sometimes set `CHROMA_DB_PATH` env var for isolated runs.
- LLM integration expects env var `GROK_API_KEY` (xAI) — code falls back gracefully if missing. Avoid committing keys.
- PDF processing: `pdf_processor.extract_text` prefers text extraction (PyPDF2) and falls back to OCR (pytesseract + pdf2image). System packages (libpoppler, tesseract) may be required in CI or dev VMs.

Where to look for examples/tests:
- Unit-ish smoke scripts: `test_basic.py` and `test_backend.py` run lightweight checks and illustrate how modules are imported during tests.
- Sample PDF generator: `create_sample_pdf.py` — use it to produce predictable PDF input for integration work.

When changing APIs:
- Update `backend/schemas.py` Pydantic models and keep frontend `api.js` request/response shapes in sync. Also update README usage examples and add a basic test in `test_basic.py` or `test_backend.py`.

Edge cases for agents:
- Avoid assuming real LLM keys during CI; preserve the graceful fallback behavior.
- Long-running tasks (OCR, embeddings) should respect existing chunking strategy in `rag_service.chunk_text` (chunk_size=1000, overlap=200).

If you need to run tests locally: run the scripts in repo root (`python test_basic.py` or `python test_backend.py`). These are smoke tests and expect imports to work; use the bootstrap or Docker if packages are missing.

If anything is unclear or you need more examples (API payloads, env var names, or where front/back cross), ask for clarification and I will add specific snippets.

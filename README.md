# Enterprise RAG Compliance Auditor

Automated compliance workflow for contract review against a policy corpus. The system ingests policy PDFs into Qdrant, extracts audit questions from contract text, retrieves and reranks supporting evidence, generates a structured JSON finding set, verifies evidence grounding, and renders a PDF report.

## Stack

- Backend: FastAPI, PyMuPDF, Qdrant, sentence-transformers, FlashRank, Anthropic/OpenAI failover, ReportLab
- Frontend: React, Vite, TailwindCSS
- Deployment: Docker Compose with Qdrant + backend + frontend

## Layout

- `backend/` FastAPI app, ingestion routes, workflow orchestration, services
- `frontend/` React UI for auditing and knowledge base management
- `docker-compose.yml` local orchestration

## Run locally

1. Start Qdrant:

```bash
docker compose up qdrant
```

2. Start the backend:

```bash
cd backend
uvicorn backend.main:app --reload --port 8000
```

3. Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

## Environment

Set API keys and configuration in a `.env` file under `backend/` or the workspace root:

- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `QDRANT_URL`
- `EMBEDDING_PROVIDER`
- `VECTOR_SIZE`

## API

- `POST /api/audit/run` - run a contract audit from pasted text or PDF upload
- `POST /api/ingest/upload` - ingest policy PDFs into the corpus
- `GET /api/ingest/stats` - get corpus stats
- `DELETE /api/ingest/document/{doc_id}` - delete a document by `doc_id`
- `PUT /api/ingest/page` - update a page and reindex it
- `GET /api/health` - health check

## Notes

The workflow includes guardrails and evidence verification, but production deployment should still wrap the model calls with observability, retry policies, secret management, and tenant-level access controls.

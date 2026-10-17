# FlowForge AI — Intelligent Data Pipeline Platform

FlowForge AI is a production-style portfolio MVP for data engineering. It ingests CSV files, profiles data quality, applies deterministic transformations, records successful pipeline runs, previews output, and exports the cleaned dataset. Optional LLM integration suggests conservative cleaning operations; AI is not required for core functionality.

## Features
- CSV upload with extension and size validation (default 15 MB)
- Data profile: row/column counts, nulls by column, duplicates, types, approximate memory use
- Transformations: normalize column names, trim whitespace, convert numeric-like fields, remove fully empty columns, de-duplicate, handle missing values, optional contains filter
- Preview transformed records and download the full CSV output
- Persistent run history using SQLite locally or PostgreSQL in Docker/production
- Optional AI suggestions through an OpenAI-compatible Chat Completions API
- Health endpoint (`/health`) and interactive API documentation (`/docs`)
- Dockerfile, Docker Compose, and tests

## Architecture

```text
Browser (responsive HTML/CSS/JS)
             |
             v
        FastAPI REST API
       /      |       \
      v       v        v
 CSV parser  Pandas   Optional LLM API
      |     transform    (suggestions only)
      v       |
 Data quality + output preview
              |
              v
 SQLAlchemy repository
       /             \
   SQLite local    PostgreSQL Docker/hosted
              |
              v
       Run history + CSV download
```

### Design notes
- Core transformations are deterministic Python code, separate from the AI suggestion endpoint.
- AI suggestions are restricted to a small allowlist of supported operations and are never executed as arbitrary generated code.
- The AI provider is optional. Without `OPENAI_API_KEY`, upload, profiling, transformation, history, and export still work.
- This MVP processes files in memory. For larger workloads, add object storage, streaming ingestion, background jobs, retries, idempotency keys, and a distributed processing engine such as Spark.

## Run locally (Python)

Requires Python 3.11+ (3.12 recommended).

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. API docs: `http://127.0.0.1:8000/docs`. Health: `http://127.0.0.1:8000/health`.

SQLite is used by default and `flowforge.db` is created in the project folder. Add `OPENAI_API_KEY` to your environment to enable AI suggestions. Never commit API keys.

## Run tests

```bash
pytest -q
```

## Run with Docker Compose (PostgreSQL)

Install Docker Desktop, then:

```bash
docker compose up --build
```

Open `http://localhost:8000`. Compose starts the FastAPI application and PostgreSQL. The local compose password is only for development—change it before using any shared environment.

To stop:

```bash
docker compose down
```

To remove local database data too (destructive):

```bash
docker compose down -v
```

## Deploy the MVP

A straightforward path is **Render + managed PostgreSQL** or another host that supports Docker and persistent managed databases.

1. Create a GitHub repository named `flowforge-ai` and push this project.
2. Create a managed PostgreSQL database with your host.
3. Create a web service from the repository and select Docker deployment.
4. Set `DATABASE_URL` to the provider's PostgreSQL URL. If the provider gives `postgres://` or `postgresql://`, adapt it to SQLAlchemy's psycopg driver form if needed: `postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME`.
5. Set `MAX_UPLOAD_MB=15`. Add `OPENAI_API_KEY` and `OPENAI_MODEL` only if you want AI suggestions.
6. Set the health check path to `/health`; the container listens on the `PORT` environment variable.
7. Deploy and verify `/health`, `/docs`, demo data, upload, transform, download, and history.

### Important deployment considerations
- A local SQLite file or container filesystem may be ephemeral on cloud hosts. Use managed PostgreSQL for persistent history.
- Uploads are processed in memory and are not retained as source files by the app.
- For public production use, add authentication, rate limiting, quotas, CSRF protections if cookie auth is added, and stricter operational monitoring. Do not expose a development database password.
- Configure provider-specific CORS only when serving a separate frontend. This project serves its frontend from the same origin.
- A hosted URL is not created by building the files; the live link exists only after a successful deployment.

## Suggested next engineering milestones
1. Add schema contracts and business-rule checks.
2. Move pipeline execution to a background worker with retries and per-run status.
3. Add S3-compatible object storage for raw and curated datasets.
4. Add Parquet output and PySpark processing for larger datasets.
5. Add OpenTelemetry metrics, structured logs, and auth.
6. Add orchestration with Airflow or Prefect.

## AI tools used
- ChatGPT: product design, architecture, code scaffolding, UI copy, test cases, and deployment documentation.
- Optional LLM API: transformation suggestions at runtime; this is disabled unless a valid API key is configured.
"# flowforge-ai" 

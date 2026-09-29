# Scenario Analytics Platform

A production-quality platform that imports operational scenario execution data from CSV, calculates KPIs, stores results in PostgreSQL, and exposes them through a REST API.

---

## Features

- CSV ingestion with full validation and error reporting
- Per-run duration calculation and scenario-level KPI aggregation
- PostgreSQL persistence (scenarios, runs, summaries)
- REST API (FastAPI) with OpenAPI/Swagger docs
- Standalone CLI pipeline runner
- Docker + docker-compose for local development
- C++ resource utilization calculator
- Comprehensive pytest test suite

---

## Architecture

```
CSV File
   |
   v
CSV Reader (validate columns, status, timestamps)
   |
   v
Processor (calculate duration_seconds per run)
   |
   v
KPI Calculator (aggregate: total_runs, success_rate, avg_duration …)
   |
   v
Repository (upsert scenarios → runs → summaries in one transaction)
   |
   v
PostgreSQL
   ^
   |
FastAPI REST API ←── HTTP clients
```

See [docs/architecture.md](docs/architecture.md) for the scalability design.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Data processing | Pandas 2.2 |
| Database | PostgreSQL 16 |
| Testing | pytest + httpx |
| Containerisation | Docker / docker-compose |
| C++ | C++17 (standard library only) |

---

## Project Structure

```
scenario-analytics-platform/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + lifespan
│   │   ├── config.py          # Settings from env vars
│   │   ├── database.py        # SQLAlchemy engine + session
│   │   ├── run_pipeline.py    # Standalone CLI entry point
│   │   ├── models/            # ORM models (Scenario, ScenarioRun, ScenarioSummary)
│   │   ├── schemas/           # Pydantic response schemas
│   │   ├── routes/            # FastAPI routers
│   │   ├── services/          # Pipeline orchestration + DB repository
│   │   └── processing/        # CSV reader + KPI processor
│   ├── requirements.txt
│   └── Dockerfile
├── data/
│   └── scenarios.csv          # 68-row realistic dataset
├── database/
│   ├── schema.sql             # Table definitions
│   ├── indexes.sql            # Performance indexes
│   └── queries.sql            # Reporting queries
├── cpp/
│   ├── main.cpp               # Resource utilization calculator
│   └── README.md
├── docs/
│   └── architecture.md        # Scalability system design
├── tests/
│   ├── test_processing.py     # Processing engine tests
│   └── test_api.py            # API endpoint tests
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Database

### Tables

**scenarios** — one row per unique scenario.
```
scenario_id (PK) | scenario_name | created_at
```

**scenario_runs** — one row per individual execution run (FK → scenarios).
```
run_id (PK) | scenario_id (FK) | status | start_time | end_time | duration_seconds | created_at
```

**scenario_summary** — one row per scenario with aggregated KPIs (FK → scenarios, 1:1).
```
scenario_id (PK/FK) | total_runs | successful_runs | failed_runs | success_rate | total_duration_seconds | average_duration_seconds | last_updated
```

### Relationships
- `scenarios` → `scenario_runs`: one-to-many
- `scenarios` → `scenario_summary`: one-to-one

---

## CSV Format

| Column | Type | Description |
|---|---|---|
| `scenario_id` | integer | Unique scenario identifier |
| `scenario_name` | string | Human-readable scenario name |
| `run_id` | integer | Unique run identifier |
| `status` | string | `SUCCESS` or `FAILED` |
| `start_time` | datetime | Run start (`YYYY-MM-DD HH:MM:SS`) |
| `end_time` | datetime | Run end (`YYYY-MM-DD HH:MM:SS`) |

Invalid records (missing fields, bad status, unparseable timestamps, end before start) are logged and skipped — they do not abort the pipeline.

---

## Processing Pipeline

```
read_csv()          → validates structure, status values, timestamps
calculate_durations() → duration_seconds = (end_time - start_time).total_seconds()
calculate_kpis()    → groups by scenario_id, aggregates:
                        total_runs, successful_runs, failed_runs,
                        success_rate = successful / total × 100,
                        total_duration_seconds, average_duration_seconds
persist_all()       → upserts scenarios → runs → summaries in one DB transaction
```

---

## API Documentation

Interactive Swagger UI available at `/docs` when the server is running.

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v1/scenarios` | List all scenarios |
| GET | `/api/v1/scenarios/{id}` | Scenario detail with summary |
| GET | `/api/v1/scenarios/{id}/summary` | KPI summary only |
| GET | `/api/v1/scenarios/{id}/runs` | All runs for a scenario |

### Example Responses

**GET /api/v1/scenarios/1**
```json
{
  "scenario_id": 1,
  "scenario_name": "Login Test",
  "summary": {
    "total_runs": 8,
    "successful_runs": 6,
    "failed_runs": 2,
    "success_rate": 75.00,
    "total_duration_seconds": 1230.00,
    "average_duration_seconds": 153.75,
    "last_updated": "2026-09-29T09:00:00Z"
  }
}
```

**404 response**
```json
{"detail": "Scenario 999 not found"}
```

---

## C++ Application

Calculates resource utilization and estimated completion time.

```
total_capacity (tasks/hour) = resources × capacity_per_resource
completion_hours             = task_volume ÷ total_capacity
utilization_pct              = (task_volume ÷ total_capacity) × 100
```

See [cpp/README.md](cpp/README.md) for compilation and sample output.

---

## Local Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16 (or Docker)
- Git

### 1. Clone

```bash
git clone <repository-url>
cd scenario-analytics-platform
```

### 2. Environment

```bash
cp .env.example .env
# Edit .env and set DATABASE_URL to your PostgreSQL connection string
```

### 3. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Create database tables

```bash
psql $DATABASE_URL -f database/schema.sql
psql $DATABASE_URL -f database/indexes.sql
```

### 5. Run the processing pipeline

```bash
cd backend
python -m app.run_pipeline --csv ../data/scenarios.csv
```

### 6. Start the API

```bash
cd backend
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`
Swagger UI at `http://localhost:8000/docs`

---

## Running Tests

```bash
# From project root
pip install -r backend/requirements.txt
pytest
```

Tests use SQLite in-memory — no PostgreSQL required for testing.

---

## Running the C++ Program

```bash
cd cpp

# Linux / macOS
g++ -std=c++17 -O2 -o calculator main.cpp
./calculator

# Windows (MinGW)
g++ -std=c++17 -O2 -o calculator.exe main.cpp
calculator.exe
```

---

## Docker

```bash
# Start PostgreSQL + API
docker-compose up --build

# Run pipeline inside the container
docker-compose exec api python -m app.run_pipeline
```

API available at `http://localhost:8000`

---

## Deployment

The application is designed for deployment on **Render** or **Railway**.

### Environment Variables (required)

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `CSV_PATH` | Path to scenarios CSV (default: `data/scenarios.csv`) |
| `LOG_LEVEL` | Logging level (default: `INFO`) |

### Render Deployment Steps

1. Push repository to GitHub.
2. Create a new **Web Service** on Render pointing to the GitHub repo.
3. Set **Root Directory** to `backend`.
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add a **PostgreSQL** database on Render and copy the connection string to `DATABASE_URL`.
7. Run the pipeline once via the Render shell: `python -m app.run_pipeline`

> **Deployment URL**: To be added after deployment is verified.

---

## Design Decisions

| Decision | Rationale |
|---|---|
| SQLAlchemy ORM | Keeps model definitions and queries in Python; avoids raw SQL in application code |
| Pydantic v2 settings | Type-safe environment variable loading with `.env` support |
| `upsert` pattern in repository | Re-running the pipeline on the same CSV is idempotent |
| SQLite for tests | No PostgreSQL required in CI; tests run anywhere |
| Pandas for aggregation | Concise groupby/agg syntax; easy to extend with new KPIs |
| Synchronous pipeline | Sufficient for current scale; async queue design documented for scale-out |
| Invalid records logged, not raised | Pipeline continues processing valid data; bad rows are surfaced in logs |

---

## Evaluation Requirement Mapping

| PDF Requirement | Implementation | Location |
|---|---|---|
| Import scenario data from CSV | `read_csv()` validates and loads CSV | `backend/app/processing/csv_reader.py` |
| Calculate total duration, success rate, failed count, KPIs | `calculate_durations()` + `calculate_kpis()` | `backend/app/processing/processor.py` |
| Error handling and logging | Validation errors logged; invalid rows skipped with reason | `csv_reader.py`, `pipeline.py` |
| Modular code structure | Separate modules: reader, processor, repository, routes, schemas | `backend/app/` |
| PostgreSQL tables: scenarios, scenario_runs, scenario_summary | ORM models + schema.sql | `models/__init__.py`, `database/schema.sql` |
| SQL scripts, indexes, aggregation queries | Three SQL files | `database/` |
| REST APIs: list, detail, summary | Four endpoints + health | `backend/app/routes/scenarios.py` |
| JSON responses + validation | Pydantic schemas + FastAPI | `schemas/__init__.py` |
| C++ resource utilization + completion time | Console app with user input | `cpp/main.cpp` |
| System design (100 → 10,000/day) | One-page design with diagram | `docs/architecture.md` |
| Deployment | Docker + Render instructions | `docker-compose.yml`, README |
| GitHub repository | Source code + README | Root of repository |
| Architecture diagram | ASCII + Mermaid in docs | `docs/architecture.md` |
| README with setup instructions | This file | `README.md` |

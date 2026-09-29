import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routes import scenarios_router

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")

    # Auto-seed the database from CSV if it is empty
    from app.models import Scenario
    from app.services.pipeline import run_pipeline

    db = SessionLocal()
    try:
        count = db.query(Scenario).count()
        if count == 0:
            # Resolve CSV path relative to this file so it works regardless
            # of the working directory (important on Render where rootDir=backend)
            csv_path = settings.csv_path
            if not os.path.isabs(csv_path):
                # Try the configured path first; if it doesn't exist, try relative
                # to the repo root (one level up from backend/)
                if not os.path.exists(csv_path):
                    alt_path = os.path.join(os.path.dirname(__file__), "..", "..", csv_path)
                    alt_path = os.path.normpath(alt_path)
                    if os.path.exists(alt_path):
                        csv_path = alt_path
            logger.info("Database is empty — seeding from CSV: %s", csv_path)
            result = run_pipeline(csv_path, db)
            logger.info("Seed complete: %s", result)
        else:
            logger.info("Database already contains %d scenario(s), skipping seed", count)
    except Exception as exc:
        logger.error("Failed to seed database on startup: %s", exc)
    finally:
        db.close()

    yield


app = FastAPI(
    title="Scenario Analytics Platform",
    description="Processes operational scenario execution data and exposes KPI metrics via REST API.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(scenarios_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

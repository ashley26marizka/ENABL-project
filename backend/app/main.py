import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.routes import scenarios_router

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")
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

import logging
from sqlalchemy.orm import Session
from app.processing import read_csv, calculate_durations, calculate_kpis
from app.services.repository import persist_all

logger = logging.getLogger(__name__)


def run_pipeline(csv_path: str, db: Session) -> dict:
    """Full ETL pipeline: read CSV → validate → calculate KPIs → persist.

    Returns a summary dict with counts of processed/invalid records.
    """
    logger.info("Pipeline started for: %s", csv_path)

    valid_df, invalid_records = read_csv(csv_path)

    if valid_df.empty:
        logger.warning("No valid records to process")
        return {"processed": 0, "invalid": len(invalid_records), "scenarios": 0}

    runs_df = calculate_durations(valid_df)
    kpi_df = calculate_kpis(runs_df)

    persist_all(db, runs_df, kpi_df)

    result = {
        "processed": len(runs_df),
        "invalid": len(invalid_records),
        "scenarios": len(kpi_df),
        "invalid_records": invalid_records,
    }
    logger.info("Pipeline complete: %s", result)
    return result

import logging
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Scenario, ScenarioRun, ScenarioSummary

logger = logging.getLogger(__name__)


def upsert_scenarios(db: Session, kpi_df: pd.DataFrame) -> None:
    """Insert or update scenario records."""
    for _, row in kpi_df.iterrows():
        scenario = db.get(Scenario, int(row["scenario_id"]))
        if not scenario:
            scenario = Scenario(scenario_id=int(row["scenario_id"]), scenario_name=row["scenario_name"])
            db.add(scenario)
    db.flush()


def upsert_runs(db: Session, runs_df: pd.DataFrame) -> None:
    """Insert scenario runs, skipping already-existing run_ids."""
    existing_ids = {r[0] for r in db.query(ScenarioRun.run_id).all()}
    new_runs = []
    for _, row in runs_df.iterrows():
        if int(row["run_id"]) in existing_ids:
            continue
        new_runs.append(ScenarioRun(
            run_id=int(row["run_id"]),
            scenario_id=int(row["scenario_id"]),
            status=row["status"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            duration_seconds=float(row["duration_seconds"]),
        ))
    if new_runs:
        db.bulk_save_objects(new_runs)
    logger.info("Inserted %d new run(s)", len(new_runs))


def upsert_summaries(db: Session, kpi_df: pd.DataFrame) -> None:
    """Insert or update scenario_summary rows."""
    for _, row in kpi_df.iterrows():
        sid = int(row["scenario_id"])
        summary = db.get(ScenarioSummary, sid)
        if summary:
            summary.total_runs = int(row["total_runs"])
            summary.successful_runs = int(row["successful_runs"])
            summary.failed_runs = int(row["failed_runs"])
            summary.success_rate = float(row["success_rate"])
            summary.total_duration_seconds = float(row["total_duration_seconds"])
            summary.average_duration_seconds = float(row["average_duration_seconds"])
        else:
            db.add(ScenarioSummary(
                scenario_id=sid,
                total_runs=int(row["total_runs"]),
                successful_runs=int(row["successful_runs"]),
                failed_runs=int(row["failed_runs"]),
                success_rate=float(row["success_rate"]),
                total_duration_seconds=float(row["total_duration_seconds"]),
                average_duration_seconds=float(row["average_duration_seconds"]),
            ))
    logger.info("Summaries upserted for %d scenario(s)", len(kpi_df))


def persist_all(db: Session, runs_df: pd.DataFrame, kpi_df: pd.DataFrame) -> None:
    """Persist scenarios, runs, and summaries in a single transaction."""
    try:
        upsert_scenarios(db, kpi_df)
        upsert_runs(db, runs_df)
        upsert_summaries(db, kpi_df)
        db.commit()
        logger.info("All data committed successfully")
    except Exception:
        db.rollback()
        logger.exception("Database commit failed — rolled back")
        raise

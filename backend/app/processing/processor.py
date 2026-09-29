import logging
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_durations(df: pd.DataFrame) -> pd.DataFrame:
    """Add duration_seconds column to run-level dataframe."""
    df = df.copy()
    df["duration_seconds"] = (df["end_time"] - df["start_time"]).dt.total_seconds().round(2)
    return df


def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate run-level data into scenario-level KPIs.

    Returns a DataFrame with one row per scenario containing:
    - scenario_id, scenario_name
    - total_runs, successful_runs, failed_runs
    - success_rate (%)
    - total_duration_seconds, average_duration_seconds
    """
    if df.empty:
        logger.warning("No data to aggregate — returning empty KPI frame")
        return pd.DataFrame(columns=[
            "scenario_id", "scenario_name", "total_runs",
            "successful_runs", "failed_runs", "success_rate",
            "total_duration_seconds", "average_duration_seconds",
        ])

    agg = df.groupby(["scenario_id", "scenario_name"]).agg(
        total_runs=("run_id", "count"),
        successful_runs=("status", lambda s: (s == "SUCCESS").sum()),
        failed_runs=("status", lambda s: (s == "FAILED").sum()),
        total_duration_seconds=("duration_seconds", "sum"),
        average_duration_seconds=("duration_seconds", "mean"),
    ).reset_index()

    agg["success_rate"] = (agg["successful_runs"] / agg["total_runs"] * 100).round(2)
    agg["total_duration_seconds"] = agg["total_duration_seconds"].round(2)
    agg["average_duration_seconds"] = agg["average_duration_seconds"].round(2)

    logger.info("KPIs calculated for %d scenario(s)", len(agg))
    return agg

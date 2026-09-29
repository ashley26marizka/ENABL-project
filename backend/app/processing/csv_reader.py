import logging
import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"scenario_id", "scenario_name", "run_id", "status", "start_time", "end_time"}
VALID_STATUSES = {"SUCCESS", "FAILED"}


def read_csv(path: str) -> tuple[pd.DataFrame, list[dict]]:
    """Read and validate CSV. Returns (valid_df, invalid_records)."""
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")
    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    logger.info("CSV loaded: %d rows", len(df))
    return _validate_rows(df)


def _validate_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    invalid = []
    mask_valid = pd.Series([True] * len(df), index=df.index)

    # Check for nulls in required fields
    null_mask = df[list(REQUIRED_COLUMNS)].isnull().any(axis=1)
    for idx in df[null_mask].index:
        invalid.append({"row": int(idx) + 2, "reason": "missing required field", "data": df.loc[idx].to_dict()})
    mask_valid &= ~null_mask

    # Validate status values
    status_mask = ~df["status"].isin(VALID_STATUSES)
    for idx in df[status_mask & mask_valid].index:
        invalid.append({"row": int(idx) + 2, "reason": f"invalid status '{df.loc[idx, 'status']}'", "data": df.loc[idx].to_dict()})
    mask_valid &= ~status_mask

    # Parse timestamps
    for col in ("start_time", "end_time"):
        df[col] = pd.to_datetime(df[col], errors="coerce")
    ts_mask = df["start_time"].isnull() | df["end_time"].isnull()
    for idx in df[ts_mask & mask_valid].index:
        invalid.append({"row": int(idx) + 2, "reason": "unparseable timestamp", "data": df.loc[idx].to_dict()})
    mask_valid &= ~ts_mask

    # end_time must be after start_time
    order_mask = df["end_time"] <= df["start_time"]
    for idx in df[order_mask & mask_valid].index:
        invalid.append({"row": int(idx) + 2, "reason": "end_time not after start_time", "data": df.loc[idx].to_dict()})
    mask_valid &= ~order_mask

    if invalid:
        logger.warning("%d invalid record(s) skipped: %s", len(invalid), invalid)

    valid_df = df[mask_valid].copy()
    logger.info("%d valid rows after validation", len(valid_df))
    return valid_df, invalid

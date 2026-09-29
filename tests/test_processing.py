import io
import pytest
import pandas as pd
from app.processing.csv_reader import read_csv
from app.processing.processor import calculate_durations, calculate_kpis


def _make_csv(content: str) -> str:
    """Write content to a temp file and return path."""
    import tempfile, os
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
    f.write(content)
    f.close()
    return f.name


VALID_CSV = """scenario_id,scenario_name,run_id,status,start_time,end_time
1,Login Test,1001,SUCCESS,2026-09-29 09:00:00,2026-09-29 09:02:30
1,Login Test,1002,FAILED,2026-09-29 10:00:00,2026-09-29 10:05:00
2,Payment Test,2001,SUCCESS,2026-09-29 11:00:00,2026-09-29 11:10:00
"""


def test_read_csv_valid():
    path = _make_csv(VALID_CSV)
    df, invalid = read_csv(path)
    assert len(df) == 3
    assert len(invalid) == 0


def test_read_csv_missing_column():
    csv = "scenario_id,scenario_name,run_id,status,start_time\n1,Test,1,SUCCESS,2026-01-01 00:00:00\n"
    path = _make_csv(csv)
    with pytest.raises(ValueError, match="missing required columns"):
        read_csv(path)


def test_read_csv_invalid_status():
    csv = VALID_CSV + "3,Other,3001,PENDING,2026-09-29 12:00:00,2026-09-29 12:01:00\n"
    path = _make_csv(csv)
    df, invalid = read_csv(path)
    assert len(df) == 3
    assert len(invalid) == 1
    assert "invalid status" in invalid[0]["reason"]


def test_read_csv_missing_field():
    csv = "scenario_id,scenario_name,run_id,status,start_time,end_time\n,Login Test,1001,SUCCESS,2026-09-29 09:00:00,2026-09-29 09:02:30\n"
    path = _make_csv(csv)
    df, invalid = read_csv(path)
    assert len(df) == 0
    assert len(invalid) == 1


def test_read_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_csv("/nonexistent/path.csv")


def test_calculate_durations():
    df = pd.DataFrame({
        "scenario_id": [1],
        "run_id": [1001],
        "status": ["SUCCESS"],
        "start_time": pd.to_datetime(["2026-09-29 09:00:00"]),
        "end_time": pd.to_datetime(["2026-09-29 09:02:30"]),
    })
    result = calculate_durations(df)
    assert result.loc[0, "duration_seconds"] == 150.0


def test_calculate_kpis_success_rate():
    df = pd.DataFrame({
        "scenario_id": [1, 1, 1],
        "scenario_name": ["Login Test"] * 3,
        "run_id": [1001, 1002, 1003],
        "status": ["SUCCESS", "SUCCESS", "FAILED"],
        "duration_seconds": [150.0, 105.0, 260.0],
    })
    kpis = calculate_kpis(df)
    row = kpis[kpis["scenario_id"] == 1].iloc[0]
    assert row["total_runs"] == 3
    assert row["successful_runs"] == 2
    assert row["failed_runs"] == 1
    assert float(row["success_rate"]) == pytest.approx(66.67, abs=0.01)


def test_calculate_kpis_empty():
    df = pd.DataFrame(columns=["scenario_id", "scenario_name", "run_id", "status", "duration_seconds"])
    kpis = calculate_kpis(df)
    assert kpis.empty


def test_calculate_kpis_all_failed():
    df = pd.DataFrame({
        "scenario_id": [2, 2],
        "scenario_name": ["Payment Test"] * 2,
        "run_id": [2001, 2002],
        "status": ["FAILED", "FAILED"],
        "duration_seconds": [490.0, 500.0],
    })
    kpis = calculate_kpis(df)
    row = kpis.iloc[0]
    assert row["success_rate"] == 0.0
    assert row["failed_runs"] == 2


def test_duration_calculation_full_pipeline():
    path = _make_csv(VALID_CSV)
    df, _ = read_csv(path)
    runs = calculate_durations(df)
    # run 1001: 09:00 -> 09:02:30 = 150s
    r = runs[runs["run_id"] == 1001].iloc[0]
    assert r["duration_seconds"] == 150.0
    # run 1002: 10:00 -> 10:05:00 = 300s
    r2 = runs[runs["run_id"] == 1002].iloc[0]
    assert r2["duration_seconds"] == 300.0

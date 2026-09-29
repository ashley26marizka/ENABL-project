import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_scenario.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Scenario, ScenarioRun, ScenarioSummary

TEST_DB_URL = "sqlite:///./test_scenario.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    # Seed test data
    s1 = Scenario(scenario_id=1, scenario_name="Login Test")
    s2 = Scenario(scenario_id=2, scenario_name="Payment Test")
    db.add_all([s1, s2])
    db.flush()
    from datetime import datetime
    db.add_all([
        ScenarioRun(run_id=1001, scenario_id=1, status="SUCCESS",
                    start_time=datetime(2026, 9, 29, 9, 0, 0),
                    end_time=datetime(2026, 9, 29, 9, 2, 30),
                    duration_seconds=150.0),
        ScenarioRun(run_id=1002, scenario_id=1, status="FAILED",
                    start_time=datetime(2026, 9, 29, 10, 0, 0),
                    end_time=datetime(2026, 9, 29, 10, 5, 0),
                    duration_seconds=300.0),
    ])
    db.add(ScenarioSummary(
        scenario_id=1, total_runs=2, successful_runs=1, failed_runs=1,
        success_rate=50.0, total_duration_seconds=450.0, average_duration_seconds=225.0,
    ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_scenarios():
    r = client.get("/api/v1/scenarios")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert data[0]["scenario_id"] == 1


def test_get_scenario():
    r = client.get("/api/v1/scenarios/1")
    assert r.status_code == 200
    data = r.json()
    assert data["scenario_name"] == "Login Test"
    assert data["summary"]["total_runs"] == 2


def test_get_scenario_not_found():
    r = client.get("/api/v1/scenarios/999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_get_summary():
    r = client.get("/api/v1/scenarios/1/summary")
    assert r.status_code == 200
    data = r.json()
    assert float(data["success_rate"]) == 50.0
    assert data["failed_runs"] == 1


def test_get_summary_not_found():
    r = client.get("/api/v1/scenarios/999/summary")
    assert r.status_code == 404


def test_get_runs():
    r = client.get("/api/v1/scenarios/1/runs")
    assert r.status_code == 200
    runs = r.json()
    assert len(runs) == 2
    assert runs[0]["run_id"] == 1001


def test_get_runs_scenario_not_found():
    r = client.get("/api/v1/scenarios/999/runs")
    assert r.status_code == 404


def test_scenario_no_summary():
    r = client.get("/api/v1/scenarios/2/summary")
    assert r.status_code == 404


def test_invalid_scenario_id_type():
    r = client.get("/api/v1/scenarios/abc")
    assert r.status_code == 422

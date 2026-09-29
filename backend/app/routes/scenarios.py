from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Scenario, ScenarioRun
from app.schemas import ScenarioOut, ScenarioDetailOut, ScenarioRunOut, ScenarioSummaryOut

router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])


@router.get("", response_model=list[ScenarioOut])
def list_scenarios(db: Session = Depends(get_db)):
    """List all scenarios."""
    return db.query(Scenario).order_by(Scenario.scenario_id).all()


@router.get("/{scenario_id}", response_model=ScenarioDetailOut)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Fetch scenario details with summary metrics."""
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    return ScenarioDetailOut(
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.scenario_name,
        summary=ScenarioSummaryOut.model_validate(scenario.summary) if scenario.summary else None,
    )


@router.get("/{scenario_id}/summary", response_model=ScenarioSummaryOut)
def get_summary(scenario_id: int, db: Session = Depends(get_db)):
    """Retrieve summary/KPI metrics for a scenario."""
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    if not scenario.summary:
        raise HTTPException(status_code=404, detail=f"No summary available for scenario {scenario_id}")
    return scenario.summary


@router.get("/{scenario_id}/runs", response_model=list[ScenarioRunOut])
def get_runs(scenario_id: int, db: Session = Depends(get_db)):
    """List all runs for a scenario."""
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    return db.query(ScenarioRun).filter(ScenarioRun.scenario_id == scenario_id).order_by(ScenarioRun.run_id).all()

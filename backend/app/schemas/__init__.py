from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class ScenarioRunOut(BaseModel):
    run_id: int
    scenario_id: int
    status: str
    start_time: datetime
    end_time: datetime
    duration_seconds: Decimal

    model_config = {"from_attributes": True}


class ScenarioSummaryOut(BaseModel):
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: Decimal
    total_duration_seconds: Decimal
    average_duration_seconds: Decimal
    last_updated: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScenarioOut(BaseModel):
    scenario_id: int
    scenario_name: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScenarioDetailOut(BaseModel):
    scenario_id: int
    scenario_name: str
    summary: Optional[ScenarioSummaryOut] = None

    model_config = {"from_attributes": True}

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    scenario_id = Column(Integer, primary_key=True)
    scenario_name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    runs = relationship("ScenarioRun", back_populates="scenario", cascade="all, delete-orphan")
    summary = relationship("ScenarioSummary", back_populates="scenario", uselist=False, cascade="all, delete-orphan")


class ScenarioRun(Base):
    __tablename__ = "scenario_runs"

    run_id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.scenario_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=False)
    duration_seconds = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    scenario = relationship("Scenario", back_populates="runs")


class ScenarioSummary(Base):
    __tablename__ = "scenario_summary"

    scenario_id = Column(Integer, ForeignKey("scenarios.scenario_id", ondelete="CASCADE"), primary_key=True)
    total_runs = Column(Integer, nullable=False, default=0)
    successful_runs = Column(Integer, nullable=False, default=0)
    failed_runs = Column(Integer, nullable=False, default=0)
    success_rate = Column(Numeric(5, 2), nullable=False, default=0.00)
    total_duration_seconds = Column(Numeric(12, 2), nullable=False, default=0.00)
    average_duration_seconds = Column(Numeric(10, 2), nullable=False, default=0.00)
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    scenario = relationship("Scenario", back_populates="summary")

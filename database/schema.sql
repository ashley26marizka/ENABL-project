-- Scenario Analytics Platform - Database Schema
-- Creates the three required tables: scenarios, scenario_runs, scenario_summary

CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id   INTEGER PRIMARY KEY,
    scenario_name VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scenario_runs (
    run_id              INTEGER PRIMARY KEY,
    scenario_id         INTEGER NOT NULL REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    status              VARCHAR(20) NOT NULL CHECK (status IN ('SUCCESS', 'FAILED')),
    start_time          TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time            TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_seconds    NUMERIC(10, 2) NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scenario_summary (
    scenario_id             INTEGER PRIMARY KEY REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    total_runs              INTEGER NOT NULL DEFAULT 0,
    successful_runs         INTEGER NOT NULL DEFAULT 0,
    failed_runs             INTEGER NOT NULL DEFAULT 0,
    success_rate            NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    total_duration_seconds  NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    average_duration_seconds NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    last_updated            TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

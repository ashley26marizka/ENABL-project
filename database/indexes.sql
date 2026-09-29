-- Scenario Analytics Platform - Indexes
-- Each index is justified below

-- Speeds up JOIN between scenario_runs and scenarios (FK lookup)
CREATE INDEX IF NOT EXISTS idx_scenario_runs_scenario_id
    ON scenario_runs(scenario_id);

-- Speeds up filtering runs by status (e.g. WHERE status = 'FAILED')
CREATE INDEX IF NOT EXISTS idx_scenario_runs_status
    ON scenario_runs(status);

-- Speeds up time-range queries on runs
CREATE INDEX IF NOT EXISTS idx_scenario_runs_start_time
    ON scenario_runs(start_time);

-- Composite index: scenario + status together for aggregation queries
CREATE INDEX IF NOT EXISTS idx_scenario_runs_scenario_status
    ON scenario_runs(scenario_id, status);

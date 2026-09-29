-- Scenario Analytics Platform - Reporting Queries

-- 1. Success rate by scenario
SELECT
    s.scenario_id,
    s.scenario_name,
    ss.total_runs,
    ss.successful_runs,
    ss.failed_runs,
    ss.success_rate
FROM scenarios s
JOIN scenario_summary ss ON s.scenario_id = ss.scenario_id
ORDER BY ss.success_rate DESC;

-- 2. Average and total duration by scenario
SELECT
    s.scenario_id,
    s.scenario_name,
    ss.total_duration_seconds,
    ss.average_duration_seconds
FROM scenarios s
JOIN scenario_summary ss ON s.scenario_id = ss.scenario_id
ORDER BY ss.average_duration_seconds DESC;

-- 3. Failed runs detail
SELECT
    s.scenario_name,
    r.run_id,
    r.start_time,
    r.end_time,
    r.duration_seconds
FROM scenario_runs r
JOIN scenarios s ON r.scenario_id = s.scenario_id
WHERE r.status = 'FAILED'
ORDER BY r.start_time DESC;

-- 4. Overall platform summary
SELECT
    COUNT(DISTINCT s.scenario_id)          AS total_scenarios,
    SUM(ss.total_runs)                     AS total_runs,
    SUM(ss.successful_runs)                AS total_successful,
    SUM(ss.failed_runs)                    AS total_failed,
    ROUND(AVG(ss.success_rate), 2)         AS avg_success_rate,
    ROUND(AVG(ss.average_duration_seconds), 2) AS avg_duration_seconds
FROM scenarios s
JOIN scenario_summary ss ON s.scenario_id = ss.scenario_id;

-- 5. Scenarios with success rate below 50% (at-risk scenarios)
SELECT
    s.scenario_id,
    s.scenario_name,
    ss.success_rate,
    ss.failed_runs
FROM scenarios s
JOIN scenario_summary ss ON s.scenario_id = ss.scenario_id
WHERE ss.success_rate < 50.0
ORDER BY ss.success_rate ASC;

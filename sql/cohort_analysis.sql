CREATE OR REPLACE VIEW reporting.cohort_analysis AS
SELECT
    cohort_month,
    cohort_size,
    total_transactions,
    total_volume,
    fraud_rate_pct,
    avg_fraud_risk_score,
    high_risk_transactions,
    retention_1m_pct,
    retention_3m_pct,
    retention_6m_pct,
    mature_1m_cohort_size,
    mature_3m_cohort_size,
    mature_6m_cohort_size,
    round(retention_1m_pct / 100.0, 4) AS retention_1m_rate,
    round(retention_3m_pct / 100.0, 4) AS retention_3m_rate,
    round(retention_6m_pct / 100.0, 4) AS retention_6m_rate,
    round(fraud_rate_pct / 100.0, 4) AS fraud_rate_ratio,
    CURRENT_TIMESTAMP AS view_generated_at
FROM marts.cohort_analysis;
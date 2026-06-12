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
    CURRENT_TIMESTAMP AS view_generated_at
FROM marts.cohort_analysis;
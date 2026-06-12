CREATE OR REPLACE VIEW reporting.merchant_risk_profiling AS
SELECT
    merchant_id,
    merchant_name,
    merchant_category,
    city,
    state,
    onboarding_date,
    total_transactions,
    total_volume,
    avg_ticket_size,
    fraud_transactions,
    fraud_rate_pct,
    avg_fraud_risk_score,
    high_risk_transactions,
    unique_customers,
    customer_tx_ratio,
    failed_transactions,
    failure_rate_pct,
    merchant_risk_category,
    CURRENT_TIMESTAMP AS view_generated_at
FROM marts.merchant_risk_profiling;
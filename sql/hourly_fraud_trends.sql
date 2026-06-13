CREATE OR REPLACE VIEW reporting.hourly_fraud_trends AS
SELECT
    tx_hour,
    merchant_category,
    payment_method,
    total_transactions,
    fraud_transactions,
    fraud_rate_pct,
    avg_transaction_amount,
    avg_fraud_risk_score,
    unique_users,
    odd_hour_transactions,
    CURRENT_TIMESTAMP AS view_generated_at
FROM marts.hourly_fraud_trends;
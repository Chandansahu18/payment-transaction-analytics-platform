CREATE OR REPLACE VIEW public.hourly_fraud_trends AS

SELECT
    tx_hour,
    merchant_category,
    payment_method,

    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraud_transactions,

    ROUND(
        SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS fraud_rate_pct,

    ROUND(AVG(amount), 2) AS avg_transaction_amount,
    ROUND(AVG(fraud_risk_score), 2) AS avg_fraud_risk_score,

    COUNT(DISTINCT user_id) AS unique_users,
    SUM(CASE WHEN is_odd_hour THEN 1 ELSE 0 END) AS odd_hour_transactions,

    CURRENT_TIMESTAMP AS view_generated_at

FROM int_transactions_enriched
GROUP BY
    tx_hour,
    merchant_category,
    payment_method
ORDER BY
    fraud_rate_pct DESC,
    tx_hour;

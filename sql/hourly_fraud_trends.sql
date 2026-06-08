WITH base AS (
    SELECT
        *,
        EXTRACT(HOUR FROM transaction_ts) AS tx_hour,
        CASE WHEN EXTRACT(HOUR FROM transaction_ts) BETWEEN 1 AND 5 THEN 1 ELSE 0 END AS is_odd_hour
    FROM fct_transactions
)

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

    COUNT(DISTINCT user_sk) AS unique_users,
    SUM(is_odd_hour) AS odd_hour_transactions,

    CURRENT_TIMESTAMP AS view_generated_at

FROM base
GROUP BY
    tx_hour,
    merchant_category,
    payment_method
ORDER BY
    fraud_rate_pct DESC,
    tx_hour;
SELECT
    m.merchant_id,
    m.merchant_name,
    m.merchant_category,
    m.city,
    m.state,
    m.onboarding_date,

    COUNT(f.transaction_id) AS total_transactions,
    COALESCE(SUM(f.amount), 0) AS total_volume,
    ROUND(AVG(f.amount), 2) AS avg_ticket_size,

    SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) AS fraud_transactions,
    ROUND(
        SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(f.transaction_id), 0),
        2
    ) AS fraud_rate_pct,

    ROUND(AVG(f.fraud_risk_score), 2) AS avg_fraud_risk_score,
    SUM(CASE WHEN f.fraud_risk_level IN ('high', 'critical') THEN 1 ELSE 0 END) AS high_risk_transactions,

    COUNT(DISTINCT f.user_sk) AS unique_customers,
    ROUND(COUNT(DISTINCT f.user_sk) * 1.0 / NULLIF(COUNT(f.transaction_id), 0), 2) AS customer_tx_ratio,

    SUM(CASE WHEN f.status = 'failed' THEN 1 ELSE 0 END) AS failed_transactions,
    ROUND(
        SUM(CASE WHEN f.status = 'failed' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(f.transaction_id), 0),
        2
    ) AS failure_rate_pct,

    CASE
        WHEN SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(f.transaction_id), 0) >= 5
             OR AVG(f.fraud_risk_score) >= 60 THEN 'High Risk'
        WHEN SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(f.transaction_id), 0) >= 2
             OR AVG(f.fraud_risk_score) >= 40 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS merchant_risk_category,

    CURRENT_TIMESTAMP AS view_generated_at

FROM dim_merchants m
LEFT JOIN fct_transactions f
    ON m.merchant_sk = f.merchant_sk
GROUP BY
    m.merchant_id,
    m.merchant_name,
    m.merchant_category,
    m.city,
    m.state,
    m.onboarding_date
ORDER BY fraud_rate_pct DESC NULLS LAST;
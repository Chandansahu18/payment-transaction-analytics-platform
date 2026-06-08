WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', MIN(transaction_ts)) AS cohort_month
    FROM int_transactions_enriched
    GROUP BY user_id
),

user_monthly_activity AS (
    SELECT
        uc.user_id,
        uc.cohort_month,
        DATE_TRUNC('month', t.transaction_ts) AS activity_month,
        (
            EXTRACT(YEAR FROM DATE_TRUNC('month', t.transaction_ts))::int - EXTRACT(YEAR FROM uc.cohort_month)::int
        ) * 12 + (
            EXTRACT(MONTH FROM DATE_TRUNC('month', t.transaction_ts))::int - EXTRACT(MONTH FROM uc.cohort_month)::int
        ) AS month_offset,
        t.transaction_id,
        t.amount,
        t.is_fraud,
        t.fraud_risk_score,
        t.fraud_risk_level
    FROM user_cohorts uc
    LEFT JOIN int_transactions_enriched t ON uc.user_id = t.user_id
)

SELECT
    cohort_month,
    COUNT(DISTINCT user_id) AS cohort_size,

    COUNT(transaction_id) AS total_transactions,
    COALESCE(SUM(amount), 0) AS total_volume,
    ROUND(
        SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(COUNT(transaction_id), 0), 2
    ) AS fraud_rate_pct,
    ROUND(AVG(fraud_risk_score), 2) AS avg_fraud_risk_score,
    SUM(CASE WHEN fraud_risk_level IN ('high', 'critical') THEN 1 ELSE 0 END) AS high_risk_transactions,

    ROUND(
        COUNT(DISTINCT CASE WHEN month_offset = 1 THEN user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT user_id), 0), 1
    ) AS retention_1m_pct,

    ROUND(
        COUNT(DISTINCT CASE WHEN month_offset = 3 THEN user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT user_id), 0), 1
    ) AS retention_3m_pct,

    CURRENT_TIMESTAMP AS view_generated_at

FROM user_monthly_activity
GROUP BY cohort_month
ORDER BY cohort_month;

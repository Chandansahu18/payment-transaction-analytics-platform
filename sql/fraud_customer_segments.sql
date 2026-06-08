WITH rfm_base AS (
    SELECT
        u.user_id,
        MAX(f.transaction_ts) AS last_transaction_ts,
        COUNT(*) AS frequency,
        SUM(f.amount) AS monetary_value,
        SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) AS fraud_count,
        COUNT(DISTINCT f.merchant_category) AS category_diversity
    FROM fct_transactions f
    LEFT JOIN dim_users u ON f.user_sk = u.user_sk
    GROUP BY u.user_id
)

SELECT
    user_id,
    DATE_PART('day', CURRENT_DATE - last_transaction_ts) AS recency_days,
    frequency,
    monetary_value,
    fraud_count,
    category_diversity,

    CASE
        WHEN DATE_PART('day', CURRENT_DATE - last_transaction_ts) <= 7 THEN 'Active'
        WHEN DATE_PART('day', CURRENT_DATE - last_transaction_ts) <= 30 THEN 'Recent'
        WHEN DATE_PART('day', CURRENT_DATE - last_transaction_ts) <= 90 THEN 'Lapsed'
        ELSE 'Inactive'
    END AS recency_segment,

    CASE
        WHEN frequency >= 50 THEN 'High Frequency'
        WHEN frequency >= 10 THEN 'Medium Frequency'
        ELSE 'Low Frequency'
    END AS frequency_segment,

    CASE
        WHEN monetary_value >= 500000 THEN 'High Value'
        WHEN monetary_value >= 50000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS monetary_segment,

    CASE
        WHEN fraud_count >= 3 THEN 'Repeat Fraudster'
        WHEN fraud_count = 1 THEN 'Single Fraud'
        ELSE 'Clean'
    END AS fraud_segment

FROM rfm_base
ORDER BY monetary_value DESC;
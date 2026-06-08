SELECT
    transaction_id,
    user_id,
    transaction_ts,
    tx_hour,
    merchant_category,
    payment_method,
    amount,

    tx_count_1h,
    tx_count_24h,
    tx_same_category_24h,

    fraud_risk_score,
    fraud_risk_level,
    fraud_reason,
    is_fraud,

    CASE
        WHEN tx_count_1h >= 3 THEN 'High Velocity (1 Hour)'
        WHEN tx_count_24h >= 5 THEN 'High Velocity (24 Hours)'
        ELSE 'Normal Velocity'
    END AS velocity_status,

    CASE
        WHEN tx_count_1h >= 3 AND tx_count_24h >= 5 THEN 'Critical Velocity Breach'
        WHEN tx_count_1h >= 3 OR tx_count_24h >= 5 THEN 'Velocity Breach'
        ELSE 'Normal'
    END AS velocity_alert_level,

    CURRENT_TIMESTAMP AS view_generated_at

FROM int_transactions_enriched
WHERE tx_count_1h >= 3
   OR tx_count_24h >= 5
ORDER BY transaction_ts DESC;
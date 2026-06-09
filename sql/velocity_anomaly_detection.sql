CREATE OR REPLACE VIEW public.velocity_anomaly_detection AS

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
        WHEN tx_count_1h >= 5 AND tx_count_24h >= 15 THEN 'High Velocity (Both)'
        WHEN tx_count_1h >= 5 THEN 'High Velocity (1 Hour)'
        WHEN tx_count_24h >= 15 THEN 'High Velocity (24 Hours)'
    END AS velocity_status,

    CASE
        WHEN tx_count_1h >= 5 AND tx_count_24h >= 15 THEN 'Critical Velocity Breach'
        WHEN tx_count_1h >= 5 OR tx_count_24h >= 15 THEN 'Velocity Breach'
    END AS velocity_alert_level,

    CURRENT_TIMESTAMP AS view_generated_at

FROM int_transactions_enriched
WHERE tx_count_1h >= 5
   OR tx_count_24h >= 15
ORDER BY transaction_ts DESC;
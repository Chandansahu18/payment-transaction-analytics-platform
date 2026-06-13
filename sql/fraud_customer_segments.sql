CREATE OR REPLACE VIEW reporting.fraud_customer_segments AS
SELECT
    user_id,
    recency_days,
    frequency,
    monetary_value,
    fraud_count,
    category_diversity,
    recency_segment,
    frequency_segment,
    monetary_segment,
    fraud_segment,
    CURRENT_TIMESTAMP AS view_generated_at
FROM marts.fraud_customer_segments;
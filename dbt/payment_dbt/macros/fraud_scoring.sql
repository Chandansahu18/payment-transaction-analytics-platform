{% macro calculate_fraud_risk_score(is_high_amount, is_risky_merchant, is_odd_hour, velocity_1h, velocity_24h) %}
    (
        (case when {{ is_high_amount }} then 30 else 0 end) +
        (case when {{ is_risky_merchant }} then 25 else 0 end) +
        (case when {{ is_odd_hour }} then 20 else 0 end) +
        (case when {{ velocity_1h }} >= {{ var('fraud_velocity_threshold_1h') }} then 15 else 0 end) +
        (case when {{ velocity_24h }} >= {{ var('fraud_velocity_threshold_24h') }} then 10 else 0 end)
    )
{% endmacro %}
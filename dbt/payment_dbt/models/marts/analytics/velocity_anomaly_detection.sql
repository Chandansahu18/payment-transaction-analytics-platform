{% set v1h = var('fraud_velocity_threshold_1h') %}
{% set v24h = var('fraud_velocity_threshold_24h') %}
{% set entry_1h = var('velocity_entry_min_1h') %}
{% set entry_24h = var('velocity_entry_min_24h') %}
{% set entry_cat = var('velocity_entry_min_category_24h') %}
{% set score_crit = var('velocity_score_critical') %}
{% set score_high = var('velocity_score_high') %}
{% set score_med = var('velocity_score_medium') %}
{% set tx_1h_crit = var('velocity_tx_1h_critical') %}
{% set tx_1h_high = var('velocity_tx_1h_high') %}
{% set tx_1h_med = var('velocity_tx_1h_medium') %}
{% set tx_24h_high = var('velocity_tx_24h_high') %}
{% set tx_24h_crit_combo = var('velocity_tx_24h_critical_combo') %}
{% set tx_24h_med = var('velocity_tx_24h_medium') %}
{% set tx_24h_action = v24h + var('velocity_action_buffer_24h') %}
{% set cat_high = var('velocity_category_high') %}
{% set cat_compound = var('velocity_category_compound') %}
{% set amt_high = var('velocity_high_amount_threshold') %}
{% set fraud_crit = var('velocity_fraud_score_critical') %}

with scored as (
    select
        transaction_id,
        user_id,
        transaction_ts,
        transaction_date,
        tx_hour,
        merchant_category,
        payment_method,
        amount,
        device_type,
        status,
        tx_count_1h,
        tx_count_24h,
        tx_same_category_24h,
        fraud_risk_score,
        fraud_risk_level,
        fraud_reason,
        is_fraud,
        is_high_amount,
        is_odd_hour,
        least(
            100,
            greatest(
                0,
                least(30, greatest(0, (tx_count_1h - {{ var('velocity_score_base_1h') }}) * {{ var('velocity_score_mult_1h') }}))
                + least(25, greatest(0, (tx_count_24h - {{ var('velocity_score_base_24h') }}) * {{ var('velocity_score_mult_24h') }}))
                + least(15, greatest(0, (tx_same_category_24h - {{ var('velocity_score_base_category') }}) * {{ var('velocity_score_mult_category') }}))
                + case when is_high_amount then {{ var('velocity_score_high_amount_pts') }} else 0 end
                + case when is_odd_hour then {{ var('velocity_score_odd_hour_pts') }} else 0 end
                + least({{ var('velocity_score_fraud_cap') }}, fraud_risk_score * {{ var('velocity_score_fraud_mult') }})
            )
        )::numeric(5, 2) as velocity_score
    from {{ ref('int_transactions_enriched') }}
    where tx_count_1h >= {{ entry_1h }}
       or tx_count_24h >= {{ entry_24h }}
       or tx_same_category_24h >= {{ entry_cat }}
)

select
    transaction_id,
    user_id,
    transaction_ts,
    transaction_date,
    tx_hour,
    merchant_category,
    payment_method,
    amount,
    device_type,
    status,
    tx_count_1h,
    tx_count_24h,
    tx_same_category_24h,
    velocity_score,
    case
        when velocity_score >= {{ score_crit }}
            or (tx_count_1h >= {{ tx_1h_crit }} and fraud_risk_score >= {{ fraud_crit }})
            or (tx_count_1h >= {{ tx_1h_high }} and tx_count_24h >= {{ tx_24h_crit_combo }})
            then 'Critical'
        when velocity_score >= {{ score_high }}
            or (tx_count_1h >= {{ tx_1h_high }} and tx_count_24h >= {{ tx_24h_high }})
            or (tx_same_category_24h >= {{ cat_high }} and amount > {{ amt_high }})
            then 'High'
        when velocity_score >= {{ score_med }}
            or tx_count_1h >= {{ tx_1h_med }}
            or tx_count_24h >= {{ tx_24h_med }}
            then 'Medium'
        else 'Low'
    end as velocity_alert_level,
    case
        when velocity_score >= {{ score_crit }}
            or (tx_count_1h >= {{ tx_1h_crit }} and fraud_risk_score >= {{ fraud_crit }})
            then true
        else false
    end as is_critical,
    case
        when velocity_score >= {{ score_high }}
            or tx_count_1h >= {{ tx_1h_med }}
            or tx_count_24h >= {{ tx_24h_action }}
            then true
        else false
    end as action_required,
    case
        when tx_count_1h >= {{ tx_1h_high }} and tx_count_24h >= {{ tx_24h_high }} and tx_same_category_24h >= {{ cat_compound }}
            then 'Compound Velocity Breach'
        when tx_count_1h >= {{ tx_1h_high }}
            then 'High Velocity (1 Hour)'
        when tx_count_24h >= {{ tx_24h_high }}
            then 'High Velocity (24 Hours)'
        when tx_same_category_24h >= {{ cat_high }}
            then 'Category Concentration'
        else 'Elevated Velocity'
    end as velocity_breach_type,
    fraud_risk_score,
    fraud_risk_level,
    fraud_reason,
    is_fraud,
    current_timestamp as dbt_updated_at
from scored
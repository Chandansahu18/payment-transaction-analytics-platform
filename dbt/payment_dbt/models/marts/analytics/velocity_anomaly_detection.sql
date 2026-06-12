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
                least(35, greatest(0, (tx_count_1h - 3) * 7))
                + least(30, greatest(0, (tx_count_24h - 10) * 2))
                + least(15, greatest(0, (tx_same_category_24h - 4) * 3))
                + case when is_high_amount then 10 else 0 end
                + case when is_odd_hour then 5 else 0 end
                + least(15, fraud_risk_score * 0.15)
            )
        )::numeric(5, 2) as velocity_score,
        case
            when tx_count_1h >= 5 and tx_count_24h >= 15 and tx_same_category_24h >= 8
                then 'Compound Velocity (1h + 24h + Category)'
            when tx_count_1h >= 5 and tx_count_24h >= 15
                then 'High Velocity (Both Windows)'
            when tx_count_1h >= 5
                then 'High Velocity (1 Hour)'
            when tx_count_24h >= 15
                then 'High Velocity (24 Hours)'
            when tx_same_category_24h >= 8
                then 'Category Concentration (24h)'
            else 'Elevated Velocity'
        end as velocity_breach_type,
        case
            when tx_count_1h >= 5 and tx_count_24h >= 15
                then 'High Velocity (Both)'
            when tx_count_1h >= 5
                then 'High Velocity (1 Hour)'
            when tx_count_24h >= 15
                then 'High Velocity (24 Hours)'
            else 'Category Spike'
        end as velocity_status
    from {{ ref('int_transactions_enriched') }}
    where tx_count_1h >= 3
       or tx_count_24h >= 10
       or tx_same_category_24h >= 6
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
    velocity_status,
    velocity_breach_type,
    case
        when velocity_score >= 65
            or (tx_count_1h >= 10 and fraud_risk_score >= 50)
            then 'Critical'
        when velocity_score >= 40
            or (tx_count_1h >= 7 and tx_count_24h >= 18)
            then 'High'
        when velocity_score >= 22
            or tx_count_1h >= 5
            or tx_count_24h >= 15
            then 'Medium'
        else 'Normal'
    end as velocity_alert_level,
    case
        when velocity_score >= 65
            or (tx_count_1h >= 10 and fraud_risk_score >= 50)
            then true
        else false
    end as is_critical,
    case
        when velocity_score >= 40
            or tx_count_1h >= 5
            or tx_count_24h >= 15
            then true
        else false
    end as action_required,
    fraud_risk_score,
    fraud_risk_level,
    fraud_reason,
    is_fraud,
    current_timestamp as dbt_updated_at
from scored
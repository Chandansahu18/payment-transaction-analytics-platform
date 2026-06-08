with base as (
    select * from {{ ref('stg_transactions') }}
),

velocity as (
    select
        transaction_id,
        count(*) over (
            partition by user_id
            order by transaction_ts
            range between interval '1 hour' preceding and current row
        ) as tx_count_1h,
        count(*) over (
            partition by user_id
            order by transaction_ts
            range between interval '24 hours' preceding and current row
        ) as tx_count_24h,
        count(*) over (
            partition by user_id, merchant_category
            order by transaction_ts
            range between interval '24 hours' preceding and current row
        ) as tx_same_category_24h
    from base
),

with_flags as (
    select
        b.*,
        v.tx_count_1h,
        v.tx_count_24h,
        v.tx_same_category_24h,
        v.tx_count_1h >= {{ var('fraud_velocity_threshold_1h', 5) }} as is_velocity_spike_1h,
        v.tx_count_24h >= {{ var('fraud_velocity_threshold_24h', 15) }} as is_velocity_spike_24h
    from base b
    left join velocity v on b.transaction_id = v.transaction_id
),

with_score as (
    select
        *,
        (
            (case when is_odd_hour then 20 else 0 end) +
            (case when is_high_amount then 30 else 0 end) +
            (case when is_risky_merchant_category then 25 else 0 end) +
            (case when is_velocity_spike_1h then 15 else 0 end) +
            (case when is_velocity_spike_24h then 10 else 0 end)
        ) as fraud_risk_score
    from with_flags
)

select
    {{ dbt_utils.generate_surrogate_key(['transaction_id']) }} as transaction_sk,
    *,
    case
        when fraud_risk_score >= 70 then 'critical'
        when fraud_risk_score >= 50 then 'high'
        when fraud_risk_score >= 30 then 'medium'
        else 'low'
    end as fraud_risk_level,
    case
        when not (
            is_odd_hour or is_high_amount or is_risky_merchant_category
            or is_velocity_spike_1h or is_velocity_spike_24h
        ) then null
        else concat_ws(' | ',
            case when is_odd_hour then 'Odd Hour' end,
            case when is_high_amount then 'High Amount' end,
            case when is_risky_merchant_category then 'Risky Category' end,
            case when is_velocity_spike_1h then 'Velocity Spike (1h)' end,
            case when is_velocity_spike_24h then 'Velocity Spike (24h)' end
        )
    end as fraud_reason,
    current_timestamp as dbt_updated_at
from with_score

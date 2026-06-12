select
    m.merchant_id,
    m.merchant_name,
    m.merchant_category,
    m.city,
    m.state,
    m.onboarding_date,
    count(f.transaction_id) as total_transactions,
    coalesce(sum(f.amount), 0) as total_volume,
    round(avg(f.amount), 2) as avg_ticket_size,
    sum(case when f.is_fraud then 1 else 0 end) as fraud_transactions,
    round(
        sum(case when f.is_fraud then 1 else 0 end) * 100.0 / nullif(count(f.transaction_id), 0),
        2
    ) as fraud_rate_pct,
    round(avg(f.fraud_risk_score), 2) as avg_fraud_risk_score,
    sum(case when f.fraud_risk_level in ('high', 'critical') then 1 else 0 end) as high_risk_transactions,
    count(distinct f.user_sk) as unique_customers,
    round(count(distinct f.user_sk) * 1.0 / nullif(count(f.transaction_id), 0), 2) as customer_tx_ratio,
    sum(case when f.status = 'failed' then 1 else 0 end) as failed_transactions,
    round(
        sum(case when f.status = 'failed' then 1 else 0 end) * 100.0 / nullif(count(f.transaction_id), 0),
        2
    ) as failure_rate_pct,
    case
        when count(f.transaction_id) = 0 then 'No Activity'
        when sum(case when f.is_fraud then 1 else 0 end) * 100.0 / nullif(count(f.transaction_id), 0) >= 5
            or avg(f.fraud_risk_score) >= 60 then 'High Risk'
        when sum(case when f.is_fraud then 1 else 0 end) * 100.0 / nullif(count(f.transaction_id), 0) >= 2
            or avg(f.fraud_risk_score) >= 40 then 'Medium Risk'
        else 'Low Risk'
    end as merchant_risk_category,
    current_timestamp as dbt_updated_at
from {{ ref('dim_merchants') }} as m
left join {{ ref('fct_transactions') }} as f
    on m.merchant_sk = f.merchant_sk
group by
    m.merchant_id,
    m.merchant_name,
    m.merchant_category,
    m.city,
    m.state,
    m.onboarding_date
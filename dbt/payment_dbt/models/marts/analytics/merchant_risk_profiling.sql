{% set high_fraud_pct = var('merchant_risk_high_fraud_rate_pct') %}
{% set med_fraud_pct = var('merchant_risk_medium_fraud_rate_pct') %}
{% set high_avg_score = var('merchant_risk_high_avg_score') %}
{% set med_avg_score = var('merchant_risk_medium_avg_score') %}
{% set min_transactions = var('merchant_risk_min_transactions') %}

with merchant_metrics as (
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
        round(avg(f.fraud_risk_score), 2) as avg_fraud_risk_score,
        sum(case when f.fraud_risk_level in ('high', 'critical') then 1 else 0 end) as high_risk_transactions,
        count(distinct f.user_sk) as unique_customers,
        sum(case when f.status = 'failed' then 1 else 0 end) as failed_transactions
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
)

select
    merchant_id,
    merchant_name,
    merchant_category,
    city,
    state,
    onboarding_date,
    total_transactions,
    total_volume,
    avg_ticket_size,
    fraud_transactions,
    case
        when total_transactions >= {{ min_transactions }} then round(
            fraud_transactions * 100.0 / nullif(total_transactions, 0),
            2
        )
    end as fraud_rate_pct,
    avg_fraud_risk_score,
    high_risk_transactions,
    unique_customers,
    round(unique_customers * 1.0 / nullif(total_transactions, 0), 2) as customer_tx_ratio,
    failed_transactions,
    round(
        failed_transactions * 100.0 / nullif(total_transactions, 0),
        2
    ) as failure_rate_pct,
    total_transactions >= {{ min_transactions }} as is_rate_reliable,
    case
        when total_transactions = 0 then 'No Activity'
        when total_transactions < {{ min_transactions }} then 'Insufficient Volume'
        when fraud_transactions * 100.0 / nullif(total_transactions, 0) >= {{ high_fraud_pct }}
            or avg_fraud_risk_score >= {{ high_avg_score }} then 'High Risk'
        when fraud_transactions * 100.0 / nullif(total_transactions, 0) >= {{ med_fraud_pct }}
            or avg_fraud_risk_score >= {{ med_avg_score }} then 'Medium Risk'
        else 'Low Risk'
    end as merchant_risk_category,
    current_timestamp as dbt_updated_at
from merchant_metrics
select
    tx_hour,
    merchant_category,
    payment_method,
    count(*) as total_transactions,
    sum(case when is_fraud then 1 else 0 end) as fraud_transactions,
    round(
        sum(case when is_fraud then 1 else 0 end) * 100.0 / nullif(count(*), 0),
        2
    ) as fraud_rate_pct,
    round(avg(amount), 2) as avg_transaction_amount,
    round(avg(fraud_risk_score), 2) as avg_fraud_risk_score,
    count(distinct user_id) as unique_users,
    sum(case when is_odd_hour then 1 else 0 end) as odd_hour_transactions,
    current_timestamp as dbt_updated_at
from {{ ref('int_transactions_enriched') }}
group by
    tx_hour,
    merchant_category,
    payment_method
select
    {{ dbt_utils.generate_surrogate_key(['user_id']) }} as user_sk,
    user_id,
    count(*) as total_transactions,
    round(avg(amount), 2) as avg_transaction_amount,
    sum(amount) as total_spend,
    sum(case when is_fraud then 1 else 0 end) as fraud_count,
    min(transaction_ts) as first_transaction_date,
    max(transaction_ts) as last_transaction_date,
    count(distinct merchant_category) as unique_categories_used,
    count(distinct merchant_id) as unique_merchants_used,
    sum(case when is_odd_hour then 1 else 0 end) as odd_hour_tx_count,
    max(fraud_risk_score) as max_fraud_risk_score,
    current_timestamp as updated_at
from {{ ref('int_transactions_enriched') }}
group by user_id

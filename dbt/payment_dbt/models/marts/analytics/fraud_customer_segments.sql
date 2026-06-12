with rfm_base as (
    select
        u.user_id,
        max(f.transaction_ts) as last_transaction_ts,
        count(*) as frequency,
        sum(f.amount) as monetary_value,
        sum(case when f.is_fraud then 1 else 0 end) as fraud_count,
        count(distinct f.merchant_category) as category_diversity
    from {{ ref('fct_transactions') }} as f
    inner join {{ ref('dim_users') }} as u on f.user_sk = u.user_sk
    group by u.user_id
)

select
    user_id,
    date_part('day', current_date - last_transaction_ts) as recency_days,
    frequency,
    monetary_value,
    fraud_count,
    category_diversity,
    case
        when date_part('day', current_date - last_transaction_ts) <= 7 then 'Active'
        when date_part('day', current_date - last_transaction_ts) <= 30 then 'Recent'
        when date_part('day', current_date - last_transaction_ts) <= 90 then 'Lapsed'
        else 'Inactive'
    end as recency_segment,
    case
        when frequency >= 30 then 'High Frequency'
        when frequency >= 8 then 'Medium Frequency'
        else 'Low Frequency'
    end as frequency_segment,
    case
        when monetary_value >= 200000 then 'High Value'
        when monetary_value >= 25000 then 'Medium Value'
        else 'Low Value'
    end as monetary_segment,
    case
        when fraud_count >= 3 then 'Repeat Fraudster'
        when fraud_count >= 1 then 'Single Fraud'
        else 'Clean'
    end as fraud_segment,
    current_timestamp as dbt_updated_at
from rfm_base
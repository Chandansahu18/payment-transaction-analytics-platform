with fct_transactions as (
    select * from {{ ref('fct_transactions') }}
),

dim_merchants as (
    select * from {{ ref('dim_merchants') }}
),

daily_merchant as (
    select
        fct.merchant_sk,
        dim.merchant_id,
        dim.merchant_name,
        dim.merchant_category,
        dim.is_high_risk_category,
        date_trunc('day', fct.transaction_ts)::date as day,
        count(*) as transaction_count,
        sum(fct.amount) as total_revenue,
        avg(fct.amount) as avg_transaction_value,
        sum(case when fct.is_fraud then 1 else 0 end) as fraud_count,
        sum(case when fct.is_fraud then fct.amount else 0 end) as fraud_loss,
        count(distinct fct.user_sk) as unique_customers
    from fct_transactions fct
    left join dim_merchants dim on fct.merchant_sk = dim.merchant_sk
    group by
        fct.merchant_sk,
        dim.merchant_id,
        dim.merchant_name,
        dim.merchant_category,
        dim.is_high_risk_category,
        date_trunc('day', fct.transaction_ts)::date
)

select * from daily_merchant
order by day, total_revenue desc

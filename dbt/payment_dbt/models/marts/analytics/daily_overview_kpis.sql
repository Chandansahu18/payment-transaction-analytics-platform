with fct_transactions as (
    select * from {{ ref('fct_transactions') }}
),

daily as (
    select
        date_trunc('day', transaction_ts)::date as day,
        count(*) as total_transactions,
        count(distinct user_sk) as active_users,
        count(distinct merchant_sk) as active_merchants,
        sum(amount) as total_revenue,
        avg(amount) as avg_transaction_value,
        sum(case when is_fraud then 1 else 0 end) as fraud_count,
        sum(case when is_fraud then amount else 0 end) as fraud_loss_amount,
        count(*) filter (
            where status = 'failed'
        ) as failed_transactions
    from fct_transactions
    group by date_trunc('day', transaction_ts)::date
)

select * from daily
order by day

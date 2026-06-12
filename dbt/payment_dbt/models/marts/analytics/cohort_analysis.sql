with transactions as (
    select
        u.user_id,
        f.transaction_ts,
        f.amount,
        f.is_fraud,
        f.fraud_risk_score,
        f.fraud_risk_level
    from {{ ref('fct_transactions') }} as f
    inner join {{ ref('dim_users') }} as u on f.user_sk = u.user_sk
),

user_cohorts as (
    select
        user_id,
        date_trunc('month', min(transaction_ts)) as cohort_month
    from transactions
    group by user_id
),

user_monthly_activity as (
    select
        user_id,
        date_trunc('month', transaction_ts) as activity_month,
        count(*) as tx_count,
        sum(amount) as total_amount,
        sum(case when is_fraud then 1 else 0 end) as fraud_tx_count,
        avg(fraud_risk_score) as avg_risk_score,
        sum(case when fraud_risk_level in ('high', 'critical') then 1 else 0 end) as high_risk_transactions
    from transactions
    group by user_id, date_trunc('month', transaction_ts)
),

cohort_activity as (
    select
        uc.user_id,
        uc.cohort_month,
        uma.tx_count,
        uma.total_amount,
        uma.fraud_tx_count,
        uma.avg_risk_score,
        uma.high_risk_transactions,
        (
            extract(year from uma.activity_month)::int - extract(year from uc.cohort_month)::int
        ) * 12
        + (
            extract(month from uma.activity_month)::int - extract(month from uc.cohort_month)::int
        ) as month_offset
    from user_cohorts as uc
    left join user_monthly_activity as uma
        on uc.user_id = uma.user_id
        and uma.activity_month >= uc.cohort_month
)

select
    cohort_month,
    count(distinct user_id) as cohort_size,
    coalesce(sum(tx_count), 0) as total_transactions,
    coalesce(sum(total_amount), 0) as total_volume,
    round(
        sum(fraud_tx_count) * 100.0 / nullif(sum(tx_count), 0),
        2
    ) as fraud_rate_pct,
    round(avg(avg_risk_score), 2) as avg_fraud_risk_score,
    coalesce(sum(high_risk_transactions), 0) as high_risk_transactions,
    round(
        count(distinct case when month_offset = 1 then user_id end) * 100.0
        / nullif(count(distinct user_id), 0),
        1
    ) as retention_1m_pct,
    round(
        count(distinct case when month_offset = 3 then user_id end) * 100.0
        / nullif(count(distinct user_id), 0),
        1
    ) as retention_3m_pct,
    round(
        count(distinct case when month_offset = 6 then user_id end) * 100.0
        / nullif(count(distinct user_id), 0),
        1
    ) as retention_6m_pct,
    current_timestamp as dbt_updated_at
from cohort_activity
group by cohort_month
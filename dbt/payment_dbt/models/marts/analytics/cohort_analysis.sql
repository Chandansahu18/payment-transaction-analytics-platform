with transactions as (
    select
        u.user_id,
        f.transaction_ts,
        f.amount,
        f.is_fraud,
        f.status,
        f.fraud_risk_score,
        f.fraud_risk_level
    from {{ ref('fct_transactions') }} as f
    inner join {{ ref('dim_users') }} as u on f.user_sk = u.user_sk
),

data_anchor as (
    select max(transaction_ts) as anchor_ts
    from transactions
),

user_cohorts as (
    select
        user_id,
        date_trunc('month', min(transaction_ts)) as cohort_month
    from transactions
    where status = 'success'
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
        sum(case when fraud_risk_level in ('high', 'critical') then 1 else 0 end) as high_risk_transactions,
        count(case when status = 'success' then 1 end) as successful_tx_count
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
        uma.successful_tx_count,
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
),

cohort_metrics as (
    select
        ca.cohort_month,
        count(distinct ca.user_id) as cohort_size,
        coalesce(sum(ca.tx_count), 0) as total_transactions,
        coalesce(sum(ca.total_amount), 0) as total_volume,
        coalesce(sum(ca.fraud_tx_count), 0) as fraud_tx_count,
        avg(ca.avg_risk_score) as avg_risk_score,
        coalesce(sum(ca.high_risk_transactions), 0) as high_risk_transactions,
        count(distinct case
            when ca.month_offset = 1 and ca.successful_tx_count > 0
                and ca.cohort_month + interval '1 month' <= date_trunc('month', a.anchor_ts)
            then ca.user_id
        end) as retained_1m_users,
        count(distinct case
            when ca.month_offset = 3 and ca.successful_tx_count > 0
                and ca.cohort_month + interval '3 months' <= date_trunc('month', a.anchor_ts)
            then ca.user_id
        end) as retained_3m_users,
        count(distinct case
            when ca.month_offset = 6 and ca.successful_tx_count > 0
                and ca.cohort_month + interval '6 months' <= date_trunc('month', a.anchor_ts)
            then ca.user_id
        end) as retained_6m_users,
        count(distinct case
            when ca.cohort_month + interval '1 month' <= date_trunc('month', a.anchor_ts)
            then ca.user_id
        end) as mature_1m_cohort_size,
        count(distinct case
            when ca.cohort_month + interval '3 months' <= date_trunc('month', a.anchor_ts)
            then ca.user_id
        end) as mature_3m_cohort_size,
        count(distinct case
            when ca.cohort_month + interval '6 months' <= date_trunc('month', a.anchor_ts)
            then ca.user_id
        end) as mature_6m_cohort_size
    from cohort_activity as ca
    cross join data_anchor as a
    group by ca.cohort_month
)

select
    cohort_month,
    cohort_size,
    total_transactions,
    total_volume,
    round(
        fraud_tx_count * 100.0 / nullif(total_transactions, 0),
        2
    ) as fraud_rate_pct,
    round(avg_risk_score, 2) as avg_fraud_risk_score,
    high_risk_transactions,
    round(
        retained_1m_users * 100.0 / nullif(mature_1m_cohort_size, 0),
        1
    ) as retention_1m_pct,
    round(
        retained_3m_users * 100.0 / nullif(mature_3m_cohort_size, 0),
        1
    ) as retention_3m_pct,
    round(
        retained_6m_users * 100.0 / nullif(mature_6m_cohort_size, 0),
        1
    ) as retention_6m_pct,
    mature_1m_cohort_size,
    mature_3m_cohort_size,
    mature_6m_cohort_size,
    current_timestamp as dbt_updated_at
from cohort_metrics
with enriched as (
    select * from {{ ref('int_transactions_enriched') }}
),

dim_users as (
    select * from {{ ref('dim_users') }}
),

dim_merchants as (
    select * from {{ ref('dim_merchants') }}
),

fact as (
    select
        enriched.transaction_sk,
        enriched.transaction_id,
        dim_users.user_sk,
        dim_merchants.merchant_sk,
        enriched.merchant_category,
        enriched.payment_method,
        enriched.amount,
        enriched.currency,
        enriched.status,
        enriched.is_fraud,
        enriched.fraud_risk_score,
        enriched.fraud_risk_level,
        enriched.fraud_reason,
        enriched.device_type,
        enriched.city,
        enriched.state,
        enriched.transaction_ts,
        enriched.raw_loaded_at
    from enriched
    left join dim_users on enriched.user_id = dim_users.user_id
    left join dim_merchants on enriched.merchant_id = dim_merchants.merchant_id
)

select * from fact

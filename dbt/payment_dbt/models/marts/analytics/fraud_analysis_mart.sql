with fct_transactions as (
    select * from {{ ref('fct_transactions') }}
),

dim_merchants as (
    select * from {{ ref('dim_merchants') }}
),

fraud_analysis as (
    select
        fct.transaction_id,
        fct.amount,
        fct.currency,
        fct.payment_method,
        fct.device_type,
        fct.city,
        fct.state,
        fct.transaction_ts,
        fct.is_fraud,
        fct.fraud_risk_score,
        fct.fraud_risk_level,
        fct.fraud_reason,
        dim.merchant_id,
        dim.merchant_name,
        dim.merchant_category,
        dim.is_high_risk_category
    from fct_transactions fct
    left join dim_merchants dim on fct.merchant_sk = dim.merchant_sk
)

select * from fraud_analysis
order by fraud_risk_score desc, transaction_ts desc

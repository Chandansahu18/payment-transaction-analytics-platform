{{
    config(
        materialized='table',
        schema='marts',
        unique_key='merchant_sk',
        tags=['marts', 'core', 'dimension']
    )
}}

select
    {{ dbt_utils.generate_surrogate_key(['merchant_id']) }} as merchant_sk,
    m.*,
    case
        when m.merchant_category in ('Travel', 'Electronics')
        then true else false
    end as is_high_risk_category,
    (current_date - m.onboarding_date) as days_since_onboarding
from {{ source('raw', 'merchants') }} m

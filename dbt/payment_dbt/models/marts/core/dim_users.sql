{{
    config(
        materialized='table',
        schema='marts',
        unique_key='user_sk',
        tags=['marts', 'core', 'dimension']
    )
}}

select
    {{ dbt_utils.generate_surrogate_key(['user_id']) }} as user_sk,
    u.*,
    (current_date - u.registration_date) as days_since_registration
from {{ source('raw', 'users') }} u

with source as (
    select * from {{ source('raw', 'transactions') }}
),

cleaned as (
    select
        transaction_id,
        user_id,
        merchant_id,
        merchant_category,
        payment_method,
        amount as amount_inr,
        currency,
        status,
        is_fraud,
        device_type,
        city,
        state,
        transaction_ts,
        created_at as raw_loaded_at,

        transaction_ts::date as transaction_date,
        extract(hour from transaction_ts) as tx_hour,
        extract(dow from transaction_ts) as tx_day_of_week,

        case
            when extract(hour from transaction_ts)
                between {{ var('odd_hour_start') }} and {{ var('odd_hour_end') }}
            then true else false
        end as is_odd_hour,

        case
            when amount >= {{ var('high_amount_threshold') }}
            then true else false
        end as is_high_amount,

        case
            when merchant_category in (
                {% for cat in var('risky_merchant_categories') %}
                    '{{ cat }}'{% if not loop.last %},{% endif %}
                {% endfor %}
            ) then true else false
        end as is_risky_merchant_category

    from source
)

select * from cleaned
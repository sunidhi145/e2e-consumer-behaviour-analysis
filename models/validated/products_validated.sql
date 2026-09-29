with source as (

    select * from {{ source('bronze', 'products') }}

)

select
    customer_product_id::bigint as customer_product_id,
    customer_id::int as customer_id,

    upper(trim(product_code)) as product_code,
    trim(product_name) as product_name,
    upper(trim(product_category)) as product_category,
    product_open_date::date as product_open_date,
    try_to_date(nullif(trim(product_close_date), '')) as product_close_date,

    trim(product_status) as product_status,

    sanctioned_limit::number(18,2) as sanctioned_limit,
    current_outstanding::number(18,2) as current_outstanding,
    holding_value::number(18,2) as holding_value,

    upper(trim(sourced_by_channel)) as sourced_by_channel,
    upper(trim(source_system)) as source_system,

    created_at::timestamp_ntz as created_at,
    updated_at::timestamp_ntz as updated_at

from source
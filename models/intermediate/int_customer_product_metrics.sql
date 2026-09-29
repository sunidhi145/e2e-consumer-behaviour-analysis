{{ config(
    alias='int_customer_product_metrics',
    materialized='table'
) }}

with products as (

    select *
    from {{ ref('products_cleansed') }}

)

select
    customer_id,

    -- Count only active products
    count(
        distinct case
            when product_status = 'ACTIVE' then product_code
        end
    ) as num_active_products

from products
group by customer_id
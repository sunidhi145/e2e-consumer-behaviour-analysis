

with products as (

    select *
    from ML_PROJ.RAW_VALIDATED_VALIDATED.products_validated

),

customers as (

    select customer_id
    from ML_PROJ.RAW_VALIDATED_CLEANSED.customers_cleansed

)

select
    p.customer_product_id,
    p.customer_id,
    p.product_code,
    p.product_name,
    p.product_category,
    p.product_open_date,
    p.product_close_date,

    case
        when upper(trim(p.product_status)) in ('ACTIVE', 'A') then 'ACTIVE'
        when upper(trim(p.product_status)) in ('INACTIVE', 'I') then 'INACTIVE'
        else null
    end as product_status,

    p.sanctioned_limit,
    p.current_outstanding,
    p.holding_value,
    p.sourced_by_channel,
    p.source_system,
    p.created_at,
    p.updated_at

from products p
inner join customers c
    on p.customer_id = c.customer_id
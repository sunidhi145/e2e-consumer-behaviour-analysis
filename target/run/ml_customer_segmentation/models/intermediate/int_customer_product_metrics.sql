
  
    

create or replace transient table ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_product_metrics
    
    
    
    
    

    as (

with products as (

    select *
    from ML_PROJ.RAW_VALIDATED_CLEANSED.products_cleansed

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
    )
;


  
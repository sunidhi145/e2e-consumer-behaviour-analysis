
  
    

create or replace transient table ML_PROJ.RAW_VALIDATED_VALIDATED.transactions_validated
    
    
    
    
    

    as (with source as (

    select * from ML_PROJ.BRONZE.transactions

)

select
    transaction_id::bigint as transaction_id,
    account_id::bigint as account_id,
    transaction_date::date as transaction_date,

    upper(trim(transaction_type)) as transaction_type,
    amount::number(18,2) as amount,
    upper(trim(currency_code)) as currency_code,
    upper(trim(channel)) as channel,
    upper(trim(payment_instrument)) as payment_instrument,
    upper(trim(merchant_category)) as merchant_category,
    upper(trim(transaction_status)) as transaction_status,
    fee_amount::number(18,2) as fee_amount,

    created_at::timestamp_ntz as created_at

from source
    )
;


  

  
    

create or replace transient table ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_txn_base
    
    
    
    
    

    as (

with transactions as (

    select *
    from ML_PROJ.RAW_VALIDATED_CLEANSED.transactions_cleansed

),

accounts as (

    select *
    from ML_PROJ.RAW_VALIDATED_CLEANSED.accounts_cleansed

)

select
    t.transaction_id,
    a.customer_id,
    t.account_id,
    t.transaction_date,
    t.transaction_type,
    t.amount,
    t.currency_code,
    t.channel,
    t.payment_instrument,
    t.merchant_category,
    t.transaction_status,
    t.fee_amount,
    t.created_at,

    -- Derived helper fields already created in cleansed layer
    t.amount_inr,
    t.is_high_value,
    t.is_digital,
    t.txn_month,
    t.is_debit,
    t.is_credit

from transactions t
inner join accounts a
    on t.account_id = a.account_id
    )
;


  
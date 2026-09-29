

with transactions as (

    select *
    from ML_PROJ.RAW_VALIDATED_VALIDATED.transactions_validated

),

accounts as (

    select *
    from ML_PROJ.RAW_VALIDATED_CLEANSED.accounts_cleansed

)

select
    t.transaction_id,
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

    
    case t.currency_code
        when 'INR' then t.amount * 1.00
        when 'USD' then t.amount * 87.25
        when 'EUR' then t.amount * 94.60
        when 'GBP' then t.amount * 111.30
        when 'JPY' then t.amount * 0.58
        else null
    end
 as amount_inr,

    case
        when 
    case t.currency_code
        when 'INR' then t.amount * 1.00
        when 'USD' then t.amount * 87.25
        when 'EUR' then t.amount * 94.60
        when 'GBP' then t.amount * 111.30
        when 'JPY' then t.amount * 0.58
        else null
    end
 > 100000 then 1
        else 0
    end as is_high_value,

    case
        when t.channel in ('MOBILE_APP', 'WEB') then 1
        else 0
    end as is_digital,

    cast(date_trunc('month', t.transaction_date) as date) as txn_month,

    case
        when t.transaction_type = 'DEBIT' then 1
        else 0
    end as is_debit,

    case
        when t.transaction_type = 'CREDIT' then 1
        else 0
    end as is_credit

from transactions t
inner join accounts a
    on t.account_id = a.account_id
where t.transaction_status = 'COMPLETED'
{{ config(materialized='table') }}

with transactions as (

    select *
    from {{ ref('transactions_validated') }}

),

accounts as (

    select *
    from {{ ref('accounts_cleansed') }}

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

    {{ to_inr('t.amount', 't.currency_code') }} as amount_inr,

    case
        when {{ to_inr('t.amount', 't.currency_code') }} > 100000 then 1
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
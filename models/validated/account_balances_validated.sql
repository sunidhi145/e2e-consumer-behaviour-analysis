with source as (

    select * from {{ source('bronze', 'account_balances') }}

)

select
    balance_id::bigint as balance_id,
    account_id::bigint as account_id,
    balance_date::date as balance_date,

    opening_balance::number(18,2) as opening_balance,
    closing_balance::number(18,2) as closing_balance,
    min_balance_in_month::number(18,2) as min_balance_in_month,
    max_balance_in_month::number(18,2) as max_balance_in_month,
    average_balance_in_month::number(18,2) as average_balance_in_month,

    upper(trim(overdraft_flag)) as overdraft_flag,
    overdraft_days_in_month::int as overdraft_days_in_month,
    upper(trim(minimum_balance_breach_flag)) as minimum_balance_breach_flag,

    interest_credited::number(18,2) as interest_credited,
    charges_debited::number(18,2) as charges_debited,
    created_at::timestamp_ntz as created_at

from source
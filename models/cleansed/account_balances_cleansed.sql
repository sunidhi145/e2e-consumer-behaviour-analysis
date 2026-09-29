{{ config(materialized='table') }}

with balances as (

    select *
    from {{ ref('account_balances_validated') }}

),

accounts as (

    select *
    from {{ ref('accounts_cleansed') }}

)

select
    b.balance_id,
    b.account_id,
    b.balance_date,
    b.opening_balance,
    b.closing_balance,
    b.min_balance_in_month,
    b.max_balance_in_month,
    b.average_balance_in_month,
    b.overdraft_flag,
    b.overdraft_days_in_month,
    b.minimum_balance_breach_flag,
    b.interest_credited,
    b.charges_debited,
    b.created_at,

    case
        when b.overdraft_flag = 'Y'
            and a.overdraft_limit is not null
            and abs(b.closing_balance) > a.overdraft_limit
        then 'Y'
        else 'N'
    end as overdraft_limit_breach_flag

from balances b
inner join accounts a
    on b.account_id = a.account_id
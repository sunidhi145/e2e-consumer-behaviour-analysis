

with balances as (

    select *
    from ML_PROJ.RAW_VALIDATED_CLEANSED.account_balances_cleansed

),

accounts as (

    select *
    from ML_PROJ.RAW_VALIDATED_CLEANSED.accounts_cleansed

),

customers as (

    -- Restrict to customers still in the final population
    select customer_id
    from ML_PROJ.RAW_VALIDATED_CLEANSED.customers_cleansed

)

select
    a.customer_id,
    b.balance_date,
    b.average_balance_in_month,
    b.closing_balance,
    b.overdraft_flag,

    -- Rank from oldest to newest month
    row_number() over (
        partition by a.customer_id
        order by b.balance_date asc
    ) as balance_month_rank_asc,

    -- Rank from newest to oldest month
    row_number() over (
        partition by a.customer_id
        order by b.balance_date desc
    ) as balance_month_rank_desc,

    -- Total available balance months per customer
    count(*) over (
        partition by a.customer_id
    ) as total_months

from balances b
inner join accounts a
    on b.account_id = a.account_id
inner join customers c
    on a.customer_id = c.customer_id
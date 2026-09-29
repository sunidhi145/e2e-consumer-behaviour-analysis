

with params as (

    -- Fixed reference date for recency metrics
    select to_date('2026-08-01') as reference_date

),

txns as (

    select *
    from ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_txn_base

),

profile as (

    -- Brings in effective_months for frequency denominators
    select *
    from ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_profile

)

select
    t.customer_id,

    -- Average completed transactions per effective month
    count(*) / nullif(p.effective_months, 0)::float as txn_frequency_per_month,

    -- Share of months with at least one completed transaction
    count(distinct t.txn_month) / nullif(p.effective_months, 0)::float as active_months_ratio,

    -- Recency from latest transaction date to reference date
    datediff('day', max(t.transaction_date), prm.reference_date) as days_since_last_txn,

    -- Average transaction size in INR
    avg(abs(t.amount_inr)) as avg_txn_amount,

    -- Coefficient of variation - stddev / mean
    coalesce(
        stddev_samp(abs(t.amount_inr)) / nullif(avg(abs(t.amount_inr)), 0),
        0
    ) as txn_amount_cv,

    -- Share of high-value transactions
    avg(t.is_high_value) as high_value_txn_ratio,

    -- Net balance between credits and debits
    (
        sum(case when t.is_credit = 1 then t.amount_inr else 0 end)
        - sum(case when t.is_debit = 1 then t.amount_inr else 0 end)
    )
    /
    nullif(
        sum(case when t.is_credit = 1 then t.amount_inr else 0 end)
        + sum(case when t.is_debit = 1 then t.amount_inr else 0 end),
        0
    ) as net_cash_flow_ratio,

    -- Share of transactions that are debits
    avg(t.is_debit) as debit_txn_share,

    -- Share of transactions through digital channels
    avg(t.is_digital) as digital_channel_ratio

from txns t
inner join profile p
    on t.customer_id = p.customer_id
cross join params prm
group by
    t.customer_id,
    p.effective_months,
    prm.reference_date
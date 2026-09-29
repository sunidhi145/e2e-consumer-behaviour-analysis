{{ config(
    alias='int_customer_profile',
    materialized='table'
) }}

with params as (

    -- Fixed reference date for all feature calculations
    select to_date('{{ var("reference_date", "2026-08-01") }}') as reference_date

),

customers as (

    select *
    from {{ ref('customers_cleansed') }}

)

select
    c.customer_id,
    c.customer_since_date,
    c.customer_status,
    c.customer_segment_declared,

    -- Raw tenure in months from onboarding to reference date
    datediff('month', c.customer_since_date, p.reference_date) as account_tenure_months,

    -- Used as denominator later; keep minimum 1 to avoid divide-by-zero
    greatest(
        datediff('month', c.customer_since_date, p.reference_date),
        1
    ) as effective_months

from customers c
cross join params p
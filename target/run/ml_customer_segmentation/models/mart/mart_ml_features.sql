
  
    

create or replace transient table ML_PROJ.RAW_VALIDATED_MART.mart_customer_ml_features
    
    
    
    
    

    as (
 
with profile as (
 
    -- Customer spine: one row per valid customer
    select *
    from ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_profile
 
),
 
balance_metrics as (
 
    select *
    from ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_balance_metrics
 
),
 
txn_metrics as (
 
    select *
    from ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_txn_metrics
 
),
 
product_metrics as (
 
    select *
    from ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_product_metrics
 
)
 
select
    p.customer_id,
 
    -- Wealth features
    coalesce(b.avg_monthly_balance, 0) as avg_monthly_balance,
    greatest(0.0, least(3.0, coalesce(b.balance_volatility_ratio, 0))) as balance_volatility_ratio,
    greatest(-1.0, least(3.0, coalesce(b.balance_growth_rate, 0))) as balance_growth_rate,
 
    -- Engagement + transaction behavior
    coalesce(t.txn_frequency_per_month, 0) as txn_frequency_per_month,
    greatest(0.0, least(1.0, coalesce(t.active_months_ratio, 0))) as active_months_ratio,
    coalesce(t.days_since_last_txn, 730) as days_since_last_txn,
    coalesce(t.avg_txn_amount, 0) as avg_txn_amount,
    coalesce(t.txn_amount_cv, 0) as txn_amount_cv,
    greatest(0.0, least(1.0, coalesce(t.high_value_txn_ratio, 0))) as high_value_txn_ratio,
    greatest(-1.0, least(1.0, coalesce(t.net_cash_flow_ratio, 0))) as net_cash_flow_ratio,
    greatest(0.0, least(1.0, coalesce(t.debit_txn_share, 0.5))) as debit_txn_share,
 
    -- Relationship depth
    greatest(coalesce(p.account_tenure_months, 1), 1) as account_tenure_months,
    coalesce(pm.num_active_products, 0) as num_active_products,
 
    -- Balance risk / digital behavior
    coalesce(b.overdraft_month_count, 0) as overdraft_month_count,
    greatest(0.0, least(1.0, coalesce(t.digital_channel_ratio, 0))) as digital_channel_ratio
 
from profile p
left join balance_metrics b
    on p.customer_id = b.customer_id
left join txn_metrics t
    on p.customer_id = t.customer_id
left join product_metrics pm
    on p.customer_id = pm.customer_id
    )
;


  
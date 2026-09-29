
  
    

create or replace transient table ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_balance_metrics
    
    
    
    
    

    as (

with source as (

    select *
    from ML_PROJ.RAW_VALIDATED_INTERMEDIATE.int_customer_monthly_balance

)

select
    customer_id,

    -- Average balance across all available months
    avg(average_balance_in_month) as avg_monthly_balance,

    -- Volatility = stddev / avg balance, capped at 3.0
    -- If denominator is too small, force capped high-volatility value
    case
        when abs(avg(average_balance_in_month)) < 1000 then 3.0
        else least(
            3.0,
            coalesce(
                stddev_samp(average_balance_in_month)
                / nullif(abs(avg(average_balance_in_month)), 0),
                0
            )
        )
    end as balance_volatility_ratio,

    -- Growth compares recent 3 months vs earliest 3 months, then clamps to [-1, 3]
    greatest(
        -1.0,
        least(
            3.0,
            (
                avg(case when balance_month_rank_desc <= 3 then closing_balance end)
                - avg(case when balance_month_rank_asc <= 3 then closing_balance end)
            )
            /
            (
                abs(avg(case when balance_month_rank_asc <= 3 then closing_balance end)) + 1
            )
        )
    ) as balance_growth_rate,

    -- Number of months where account went into overdraft
    sum(case when overdraft_flag = 'Y' then 1 else 0 end) as overdraft_month_count

from source
group by customer_id
    )
;


  
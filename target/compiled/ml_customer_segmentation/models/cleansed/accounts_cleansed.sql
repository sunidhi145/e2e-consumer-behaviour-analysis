

with source as (

    select *
    from ML_PROJ.RAW_VALIDATED_VALIDATED.accounts_validated

)

select
    account_id,
    customer_id,
    account_type,
    product_scheme_code,
    account_open_date,
    account_close_date,
    account_status,
    interest_rate,
    minimum_balance_required,
    overdraft_limit,
    debit_card_issued_flag,
    cheque_book_issued_flag,
    internet_banking_enabled_flag,
    mobile_banking_enabled_flag,
    nominee_registered_flag,
    is_salary_account_flag,
    dormancy_flag,
    source_system,
    created_at,
    updated_at

from source
where account_status = 'ACTIVE'
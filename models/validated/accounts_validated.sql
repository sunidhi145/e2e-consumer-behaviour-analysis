with source as (

    select * from {{ source('bronze', 'accounts') }}

)

select
    account_id::bigint as account_id,
    customer_id::int as customer_id,

    upper(trim(account_type)) as account_type,
    upper(trim(product_scheme_code)) as product_scheme_code,
    account_open_date::date as account_open_date,
    try_to_date(nullif(trim(account_close_date), '')) as account_close_date,
    upper(trim(account_status)) as account_status,

    interest_rate::number(5,2) as interest_rate,
    minimum_balance_required::number(18,2) as minimum_balance_required,
    overdraft_limit::number(18,2) as overdraft_limit,

    upper(trim(debit_card_issued_flag)) as debit_card_issued_flag,
    upper(trim(cheque_book_issued_flag)) as cheque_book_issued_flag,
    upper(trim(internet_banking_enabled_flag)) as internet_banking_enabled_flag,
    upper(trim(mobile_banking_enabled_flag)) as mobile_banking_enabled_flag,
    upper(trim(nominee_registered_flag)) as nominee_registered_flag,
    upper(trim(is_salary_account_flag)) as is_salary_account_flag,
    upper(trim(dormancy_flag)) as dormancy_flag,
    upper(trim(source_system)) as source_system,

    created_at::timestamp_ntz as created_at,
    updated_at::timestamp_ntz as updated_at

from source
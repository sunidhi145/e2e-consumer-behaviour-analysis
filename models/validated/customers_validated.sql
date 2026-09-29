with source as (

    select * from {{ source('bronze', 'customers') }}

)

select
    customer_id::int as customer_id,

    trim(pan_number) as pan_number,
    trim(first_name) as first_name,
    trim(last_name) as last_name,
    trim(date_of_birth) as date_of_birth,
    trim(gender) as gender,
    trim(marital_status) as marital_status,
    trim(email) as email,
    trim(phone_primary) as phone_primary,
    trim(address_line) as address_line,
    trim(city) as city,
    trim(state) as state,
    trim(pincode) as pincode,
    trim(occupation) as occupation,

    upper(trim(annual_income_band)) as annual_income_band,
    upper(trim(education_level)) as education_level,
    customer_since_date::date as customer_since_date,
    upper(trim(home_branch_code)) as home_branch_code,
    nullif(trim(relationship_manager_id), '') as relationship_manager_id,
    upper(trim(customer_segment_declared)) as customer_segment_declared,
    upper(trim(kyc_status)) as kyc_status,
    kyc_last_updated_date::date as kyc_last_updated_date,
    upper(trim(risk_category)) as risk_category,
    upper(trim(customer_status)) as customer_status,
    upper(trim(is_staff_flag)) as is_staff_flag,
    upper(trim(preferred_language)) as preferred_language,
    upper(trim(preferred_contact_mode)) as preferred_contact_mode,
    upper(trim(marketing_consent_flag)) as marketing_consent_flag,
    upper(trim(source_system)) as source_system,

    created_at::timestamp_ntz as created_at,
    updated_at::timestamp_ntz as updated_at

from source
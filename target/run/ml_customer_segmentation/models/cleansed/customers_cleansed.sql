
  
    

create or replace transient table ML_PROJ.RAW_VALIDATED_CLEANSED.customers_cleansed
    
    
    
    
    

    as (

with ranked as (

    select
        *,
        row_number() over (
            partition by customer_id
            order by updated_at desc, created_at desc
        ) as rn
    from ML_PROJ.RAW_VALIDATED_VALIDATED.customers_validated

),

deduped as (

    select *
    from ranked
    where rn = 1

),

cleansed as (

    select
        customer_id,

        coalesce(
            try_to_date(trim(date_of_birth), 'YYYY-MM-DD'),
            try_to_date(trim(date_of_birth), 'DD/MM/YYYY'),
            try_to_date(trim(date_of_birth), 'DD-MM-YYYY'),
            try_to_date(trim(date_of_birth), 'DD-MON-YYYY'),
            try_to_date(trim(date_of_birth), 'YYYY/MM/DD')
        ) as date_of_birth,

        case
            when upper(trim(gender)) in ('M', 'MALE') then 'M'
            when upper(trim(gender)) in ('F', 'FEMALE') then 'F'
            else null
        end as gender,

        case
            when upper(trim(marital_status)) in ('Y', 'YES') then 'Y'
            when upper(trim(marital_status)) in ('N', 'NO') then 'N'
            else null
        end as marital_status,

        initcap(lower(trim(city))) as city,
        initcap(lower(trim(state))) as state,
        trim(pincode) as pincode,
        initcap(lower(trim(occupation))) as occupation,

        annual_income_band,
        education_level,
        customer_since_date,
        home_branch_code,
        relationship_manager_id,
        customer_segment_declared,
        kyc_status,
        kyc_last_updated_date,
        risk_category,
        customer_status,
        is_staff_flag,
        preferred_language,
        preferred_contact_mode,
        marketing_consent_flag,
        source_system,
        created_at,
        updated_at

    from deduped

)

select *
from cleansed
where customer_status = 'ACTIVE'
  and is_staff_flag = 'N'
    )
;


  
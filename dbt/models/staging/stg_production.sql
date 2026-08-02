with source as (
    select *
    from {{ source('energy_data', 'production_by_type') }}
),

cleaned as (
    select
        production_type,
        start_date,
        end_date,
        updated_date,
        value_mw
    from source
    where production_type != 'TOTAL'
)

select * from cleaned
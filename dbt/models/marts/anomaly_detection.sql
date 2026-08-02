with production as (
    select * from {{ ref('stg_production') }}
),

averages as (
    select
        production_type,
        extract(hour from start_date) as hour_of_day,
        avg(value_mw) as avg_value_mw
    from production
    group by production_type, hour_of_day
),

anomalies as (
    select
        p.production_type,
        p.start_date,
        p.value_mw,
        a.avg_value_mw,
        round((p.value_mw - a.avg_value_mw) / nullif(a.avg_value_mw, 0) * 100, 2) as deviation_pct,
        case
            when abs(p.value_mw - a.avg_value_mw) > a.avg_value_mw * 0.5 then true
            else false
        end as is_anomaly
    from production p
    join averages a
        on p.production_type = a.production_type
        and extract(hour from p.start_date) = a.hour_of_day
)

select * from anomalies
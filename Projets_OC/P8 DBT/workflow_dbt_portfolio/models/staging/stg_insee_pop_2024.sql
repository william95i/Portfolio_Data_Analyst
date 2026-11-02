with source_rows as (
    select
        translate(upper(trim(region)), 'ÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ', 'AAAEEEEIIOOUUUC') as region_ascii,
        ensemble_0_19, ensemble_20_39, ensemble_40_59, ensemble_60_74, ensemble_75_plus,
        hommes_0_19, hommes_20_39, hommes_40_59, hommes_60_74, hommes_75_plus,
        femmes_0_19, femmes_20_39, femmes_40_59, femmes_60_74, femmes_75_plus
    from {{ source('oc_raw', 'POPULATION') }}
),
detail_only as (
    select *
    from source_rows
    where region_ascii not in (
        'DOM', 'DROM', 'FRANCE METROPOLITAINE', 'FRANCE METROPOLITAINE ET DOM'
    )
),
unpivoted as (
    select region_ascii, variable, population
    from detail_only
    unpivot (population for variable in (
        ensemble_0_19, ensemble_20_39, ensemble_40_59, ensemble_60_74, ensemble_75_plus,
        hommes_0_19, hommes_20_39, hommes_40_59, hommes_60_74, hommes_75_plus,
        femmes_0_19, femmes_20_39, femmes_40_59, femmes_60_74, femmes_75_plus
    ))
),
normalized as (
    select
        case
            when region_ascii in ('GUADELOUPE', 'GUYANE', 'MARTINIQUE', 'MAYOTTE', 'LA REUNION') then 'DROM'
            when region_ascii = 'CENTRE-VAL-DE-LOIRE' then 'CENTRE-VAL DE LOIRE'
            else region_ascii
        end as region,
        case split_part(variable, '_', 1)
            when 'ENSEMBLE' then 'ALL'
            when 'HOMMES' then 'HOMME'
            when 'FEMMES' then 'FEMME'
        end as gender,
        case split_part(variable, '_', 2)
            when '0' then '0-19'
            when '20' then '20-39'
            when '40' then '40-59'
            when '60' then '60-74'
            when '75' then '75+'
        end as age_group,
        population
    from unpivoted
)
select region, gender, age_group, sum(population) as population
from normalized
where region is not null and gender is not null and age_group is not null
group by region, gender, age_group

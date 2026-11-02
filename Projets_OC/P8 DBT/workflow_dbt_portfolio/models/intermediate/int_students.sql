with normalized as (
    select
        user_id,
        upper(path_category) as path_category,
        translate(upper(trim(region)), 'ÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ', 'AAAEEEEIIOOUUUC') as region_ascii,
        trim(age_group) as age_group_raw,
        case
            when upper(trim(gender)) in ('M', 'H', 'HOMME') then 'HOMME'
            when upper(trim(gender)) in ('F', 'FEMME') then 'FEMME'
            else 'INCONNU'
        end as gender,
        year_path_started
    from {{ ref('stg_students') }}
)
select
    user_id,
    path_category,
    case
        when region_ascii in ('GUADELOUPE', 'GUYANE', 'MARTINIQUE', 'MAYOTTE', 'LA REUNION', 'DOM', 'DROM') then 'DROM'
        when region_ascii = 'CENTRE-VAL-DE-LOIRE' then 'CENTRE-VAL DE LOIRE'
        else region_ascii
    end as region,
    case
        when age_group_raw in ('20-24 ans', '25-29 ans', '30-34 ans', '35-39 ans') then '20-39'
        when age_group_raw in ('40-44 ans', '45-49 ans', '50-54 ans', '55-59 ans') then '40-59'
        when age_group_raw in ('60-64 ans', '65-69 ans', '70-74 ans') then '60-74'
        when age_group_raw like '75%' then '75+'
        -- Regroupement demandé par le projet : approximation, car 75+ est inclus dans la source.
        when age_group_raw = '60 ans ou plus' then '60-74'
        else age_group_raw
    end as age_group,
    age_group_raw,
    (age_group_raw = '60 ans ou plus') as age_group_approximation,
    gender,
    year_path_started
from normalized

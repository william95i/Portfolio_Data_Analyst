-- Grain : année du dernier parcours retenu x région x âge x genre.
-- Le ratio porte sur le segment et utilise la population 2024 comme référence.
with students as (
    select
        year_path_started as year,
        region,
        age_group,
        gender,
        count(*) as students_count,
        sum(case when age_group_approximation then 1 else 0 end) as approximate_age_count
    from {{ ref('int_students') }}
    group by 1, 2, 3, 4
)
select
    s.year,
    s.region,
    s.age_group,
    s.gender,
    s.students_count,
    s.approximate_age_count,
    p.population as population_insee_2024,
    round(10000.0 * s.students_count / nullif(p.population, 0), 4)
        as students_per_10000_inhabitants
from students s
left join {{ ref('stg_insee_pop_2024') }} p
    on s.region = p.region
   and s.age_group = p.age_group
   and p.gender = case when s.gender = 'INCONNU' then 'ALL' else s.gender end

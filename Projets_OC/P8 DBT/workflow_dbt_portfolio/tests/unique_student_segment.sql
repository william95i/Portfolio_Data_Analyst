select year, region, age_group, gender
from {{ ref('fct_students_enriched') }}
group by 1, 2, 3, 4
having count(*) > 1

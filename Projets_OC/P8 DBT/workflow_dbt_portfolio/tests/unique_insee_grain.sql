select region, gender, age_group
from {{ ref('stg_insee_pop_2024') }}
group by 1, 2, 3
having count(*) > 1

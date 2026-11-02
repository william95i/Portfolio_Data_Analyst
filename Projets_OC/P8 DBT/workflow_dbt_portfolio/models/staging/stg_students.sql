-- Une ligne par utilisateur : dernier début de parcours connu.
-- En cas d'égalité sur l'année, le tri lexical rend le choix reproductible,
-- sans prétendre qu'il s'agit du parcours chronologiquement le plus récent.
select
    user_id,
    path_category_name as path_category,
    age_group,
    gender,
    region,
    year_path_started
from {{ source('oc_raw', 'students') }}
where user_id is not null
qualify row_number() over (
    partition by user_id
    order by year_path_started desc nulls last,
             path_category_name, age_group, gender, region
) = 1

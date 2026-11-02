select 1 as discrepancy
where (select sum(population) from {{ ref('stg_insee_pop_2024') }} where gender = 'ALL')
   <> 68373433

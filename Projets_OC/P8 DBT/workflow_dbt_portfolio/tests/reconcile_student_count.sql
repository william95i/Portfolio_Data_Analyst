select 1 as discrepancy
where (select count(*) from {{ ref('int_students') }})
   <> (select coalesce(sum(students_count), 0) from {{ ref('fct_students_enriched') }})

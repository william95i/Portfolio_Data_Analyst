-- Requêtes reprises du fichier de travail « Hospital sql.sql » et adaptées à MySQL 8.
-- Les alias des résultats sont en anglais.
-- La période analysée est 2011–2021 ; 2022 est une année incomplète.
USE hospital_db;

-- 1a. Nombre de visites par année.
SELECT YEAR(`Start`) AS encounter_year, COUNT(*) AS number_of_encounters
FROM encounters
WHERE `Start` < '2022-01-01'
GROUP BY YEAR(`Start`)
ORDER BY encounter_year;

-- 1b. Répartition annuelle des classes de visites.
SELECT YEAR(`Start`) AS encounter_year, EncounterClass,
       COUNT(*) AS number_of_encounters,
       ROUND(100.0 * COUNT(*) /
             SUM(COUNT(*)) OVER (PARTITION BY YEAR(`Start`)), 2) AS percentage_class
FROM encounters
WHERE `Start` < '2022-01-01'
GROUP BY YEAR(`Start`), EncounterClass
ORDER BY encounter_year, percentage_class DESC;

-- 1c. Au plus 24 h ou plus de 24 h (24 h exactement dans la première classe).
WITH encounter_durations AS (
    SELECT CASE WHEN TIMESTAMPDIFF(SECOND, `Start`, Stop) > 86400
                THEN 'Over 24 hours' ELSE '24 hours or less' END AS duration_category
    FROM encounters
    WHERE `Start` < '2022-01-01' AND Stop >= `Start`
)
SELECT duration_category, COUNT(*) AS encounter_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM encounter_durations
GROUP BY duration_category;

-- 2a. Visites dont la couverture versée par l'assureur est nulle.
SELECT SUM(Payer_Coverage = 0) AS number_without_cover,
       ROUND(100.0 * SUM(Payer_Coverage = 0) / COUNT(*), 2) AS percentage_without_cover
FROM encounters
WHERE `Start` < '2022-01-01';

-- 2b. Dix descriptions de procédures les plus fréquentes.
SELECT p.Description, COUNT(*) AS number_of_procedures,
       ROUND(AVG(p.Base_Cost), 2) AS average_cost
FROM procedures AS p
JOIN encounters AS e ON e.Id = p.Encounter
WHERE e.`Start` < '2022-01-01'
GROUP BY p.Description
ORDER BY number_of_procedures DESC, p.Description
LIMIT 10;

-- 2c. Dix codes de procédures au coût de base moyen le plus élevé.
SELECT p.Code, p.Description,
       ROUND(AVG(p.Base_Cost), 2) AS average_base_cost,
       COUNT(*) AS number_of_times_performed
FROM procedures AS p
JOIN encounters AS e ON e.Id = p.Encounter
WHERE e.`Start` < '2022-01-01'
GROUP BY p.Code, p.Description
ORDER BY average_base_cost DESC, p.Code
LIMIT 10;

-- 2d. Coût total moyen d'une visite selon l'assureur, y compris NO_INSURANCE.
SELECT p.NAME AS Healthcare,
       ROUND(AVG(e.Total_Claim_Cost), 2) AS average_total_claim_cost
FROM encounters AS e
JOIN payers AS p ON p.Id = e.Payer
WHERE e.`Start` < '2022-01-01'
GROUP BY p.Id, p.NAME
ORDER BY average_total_claim_cost DESC;

-- 3a. Patients distincts avec un séjour inpatient, par trimestre.
SELECT YEAR(`Start`) AS admission_year, QUARTER(`Start`) AS admission_quarter,
       COUNT(DISTINCT Patient) AS unique_patients
FROM encounters
WHERE EncounterClass = 'inpatient' AND `Start` < '2022-01-01'
GROUP BY YEAR(`Start`), QUARTER(`Start`)
ORDER BY admission_year, admission_quarter;

-- 3b. Patients avec un nouveau séjour inpatient dans les 30 jours
-- suivant la fin du séjour inpatient précédent.
WITH inpatient_encounters AS (
    SELECT Patient, `Start`, Stop,
           LAG(Stop) OVER (PARTITION BY Patient ORDER BY `Start`, Id) AS previous_stop
    FROM encounters
    WHERE EncounterClass = 'inpatient' AND `Start` < '2022-01-01'
)
SELECT COUNT(DISTINCT Patient) AS readmitted_patients
FROM inpatient_encounters
WHERE previous_stop IS NOT NULL
  AND `Start` >= previous_stop
  AND `Start` <= previous_stop + INTERVAL 30 DAY;

-- 3c. Patients ayant le plus de séjours inpatient répétés,
-- sans limite de 30 jours : ce classement ne mesure pas les réadmissions.
WITH inpatient_encounters AS (
    SELECT Patient, `Start`,
           LAG(Stop) OVER (PARTITION BY Patient ORDER BY `Start`, Id) AS previous_stop
    FROM encounters
    WHERE EncounterClass = 'inpatient' AND `Start` < '2022-01-01'
)
SELECT Patient AS patient_id, COUNT(*) AS readmission_count
FROM inpatient_encounters
WHERE previous_stop IS NOT NULL AND `Start` >= previous_stop
GROUP BY Patient
ORDER BY readmission_count DESC, patient_id
LIMIT 10;

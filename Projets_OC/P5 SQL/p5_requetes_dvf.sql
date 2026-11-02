-- P5 — Analyse immobilière DVF, premier semestre 2020
-- Ces douze requêtes reprennent les analyses présentées dans le document Word.
-- Elles utilisent les sept tables du schéma MySQL fourni avec le projet.
-- Les résultats indiqués ci-dessous proviennent de l'exécution du projet ;
-- les exports de ce dossier ne contiennent pas les lignes nécessaires pour
-- les recalculer ici.
-- Requête 1 — Nombre de lignes « appartement » dans la table local.
-- Résultat obtenu : 31 201 lignes d'appartements.
-- Le périmètre temporel est celui de la base décrite ci-dessus.
-- COUNT compte des lignes de locaux, pas des mutations distinctes.
SELECT COUNT(m.ID_Mutation) AS nb_appartements
FROM mutation AS m
JOIN local AS l ON m.ID_Mutation = l.ID_Mutation
WHERE l.TYPE_Local = 'appartement';

-- Requête 2 — Nombre de mutations distinctes avec appartement par région.
-- Résultat obtenu : 13 995 mutations en Île-de-France, première région.
-- Le périmètre temporel est celui de la base décrite ci-dessus.
SELECT
    r.REG_Nom,
    COUNT(DISTINCT m.ID_Mutation) AS nb_ventes
FROM mutation AS m
JOIN local AS l ON l.ID_Mutation = m.ID_Mutation
JOIN commune AS c ON c.COM_Code = m.COM_Code
JOIN departement AS d ON d.DEP_Code = c.DEP_Code
JOIN region AS r ON r.REG_Code = d.REG_Code
WHERE l.TYPE_Local = 'Appartement'
GROUP BY r.REG_Nom
ORDER BY nb_ventes DESC;

-- Requête 3 — Proportion des lignes d'appartements par nombre de pièces.
-- Résultat obtenu : 9 717 lignes de deux pièces, soit environ
-- 31,14 % des lignes d'appartements.
SELECT
    l.NOMBRE_Pieces,
    COUNT(*) AS nb_ventes,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS proportion_piece
FROM mutation AS m
JOIN local AS l ON l.ID_Mutation = m.ID_Mutation
WHERE l.TYPE_Local = 'Appartement'
GROUP BY l.NOMBRE_Pieces
ORDER BY l.NOMBRE_Pieces;

-- Requête 4 — Dix départements au prix moyen par m² le plus élevé.
-- Résultat obtenu : Paris arrive en tête avec 12 129,39 €/m².
-- La formule attribue toute la valeur de la mutation à chaque local
-- associé ; ce choix doit être examiné pour les mutations multilots.
SELECT
    d.DEP_Code,
    d.DEP_Nom,
    ROUND(AVG(m.VALEUR_Fonciere / l.SURFACE_Reele_Batie), 2)
        AS Prix_m2_moyen
FROM mutation AS m
JOIN local AS l ON m.ID_Mutation = l.ID_Mutation
JOIN commune AS c ON m.COM_Code = c.COM_Code
JOIN departement AS d ON c.DEP_Code = d.DEP_Code
WHERE l.SURFACE_Reele_Batie IS NOT NULL
  AND l.SURFACE_Reele_Batie > 0
  AND m.VALEUR_Fonciere > 0
GROUP BY d.DEP_Code, d.DEP_Nom
ORDER BY Prix_m2_moyen DESC
LIMIT 10;

-- Requête 5 — Prix moyen par m² des maisons en Île-de-France.
-- Résultat obtenu : 3 997,71 €/m².
SELECT
    ROUND(AVG(m.VALEUR_Fonciere / l.SURFACE_Reele_Batie), 2)
        AS Prix_m2_moyen_IDF
FROM mutation AS m
JOIN local AS l ON m.ID_Mutation = l.ID_Mutation
JOIN commune AS c ON m.COM_Code = c.COM_Code
JOIN departement AS d ON c.DEP_Code = d.DEP_Code
JOIN region AS r ON d.REG_Code = r.REG_Code
WHERE l.TYPE_Local = 'Maison'
  AND r.REG_Code = '11'
  AND l.SURFACE_Reele_Batie > 0
  AND m.VALEUR_Fonciere > 0;

-- Requête 6 — Dix lignes « appartement » à valeur foncière maximale.
-- Résultat obtenu : première ligne à 9 000 000 €,
-- surface = 10 m², région = Île-de-France.
-- La valeur foncière porte sur la mutation entière : elle ne décrit
-- pas nécessairement le prix de ce seul appartement.
SELECT
    m.VALEUR_Fonciere AS Prix,
    l.SURFACE_Reele_Batie AS Surface_m2,
    r.REG_Nom AS Region
FROM mutation AS m
JOIN local AS l ON m.ID_Mutation = l.ID_Mutation
JOIN commune AS c ON c.COM_Code = m.COM_Code
JOIN departement AS d ON d.DEP_Code = c.DEP_Code
JOIN region AS r ON r.REG_Code = d.REG_Code
WHERE l.TYPE_Local = 'Appartement'
  AND m.VALEUR_Fonciere > 0
  AND l.SURFACE_Reele_Batie > 0
ORDER BY m.VALEUR_Fonciere DESC
LIMIT 10;

-- Requête 7 — Évolution du nombre de mutations entre T1 et T2 2020.
-- Résultat obtenu : T1 = 16 679, T2 = 17 287, soit +3,65 %.
SELECT
    COUNT(CASE WHEN Date_Mutation BETWEEN '2020-01-01' AND '2020-03-31'
        THEN 1 END) AS Ventes_T1,
    COUNT(CASE WHEN Date_Mutation BETWEEN '2020-04-01' AND '2020-06-30'
        THEN 1 END) AS Ventes_T2,
    ROUND((
        COUNT(CASE WHEN Date_Mutation BETWEEN '2020-04-01' AND '2020-06-30'
            THEN 1 END)
        - COUNT(CASE WHEN Date_Mutation BETWEEN '2020-01-01' AND '2020-03-31'
            THEN 1 END)
    ) / COUNT(CASE WHEN Date_Mutation BETWEEN '2020-01-01' AND '2020-03-31'
        THEN 1 END) * 100, 2) AS Taux_Evolution
FROM mutation;

-- Requête 8 — Prix moyen par m² des appartements de plus de 4 pièces,
-- par région.
-- Résultat obtenu : Île-de-France = 8 015,09 €/m².
-- Même réserve sur les mutations comportant plusieurs locaux.
SELECT
    r.REG_Nom AS Region,
    ROUND(AVG(m.VALEUR_Fonciere / l.SURFACE_Reele_Batie), 2)
        AS Prix_m2_moyen
FROM mutation AS m
JOIN local AS l ON m.ID_Mutation = l.ID_Mutation
JOIN commune AS c ON m.COM_Code = c.COM_Code
JOIN departement AS d ON d.DEP_Code = c.DEP_Code
JOIN region AS r ON r.REG_Code = d.REG_Code
WHERE l.TYPE_Local = 'Appartement'
  AND l.NOMBRE_Pieces > 4
  AND l.SURFACE_Reele_Batie > 0
  AND m.VALEUR_Fonciere > 0
GROUP BY r.REG_Nom
ORDER BY Prix_m2_moyen DESC;

-- Requête 9 — Communes ayant au moins 50 mutations au premier trimestre.
-- Résultat obtenu : Paris 17e arrive en tête avec 228 mutations ;
-- Issy-les-Moulineaux en compte 50 et répond au seuil demandé.
SELECT
    c.COM_Nom AS Commune,
    COUNT(m.ID_Mutation) AS nb_ventes
FROM mutation AS m
JOIN commune AS c ON m.COM_Code = c.COM_Code
WHERE m.Date_Mutation BETWEEN '2020-01-01' AND '2020-03-31'
GROUP BY c.COM_Code, c.COM_Nom
HAVING COUNT(m.ID_Mutation) >= 50
ORDER BY nb_ventes DESC;

-- Requête 10 — Écart de prix moyen par m² entre appartements de trois
-- et deux pièces. Résultat : 4 294,86 contre 4 948,43 €/m²,
-- soit -13,21 % pour les trois pièces.
SELECT
    ROUND(AVG(CASE WHEN l.NOMBRE_Pieces = 2
        THEN m.VALEUR_Fonciere / l.SURFACE_Reele_Batie END), 2)
        AS Prix_m2_2p,
    ROUND(AVG(CASE WHEN l.NOMBRE_Pieces = 3
        THEN m.VALEUR_Fonciere / l.SURFACE_Reele_Batie END), 2)
        AS Prix_m2_3p,
    ROUND((
        AVG(CASE WHEN l.NOMBRE_Pieces = 3
            THEN m.VALEUR_Fonciere / l.SURFACE_Reele_Batie END)
        - AVG(CASE WHEN l.NOMBRE_Pieces = 2
            THEN m.VALEUR_Fonciere / l.SURFACE_Reele_Batie END)
    ) / AVG(CASE WHEN l.NOMBRE_Pieces = 2
        THEN m.VALEUR_Fonciere / l.SURFACE_Reele_Batie END) * 100, 2)
        AS Diff_Pourcentage
FROM mutation AS m
JOIN local AS l ON m.ID_Mutation = l.ID_Mutation
WHERE l.TYPE_Local = 'Appartement'
  AND l.SURFACE_Reele_Batie > 0
  AND m.VALEUR_Fonciere > 0;

-- Requête 11 — Trois communes aux valeurs foncières moyennes les plus
-- élevées par département parmi 06, 13, 33, 59 et 69.
-- Résultat obtenu dans MySQL (valeur moyenne arrondie à l'euro) :
-- 13 : Gignac-la-Nerthe 330 000 ; Saint-Savournin 314 425 ; Cassis 313 417.
-- 33 : Lège-Cap-Ferret 549 501 ; Vayres 335 000 ; Arcachon 307 436.
-- 59 : Bersée 433 202 ; Cysoing 408 550 ; Halluin 322 250.
-- 6 : Saint-Jean-Cap-Ferrat 968 750 ; Èze 655 000 ; Mouans-Sartoux 476 898.
-- 69 : Ville-sur-Jarnioux 485 300 ; Lyon 2e 455 217 ; Lyon 6e 426 968.
WITH Classement AS (
    SELECT
        d.DEP_Code,
        c.COM_Nom AS Commune,
        ROUND(AVG(m.VALEUR_Fonciere), 0) AS Valeur_Fonciere_Moyenne,
        ROW_NUMBER() OVER (
            PARTITION BY d.DEP_Code
            ORDER BY AVG(m.VALEUR_Fonciere) DESC
        ) AS rang
    FROM mutation AS m
    JOIN commune AS c ON m.COM_Code = c.COM_Code
    JOIN departement AS d ON c.DEP_Code = d.DEP_Code
    WHERE d.DEP_Code IN ('06', '13', '33', '59', '69')
      AND m.VALEUR_Fonciere > 0
    GROUP BY d.DEP_Code, c.COM_Nom
)
SELECT DEP_Code, Commune, Valeur_Fonciere_Moyenne
FROM Classement
WHERE rang <= 3
ORDER BY DEP_Code, Valeur_Fonciere_Moyenne DESC;

-- Requête 12 — Vingt communes de plus de 10 000 habitants ayant le plus
-- de mutations pour 1 000 habitants. Résultat : Paris 2e arrive en tête
-- avec 127 mutations pour 21 735 habitants, soit 5,84 pour 1 000.

SELECT
    c.COM_Nom AS Commune,
    p.PTOT,
    COUNT(m.ID_Mutation) AS nb_ventes,
    ROUND((COUNT(m.ID_Mutation) / p.PTOT) * 1000, 2)
        AS ventes_pour_1000_hab
FROM mutation AS m
JOIN commune AS c ON m.COM_Code = c.COM_Code
JOIN population AS p ON c.COM_Code = p.COM_Code
WHERE p.PTOT > 10000
GROUP BY c.COM_Nom, p.PTOT
ORDER BY ventes_pour_1000_hab DESC
LIMIT 20;

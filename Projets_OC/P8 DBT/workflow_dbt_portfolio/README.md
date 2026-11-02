# Analyse sociodémographique des apprenants OpenClassrooms

Avec dbt et Snowflake, j'ai préparé des données d'apprenants et les ai comparées à la population INSEE de 2024 par région, âge et genre. La [présentation](../Presentation_P8_portfolio_corrigee.pptx) montre les résultats ; les modèles ci-dessous expliquent leur préparation.

## Données de départ

| Table source dans Snowflake | Contenu | Rôle dans le projet |
| --- | --- | --- |
| `oc_raw.students` | Parcours, région, âge, genre et année de début ; identifiants fictifs | Retenir le dernier parcours de chaque apprenant |
| `oc_raw.POPULATION` | Estimations INSEE 2024 par région, sexe et âge | Servir de population de référence |

## Les modèles dbt

| Modèle | Ce qu'il contient | Niveau de détail |
| --- | --- | --- |
| `stg_students` | Dernier parcours connu | Une ligne par `user_id` |
| `stg_insee_pop_2024` | Population réorganisée par région, genre et âge | Une ligne par catégorie |
| `int_students` | Régions, genres et âges harmonisés | Une ligne par apprenant |
| `fct_students_enriched` | Effectifs et ratio pour 10 000 habitants | Une ligne par année, région, âge et genre |

Les modèles `stg_` et `int_` sont des vues ; `fct_students_enriched` est une table.

L'année correspond au **début du dernier parcours retenu**, pas à toutes les inscriptions de l'année. Pour les genres inconnus, le ratio utilise la population de l'ensemble des sexes. La catégorie « 60–74 ans » inclut aussi des « 60 ans ou plus » ; `age_group_approximation` les signale.

La comparaison rapproche des parcours commencés entre **2022 et 2025** de la population de **2024**. Elle décrit les données disponibles, sans mesurer l'évolution des inscriptions.


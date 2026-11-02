# P9 — Analyse des ventes de la librairie Lapage

J'ai étudié les ventes de la librairie de mars 2021 à février 2023 : chiffre d'affaires, catégories de livres et habitudes d'achat. Les ventes et les clients du jeu de données sont fictifs. Quatre comptes (`c_1609`, `c_4958`, `c_6714`, `c_3454`) sont des clients BtoB.

## Livrables

- [`Atitso_William_2_Notebooks_062026/Analyses_ventes.ipynb`](Atitso_William_2_Notebooks_062026/Analyses_ventes.ipynb) : nettoyage, indicateurs commerciaux et graphiques descriptifs.
- [`Atitso_William_2_Notebooks_062026/Analyses_stats.ipynb`](Atitso_William_2_Notebooks_062026/Analyses_stats.ipynb) : tests statistiques et analyse des associations entre âge, genre et achats.
- [Présentation](Presentation_P9_portfolio_corrigee.pptx) : synthèse des résultats.
- [`Data/`](Data/) : trois fichiers CSV utilisés pour l'analyse.

## Résultats

| Indicateur | Résultat | Périmètre |
| --- | ---: | --- |
| Chiffre d'affaires | 12 027 663,10 € | Toutes les ventes |
| Lignes de vente | 687 534 | Transactions non vides |
| Sessions d'achat | 345 505 | Identifiants de session distincts |
| Clients actifs | 8 600 | Clients ayant au moins une vente |
| Panier moyen | 34,81 € | CA / nombre de sessions |
| Part de CA de la catégorie 2 | 23,1 % | Toutes les ventes |
| Part de CA des dix premières références | 5,17 % | Toutes les ventes |
| Coefficient de Gini du CA par client | 0,398 | Clients BtoC uniquement |
| Corrélation de Spearman : âge / CA par client | −0,1845 | Clients BtoC uniquement |
| Corrélation de Spearman : âge / sessions par client | 0,2120 | Clients BtoC uniquement |

Les indicateurs globaux incluent les comptes BtoB. Les analyses par âge ou par genre, ainsi que la courbe de Lorenz, portent uniquement sur les particuliers.

## Reproduire l'analyse

Avec Python 3.12 et [`requirements.txt`](requirements.txt), ouvrir les notebooks dans leur dossier. Chacun lit les CSV de `Data/` et peut être exécuté seul.

## Limites

L'âge est estimé à partir de l'année de naissance, avec 2022 comme référence. Les achats répétés d'un même client ne sont pas indépendants dans les tests sur les lignes de vente. Les corrélations ne prouvent pas de lien de cause à effet. Deux années ne suffisent pas à établir une saisonnalité durable. Sans données de coûts, de marges ou de stock, les recommandations restent des pistes à tester.


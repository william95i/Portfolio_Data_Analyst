# Analyse immobilière avec SQL

J'ai construit une base MySQL à partir des [données DVF](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres) et de référentiels géographiques pour analyser les ventes immobilières du premier semestre 2020.

Les [douze requêtes SQL](p5_requetes_dvf.sql) et la [présentation](Atitso_William_2_support_presentation_032026.pptx) montrent les analyses. Le [dictionnaire](Atitiso_William_1_dictionnaire_de_donnees_032026.xlsx) et le [schéma SQL](schema.sql) décrivent les sept tables.

## Ce que montrent les requêtes

| Requête | Résultat obtenu |
|---|---|
| 1 | **31 201** lignes d'appartements dans la base. |
| 2 | **13 995** mutations distinctes avec appartement en Île-de-France, devant les autres régions. |
| 3 | Les deux-pièces représentent **9 717 lignes**, soit **31,14 %** des appartements comptés. |
| 4 | Paris arrive en tête du classement des départements avec **12 129,39 €/m²** en moyenne, puis les Hauts-de-Seine (**7 415,28 €/m²**). |
| 5 | Le prix moyen calculé pour les maisons en Île-de-France est de **3 997,71 €/m²**. |
| 6 | La première ligne du classement des appartements affiche **9 000 000 €** pour **10 m²**, en Île-de-France. Cette valeur doit être lue avec prudence : le prix porte sur la mutation entière. |
| 7 | Les mutations passent de **16 679** au premier trimestre à **17 287** au second, soit **+3,65 %**. |
| 8 | Pour les appartements de plus de quatre pièces, l'Île-de-France présente le prix moyen le plus élevé : **8 015,09 €/m²**. |
| 9 | **Paris 17e** arrive en tête des communes ayant au moins 50 mutations au premier trimestre, avec **228**. **Issy-les-Moulineaux**, avec **50**, entre aussi dans la sélection. |
| 10 | Le prix moyen est de **4 948,43 €/m²** pour les deux-pièces et de **4 294,86 €/m²** pour les trois-pièces, soit un écart de **−13,21 %** pour ces derniers. |
| 11 | Les trois communes en tête de chaque département figurent dans le tableau ci-dessous. |
| 12 | Parmi les communes de plus de 10 000 habitants, **Paris 2e** arrive en tête avec **127 mutations** pour **21 735 habitants**, soit **5,84 mutations pour 1 000 habitants**. |

### Requête 11 — Trois communes par département

La requête classe les communes selon leur **valeur foncière moyenne par mutation**, arrondie à l'euro.

| Département | Rang | Commune | Valeur foncière moyenne |
|---|---:|---|---:|
| Bouches-du-Rhône (13) | 1 | Gignac-la-Nerthe | 330 000 € |
| Bouches-du-Rhône (13) | 2 | Saint-Savournin | 314 425 € |
| Bouches-du-Rhône (13) | 3 | Cassis | 313 417 € |
| Gironde (33) | 1 | Lège-Cap-Ferret | 549 501 € |
| Gironde (33) | 2 | Vayres | 335 000 € |
| Gironde (33) | 3 | Arcachon | 307 436 € |
| Nord (59) | 1 | Bersée | 433 202 € |
| Nord (59) | 2 | Cysoing | 408 550 € |
| Nord (59) | 3 | Halluin | 322 250 € |
| Alpes-Maritimes (6) | 1 | Saint-Jean-Cap-Ferrat | 968 750 € |
| Alpes-Maritimes (6) | 2 | Èze | 655 000 € |
| Alpes-Maritimes (6) | 3 | Mouans-Sartoux | 476 898 € |
| Rhône (69) | 1 | Ville-sur-Jarnioux | 485 300 € |
| Rhône (69) | 2 | Lyon 2e | 455 217 € |
| Rhône (69) | 3 | Lyon 6e | 426 968 € |

## Lire les chiffres correctement

Les requêtes 1 et 3 comptent des **lignes de locaux** ; la requête 2 compte des **mutations distinctes**. Un prix au mètre carré calculé avec la valeur d'une mutation entière peut être trompeur si elle comprend plusieurs locaux, notamment pour la ligne à 9 millions d'euros et 10 m².

Toutes les ventes de la base se situent entre janvier et juin 2020. La table de population ne porte que sur une année.


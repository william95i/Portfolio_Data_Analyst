# Étude de marché pour l'exportation de volaille

Quels pays étudier en priorité pour exporter de la volaille ? J'ai rapproché des données alimentaires, démographiques, économiques et institutionnelles de **2017**, regroupé les pays aux profils proches, puis construit un score pour comparer les marchés. Ce classement sert à orienter la recherche commerciale.

## Données et démarche

Les fichiers de [`Données p11`](Donn%C3%A9es%20p11/) viennent de deux sources : la [FAO](https://www.fao.org/faostat/en/) et la [Banque mondiale](https://datacatalog.worldbank.org/). Ils couvrent la volaille, la population, le PIB par habitant et la gouvernance.

Le premier [notebook](Notebooks/Atitso_William_1_preparation_nettoyage_analyse_exploratoire_092026.ipynb) prépare les données et produit `df_final_cleaned.csv`.

Le second [notebook](Notebooks/Atitso_William_2_clustering_visualisations_092026.ipynb) traite les valeurs extrêmes, réalise une ACP et compare la classification hiérarchique à K-means. J'ai retenu **quatre groupes** pour mieux lire les profils des pays. Le score d'attractivité pondère les importations (30 %), la dépendance aux importations (25 %), le PIB par habitant (15 %), la population (10 %), la stabilité politique (10 %) et la qualité de la réglementation (10 %). Ces poids sont des choix d'analyse.

## Ce que montrent les calculs

- Le fichier nettoyé contient **164 pays**, sans doublon ni valeur manquante. Le Laos, l'Ouzbékistan et la Corée du Nord ont été écartés faute de données suffisantes.
- Les trois premières composantes de l'ACP expliquent **74,86 %** de la variance. Les quatre groupes K-means comptent respectivement **48, 67, 39 et 10 pays**.
- Le score de silhouette vaut **0,4948** pour deux groupes et **0,4868** pour quatre ; le choix de quatre groupes facilite l'interprétation.
- Le classement place **Hong Kong (0,736)** devant **le Japon (0,643)**, **le Luxembourg (0,583)**, **l'Allemagne (0,574)** et **les Émirats arabes unis (0,556)**. La [présentation](Atitso_William_3_presentation_092026.pptx) propose une lecture qualitative.

Hong Kong est une plateforme de réexportation : sa première place ne suffit donc pas à en faire une cible. Le score ignore aussi les droits de douane, les règles sanitaires, la logistique et la concurrence. La dépendance aux importations est approchée par `importations / (importations + production)`, une formule simplificatrice.

## Reproduire l'analyse

Avec Python 3.12 et [`requirements.txt`](requirements.txt), exécuter le notebook de préparation, puis celui de clustering. Les chemins sont relatifs au projet ; `df_final.csv` et `df_final_cleaned.csv` peuvent être régénérés.

Les résultats décrivent **2017**. Certaines valeurs manquantes de production, d'importation ou d'exportation sont remplacées par zéro, ce qui peut modifier le profil d'un pays.

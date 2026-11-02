# Étude sur l’alimentation dans le monde

J'ai étudié la sous-nutrition, la disponibilité alimentaire et l'aide alimentaire à partir des données du projet. Le notebook calcule les indicateurs repris dans la présentation.

## Données et notebook

Le [notebook](Atitso_William_1_notebook_122025.ipynb) utilise les quatre fichiers de `Donnees p4` : population, sous-nutrition, disponibilité et aide alimentaires. `ISO1.csv` et `mapping_countries_FR_EN.csv` servent aux analyses complémentaires sur l'Afrique. Les dépendances sont dans [`requirements.txt`](requirements.txt).

## Ce que montrent les données

- Le calcul pour 2017 aboutit à environ **537,7 millions** de personnes sous-nourries, soit **7,1 %** de la population prise en compte.
- Dans la comparaison entre alimentation humaine, alimentation animale et pertes, les parts sont respectivement de **73,5 %**, **19,7 %** et **6,8 %**. Les autres utilisations ne font pas partie du dénominateur de ce graphique.
- Pour les principales céréales étudiées, la répartition entre les deux usages alimentaires est de **54,1 % pour les humains** et **45,9 % pour les animaux**. La production totale de ces céréales n’est pas le dénominateur de ces deux pourcentages.
- L'aide alimentaire est mesurée en **quantités**, converties en kilogrammes, et non en dollars. Pour le Soudan, le Soudan du Sud et l'Éthiopie, aucune valeur n'est renseignée en 2016 parmi les cinq pays étudiés.

La disponibilité calorique est théorique : elle ne mesure pas ce que chacun consomme. La comparaison Afrique/monde utilise des moyennes simples par pays. L'aide couvre 2013-2016, la disponibilité 2017 et la sous-nutrition 2016-2018, centrée sur 2017.


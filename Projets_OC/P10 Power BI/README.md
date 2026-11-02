# P10 — Accès à l’eau et stabilité politique

Ce tableau de bord Power BI compare l'accès à l'eau potable, la mortalité liée aux services WASH, la stabilité politique et la population. On peut explorer les résultats à l'échelle mondiale, régionale ou nationale.

## Livrables

- `Atitso_William_2_Dashboard_092026.pbix` : tableau de bord avec trois vues et données intégrées.
- `Atitso_William_1_presentation_092026.pptx` : démarche et résultats.
- `DAN-P10-donnees/` : CSV sources et dictionnaire de données.

## Données et méthode

Le modèle rapproche sept CSV après harmonisation des noms de pays. `Population.csv` vient de la Banque mondiale ; la référence précise du jeu n'est pas conservée dans le CSV. Ses valeurs sont en milliers : Power Query les convertit en personnes et retient les années 2000 à 2018.

Le score DWFA combine l'accès aux services d'eau de base (40 %), la stabilité politique (30 %) et la mortalité WASH inversée (30 %). Ces poids sont propres à cette analyse.

## Ouvrir et actualiser le dashboard

Le `.pbix` s'ouvre avec ses données intégrées. Pour l'actualiser sur un autre ordinateur, ouvrir **Transformer les données** dans Power BI Desktop et remplacer les chemins `File.Contents(...)` par ceux des CSV de `DAN-P10-donnees`. Vérifier les requêtes `FaitsDWFA`, `WASH`, `Stabilité Politique`, `Region`, `mapping countries`, `DimPays` et `Population`. `Region` lit deux fichiers : `RegionCountry.csv` et `ISO1.csv`.

`Population.csv` utilise le séparateur `;` ; les autres CSV utilisent la virgule. Appliquer les changements, puis actualiser le modèle.

## Périmètre des résultats

L'accès à l'eau est renseigné jusqu'en 2017, la population et la stabilité politique jusqu'en 2018, et la mortalité WASH pour 2016 seulement. Le tableau de bord compare ces indicateurs sans établir de lien de cause à effet.

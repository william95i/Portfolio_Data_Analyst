# P13 — Améliorer Bottleneck et construire mon portfolio

Ce projet comporte deux parties : améliorer mon analyse e-commerce du P6, puis présenter mes réalisations et ma veille dans un [portfolio de Data Analyst](../../README.md).

## Partie 1 — Bottleneck

J'ai repris le rapprochement entre l'ERP, le site Web et la table de liaison. Le notebook et le pipeline contrôlent les fichiers, suivent les produits dans les jointures et signalent les valeurs à examiner. Les alertes ne corrigent pas les données automatiquement.

J'ai comparé trois façons de traiter les identifiants. Le profil **Exports reproduits** retrouve les **714 produits** de `df_final` et les **713** de `df_clean` après le filtre historique sur les marges positives. Ce résultat reproduit les exports du P6 sans valider à lui seul les règles métier. L'IA m'a aidé à explorer les options ; j'ai vérifié ses propositions sur les fichiers et les résultats.

## Partie 2 — Portfolio et veille

La [page d'accueil](../../README.md) présente mes projets. La [page de veille](../../VEILLE.md) explique les sources consultées et les choix faits pour Bottleneck ; la documentation ci-dessous donne le détail des essais.

## Livrables

- [Notebook P6 amélioré](notebooks/P6_Bottleneck_ameliore_finalise.ipynb) et [pipeline Python](src/pipeline.py).
- [Comparaison des options](comparaison_options.md) : essais, choix et limites.
- [Documentation du P13](output/pdf/Documentation_P13_Missions_1_2.pdf) : besoin, veille, IA et résultats.
- [Rapport et alertes du POC](outputs/poc_20260924/export_observed/).
- [Suivi du projet](suivi_et_documentation.md) : traitement d'un nouveau lot et revue des alertes.
- [Script de veille pandas](src/veille_pandas.py) : lancé chaque lundi à 12 h sur mon PC par Windows. Il repère les versions stables et garde une [trace datée](output/veille_pandas_state.json). Après lecture des notes, `python src/veille_pandas.py --mark-reviewed X.Y.Z` marque la version comme examinée ; aucune mise à jour n'est faite automatiquement.

Les classeurs `erp.xlsx`, `liaison.xlsx`, `web.xlsx`, `df_final.xlsx` et `df_clean.xlsx` ne sont pas dans ce dossier. Les rapports enregistrés montrent les résultats du lot étudié ; le [guide de suivi](suivi_et_documentation.md) explique comment relancer le pipeline avec les fichiers d'entrée.

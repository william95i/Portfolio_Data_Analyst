# Suivi et utilisation du P13

*État au 2 novembre 2026.*

## Avancement

- **Réalisé sur le lot fourni :** [notebook P6 amélioré](notebooks/P6_Bottleneck_ameliore_finalise.ipynb), [contrôles et rapports](outputs/poc_20260924/), [comparaison des méthodes](comparaison_options.md).
- **Portfolio :** [page d'accueil](../../README.md) et [page de veille](../../VEILLE.md) créées.
- **Veille :** le script Python est programmé chaque lundi à 12 h dans Windows ; son lancement de test par le Planificateur a réussi le 26 octobre. Codex lit sa trace à 12 h 10. La version 3.1.0 a été examinée manuellement ; le contrôle du 2 novembre a réussi sans nouvelle version signalée.
- **Remise finale :** relecture des livrables en cours.

## Traiter un nouveau lot

1. Conserver les originaux et placer des copies de `erp.xlsx`, `liaison.xlsx` et `web.xlsx` dans un même dossier.
2. Ouvrir le P13 dans VS Code et lancer le [pipeline](src/pipeline.py) en indiquant ce dossier d'entrée et un **nouveau dossier de résultats daté**.
3. Lire `rapport_qualite.json` pour les contrôles et `anomalies_poc.csv` pour les cas à examiner. Comparer les résultats au lot précédent.
4. Faire valider les décisions par le référent métier. Pour chaque cas, noter le lot, le produit, l'alerte, la décision, sa justification et la personne qui l'a validée. Si une règle change, mettre aussi à jour le code et la documentation.

Une alerte signale un point à vérifier : elle ne corrige pas la donnée. Le pipeline doit être **relancé manuellement** pour chaque lot et n'envoie aucun message automatique. Pour présenter les résultats à l'équipe, partir d'une alerte concrète et montrer comment elle conduit à une décision métier.

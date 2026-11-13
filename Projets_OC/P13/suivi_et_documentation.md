# Suivi et utilisation du P13

*État au 9 novembre 2026.*

## Avancement

- **Réalisé sur le lot fourni :** [notebook P6 amélioré](notebooks/P6_Bottleneck_ameliore_finalise.ipynb), [contrôles et rapports](outputs/poc_20260924/), [comparaison des méthodes](comparaison_options.md).
- **Portfolio :** [page d'accueil](../../README.md) et [page de veille](../../VEILLE.md) créées.
- **Veille :** le script Python est programmé chaque lundi à 12 h dans Windows. La version 3.1.1 a été repérée et ses notes ont été examinées le 9 novembre ; le P13 reste sur pandas 3.0.1.
- **Contrôle des données :** un script vérifie chaque jour à midi si un nouveau lot complet a été déposé. Le 9 novembre, la tâche Windows a traité des copies du seul lot fourni. Les trois CSV obtenus sont identiques à ceux du lancement manuel avec la méthode **Données d'origine** (`raw`) ; seul l'horodatage du rapport JSON diffère. Aucun autre lot n'est disponible pour ce projet.
- **Remise finale :** relecture des livrables en cours.

## Traiter un nouveau lot automatiquement

1. Conserver les originaux. Placer des copies de `erp.xlsx`, `liaison.xlsx` et `web.xlsx` dans un sous-dossier de `lots_a_traiter`, par exemple `lots_a_traiter/lot_001/`.
2. Quand le PC est allumé, la tâche Windows « Portfolio P13 Controle donnees » vérifie ce dossier chaque jour à midi. Elle attend que les trois fichiers soient présents et que leur copie soit terminée.
3. Lire les résultats dans `outputs/controle_auto/lot_001__.../` : `rapport_qualite.json` pour les contrôles et `anomalies_poc.csv` pour les cas à examiner. Le fichier `journal.jsonl` garde la trace des exécutions et des échecs.
4. Faire valider les décisions par le référent métier. Pour chaque cas, noter le lot, le produit, l'alerte, la décision, sa justification et la personne qui l'a validée. Si une règle change, mettre aussi à jour le code et la documentation.

Le [script automatique](src/auto_controle.py) utilise la méthode **Données d'origine** (`raw`) : il signale les écarts sans appliquer les corrections d'identifiants propres au lot historique. Il ne traite pas deux fois des fichiers inchangés ; si leur contenu change, il crée un nouveau dossier de résultats. Une alerte signale un point à vérifier : elle ne corrige pas la donnée et n'envoie aucun message. La décision reste humaine.

Pour lancer un contrôle sans attendre le lendemain midi, ouvrir le P13 dans VS Code et exécuter `python src/auto_controle.py` avec l'environnement Python du projet. Le [pipeline](src/pipeline.py) reste disponible pour lancer directement un lot avec des options particulières.

Les classeurs source sont conservés localement dans `lots_a_traiter`, exclu de Git. Le test sur leurs copies a produit les mêmes CSV en manuel et en automatique. Refaire exactement ce test demande les mêmes classeurs et les versions de [requirements.txt](requirements.txt) ; le dépôt présente le code et les résultats vérifiés sans diffuser ces sources.

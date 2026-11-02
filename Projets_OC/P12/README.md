# Détecter les faux billets à partir de leurs mesures

Ce projet classe les billets comme authentiques ou contrefaits à partir de six mesures. J'ai comparé plusieurs méthodes, puis enregistré un modèle que le script Python peut appliquer à un billet ou à un CSV.

## Données et méthode

`billets.csv` contient 1 500 billets : 1 000 authentiques et 500 contrefaits. Le modèle utilise `diagonal`, `height_left`, `height_right`, `margin_low`, `margin_up` et `length`. Les 37 valeurs manquantes de `margin_low` sont remplacées par la médiane calculée sur l'entraînement.

Le notebook réserve 20 % des billets au test. Il compare régression logistique, KNN et Random Forest ; K-Means est examiné à part. La régression logistique a été retenue pour son rappel moyen des faux billets en validation croisée : **98,8 %** sur cinq plis d'entraînement.

Sur les **300 billets du test**, le modèle classe correctement les **200 authentiques** et détecte **97 contrefaçons sur 100**. Il laisse passer trois faux billets. L'exactitude est de **99 %** et le rappel des contrefaçons de **97 %** sur cet échantillon.

## Fichiers du projet

- `Atitso_William_1_analyse_092026.ipynb` : analyse, comparaison et entraînement.
- `Atitso_William_2_Script_092026.py` : prédiction manuelle ou depuis un CSV.
- `Atitso_William_3_Presentation_092026.pptx` : démarche et résultats.
- `Atitso_William_4_Test_092026.ipynb` : démonstration des prédictions.
- `modele_billets.pkl` : modèle enregistré.
- `billets.csv` : données d'analyse.

## Exécuter dans VS Code

Ouvrir `P12` dans VS Code avec Python et Jupyter, puis installer les bibliothèques utilisées dans le notebook. Exécuter ses cellules avec `P12` comme dossier courant : il lit `billets.csv` et enregistre `modele_billets.pkl`.

Le script charge le modèle placé à côté de lui. Sans argument, il demande les six mesures dans le terminal. Avec un chemin CSV, il crée un fichier `_predictions.csv` à côté du fichier d'entrée. Le CSV doit contenir les six colonnes indiquées plus haut ; `is_genuine` est facultative. Dans le notebook de démonstration, renseigner le chemin dans `tester_fichier(...)`.

## Limites

Le test provient du même fichier que l'entraînement. Avant tout usage réel, il faudrait vérifier le modèle sur d'autres billets étiquetés. Les probabilités affichées restent des estimations.

"""Prediction des billets avec le modele entraine dans le notebook."""
from pathlib import Path
from math import isfinite
import sys
from typing import Any, Sequence

import joblib
import pandas as pd

# Affiche correctement les accents dans les terminaux Windows recents.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

COLS = [
    "diagonal", "height_left", "height_right",
    "margin_low", "margin_up", "length"
]
DOSSIER_SCRIPT = Path(__file__).resolve().parent
CHEMIN_MODELE = DOSSIER_SCRIPT / "modele_billets.pkl"
_MODELE = None


def charger_modele() -> object:
    """Charge le modèle une fois, puis le réutilise pour les prédictions."""
    global _MODELE
    if _MODELE is not None:
        return _MODELE
    if not CHEMIN_MODELE.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {CHEMIN_MODELE}. "
            "Il faut d'abord entraîner et enregistrer la régression logistique depuis le notebook."
        )
    _MODELE = joblib.load(CHEMIN_MODELE)
    return _MODELE


def verifier_mesures(valeurs: Sequence[float]) -> list[float]:
    """Vérifie que les six mesures saisies sont bien des nombres finis."""
    try:
        mesures = [float(v) for v in valeurs]
    except (TypeError, ValueError):
        raise ValueError("Les six mesures doivent être des nombres.") from None
    if not all(isfinite(v) for v in mesures):
        raise ValueError("Les mesures doivent être des nombres finis (pas NaN ou infinis).")
    return mesures


def obtenir_confiance(
    modele: Any,
    donnees: pd.DataFrame,
    predictions: Sequence[Any],
) -> list[float]:
    """Renvoie la probabilité estimée de la classe prédite pour chaque billet."""
    probabilites = modele.predict_proba(donnees)
    index_classes = {classe: i for i, classe in enumerate(modele.classes_)}
    return [
        float(probabilites[i, index_classes[prediction]])
        for i, prediction in enumerate(predictions)
    ]


def predire_billet(diagonal: float, height_left: float, height_right: float,
                   margin_low: float, margin_up: float, length: float) -> str:
    valeurs = verifier_mesures(
        [diagonal, height_left, height_right, margin_low, margin_up, length]
    )
    billet = pd.DataFrame([dict(zip(COLS, valeurs))])
    modele = charger_modele()
    prediction = modele.predict(billet)[0]
    confiance = obtenir_confiance(modele, billet, [prediction])[0]
    resultat = "Billet contrefait" if prediction == 1 else "Billet authentique"
    return f"{resultat} (probabilité estimée : {confiance:.2%})"


def tester_fichier(chemin: str | Path) -> Path:
    """Prédit les billets d'un CSV et écrit un CSV de résultats à côté de l'entrée."""
    chemin = Path(chemin).expanduser().resolve()
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    # sep=None reconnaît notamment les fichiers séparés par ; ou par ,.
    df = pd.read_csv(chemin, sep=None, engine="python", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    # Certains fichiers fournis sont lus en une seule colonne malgré le séparateur.
    if len(df.columns) == 1:
        contenu = df.iloc[:, 0].astype(str).str.replace('"', '', regex=False)
        df = contenu.str.split(";", expand=True)
        if df.shape[1] != len(COLS):
            raise ValueError(
                f"Le CSV doit contenir les six mesures, séparées par des points-virgules. "
                f"{df.shape[1]} colonne(s) obtenue(s) après lecture."
            )
        # read_csv a déjà lu l'en-tête, les lignes restantes sont les données.
        df.columns = COLS

    df.columns = df.columns.astype(str).str.replace("\ufeff", "", regex=False).str.strip()
    manquantes = [colonne for colonne in COLS if colonne not in df.columns]
    if manquantes:
        raise ValueError(f"Colonnes manquantes dans le CSV : {', '.join(manquantes)}")

    # On garde une copie pour distinguer les valeurs manquantes du texte invalide.
    mesures_brutes = df[COLS].copy()
    for colonne in COLS:
        df[colonne] = pd.to_numeric(df[colonne], errors="coerce")

    # Les NaN déjà présents sont imputés par le SimpleImputer du pipeline.
    # Une valeur texte qui devient NaN doit en revanche être signalée.
    non_numeriques = df[COLS].isna() & mesures_brutes.notna()
    if non_numeriques.any().any():
        lignes = non_numeriques.any(axis=1).to_numpy().nonzero()[0] + 2
        raise ValueError(f"Mesure non numérique aux lignes : {lignes.tolist()}")

    valeurs = df[COLS].to_numpy(dtype=float)
    lignes_infinies = [
        i + 2 for i, ligne in enumerate(valeurs)
        if any(not isfinite(float(v)) for v in ligne if not pd.isna(v))
    ]
    if lignes_infinies:
        raise ValueError(f"Valeur infinie dans les mesures aux lignes : {lignes_infinies}")

    modele = charger_modele()
    predictions = modele.predict(df[COLS])
    df["prediction"] = predictions
    df["resultat"] = df["prediction"].map({1: "Contrefait", 0: "Authentique"})
    df["probabilite_prediction_pct"] = [
        round(probabilite * 100, 2)
        for probabilite in obtenir_confiance(modele, df[COLS], predictions)
    ]
    sortie = chemin.with_name(f"{chemin.stem}_predictions.csv")
    df.to_csv(sortie, sep=";", index=False, encoding="utf-8-sig")
    print(f"Fichier généré : {sortie}")
    return sortie


def prediction_manuel() -> None:
    print("\nSaisie des valeurs du billet :")
    invites = ["Diagonale", "Hauteur gauche", "Hauteur droite",
               "Marge basse", "Marge haute", "Longueur"]
    try:
        valeurs = [float(input(f"{nom} : ")) for nom in invites]
        print("\nRésultat :", predire_billet(*valeurs))
    except (ValueError, FileNotFoundError) as erreur:
        print(f"Erreur : {erreur}")


def main() -> None:
    if len(sys.argv) > 1:
        try:
            tester_fichier(sys.argv[1])
        except (FileNotFoundError, ValueError) as erreur:
            print(f"Erreur : {erreur}")
    else:
        prediction_manuel()


if __name__ == "__main__":
    main()

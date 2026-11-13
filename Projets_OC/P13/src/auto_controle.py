# %% [markdown]
# # Contrôle automatique des nouveaux lots P13
#
# Placer une copie des trois classeurs dans un sous-dossier de `lots_a_traiter` :
# `lot_001/erp.xlsx`, `lot_001/liaison.xlsx` et `lot_001/web.xlsx`.
# Ce script vérifie les lots présents et lance le pipeline pour chaque nouveau lot.
# Il ne change jamais les fichiers d'entrée ni les règles métier.

"""Lance le pipeline P13 sur les nouveaux lots complets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
INPUT_ROOT = PROJECT_DIR / "lots_a_traiter"
OUTPUT_ROOT = PROJECT_DIR / "outputs" / "controle_auto"
REQUIRED_FILES = ("erp.xlsx", "liaison.xlsx", "web.xlsx")
RESULT_FILES = (
    "jointure_poc.csv",
    "df_clean_historique_poc.csv",
    "anomalies_poc.csv",
    "rapport_qualite.json",
)


# %% [markdown]
# ## Reconnaitre un lot déjà traité
#
# L'empreinte dépend du contenu des trois classeurs. Si un classeur change,
# le prochain passage crée un résultat distinct. Un dossier incomplet ou un
# fichier encore en cours de copie est ignoré jusqu'au passage suivant.

def lot_fingerprint(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()[:16]


def file_is_stable(path: Path, min_age_seconds: int) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    if min_age_seconds == 0:
        return True
    return datetime.now(timezone.utc).timestamp() - path.stat().st_mtime >= min_age_seconds


def write_journal(output_root: Path, entry: dict) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    with (output_root / "journal.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(entry, ensure_ascii=False) + "\n")


# %% [markdown]
# ## Lancer le pipeline
#
# Les résultats arrivent dans un nouveau dossier seulement si les quatre
# fichiers attendus ont été produits. En cas d'erreur, le journal garde le
# message et le lot pourra être réessayé au passage suivant.

def process_lot(lot_dir: Path, output_root: Path, min_age_seconds: int) -> str:
    paths = [lot_dir / name for name in REQUIRED_FILES]
    if not all(file_is_stable(path, min_age_seconds) for path in paths):
        return "en attente"

    fingerprint = lot_fingerprint(paths)
    target = output_root / f"{lot_dir.name}__{fingerprint}"
    if (target / "controle.json").is_file():
        return "déjà contrôlé"

    staging = output_root / f".{lot_dir.name}__{fingerprint}.en_cours"
    staging.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(PROJECT_DIR / "src" / "pipeline.py"),
        "--input-dir", str(lot_dir),
        "--output-dir", str(staging),
        "--correction-profile", "raw",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if result.returncode != 0 or not all((staging / name).is_file() for name in RESULT_FILES):
        write_journal(output_root, {
            "date_utc": checked_at,
            "lot": lot_dir.name,
            "empreinte": fingerprint,
            "etat": "échec",
            "message": (result.stderr or result.stdout)[-2000:],
        })
        return "échec (voir journal.jsonl)"

    if lot_fingerprint(paths) != fingerprint:
        write_journal(output_root, {
            "date_utc": checked_at,
            "lot": lot_dir.name,
            "empreinte": fingerprint,
            "etat": "échec",
            "message": "Un fichier d'entrée a changé pendant le contrôle ; nouveau passage nécessaire.",
        })
        return "fichiers modifiés pendant le contrôle"

    (staging / "controle.json").write_text(
        json.dumps({
            "lot": lot_dir.name,
            "empreinte": fingerprint,
            "controle_le_utc": checked_at,
            "profil": "raw",
            "revue_humaine": "à faire",
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if target.exists():
        # Un contrôle plus ancien du même lot peut avoir échoué avant validation.
        return "résultat existant à vérifier"
    os.replace(staging, target)
    write_journal(output_root, {
        "date_utc": checked_at,
        "lot": lot_dir.name,
        "empreinte": fingerprint,
        "etat": "contrôlé, revue humaine à faire",
        "resultats": str(target),
    })
    return "contrôlé, revue humaine à faire"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--min-age-seconds", type=int, default=60)
    args = parser.parse_args()
    if args.min_age_seconds < 0:
        parser.error("--min-age-seconds doit être positif ou nul")
    args.input_root.mkdir(parents=True, exist_ok=True)
    args.output_root.mkdir(parents=True, exist_ok=True)

    lots = sorted(path for path in args.input_root.iterdir() if path.is_dir())
    if not lots:
        print(f"Aucun lot à contrôler dans {args.input_root}")
        return 0
    had_failure = False
    for lot in lots:
        try:
            status = process_lot(lot, args.output_root, args.min_age_seconds)
            print(f"{lot.name} : {status}")
            had_failure |= status.startswith("échec") or status.startswith("fichiers modifiés")
        except (OSError, ValueError) as exc:
            had_failure = True
            write_journal(args.output_root, {
                "date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "lot": lot.name,
                "etat": "échec",
                "message": str(exc),
            })
            print(f"{lot.name} : échec (voir journal.jsonl)", file=sys.stderr)
    return 1 if had_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())

# %% [markdown]
# # Veille pandas du P13
#
# Mon pipeline utilise pandas pour lire des fichiers Excel, faire des jointures,
# contrôler les valeurs manquantes et créer des exports. Ce script repère les
# nouvelles versions ; je lis ensuite les notes avant de décider quoi tester.
#
# Depuis le dossier P13 : `python src/veille_pandas.py`
# Après lecture des notes : `python src/veille_pandas.py --mark-reviewed X.Y.Z`

# %%
"""Surveille les versions stables de pandas utiles au projet P13.

Utilisation : python src/veille_pandas.py
Le controle ne modifie jamais les dependances ni les donnees du projet.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# %% [markdown]
# ## Source et thèmes suivis
#
# La liste vient des versions officielles publiées sur GitHub. Je garde seulement
# les versions stables et cherche dans chaque annonce des termes liés au P13.
# Ce repérage aide à trier les annonces ; il ne remplace pas la lecture des notes.

# %%
RELEASES_URL = "https://api.github.com/repos/pandas-dev/pandas/releases?per_page=100"
BASELINE_VERSION = "3.1.0"  # Derniere version examinee le 26 octobre 2026.
DEFAULT_STATE = Path(__file__).resolve().parents[1] / "output" / "veille_pandas_state.json"
VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
TOPICS = {
    "lecture Excel": (r"\bread_excel\b", r"\bexcel\b", r"\bopenpyxl\b", r"\bxlsx\b"),
    "jointures": (r"\bmerge\b", r"\bjoin\b"),
    "valeurs manquantes": (r"\bmissing\b", r"\bfillna\b", r"\bisna\b", r"\bnull\b"),
    "exports": (r"\bto_excel\b", r"\bto_csv\b", r"\bexport\b"),
}


def version_key(tag: str) -> tuple[int, int, int] | None:
    match = VERSION_PATTERN.fullmatch(tag)
    return tuple(map(int, match.groups())) if match else None


# %% [markdown]
# ## Suivi des contrôles
#
# Un fichier JSON conserve la dernière version relue et les contrôles datés.
# Une nouvelle version reste donc signalée aux passages suivants jusqu'à ce que
# je la marque comme examinée. Le script n'installe aucune mise à jour.

# %%
def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"last_reviewed_version": BASELINE_VERSION}
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or version_key(state.get("last_reviewed_version", "")) is None:
        raise ValueError(f"Etat de veille invalide : {path}")
    if not isinstance(state.get("checks", []), list):
        raise ValueError(f"Historique de veille invalide : {path}")
    return state


def fetch_releases() -> list[dict]:
    request = Request(
        RELEASES_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "p13-pandas-watch"},
    )
    with urlopen(request, timeout=20) as response:
        releases = json.load(response)
    if not isinstance(releases, list):
        raise ValueError("La reponse GitHub ne contient pas de liste de versions.")
    return releases


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".veille_pandas_",
            suffix=".tmp", delete=False,
        ) as temporary:
            json.dump(state, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


# %% [markdown]
# ## Lancer le contrôle
#
# Le script affiche la date, les nouvelles versions, les liens officiels et les
# thèmes repérés. En cas d'échec réseau, il ne valide pas le contrôle.
# L'option `--dry-run` permet un essai sans enregistrer de date.

# %%
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="Fichier de suivi JSON")
    parser.add_argument("--releases-file", type=Path, help="Reponse GitHub locale pour un essai hors ligne")
    parser.add_argument("--dry-run", action="store_true", help="Afficher sans enregistrer le suivi")
    parser.add_argument(
        "--mark-reviewed", metavar="VERSION",
        help="Marquer une version comme relue, apres verification humaine des notes",
    )
    args = parser.parse_args()

    try:
        state = read_state(args.state)
        if args.mark_reviewed:
            current = state["last_reviewed_version"]
            requested = args.mark_reviewed.removeprefix("v")
            if version_key(requested) is None or version_key(requested) < version_key(current):
                raise ValueError(f"Version invalide ou anterieure a {current} : {requested}")
            state["last_reviewed_version"] = requested
            state["last_reviewed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            if not args.dry_run:
                write_state(args.state, state)
            print(f"Pandas {requested} marque comme relu. Aucune dependance modifiee.")
            return 0

        releases = (
            json.loads(args.releases_file.read_text(encoding="utf-8"))
            if args.releases_file else fetch_releases()
        )
        if not isinstance(releases, list):
            raise ValueError("La liste des versions est invalide.")

        last_reviewed = state["last_reviewed_version"]
        stable = [
            release for release in releases
            if isinstance(release, dict)
            and not release.get("draft") and not release.get("prerelease")
            and version_key(str(release.get("tag_name", ""))) is not None
        ]
        if not stable:
            raise ValueError("Aucune version stable trouvee : controle non enregistre.")
        if last_reviewed not in {str(r["tag_name"]).removeprefix("v") for r in stable}:
            raise ValueError(
                f"La version de reference {last_reviewed} n'apparait plus dans les 100 versions recues. "
                "Verifier l'historique avant de poursuivre."
            )

        new_releases = sorted(
            (r for r in stable if version_key(str(r["tag_name"])) > version_key(last_reviewed)),
            key=lambda r: version_key(str(r["tag_name"])),
        )
        checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"Controle du {checked_at} | derniere version relue : {last_reviewed}")
        if not new_releases:
            print("Aucune nouvelle version stable de pandas.")

        detected = []
        for release in new_releases:
            version = str(release["tag_name"]).removeprefix("v")
            body = str(release.get("body") or "")
            matched = [
                topic for topic, patterns in TOPICS.items()
                if any(re.search(pattern, body, flags=re.IGNORECASE) for pattern in patterns)
            ]
            detected.append({"version": version, "topics": matched, "url": release.get("html_url")})
            print(f"\nPandas {version} | publication : {release.get('published_at') or 'date inconnue'}")
            print(f"Annonce : {release.get('html_url') or 'lien absent'}")
            print(f"Notes : https://pandas.pydata.org/docs/whatsnew/v{version}.html")
            if matched:
                print("Termes reperes dans l'annonce : " + ", ".join(matched))
            else:
                print("Aucun terme cible dans l'annonce courte ; lire les notes completes.")
            print("Decision : verifier les notes et tester le pipeline avant toute mise a jour.")

        state["last_checked_at_utc"] = checked_at
        state["checks"] = (state.get("checks", []) + [{
            "checked_at_utc": checked_at,
            "last_reviewed_version": last_reviewed,
            "new_releases": detected,
        }])[-52:]
        if not args.dry_run:
            write_state(args.state, state)
            print(f"\nSuivi enregistre : {args.state}")
        else:
            print("\nEssai sans modification du suivi.")
        return 0
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Echec de la veille : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

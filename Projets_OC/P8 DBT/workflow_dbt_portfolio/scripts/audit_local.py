"""Contrôles locaux des sources P8 ; ne produit aucune donnée individuelle."""

from collections import Counter, defaultdict
from pathlib import Path
import csv
import json
import unicodedata


BASE = Path(__file__).resolve().parents[2]


def ascii_upper(value):
    normalized = unicodedata.normalize("NFKD", (value or "").strip().upper())
    return "".join(c for c in normalized if not unicodedata.combining(c))


def region(value):
    name = ascii_upper(value)
    if name in {"GUADELOUPE", "GUYANE", "MARTINIQUE", "MAYOTTE", "LA REUNION", "DOM", "DROM"}:
        return "DROM"
    if name == "CENTRE-VAL-DE-LOIRE":
        return "CENTRE-VAL DE LOIRE"
    return name


def age(value):
    value = (value or "").strip()
    if value in {"20-24 ans", "25-29 ans", "30-34 ans", "35-39 ans"}:
        return "20-39"
    if value in {"40-44 ans", "45-49 ans", "50-54 ans", "55-59 ans"}:
        return "40-59"
    if value in {"60-64 ans", "65-69 ans", "70-74 ans"}:
        return "60-74"
    if value.startswith("75"):
        return "75+"
    if value == "60 ans ou plus":
        return "60-74"
    return value


def gender(value):
    value = (value or "").strip().upper()
    if value in {"M", "H", "HOMME"}:
        return "HOMME"
    if value in {"F", "FEMME"}:
        return "FEMME"
    return "INCONNU"


source = next(BASE.glob("DATASET*.csv"))
with source.open(encoding="utf-8-sig", newline="") as stream:
    raw = list(csv.DictReader(stream))

by_user = defaultdict(list)
for row in raw:
    if row["USER_ID"]:
        by_user[row["USER_ID"]].append(row)

latest = []
tie_users = 0
for records in by_user.values():
    max_year = max((r["YEAR_PATH_STARTED"] for r in records), default="")
    tied = [r for r in records if r["YEAR_PATH_STARTED"] == max_year]
    if len({tuple(r.values()) for r in tied}) > 1:
        tie_users += 1
    latest.append(sorted(tied, key=lambda r: (r["PATH_CATEGORY_NAME"], r["AGE_GROUP"], r["GENDER"], r["REGION"]))[0])

raw_grain = Counter((r["YEAR_PATH_STARTED"], region(r["REGION"]), age(r["AGE_GROUP"]), gender(r["GENDER"])) for r in latest)
export = next(BASE.glob("Atitso_William_1*donnéescsv*.csv"))
with export.open(encoding="utf-8-sig", newline="") as stream:
    exported = list(csv.DictReader(stream, delimiter=";"))
export_grain = {}
duplicate_export_keys = Counter()
inconsistent_duplicates = 0
for row in exported:
    key = (row["ANNEE"], region(row["REGION"]), row["CATEGORIE D'AGE"], row["GENRE"])
    count = int(row["NOMBRE D'ETUDIANTS"])
    duplicate_export_keys[key] += 1
    if key in export_grain and export_grain[key] != count:
        inconsistent_duplicates += 1
    export_grain.setdefault(key, count)


population = BASE / "Population 2024.csv"
with population.open(encoding="utf-8-sig", newline="") as stream:
    pop_rows = list(csv.reader(stream, delimiter=";"))
regions_pop = {}
for row in pop_rows[5:18] + pop_rows[19:24]:
    name = region(row[0])
    value = int(row[6].replace(" ", ""))
    regions_pop[name] = regions_pop.get(name, 0) + value

def count_by(index):
    result = Counter()
    for key, count in raw_grain.items():
        result[key[index]] += count
    return dict(sorted(result.items()))


report = {
    "raw_rows": len(raw),
    "unique_users": len(by_user),
    "conflicting_latest_year_ties": tie_users,
    "latest_records": len(latest),
    "raw_vs_export_grain_match_after_documented_age_harmonization": raw_grain == export_grain,
    "raw_60_plus_count": sum(r["AGE_GROUP"] == "60 ans ou plus" for r in latest),
    "raw_grain_keys": len(raw_grain),
    "export_rows": len(exported),
    "export_unique_keys": len(export_grain),
    "export_duplicate_keys": sum(n > 1 for n in duplicate_export_keys.values()),
    "export_inconsistent_duplicate_counts": inconsistent_duplicates,
    "export_deduplicated_count": sum(export_grain.values()),
    "by_year": count_by(0),
    "by_region": count_by(1),
    "by_age": count_by(2),
    "by_gender": count_by(3),
    "population_source_sum": sum(regions_pop.values()),
    "population_source_total": int(pop_rows[25][6].replace(" ", "")),
    "population_idf": regions_pop.get("ILE-DE-FRANCE"),
    "population_drom": regions_pop.get("DROM"),
}
print(json.dumps(report, ensure_ascii=False, indent=2))
if raw_grain != export_grain:
    raise SystemExit("Échec : les effectifs bruts et l'export dédoublonné divergent.")
if inconsistent_duplicates:
    raise SystemExit("Échec : l'export répète un grain avec des effectifs différents.")
if sum(regions_pop.values()) != report["population_source_total"]:
    raise SystemExit("Échec : la population régionale ne se réconcilie pas au total INSEE.")

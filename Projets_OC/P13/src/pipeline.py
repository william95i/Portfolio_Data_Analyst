"""Pipeline POC de préparation et de contrôle des données Bottleneck."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from quality_checks import (
    anomaly_rows,
    duplicate_key_count,
    profile_table,
    require_columns,
)


REQUIRED = {
    "erp": {
        "product_id",
        "onsale_web",
        "price",
        "stock_quantity",
        "stock_status",
        "purchase_price",
    },
    "liaison": {"id_web", "product_id"},
    "web": {"sku", "total_sales", "post_type", "post_title", "product_type"},
}
WEB_SKU_CORRECTIONS = {
    "38": "00038",
    "41": "00041",
    "13127-1": "13127",
    "bon-cadeau-25-euros": "25000",
}
LIAISON_ID_CORRECTIONS = {
    "bon-cadeau-25-euros": "25000",
    "13127-1": "13127",
    "14680-1": "14680",
}
EXPORTED_WEB_CORRECTIONS = {
    "13127-1": "13127",
    "bon-cadeau-25-euros": "25000",
}
EXPORTED_LIAISON_CORRECTIONS = {
    "bon-cadeau-25-euros": "25000",
    "13127-1": "13127",
}


def _canonical_identifier(value: Any) -> object:
    """Normalize numeric Excel identifiers while preserving
    text identifiers."""
    if pd.isna(value):
        return pd.NA
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)) and math.isfinite(float(value)):
        if float(value).is_integer():
            return str(int(value))
    text = str(value).strip()
    return text if text else pd.NA


def _load_input(path: Path, table_name: str) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Fichier {table_name} introuvable : {path}")
    frame = pd.read_excel(path, sheet_name=0)
    if frame.columns.duplicated().any():
        duplicates = (
            frame.columns[frame.columns.duplicated()].astype(str).tolist()
        )
        raise ValueError(
            f"{path.name}: noms de colonnes en double : {duplicates}"
        )
    require_columns(frame, REQUIRED[table_name], path.name)
    return frame


def build_pipeline(
    input_dir: Path,
    vat_multiplier: float,
    correction_profile: str = "export_observed",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], pd.DataFrame]:
    if correction_profile == "notebook_code":
        web_join_map = WEB_SKU_CORRECTIONS
        liaison_join_map = LIAISON_ID_CORRECTIONS
        web_label_map = WEB_SKU_CORRECTIONS
        liaison_label_map = LIAISON_ID_CORRECTIONS
    elif correction_profile == "export_observed":
        # Les exports montrent que les clés brutes ont servi à joindre,
        # puis que certains identifiants ont été corrigés dans le
        # résultat visible.
        web_join_map = {}
        liaison_join_map = {}
        web_label_map = EXPORTED_WEB_CORRECTIONS
        liaison_label_map = EXPORTED_LIAISON_CORRECTIONS
    elif correction_profile == "raw":
        web_join_map = {}
        liaison_join_map = {}
        web_label_map = {}
        liaison_label_map = {}
    else:
        raise ValueError(
            "correction_profile doit être 'notebook_code', "
            "'export_observed' ou 'raw'"
        )
    erp = _load_input(input_dir / "erp.xlsx", "erp")
    liaison = _load_input(input_dir / "liaison.xlsx", "liaison")
    web = _load_input(input_dir / "web.xlsx", "web")

    profiles = [
        profile_table(erp, "erp_source"),
        profile_table(liaison, "liaison_source"),
        profile_table(web, "web_source"),
    ]
    checks: list[dict[str, Any]] = []

    # La jointure du P6 repose sur une ligne ERP et une ligne liaison
    # par product_id.
    for name, frame in (("ERP", erp), ("liaison", liaison)):
        duplicate_count = duplicate_key_count(frame, "product_id")
        checks.append({
            "check": f"unicité product_id ({name})",
            "status": "OK" if duplicate_count == 0 else "À examiner",
            "rows_flagged": duplicate_count,
            "detail": (
                "Une clé répétée peut multiplier les lignes "
                "à la jointure."
            ),
        })
        if duplicate_count:
            raise ValueError(
                f"Clé product_id dupliquée dans {name}; jointure arrêtée."
            )

    web_products = web.loc[web["post_type"].eq("product")].copy()
    web_non_products = int(len(web) - len(web_products))
    web_missing_sku = int(web_products["sku"].isna().sum())
    web_missing_sku_all_types = int(web["sku"].isna().sum())
    web_products = web_products.loc[web_products["sku"].notna()].copy()
    web_products["sku_web_source"] = web_products["sku"]
    raw_web_key = web_products["sku"].map(_canonical_identifier)
    web_products["_sku_output"] = raw_web_key.replace(web_label_map)
    web_products["_join_sku"] = raw_web_key.replace(web_join_map)
    web_join_corrections = {
        key: int(raw_web_key.eq(key).sum())
        for key in web_join_map
        if raw_web_key.eq(key).any()
    }
    web_label_corrections = {
        key: int(raw_web_key.eq(key).sum())
        for key in web_label_map
        if raw_web_key.eq(key).any()
    }
    web_products["_join_sku"] = raw_web_key.replace(web_join_map).astype(
        "string"
    )
    web_products = web_products.loc[web_products["_join_sku"].notna()].copy()
    duplicate_web_sku_rows = int(
        web_products["_join_sku"].duplicated(keep=False).sum()
    )
    duplicate_web_sku_removed = int(
        web_products["_join_sku"].duplicated(keep="first").sum()
    )
    # Le profil notebook_code reproduit explicitement l'ancienne déduplication
    # pour comparer ses effets. Les profils raw/export_observed conservent les
    # clés répétées et leurs lignes; elles restent visibles comme alertes.
    if correction_profile == "notebook_code":
        web_products = web_products.drop_duplicates(
            subset="_join_sku", keep="first"
        )

    checks.extend([
        {
            "check": "filtrage des lignes Web",
            "status": "Information",
            "rows_flagged": web_non_products,
            "detail": (
                "Lignes écartées car post_type n'est pas 'product', "
                "comme dans le notebook P6."
            ),
        },
        {
            "check": "SKU Web manquants parmi les produits",
            "status": "À examiner" if web_missing_sku else "OK",
            "rows_flagged": web_missing_sku,
            "detail": (
                "Lignes laissées hors rapprochement produit; "
                "elles ne sont pas supprimées des sources."
            ),
        },
        {
            "check": "SKU Web répétés",
            "status": "À examiner" if duplicate_web_sku_rows else "OK",
            "rows_flagged": duplicate_web_sku_rows,
            "detail": (
                "Pour reproduire le P6, première occurrence conservée; "
                f"{duplicate_web_sku_removed} ligne(s) non retenue(s)."
            ),
        },
        {
            "check": "SKU Web manquants toutes lignes confondues",
            "status": "Information" if web_missing_sku_all_types else "OK",
            "rows_flagged": web_missing_sku_all_types,
            "detail": (
                "Ce compte inclut les lignes de pièces jointes et autres "
                "types Web; il est distinct des produits sans SKU."
            ),
        },
        {
            "check": "prix ERP négatifs (source complète)",
            "status": (
                "À examiner"
                if pd.to_numeric(erp["price"], errors="coerce").lt(0).any()
                else "OK"
            ),
            "rows_flagged": int(
                pd.to_numeric(erp["price"], errors="coerce").lt(0).sum()
            ),
            "detail": (
                "Valeurs signalées sur la source ERP entière, y compris les "
                "produits non rapprochés."
            ),
        },
        {
            "check": "stock ERP négatif (source complète)",
            "status": (
                "À examiner"
                if pd.to_numeric(
                    erp["stock_quantity"], errors="coerce"
                ).lt(0).any()
                else "OK"
            ),
            "rows_flagged": int(
                pd.to_numeric(
                    erp["stock_quantity"], errors="coerce"
                ).lt(0).sum()
            ),
            "detail": (
                "Valeurs conservées; leur sens métier n'est pas présumé."
            ),
        },
        {
            "check": "ventes Web négatives (source complète)",
            "status": (
                "À examiner"
                if pd.to_numeric(
                    web["total_sales"], errors="coerce"
                ).lt(0).any()
                else "OK"
            ),
            "rows_flagged": int(
                pd.to_numeric(web["total_sales"], errors="coerce").lt(0).sum()
            ),
            "detail": (
                "Valeurs signalées sur la source Web entière, même si la "
                "ligne ne rejoint aucun produit ERP."
            ),
        },
    ])

    erp = erp.copy()
    liaison = liaison.copy()
    erp["_product_id_key"] = erp["product_id"].map(_canonical_identifier)
    liaison["_product_id_key"] = liaison["product_id"].map(
        _canonical_identifier
    )
    liaison["id_web_source"] = liaison["id_web"]
    raw_liaison_key = liaison["id_web"].map(_canonical_identifier)
    liaison["id_web"] = raw_liaison_key.replace(liaison_label_map)
    liaison["_join_sku"] = raw_liaison_key.replace(liaison_join_map)
    liaison_join_corrections = {
        key: int(raw_liaison_key.eq(key).sum())
        for key in liaison_join_map
        if raw_liaison_key.eq(key).any()
    }
    liaison_label_corrections = {
        key: int(raw_liaison_key.eq(key).sum())
        for key in liaison_label_map
        if raw_liaison_key.eq(key).any()
    }
    liaison["_join_sku"] = liaison["_join_sku"].astype("string")
    web_products["_join_sku"] = web_products["_join_sku"].astype("string")

    erp_liaison = erp.merge(
        liaison.drop(columns=["product_id"]),
        how="left",
        on="_product_id_key",
        validate="one_to_one",
        indicator="_erp_liaison_match",
        suffixes=("", "_liaison"),
    )
    erp_liaison_unmatched = int(
        erp_liaison["_erp_liaison_match"].ne("both").sum()
    )
    liaison_missing_web_id = int(liaison["id_web"].isna().sum())

    joined = erp_liaison.merge(
        web_products.drop(columns=["sku"]),
        how="left",
        on="_join_sku",
        validate=("many_to_one" if correction_profile == "notebook_code" else None),
        indicator="_web_match",
        suffixes=("", "_web"),
    )
    unmatched_web = int(joined["_web_match"].ne("both").sum())
    matched = joined.loc[joined["_web_match"].eq("both")].copy()
    matched["sku"] = matched["_sku_output"]
    duplicate_output_sku_rows = int(
        matched.loc[matched["sku"].notna(), "sku"].duplicated(keep=False).sum()
    )

    # Les calculs reprennent ceux du P6; valeurs d'origine gardées
    # dans le jeu joint.
    matched["price_ht"] = (
        pd.to_numeric(matched["price"], errors="coerce") / vat_multiplier
    )
    matched["taux_marge"] = (
        (
            matched["price_ht"]
            - pd.to_numeric(matched["purchase_price"], errors="coerce")
        )
        / matched["price_ht"]
        * 100
    )
    matched["Valorisation_stock_euros"] = (
        pd.to_numeric(matched["stock_quantity"], errors="coerce")
        * pd.to_numeric(matched["price"], errors="coerce")
    )
    sales = pd.to_numeric(matched["total_sales"], errors="coerce")
    stock = pd.to_numeric(matched["stock_quantity"], errors="coerce")
    # Le P6 remplaçait les dénominateurs nuls/manquants par 0. Le POC garde
    # la valeur inconnue et émet un indicateur afin de ne pas masquer le cas.
    matched["mois_stock"] = stock.div(sales.where(sales.gt(0)))
    matched["flag_mois_stock_indefini"] = sales.isna() | sales.le(0)
    price = pd.to_numeric(matched["price"], errors="coerce")
    price_std = price.std(ddof=1)
    matched["z_score"] = (
        (price - price.mean()) / price_std
        if price_std and not pd.isna(price_std)
        else np.nan
    )
    matched["flag_prix_zscore_sup_3"] = matched["z_score"].gt(3)
    matched["stock_status_2"] = np.where(stock.eq(0), "outofstock", "instock")

    # Contrôles : on signale les cas et on garde les valeurs source.
    rules = {
        "prix négatif": (
            "price",
            pd.to_numeric(matched["price"], errors="coerce").lt(0),
        ),
        "stock négatif": ("stock_quantity", stock.lt(0)),
        "ventes négatives": ("total_sales", sales.lt(0)),
        "marge négative": ("taux_marge", matched["taux_marge"].lt(0)),
        "SKU manquant après jointure": ("sku", matched["sku"].isna()),
        "mois de stock non calculable": (
            "total_sales",
            matched["flag_mois_stock_indefini"],
        ),
        "prix à plus de 3 écarts-types": (
            "z_score",
            matched["flag_prix_zscore_sup_3"],
        ),
    }
    anomaly_report = anomaly_rows(matched, "sku", rules)

    checks.extend([
        {
            "check": "lignes ERP sans correspondance dans liaison",
            "status": "À examiner" if erp_liaison_unmatched else "OK",
            "rows_flagged": erp_liaison_unmatched,
            "detail": (
                "Jointure ERP–liaison conservée en left join pour "
                "rendre les absences visibles."
            ),
        },
        {
            "check": "identifiants Web manquants dans liaison",
            "status": "À examiner" if liaison_missing_web_id else "OK",
            "rows_flagged": liaison_missing_web_id,
            "detail": (
                "product_id peut exister dans liaison alors que id_web est "
                "vide; ces cas empêchent le rapprochement Web."
            ),
        },
        {
            "check": "lignes ERP/liaison sans correspondance Web",
            "status": "À examiner" if unmatched_web else "OK",
            "rows_flagged": unmatched_web,
            "detail": (
                "Lignes non appariées exclues du jeu produit apparié, "
                "comptées dans ce rapport."
            ),
        },
        {
            "check": "marges négatives",
            "status": (
                "À examiner"
                if int(matched["taux_marge"].lt(0).sum())
                else "OK"
            ),
            "rows_flagged": int(matched["taux_marge"].lt(0).sum()),
            "detail": (
                "Le POC conserve ces produits dans la sortie d'analyse et "
                "compare séparément le filtre historique taux_marge > 0."
            ),
        },
        {
            "check": "écart stock_status / statut calculé",
            "status": (
                "À examiner"
                if int(
                    matched["stock_status"].ne(matched["stock_status_2"]).sum()
                )
                else "OK"
            ),
            "rows_flagged": int(
                matched["stock_status"].ne(matched["stock_status_2"]).sum()
            ),
            "detail": (
                "Statut calculé comme dans le contrôle P6 : stock nul => "
                "outofstock, sinon instock."
            ),
        },
        {
            "check": "SKU de sortie associés à plusieurs product_id",
            "status": "À examiner" if duplicate_output_sku_rows else "OK",
            "rows_flagged": duplicate_output_sku_rows,
            "detail": (
                "Les lignes sont conservées grâce à product_id; le SKU est "
                "signalé comme référence métier non unique après correction."
            ),
        },
    ])

    profiles.extend(
        [
            profile_table(erp_liaison, "erp_liaison"),
            profile_table(matched, "jointure_produits"),
            profile_table(anomaly_report, "anomalies"),
        ]
    )
    report = {
        "project": "POC P13 — Bottleneck",
        "correction_profile": correction_profile,
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_files": ["erp.xlsx", "liaison.xlsx", "web.xlsx"],
        "steps": {
            "web_non_product_rows": web_non_products,
            "web_product_rows_missing_sku": web_missing_sku,
            "web_all_rows_missing_sku": web_missing_sku_all_types,
            "web_duplicate_sku_rows": duplicate_web_sku_rows,
            "web_duplicate_sku_rows_removed_keep_first": (
                duplicate_web_sku_removed
            ),
            "web_sku_corrections_to_join_key": web_join_corrections,
            "web_sku_corrections_to_output_label": web_label_corrections,
            "liaison_id_web_corrections_to_join_key": liaison_join_corrections,
            "liaison_id_web_corrections_to_output_label": (
                liaison_label_corrections
            ),
            "erp_without_liaison": erp_liaison_unmatched,
            "liaison_rows_missing_id_web": liaison_missing_web_id,
            "joined_rows_without_web_match": unmatched_web,
            "matched_product_rows": int(len(matched)),
            "duplicate_output_sku_rows": duplicate_output_sku_rows,
            "historical_margin_filter_rows_kept": int(
                matched["taux_marge"].gt(0).sum()
            ),
            "historical_margin_filter_rows_removed": int(
                matched["taux_marge"].le(0).sum()
            ),
            "historical_margin_filter_skus_removed": matched.loc[
                matched["taux_marge"].le(0), "sku"
            ].astype(str).tolist(),
        },
        "profiles": profiles,
        "checks": checks,
        "limitations": [
            (
                "La signification métier des prix, ventes et "
                "stocks négatifs n'est pas validée."
            ),
            (
                "Le filtre historique taux_marge > 0 est reproduit uniquement "
                "pour comparaison."
            ),
            (
                "Le contrôle z-score est une alerte exploratoire; "
                "il ne décide pas si un prix est erroné."
            ),
            (
                "La source de liaison utilisée est liaison.xlsx; sa copie "
                "fournie a les mêmes valeurs."
            ),
            (
                "Les règles n'ont été évaluées que sur les classeurs "
                "fournis."
            ),
        ],
    }
    return (
        matched,
        matched.loc[matched["taux_marge"].gt(0)].copy(),
        report,
        anomaly_report,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Dossier contenant erp.xlsx, liaison.xlsx et web.xlsx",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Dossier de sortie du POC",
    )
    parser.add_argument(
        "--vat-multiplier",
        type=float,
        default=1.2,
        help="Coefficient TTC/HT repris du notebook P6",
    )
    parser.add_argument(
        "--correction-profile",
        choices=("notebook_code", "export_observed", "raw"),
        default="export_observed",
        help=(
            "'notebook_code' applique les mappings du code; "
            "'export_observed' ceux visibles dans df_final; "
            "'raw' ne corrige pas les identifiants."
        ),
    )
    args = parser.parse_args()
    if args.vat_multiplier <= 0:
        parser.error("--vat-multiplier doit être strictement positif")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    joined, historical_clean, report, anomalies = build_pipeline(
        args.input_dir, args.vat_multiplier, args.correction_profile
    )

    # Exporter les clés et mesures utiles au POC; les colonnes Web
    # non nécessaires aux contrôles (URL, auteur, contenu éditorial)
    # restent dans la source.
    wanted = [
        "product_id",
        "id_web",
        "sku",
        "post_title",
        "product_type",
        "onsale_web",
        "price",
        "price_ht",
        "purchase_price",
        "taux_marge",
        "stock_quantity",
        "stock_status",
        "stock_status_2",
        "total_sales",
        "mois_stock",
        "Valorisation_stock_euros",
        "z_score",
        "flag_prix_zscore_sup_3",
        "flag_mois_stock_indefini",
        "sku_web_source",
        "id_web_source",
    ]
    output_columns = [column for column in wanted if column in joined.columns]
    joined[output_columns].to_csv(
        args.output_dir / "jointure_poc.csv",
        index=False,
        encoding="utf-8-sig",
    )
    historical_clean[output_columns].to_csv(
        args.output_dir / "df_clean_historique_poc.csv",
        index=False,
        encoding="utf-8-sig",
    )
    anomalies.to_csv(
        args.output_dir / "anomalies_poc.csv",
        index=False,
        encoding="utf-8-sig",
    )
    (args.output_dir / "rapport_qualite.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report["steps"], ensure_ascii=False, indent=2))
    print(f"\nFichiers produits dans : {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()

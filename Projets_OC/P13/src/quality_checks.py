"""Contrôles qualité simples et explicites pour le POC Bottleneck."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def profile_table(frame: pd.DataFrame, name: str) -> dict[str, object]:
    """Return a compact table profile without altering its contents."""
    return {
        "table": name,
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "duplicate_rows": int(frame.duplicated().sum()),
        "missing_by_column": {
            str(column): int(count)
            for column, count in frame.isna().sum().items()
            if count
        },
    }


def require_columns(
    frame: pd.DataFrame,
    required: Iterable[str],
    table_name: str,
) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(
            f"{table_name}: colonnes obligatoires absentes : {', '.join(missing)}"
        )


def duplicate_key_count(frame: pd.DataFrame, key: str) -> int:
    """Count rows whose key is duplicated, excluding missing keys."""
    valid = frame[key].notna()
    return int(frame.loc[valid, key].duplicated(keep=False).sum())


def anomaly_rows(
    frame: pd.DataFrame,
    key_column: str,
    rules: dict[str, tuple[str, pd.Series]],
) -> pd.DataFrame:
    """Build a long-form list of flagged records and their rule names."""
    records: list[pd.DataFrame] = []
    for rule_name, (column, mask) in rules.items():
        selected = frame.loc[mask.fillna(False), [key_column, column]].copy()
        if selected.empty:
            continue
        selected.insert(0, "rule", rule_name)
        selected.rename(columns={key_column: "sku", column: "value_observed"}, inplace=True)
        selected["column"] = column
        selected["action"] = "À examiner; aucune correction automatique"
        records.append(selected[["rule", "sku", "column", "value_observed", "action"]])

    if not records:
        return pd.DataFrame(
            columns=["rule", "sku", "column", "value_observed", "action"]
        )
    return pd.concat(records, ignore_index=True)

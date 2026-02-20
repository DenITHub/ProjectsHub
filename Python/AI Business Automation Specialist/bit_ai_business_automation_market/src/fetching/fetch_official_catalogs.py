# src/fetching/fetch_official_catalogs.py

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
fetch_official_catalogs.py

Берёт ручные CSV с официальными Beruf(en) по DE/AT/CH,
нормализует и объединяет в единый каталог:

    data/processed/catalog_official_berufe.csv

Этот файл потом используется в similarity-отчётах и в скрейп-пайплайне.
"""

from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"

CATALOGS_DIR = DATA_DIR / "raw" / "catalogs"

DE_FILE = CATALOGS_DIR / "de_berufe_manual.csv"
AT_FILE = CATALOGS_DIR / "at_berufe_manual.csv"
CH_FILE = CATALOGS_DIR / "ch_berufe_manual.csv"

PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_FILE = PROCESSED_DIR / "catalog_official_berufe.csv"


def load_and_normalize(path: Path, expected_country=None) -> pd.DataFrame:
    """Загружает CSV и приводит к общему формату:
       columns = [country, source, official_title, kldb_code, notes]
    """
    df = pd.read_csv(path, sep=";", dtype=str)
    df.columns = [c.strip().lower() for c in df.columns]

    base_cols = ["country", "source", "official_title"]
    for col in base_cols:
        if col not in df.columns:
            raise ValueError(f"{path}: missing column {col} (got: {df.columns})")

    # notes
    if "notes" not in df.columns:
        df["notes"] = ""

    if "kldb_code" not in df.columns:
        df["kldb_code"] = ""

    if expected_country is not None:
        df["country"] = expected_country

    df = df[["country", "source", "official_title", "kldb_code", "notes"]]

    for col in ["country", "source", "official_title", "kldb_code", "notes"]:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    df["country"] = df["country"].str.upper()
    return df


def build_catalog_official_berufe() -> pd.DataFrame:
    """Объединяет DE/AT/CH в единый каталог + dedup."""
    df_de = load_and_normalize(DE_FILE, expected_country="DE")
    df_at = load_and_normalize(AT_FILE, expected_country="AT")
    df_ch = load_and_normalize(CH_FILE, expected_country="CH")

    df_all = pd.concat([df_de, df_at, df_ch], ignore_index=True)

    df_all["official_title_norm"] = (
        df_all["official_title"]
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    df_all["notes_norm"] = (
        df_all["notes"]
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    df_unique = df_all.drop_duplicates(
        subset=["country", "source", "official_title_norm", "kldb_code", "notes_norm"],
        keep="first",
    ).copy()

    df_unique = df_unique[["country", "source", "official_title", "kldb_code", "notes"]]

    df_unique = df_unique.sort_values(
        by=["country", "official_title", "source", "kldb_code"],
        ignore_index=True,
    )

    return df_unique


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df_catalog = build_catalog_official_berufe()
    df_catalog.to_csv(OUTPUT_FILE, sep=";", index=False)

    print(f"[fetch_official_catalogs] rows: {len(df_catalog)}")
    print(f"[fetch_official_catalogs] saved → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

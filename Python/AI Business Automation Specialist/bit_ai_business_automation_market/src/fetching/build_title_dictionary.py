#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
build_title_dictionary.py

1. Читает:
   - at_berufe_manual.csv
   - ch_berufe_manual.csv
   - de_berufe_manual.csv

2. Приводит к единой структуре:
   columns = ['country', 'source', 'official_title', 'kldb_code', 'notes']

3. Нормализует строки (обрезает пробелы, схлопывает множественные пробелы).

4. Удаляет дубликаты.

5. Сохраняет единый справочник:
   - title_dictionary_de_at_ch.csv

6. (Опционально) загружает в таблицу catalog_official_berufe.
"""

import pandas as pd
from sqlalchemy import create_engine

# DB_URL = "mysql+mysqlconnector://user:password@localhost:3306/your_db"
# DB_URL = "postgresql+psycopg2://user:password@localhost:5432/your_db"
DB_URL = "mysql+mysqlconnector://user:password@localhost:3306/your_db"

AT_FILE = "at_berufe_manual.csv"
CH_FILE = "ch_berufe_manual.csv"
DE_FILE = "de_berufe_manual.csv"
OUTPUT_FILE = "title_dictionary_de_at_ch.csv"


def load_and_normalize(path: str, expected_country: str | None = None) -> pd.DataFrame:
    """Загружает CSV и приводит к базовому виду.

    - delimiter=';'
    - нормализует названия колонок (lower + strip)
    - добавляет kldb_code, если нет
    - нормализует строки (strip + схлопывание пробелов)
    """

    df = pd.read_csv(path, sep=";", quotechar='"', dtype=str)

    df.columns = [c.strip().lower() for c in df.columns]

    # country, source, official_title, notes

    base_cols = ["country", "source", "official_title", "notes"]
    for col in base_cols:
        if col not in df.columns:
            raise ValueError(f"{path}: column '{col}' not found in header {df.columns}")

    if "kldb_code" not in df.columns:
        df["kldb_code"] = ""

    if expected_country is not None:
        df["country"] = expected_country

    df = df[["country", "source", "official_title", "kldb_code", "notes"]]

    str_cols = ["country", "source", "official_title", "kldb_code", "notes"]
    for col in str_cols:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)  # схлопываем повторяющиеся пробелы
        )

    df["country"] = df["country"].str.upper()

    df["source"] = df["source"].str.strip()

    return df


def build_title_dictionary() -> pd.DataFrame:
    """Собирает единый справочник DE/AT/CH."""

    df_at = load_and_normalize(AT_FILE, expected_country="AT")
    df_ch = load_and_normalize(CH_FILE, expected_country="CH")
    df_de = load_and_normalize(DE_FILE, expected_country="DE")

    df_all = pd.concat([df_at, df_ch, df_de], ignore_index=True)

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

    df_all_unique = df_all.drop_duplicates(
        subset=["country", "source", "official_title_norm", "kldb_code", "notes_norm"],
        keep="first",
    ).copy()

    df_all_unique = df_all_unique[
        ["country", "source", "official_title", "kldb_code", "notes"]
    ]

    df_all_unique = df_all_unique.sort_values(
        by=["country", "official_title", "source", "kldb_code"],
        ignore_index=True,
    )

    return df_all_unique


def save_to_csv(df: pd.DataFrame, path: str) -> None:
    """Сохраняем словарь в CSV (под твой формат: ; как разделитель)."""
    df.to_csv(path, sep=";", index=False)


def load_into_db(df: pd.DataFrame) -> None:
    """Заливает словарь в catalog_official_berufe.

    ВАЖНО: предполагается, что таблица уже создана.
    Рекомендуется заранее очистить/перезаписать записи нужных источников,
    либо настроить UNIQUE-ограничения в самой БД.
    """

    engine = create_engine(DB_URL)

    with engine.begin() as conn:
        conn.execute(
            """
            DELETE FROM catalog_official_berufe
            WHERE source IN ('AMS', 'BVZ', 'KldB')
            """
        )

    df.to_sql(
        name="catalog_official_berufe",
        con=engine,
        if_exists="append",  # таблица уже существует
        index=False,
        method="multi",
        chunksize=1000,
    )


def main():
    df = build_title_dictionary()
    print(f"Unified rows: {len(df)}")

    save_to_csv(df, OUTPUT_FILE)
    print(f"Saved unified dictionary to: {OUTPUT_FILE}")

    # load_into_db(df)
    # print("Loaded data into catalog_official_berufe")


if __name__ == "__main__":
    main()

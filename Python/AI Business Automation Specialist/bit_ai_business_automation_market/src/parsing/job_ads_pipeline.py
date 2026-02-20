#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
job_ads_pipeline.py

Pipeline для обработки сырых вакансий:

1) Читает данные из CSV / Parquet / JSON.
   Ожидаемые минимальные колонки:
      - id (или job_id)         [опционально]
      - country                  [DE / AT / CH]
      - raw_title                [строка, исходный тайтл]
      - description              [полное описание вакансии]
      - source                   [опционально: job board / system]

2) Нормализует тайтл -> title_normalized (cluster id)
   - использует src.classification.title_normalizer.normalize_title

3) Извлекает скиллы -> столбцы skill_*
   - использует src.classification.skill_extractor.extract_skills

4) Сохраняет результат в data/processed/job_ads_labeled.parquet
   (или путь, заданный аргументом --output).

Использование:
    python -m src.parsing.job_ads_pipeline --input data/raw/job_ads/de/sample.csv

"""

import argparse
import json
from pathlib import Path
from typing import Optional

import pandas as pd

from ..config import RAW_DIR, PROCESSED_DIR
from ..classification.title_normalizer import normalize_title
from ..classification.skill_extractor import extract_skills


def detect_format(path: Path) -> str:
    """
    Определение формата по расширению файла.
    """
    suffix = path.suffix.lower()
    if suffix in [".csv"]:
        return "csv"
    if suffix in [".parquet", ".pq"]:
        return "parquet"
    if suffix in [".json"]:
        return "json"
    raise ValueError(f"Unsupported file extension: {suffix}")


def load_job_ads(input_path: Path, fmt: Optional[str] = None) -> pd.DataFrame:
    """
    Загрузка сырых вакансий в DataFrame.
    """
    if fmt is None:
        fmt = detect_format(input_path)

    if fmt == "csv":
        df = pd.read_csv(input_path)
    elif fmt == "parquet":
        df = pd.read_parquet(input_path)
    elif fmt == "json":
        df = pd.read_json(input_path, orient="records", lines=False)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    return df


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Приводим DataFrame к ожидаемым колонкам:
    - country
    - raw_title
    - description
    - source
    - job_id (если возможно)
    """

    if "country" not in df.columns:
        df["country"] = pd.NA

    if "raw_title" not in df.columns:
        candidates = ["title", "job_title", "position"]
        found = None
        for c in candidates:
            if c in df.columns:
                found = c
                break
        if found is None:
            raise ValueError("No 'raw_title' or equivalent (title/job_title/position) column found.")
        df = df.rename(columns={found: "raw_title"})

    if "description" not in df.columns:
        candidates = ["job_description", "desc", "body", "content"]
        found = None
        for c in candidates:
            if c in df.columns:
                found = c
                break
        if found is None:
            raise ValueError("No 'description' or equivalent column found.")
        df = df.rename(columns={found: "description"})

    if "source" not in df.columns:
        df["source"] = pd.NA

    if "job_id" not in df.columns:
        candidates = ["id", "jobid", "job_id"]
        found = None
        for c in candidates:
            if c in df.columns:
                found = c
                break
        if found is not None and found != "job_id":
            df = df.rename(columns={found: "job_id"})
        elif found is None:
            df["job_id"] = range(1, len(df) + 1)

    return df


def apply_title_normalization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Применяем normalize_title к колонке raw_title.
    """
    df["title_normalized"] = df["raw_title"].astype(str).apply(normalize_title)
    return df


def apply_skill_extraction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Применяем extract_skills к тексту (title + description).
    """
    texts = (df["raw_title"].fillna("").astype(str) + " " +
             df["description"].fillna("").astype(str))

    skill_dicts = [extract_skills(t) for t in texts]

    skills_df = pd.DataFrame(skill_dicts)
    if not skills_df.empty:
        for col in skills_df.columns:
            df[col] = skills_df[col].astype("Int64")

    return df


def process_job_ads(input_path: Path,
                    output_path: Optional[Path] = None,
                    input_format: Optional[str] = None) -> Path:
    """
    Полный пайплайн:
      - загрузка
      - нормализация колонок
      - нормализация тайтлов
      - извлечение скиллов
      - сохранение Parquet
    """
    print(f"[INFO] Loading raw job ads from: {input_path}")
    df = load_job_ads(input_path, fmt=input_format)
    print(f"[INFO] Loaded {len(df)} rows.")

    df = ensure_columns(df)
    print("[INFO] Columns after ensure_columns:", list(df.columns))

    df = apply_title_normalization(df)
    print("[INFO] Applied title normalization.")

    df = apply_skill_extraction(df)
    print("[INFO] Applied skill extraction.")

    if output_path is None:
        output_path = PROCESSED_DIR / "job_ads_labeled.parquet"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"[INFO] Saved processed job ads to: {output_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline zur Verarbeitung von Rohdaten zu Stellenanzeigen (AI Business Automation Cluster)."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Pfad zur Eingabedatei (CSV / Parquet / JSON)."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Pfad zur Ausgabedatei (Parquet). Optional. Default: data/processed/job_ads_labeled.parquet"
    )
    parser.add_argument(
        "--format",
        type=str,
        default=None,
        choices=["csv", "parquet", "json"],
        help="Inputformat (csv/parquet/json). Wird ansonsten aus der Dateiendung abgeleitet."
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = Path(args.output) if args.output else None

    process_job_ads(
        input_path=input_path,
        output_path=output_path,
        input_format=args.format,
    )


if __name__ == "__main__":
    main()

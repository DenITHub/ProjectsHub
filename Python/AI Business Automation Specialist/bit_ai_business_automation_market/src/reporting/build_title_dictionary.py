# src/reporting/build_title_dictionary.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict

import pandas as pd

from src.config import DATA_DIR

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def base_titles_manual() -> List[Dict]:
    """
    Базовые, вручную отобранные названия (те, что у нас уже были) –
    сюда можно скопировать твой текущий список 65 позиций.
    Для примера оставляю несколько, остальное можно вставить из старого CSV.
    """
    rows = [
        {"title": "AI Business Automation Specialist", "country": "DE;AT;CH", "category": "direct", "recommended_for_search": True},
        {"title": "AI Automation Specialist", "country": "DE;AT;CH", "category": "direct", "recommended_for_search": True},
        {"title": "AI & Automation Consultant", "country": "DE;AT;CH", "category": "direct", "recommended_for_search": True},
        {"title": "KI-Automation Specialist", "country": "DE;AT;CH", "category": "direct", "recommended_for_search": True},
        {"title": "AI Workflow Automation Specialist", "country": "DE;AT;CH", "category": "direct", "recommended_for_search": True},
        # --- business / process ---
        {"title": "Business Process Automation Specialist", "country": "DE;AT;CH", "category": "process", "recommended_for_search": True},
        {"title": "Spezialist:in für Geschäftsprozessautomatisierung", "country": "DE", "category": "process", "recommended_for_search": True},
        {"title": "Workflow Automation Engineer", "country": "DE;AT;CH", "category": "process", "recommended_for_search": True},
        {"title": "Prozessmanager Digitalisierung & Automatisierung", "country": "DE", "category": "process", "recommended_for_search": True},
        # --- CRM/Marketing ---
        {"title": "CRM Automation Specialist", "country": "DE;AT;CH", "category": "crm", "recommended_for_search": True},
        {"title": "Marketing Automation Specialist (mit AI-Fokus)", "country": "DE;AT;CH", "category": "crm", "recommended_for_search": True},
        {"title": "Growth & Automation Specialist", "country": "DE;AT;CH", "category": "crm", "recommended_for_search": False},
        {"title": "Business Analyst (Digitalisierung & Automatisierung)", "country": "DE;AT;CH", "category": "adjacent", "recommended_for_search": True},
        {"title": "Digital Business Analyst", "country": "DE;AT;CH", "category": "adjacent", "recommended_for_search": True},
        {"title": "Business-Intelligence-Consultant", "country": "DE;AT;CH", "category": "adjacent", "recommended_for_search": True},
    ]
    return rows


def combinatorial_titles() -> List[Dict]:
    """
    Генерация дополнительных комбинаций:  AI/KI + Automation/Process/Workflow + Specialist/Consultant/Manager.
    """
    prefixes = ["AI", "KI", "Digital", "Business", "Process"]
    middles = ["Automation", "Process Automation", "Workflow Automation", "Business Automation"]
    suffixes = ["Specialist", "Consultant", "Manager", "Engineer", "Expert"]

    rows: List[Dict] = []

    for p in prefixes:
        for m in middles:
            for s in suffixes:
                title = f"{p} {m} {s}"
                rows.append(
                    {
                        "title": title,
                        "country": "DE;AT;CH",
                        "category": "generated",
                        "recommended_for_search": (
                            "Automation" in m and s in {"Specialist", "Consultant", "Manager"}
                        ),
                    }
                )
    return rows


def deduplicate_rows(rows: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["title_norm"] = df["title"].str.strip().str.lower()
    df = (
        df.sort_values(["title_norm", "category"])
        .drop_duplicates(subset=["title_norm"], keep="first")
        .drop(columns=["title_norm"])
        .reset_index(drop=True)
    )
    return df


def main():
    rows = []
    rows.extend(base_titles_manual())
    rows.extend(combinatorial_titles())

    df = deduplicate_rows(rows)

    out_path = DATA_DIR / "reference" / "title_dictionary_de_at_ch.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    logger.info(f"[OK] title_dictionary_de_at_ch.csv сгенерирован: {out_path} ({len(df)} строк)")


if __name__ == "__main__":
    main()

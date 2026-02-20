#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
market_titles_build.py

Формирует список рыночных названий профессий, связанных с
"AI Business Automation Specialist".

1. Базовый список — добавляем вручную (или генерируем автоматически позже).
2. Чистим, нормализуем.
3. Удаляем дубли.
4. Сохраняем в CSV.
"""

import pandas as pd


OUTPUT = "market_titles_ai_business_automation.csv"

BASE_TITLES = [
    "AI Business Automation Specialist",
    "AI Automation Specialist",
    "AI Automation Engineer",
    "AI Process Automation Specialist",
    "Workflow Automation Specialist",
    "Business Process Automation Specialist",
    "Automation Specialist",
    "Automation Engineer",
    "Digital Process Automation Consultant",
    "Process Automation Consultant",
    "Process Automation Analyst",
    "AI Operations Specialist",
    "AI Integration Specialist",
    "Intelligent Process Automation Specialist",
    "IPA Specialist",
    "RPA Developer",
    "RPA Consultant",
    "RPA Engineer",
    "Conversational AI Specialist",
    "Chatbot Automation Specialist",
    "Prompt Engineer (Automation Track)",
    "Automation Architect",
    "Business Automation Analyst",
    "Automation Product Owner",
    "Automation Manager",
]

def build_market_titles():
    df = pd.DataFrame({"market_title": BASE_TITLES})

    df["market_title"] = (
        df["market_title"]
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    df = df.drop_duplicates().sort_values("market_title").reset_index(drop=True)

    df.to_csv(OUTPUT, sep=";", index=False)
    print(f"Saved market titles → {OUTPUT}")
    return df


if __name__ == "__main__":
    build_market_titles()

from pathlib import Path
from typing import List

import pandas as pd
import matplotlib.pyplot as plt

from ..reporting.summary_tables import (
    summarize_by_title,
    summarize_by_country_and_title,
    build_skill_matrix,
)


def plot_top_titles(df: pd.DataFrame,
                    title_col: str = "title_normalized",
                    top_n: int = 15,
                    out_path: Path = None) -> Path:
    top_titles = (
        df[title_col]
        .value_counts()
        .head(top_n)
        .sort_values(ascending=True)
    )

    plt.figure(figsize=(8, 6))
    top_titles.plot(kind="barh")
    plt.xlabel("Anzahl der Stellenanzeigen")
    plt.ylabel("Titel (normalisiert)")
    plt.title("Top Jobtitel im Cluster AI Business Automation (DE/AT/CH)")
    plt.tight_layout()

    if out_path is None:
        out_path = Path("docs/top_titles.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_skill_heatmap(df: pd.DataFrame,
                       title_col: str = "title_normalized",
                       skill_cols: List[str] = None,
                       top_titles: List[str] = None,
                       out_path: Path = None) -> Path:
    matrix = build_skill_matrix(df, title_col=title_col, skill_cols=skill_cols)

    if top_titles is not None:
        matrix = matrix.loc[[t for t in top_titles if t in matrix.index]]

    plt.figure(figsize=(10, 6))
    plt.imshow(matrix.values, aspect="auto")
    plt.colorbar(label="Anteil der Stellenanzeigen mit Skill")
    plt.xticks(range(len(matrix.columns)),
               [c.replace("skill_", "") for c in matrix.columns],
               rotation=45, ha="right")
    plt.yticks(range(len(matrix.index)), matrix.index)
    plt.title("Skill-Profil pro Jobtitel (Durchschnittliche Häufigkeit)")
    plt.tight_layout()

    if out_path is None:
        out_path = Path("docs/skill_heatmap.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def generate_markdown_report(df: pd.DataFrame,
                             output_md: Path = Path("docs/03_market_analysis_de_at_ch.md")) -> Path:
    """
    Генерирует простой Markdown-отчет:
    - таблица топ-титулов
    - таблица по странам
    - вставка картинок с графиками.
    """
    output_md.parent.mkdir(parents=True, exist_ok=True)

    top_titles_df = summarize_by_title(df)
    country_title_df = summarize_by_country_and_title(df)

    top_titles_plot = plot_top_titles(df)
    skill_heatmap_plot = plot_skill_heatmap(df)

    lines = []
    lines.append("# Marktanalyse AI Business Automation Specialist (DE/AT/CH)")
    lines.append("")
    lines.append("## Top Jobtitel (normalisiert)")
    lines.append("")
    lines.append(top_titles_df.to_markdown(index=False))
    lines.append("")
    lines.append(f"![Top Titel]({top_titles_plot.as_posix()})")
    lines.append("")
    lines.append("## Verteilung nach Ländern und Titeln")
    lines.append("")
    lines.append(country_title_df.to_markdown(index=False))
    lines.append("")
    lines.append(f"![Skill-Heatmap]({skill_heatmap_plot.as_posix()})")

    output_md.write_text("\n".join(lines), encoding="utf-8")
    return output_md

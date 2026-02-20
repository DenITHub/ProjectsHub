from __future__ import annotations

from pathlib import Path
import logging
import json
from typing import Dict, Any, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.classification.role_matcher import get_embedding, cosine_sim
from src.config import DATA_DIR

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]      # .../bit_ai_business_automation_market
DOCS_DIR = ROOT_DIR / "docs"                        # все .md
IMG_DIR = DOCS_DIR / "img"                          # все картинки

DOCS_DIR.mkdir(exist_ok=True)
IMG_DIR.mkdir(exist_ok=True)

ROLE_PROFILE_MD = DOCS_DIR / "01_role_profile.md"
REPORT_MD = DOCS_DIR / "05_similarity_official_berufe.md"
CATALOG_SCORED_CSV = DATA_DIR / "processed" / "catalog_official_berufe_scored.csv"


def _fallback_role_text() -> str:
    return (
        "AI Business Automation Specialist ist eine hybride Rolle zwischen "
        "Business-Analyse, Prozessmanagement, Integrationen und KI-gestützter "
        "Workflow-Automatisierung. Ziel: operative Kosten senken, Prozesse "
        "standardisieren und automatisierte Workflows zwischen CRM, ERP, "
        "Helpdesk und Marketing-Tools aufbauen."
    )


def load_role_profile_vector() -> np.ndarray:
    """
    1) Пробуем взять подробный профиль из JSON.
    2) Если что-то не так → берём текстовый fallback.
    Всегда возвращаем НЕ пустой вектор.
    """
    text = ""

    json_path = DATA_DIR / "reference" / "role_profile_ai_business_automation.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
            text = (
                profile.get("role_name", "")
                + "\n"
                + profile.get("summary", "")
                + "\n"
                + "\n".join(profile.get("core_tasks", []))
            )
        except Exception as e:
            logger.warning(f"[WARN] Konnte JSON-Profil nicht lesen ({json_path}): {e}")

    if not text.strip():
        logger.warning("[WARN] Rollenprofil aus JSON leer – benutze Fallback-Text.")
        text = _fallback_role_text()

    emb = get_embedding(text)
    vec = np.array(emb, dtype=float)

    norm = np.linalg.norm(vec)
    logger.info(f"[DEBUG] role_vec norm = {norm:.6f}")

    if norm == 0.0:
        logger.error("[ERROR] role_vec ist Nullvektor – Embeddings liefern 0. "
                     "Bitte API-Key / get_embedding prüfen.")
    return vec


def load_official_catalog() -> pd.DataFrame:
    path = DATA_DIR / "processed" / "catalog_official_berufe.csv"

    df = pd.read_csv(
        path,
        sep=";",          # наш реальный разделитель
        dtype=str,
        engine="python",
        on_bad_lines="warn",
    )

    df = df.fillna("")
    for col in ["country", "source", "official_title", "kldb_code", "notes"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )
        else:
            df[col] = ""

    return df


# ----- Mapping offizieller Beruf → BIT-Rolle -----
def load_bit_mapping() -> pd.DataFrame:
    path = DATA_DIR / "reference" / "official_berufe_bit_mapping.csv"
    if not path.exists():
        logger.warning(f"[WARN] Mapping-Datei nicht gefunden: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path, sep=";", dtype=str).fillna("")

    for col in [
        "country",
        "source",
        "official_title",
        "official_title_en",
        "bit_role_level",
        "bit_role_label",
        "comment",
    ]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )
    return df


# ----- Similarity-Berechnung -----
def compute_similarity(df: pd.DataFrame, role_vec: np.ndarray) -> pd.DataFrame:
    """
    Считаем похожесть official_berufe на профиль роли.
    Используем official_title + notes.
    """
    if "official_title" not in df.columns:
        raise ValueError(
            f"DataFrame does not contain 'official_title' column. Columns: {df.columns}"
        )

    title_col = "official_title"
    notes_col = "notes" if "notes" in df.columns else None

    if notes_col:
        texts: List[str] = (
            df[title_col].fillna("") + " " + df[notes_col].fillna("")
        ).tolist()
    else:
        texts = df[title_col].fillna("").tolist()

    emb_list = [get_embedding(t) for t in texts]
    emb_arr = np.vstack(emb_list).astype(float)

    norms = np.linalg.norm(emb_arr, axis=1)
    logger.info(
        "[DEBUG] embeddings norms: min=%.6f max=%.6f",
        float(norms.min()),
        float(norms.max()),
    )

    sims = [cosine_sim(role_vec, v) for v in emb_arr]
    df_out = df.copy()
    df_out["similarity"] = sims

    logger.info(
        "[DEBUG] similarity stats: min=%.6f max=%.6f",
        float(df_out["similarity"].min()),
        float(df_out["similarity"].max()),
    )
    return df_out


def plot_top10_by_country(df: pd.DataFrame, country: str, output_path: Path) -> None:
    subset = (
        df[df["country"] == country]
        .sort_values("similarity", ascending=False)
        .head(10)
    )

    if subset.empty:
        logger.warning(f"[WARN] Keine Daten für {country}, Plot wird übersprungen.")
        return

    x = subset["similarity"]
    y = subset["official_title"]

    plt.figure(figsize=(10, 6))
    plt.barh(y, x)
    plt.gca().invert_yaxis()
    plt.xlabel("Similarity")
    plt.title(f"Top-10 offizieller Berufe – {country}")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    logger.info(f"[INFO] Saved plot for {country} → {output_path}")

def plot_top10_global(df: pd.DataFrame, output_path: Path) -> None:
    """
    Глобальный Top-10 список официальных профессий по similarity к роли
    (без разделения по странам).
    """

    if "official_title" not in df.columns or "similarity" not in df.columns:
        logger.warning("[WARN] Für globalen Top-10-Plot fehlen Spalten.")
        return

    subset = (
        df.groupby("official_title", as_index=False)["similarity"]
        .max()
        .sort_values("similarity", ascending=False)
        .head(10)
    )

    if subset.empty:
        logger.warning("[WARN] Globaler Top-10-Plot: keine Daten.")
        return

    x = subset["similarity"]
    y = subset["official_title"]

    plt.figure(figsize=(10, 6))
    plt.barh(y, x)
    plt.gca().invert_yaxis()
    plt.xlabel("Cosine Similarity Score")
    plt.title("Top 10 offizielle Berufe – Nähe zur Rolle AI Business Automation Specialist")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    logger.info(f"[INFO] Saved global top-10 plot → {output_path}")


def plot_heatmap(df: pd.DataFrame, output_path: Path) -> None:
    """
    Улучшенная тепловая карта:

    - Для каждой страны (DE/AT/CH) берём свои топ-10 профессий по similarity.
    - Рисуем 3 независимые панели: у каждой свой список профессий по оси Y.
    - Цветовая гамма по странам: DE -> Blues, AT -> Reds, CH -> Greens.
    - Общий colorbar справа показывает шкалу Cosine Similarity.
    - В каждой ячейке подписано числовое значение (0.xx).
    """

    countries = ["DE", "AT", "CH"]
    cmaps = {"DE": "Blues", "AT": "Reds", "CH": "Greens"}
    title_map = {"DE": "Deutschland", "AT": "Österreich", "CH": "Schweiz"}

    per_country = {}
    for c in countries:
        sub = (
            df[df["country"] == c]
            .sort_values("similarity", ascending=False)
            .head(10)[["official_title", "similarity"]]
            .copy()
        )
        per_country[c] = sub

    if all(len(sub) == 0 for sub in per_country.values()):
        logger.warning("[WARN] Keine Daten für Heatmap, alle Subsets leer.")
        return

    vals = []
    for sub in per_country.values():
        if len(sub):
            vals.extend(sub["similarity"].tolist())

    vmin = float(min(vals))
    vmax = float(max(vals))

    max_rows = max(len(sub) for sub in per_country.values())
    fig_height = max(4, 0.5 * max_rows)

    fig, axes = plt.subplots(
        1, len(countries),
        figsize=(12, fig_height),
        sharex=False,
        sharey=False,
    )

    if len(countries) == 1:
        axes = [axes]

    last_im = None

    for ax, country in zip(axes, countries):
        sub = per_country[country]
        if sub.empty:
            ax.axis("off")
            continue

        data = sub["similarity"].values.reshape(-1, 1)  # (n, 1)

        im = ax.imshow(
            data,
            aspect="auto",
            cmap=cmaps.get(country, "viridis"),
            vmin=vmin,
            vmax=vmax,
        )
        last_im = im

        ax.set_xticks([0])
        ax.set_xticklabels([country], fontsize=11)

        ax.set_yticks(np.arange(len(sub)))
        ax.set_yticklabels(sub["official_title"], fontsize=7)
        if country == "DE":
            ax.set_ylabel("Official Title")

        ax.set_title(title_map.get(country, country))

        mid_val = (vmin + vmax) / 2.0
        for i, val in enumerate(sub["similarity"]):
            val = float(val)
            text_color = "white" if val >= mid_val else "black"
            ax.text(
                0,
                i,
                f"{val:.2f}",
                ha="center",
                va="center",
                fontsize=6,
                color=text_color,
            )

    fig.suptitle(
    "Similarity Heatmap – offizielle Berufe (Top-10 DE/AT/CH)",
    fontsize=14,
)

    fig.subplots_adjust(left=0.15, right=0.88, top=0.88, bottom=0.10)

    if last_im is not None:
      # [left, bottom, width, height]
      cbar_ax = fig.add_axes([0.90, 0.12, 0.025, 0.70])
      cbar = fig.colorbar(last_im, cax=cbar_ax)
      cbar.set_label("Cosine Similarity", rotation=270, labelpad=10)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=[0.0, 0.0, 0.88, 0.88])
    plt.savefig(output_path, dpi=200)
    plt.close(fig)

    logger.info(f"[INFO] Saved heatmap → {output_path}")


def generate_similarity_report() -> str:
    role_vec = load_role_profile_vector()
    df = load_official_catalog()
    df_sim = compute_similarity(df, role_vec)

    # CSV
    CATALOG_SCORED_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_sim.to_csv(CATALOG_SCORED_CSV, index=False)
    logger.info(f"[OK] catalog_official_berufe_scored.csv gespeichert: {CATALOG_SCORED_CSV}")
    plot_top10_global(
        df_sim,
        IMG_DIR / "top10_official_berufe_similarity.png",
    )

    plot_top10_by_country(df_sim, "DE", IMG_DIR / "top10_official_berufe_de.png")
    plot_top10_by_country(df_sim, "AT", IMG_DIR / "top10_official_berufe_at.png")
    plot_top10_by_country(df_sim, "CH", IMG_DIR / "top10_official_berufe_ch.png")
    plot_heatmap(df_sim, IMG_DIR / "heatmap_official_berufe_de_at_ch.png")

    # Markdown
    lines: List[str] = []
    lines.append("# Top-10 offizielle Berufe – Nähe zur Rolle AI Business Automation Specialist\n")
    lines.append("![Top-10 offizielle Berufe](img/top10_official_berufe_similarity.png)\n")

    labels = [("DE", "Deutschland"), ("AT", "Österreich"), ("CH", "Schweiz")]
    for country, label in labels:
        top = df_sim[df_sim["country"] == country].nlargest(10, "similarity")
        if top.empty:
            continue

        cols = ["official_title", "source", "kldb_code", "similarity"]
        existing_cols = [c for c in cols if c in top.columns]
        top_view = top[existing_cols].copy()

        rename_map = {
            "official_title": "Beruf",
            "source": "Quelle",
            "kldb_code": "KldB-Code",
            "similarity": "Similarity",
        }
        top_view = top_view.rename(
            columns={k: v for k, v in rename_map.items() if k in top_view.columns}
        )

        lines.append(f"## {label}\n")
        lines.append(top_view.to_markdown(index=False))
        lines.append("")

    lines.append("## Heatmap\n")
    lines.append("Siehe Abbildung: `docs/img/heatmap_official_berufe_de_at_ch.png`.\n")

    # --- Mapping: offizielle Berufe → BIT Role Level ---
    mapping_df = load_bit_mapping()
    lines.append("## Mapping: Offizielle Berufe → BIT Role Level\n")

    if mapping_df.empty:
        lines.append(
            "_Mapping-Tabelle ist noch nicht gepflegt. "
            "Sobald `official_berufe_bit_mapping.csv` ausgefüllt ist, wird sie hier angezeigt._\n"
        )
    else:
        key_cols = ["country", "source", "official_title"]
        missing = [c for c in key_cols if c not in mapping_df.columns]

        if missing:
            logger.warning(
                "[WARN] Mapping-CSV ohne erwartete Spalten %s. Spalten im Mapping: %s",
                missing,
                list(mapping_df.columns),
            )
            lines.append(
                "_Hinweis: Mapping-Datei `official_berufe_bit_mapping.csv` ist noch nicht "
                "korrekt formatiert – Merge übersprungen._\n"
            )
        else:
            merged = df_sim.merge(
                mapping_df,
                on=["country", "source", "official_title"],
                how="inner",
                suffixes=("", "_map"),
            )

            merged = merged[merged["bit_role_level"].str.len() > 0].copy()

            if merged.empty:
                lines.append(
                    "_Mapping-Datei gefunden, aber keine Übereinstimmung mit dem aktuellen Katalog._\n"
                )
            else:
                cols = [
                    "country",
                    "official_title",
                    "official_title_en",
                    "bit_role_level",
                    "bit_role_label",
                    "similarity",
                    "comment",
                ]
                existing_cols = [c for c in cols if c in merged.columns]

                table = (
                    merged[existing_cols]
                    .sort_values(["bit_role_level", "similarity"], ascending=[True, False])
                )
                lines.append(table.to_markdown(index=False))
                lines.append("")

    market_block = DOCS_DIR / "market_titles_mapping.md"
    if market_block.exists():
        lines.append("\n## Market-Titles (DE/EN) – Zuordnung zu Top-Berufen\n")
        lines.append(market_block.read_text(encoding="utf-8"))

    md = "\n".join(lines)
    REPORT_MD.write_text(md, encoding="utf-8")
    logger.info(f"[OK] Markdown-Report aktualisiert: {REPORT_MD}")

    return md


def main() -> None:
    generate_similarity_report()


if __name__ == "__main__":
    main()

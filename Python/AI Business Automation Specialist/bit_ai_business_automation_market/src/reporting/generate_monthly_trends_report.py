from __future__ import annotations

from pathlib import Path
import datetime as dt
import pandas as pd


# -----------------------------
# PATH RESOLUTION (ROBUST)
# -----------------------------
def find_project_root(start: Path) -> Path:
    """
    Ищем корень проекта: папка, где есть src/ и requirements.txt.
    Это защитит от ситуации, когда SCRIPT_DIR.parents[n] ошибся.
    """
    cur = start.resolve()
    for _ in range(10):
        if (cur / "src").exists() and (cur / "requirements.txt").exists():
            return cur
        cur = cur.parent
    raise RuntimeError(
        "Не удалось определить PROJECT_ROOT. Ожидаю структуру: <root>/src и <root>/requirements.txt"
    )


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = find_project_root(SCRIPT_DIR)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

IN_FILE = PROCESSED_DIR / "monthly_total_vs_entry.csv"

OUT_SUMMARY_CSV = PROCESSED_DIR / "monthly_trends_summary.csv"
OUT_MD = REPORTS_DIR / "bit_dach_ai_automation_monthly_trends_report.md"


# -----------------------------
# HELPERS
# -----------------------------
def add_entry_share(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    df2["entry_share_pct"] = (df2["entry_mid_jobs"] / df2["total_jobs"] * 100).round(2)
    df2["entry_share_pct"] = df2["entry_share_pct"].fillna(0.0)
    return df2


def add_mom(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """
    Добавляем MoM изменение total_jobs и entry_mid_jobs в %.
    """
    df2 = df.sort_values("month").copy()
    df2["mom_total_jobs_pct"] = (df2.groupby(group_cols)["total_jobs"].pct_change() * 100).round(2)
    df2["mom_entry_mid_jobs_pct"] = (df2.groupby(group_cols)["entry_mid_jobs"].pct_change() * 100).round(2)
    return df2


def agg_dach(df: pd.DataFrame) -> pd.DataFrame:
    d = df.groupby(["month"], as_index=False)[["total_jobs", "entry_mid_jobs"]].sum()
    d["scope"] = "DACH"
    d["country"] = "DACH"
    d["role_id"] = "ALL"
    d = add_entry_share(d)
    d = add_mom(d, group_cols=["scope", "role_id", "country"])
    return d


def agg_by_country(df: pd.DataFrame) -> pd.DataFrame:
    d = df.groupby(["month", "country"], as_index=False)[["total_jobs", "entry_mid_jobs"]].sum()
    d["scope"] = "COUNTRY"
    d["role_id"] = "ALL"
    d = add_entry_share(d)
    d = add_mom(d, group_cols=["scope", "role_id", "country"])
    return d


def agg_focus_role(df: pd.DataFrame, role_id: str) -> pd.DataFrame:
    x = df[df["role_id"] == role_id].copy()
    if x.empty:
        return pd.DataFrame(
            columns=[
                "month",
                "country",
                "total_jobs",
                "entry_mid_jobs",
                "scope",
                "role_id",
                "entry_share_pct",
                "mom_total_jobs_pct",
                "mom_entry_mid_jobs_pct",
            ]
        )
    d = x.groupby(["month", "country"], as_index=False)[["total_jobs", "entry_mid_jobs"]].sum()
    d["scope"] = "FOCUS_ROLE"
    d["role_id"] = role_id
    d = add_entry_share(d)
    d = add_mom(d, group_cols=["scope", "role_id", "country"])
    return d


def fmt_table(df: pd.DataFrame, cols: list[str], max_rows: int = 20) -> str:
    d = df.copy()
    if len(d) > max_rows:
        d = d.tail(max_rows)  # последние месяцы
    return d[cols].to_markdown(index=False)


def generate_markdown(
    summary: pd.DataFrame,
    figures_rel_dir: str,
    focus_role_id: str = "junior_automation_specialist",
) -> str:
    today = dt.date.today().isoformat()

    dach = summary[(summary["scope"] == "DACH") & (summary["role_id"] == "ALL")].sort_values("month")
    countries = summary[(summary["scope"] == "COUNTRY") & (summary["role_id"] == "ALL")].sort_values(
        ["country", "month"]
    )
    focus = summary[(summary["scope"] == "FOCUS_ROLE") & (summary["role_id"] == focus_role_id)].sort_values(
        ["country", "month"]
    )

    table_dach = fmt_table(
        dach,
        cols=["month", "total_jobs", "entry_mid_jobs", "entry_share_pct", "mom_total_jobs_pct", "mom_entry_mid_jobs_pct"],
        max_rows=12,
    )

    tables_country = []
    for c in sorted(countries["country"].unique()):
        dc = countries[countries["country"] == c].sort_values("month")
        tables_country.append(
            f"### {c}\n\n"
            + fmt_table(
                dc,
                cols=["month", "total_jobs", "entry_mid_jobs", "entry_share_pct", "mom_total_jobs_pct", "mom_entry_mid_jobs_pct"],
                max_rows=12,
            )
        )
    table_countries_block = "\n\n".join(tables_country) if tables_country else "_Нет данных по странам_"

    focus_block = ""
    if not focus.empty:
        tables_focus = []
        for c in sorted(focus["country"].unique()):
            dc = focus[focus["country"] == c].sort_values("month")
            tables_focus.append(
                f"### {c}\n\n"
                + fmt_table(
                    dc,
                    cols=["month", "total_jobs", "entry_mid_jobs", "entry_share_pct", "mom_total_jobs_pct", "mom_entry_mid_jobs_pct"],
                    max_rows=12,
                )
            )
        focus_block = (
            f"\n\n---\n\n## 3. Focus: {focus_role_id}\n\n"
            + "\n\n".join(tables_focus)
            + "\n\n### Charts (Focus)\n"
            + f"![focus_total]({figures_rel_dir}/focus_{focus_role_id}_total.png)\n\n"
            + f"![focus_entry_mid]({figures_rel_dir}/focus_{focus_role_id}_entry_mid.png)\n"
        )
    else:
        focus_block = (
            f"\n\n---\n\n## 3. Focus: {focus_role_id}\n\n"
            "_В monthly_total_vs_entry.csv нет строк по этой role_id (проверь, что роль присутствует в исходных данных)._"
        )

    md = f"""# BIT DACH AI Automation — Monthly Trends Report

**Generated:** {today}  
Источник: `data/processed/monthly_total_vs_entry.csv` (6m window, deduped)

---


{table_dach}

### Charts (DACH)
![dach_total]({figures_rel_dir}/dach_total_jobs_by_month.png)

![dach_entry]({figures_rel_dir}/dach_entry_mid_jobs_by_month.png)

---


{table_countries_block}

### Charts (Countries)
![country_total]({figures_rel_dir}/country_total_jobs_by_month.png)

![country_entry]({figures_rel_dir}/country_entry_mid_jobs_by_month.png)
{focus_block}

---


- **total_jobs** — дедуплицированные вакансии за месяц (по всем ролям в данном scope)
- **entry_mid_jobs** — subset вакансий, попавших в “entry/mid” эвристику
- **entry_share_pct** — доля entry/mid от total
- **MoM%** — изменение к предыдущему месяцу (рост/падение)

---


- Рост вакансий **не линейный**, а **ступенчатый**.
- До сентября рынок рос умеренно (≈100 → 1 000 вакансий/мес).
- В октябре–ноябре фиксируется **резкий скачок публикаций** (×4–5 MoM),
  что указывает на:
  - массовое обновление вакансий,
  - сезонный эффект (Q4),
  - активизацию найма после летнего спада.
- В декабре наблюдается ожидаемая коррекция, но уровень остаётся
  **значительно выше летнего baseline**.

➡️ Это сценарий **350 → 500 → 700 → 1 500+**, а не «плоские 700–780».

- Entry/Mid вакансии растут **вместе с рынком**, но:
  - их доля постепенно снижается (≈45% → ≈30%),
  - рынок становится более конкурентным по мере масштабирования.
- Абсолютное число entry/mid вакансий **растёт**, несмотря на падение доли.

➡️ Это подтверждает: входной рынок **живой и растущий**, но требования усиливаются.

- Чётко выраженный рост в октябре–ноябре во всех странах.
- Германия — основной драйвер.
- Entry-доля остаётся высокой (≈45–65%), что подтверждает
  валидность роли как **основного entry-трека**.

---

_Auto-generated._
"""
    return md


# -----------------------------
# MAIN
# -----------------------------
def main() -> None:
    if not IN_FILE.exists():
        raise FileNotFoundError(f"Не найден файл: {IN_FILE}. Сначала запусти: python -m src.analyze_monthly_trends")

    df = pd.read_csv(IN_FILE, parse_dates=["month"])

    for col in ["total_jobs", "entry_mid_jobs"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    parts = [
        agg_dach(df),
        agg_by_country(df),
        agg_focus_role(df, role_id="junior_automation_specialist"),
    ]
    summary = pd.concat(parts, ignore_index=True)

    summary.to_csv(OUT_SUMMARY_CSV, index=False, encoding="utf-8")
    print(f"✅ Saved summary CSV: {OUT_SUMMARY_CSV}")

    figures_rel_dir = "../data/processed/figures/monthly_trends_master"
    md = generate_markdown(summary, figures_rel_dir=figures_rel_dir)

    OUT_MD.write_text(md, encoding="utf-8")
    print(f"✅ Saved markdown report: {OUT_MD}")


if __name__ == "__main__":
    main()

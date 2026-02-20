from __future__ import annotations

from pathlib import Path
import datetime
import pandas as pd

# -----------------------------
# PATH CONFIGURATION
# -----------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_FILE = PROCESSED_DIR / "summary_linkedin_market.csv"


# -----------------------------
# HELPERS
# -----------------------------
def add_entry_share(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    # Safe calc even if some values are missing/0
    def _calc(r) -> float:
        total = r.get("total_jobs", 0)
        entry = r.get("entry_mid_jobs", 0)
        if pd.isna(total) or total <= 0 or pd.isna(entry):
            return 0.0
        return round((entry / total) * 100, 2)

    df2["entry_share_pct"] = df2.apply(_calc, axis=1)
    return df2


def _rename_for_pdf(df: pd.DataFrame) -> pd.DataFrame:
    """Make column names shorter for Marp/PDF layout."""
    df2 = df.copy()
    rename_map = {
        "after_date_filter": "after_date",
        "entry_mid_jobs": "entry_mid",
        "entry_share_pct": "entry_share_%",
    }
    return df2.rename(columns=rename_map)


def build_table_counts(df: pd.DataFrame, max_rows: int = 10) -> str:
    """Narrow counts table (PDF-friendly)."""
    cols = ["country", "role_id", "raw_total", "after_date_filter", "total_jobs", "entry_mid_jobs"]
    df2 = df.copy()
    for c in cols:
        if c not in df2.columns:
            df2[c] = None

    df2 = df2[cols]
    df2 = _rename_for_pdf(df2)

    if len(df2) > max_rows:
        df2 = df2.head(max_rows)

    return df2.to_markdown(index=False)


def build_table_share(df: pd.DataFrame, max_rows: int = 10) -> str:
    """Separate compact table with entry share % (PDF-friendly)."""
    df2 = add_entry_share(df)

    cols = ["country", "role_id", "entry_share_pct"]
    for c in cols:
        if c not in df2.columns:
            df2[c] = None

    df2 = df2[cols]
    df2 = _rename_for_pdf(df2)

    if len(df2) > max_rows:
        df2 = df2.head(max_rows)

    return df2.to_markdown(index=False)


def generate_markdown(summary: pd.DataFrame) -> str:
    today = datetime.date.today().isoformat()

    # Overall tables
    table_all_counts = build_table_counts(summary, max_rows=10)
    table_all_share = build_table_share(summary, max_rows=10)

    # Focus role
    df_focus = summary[summary["role_id"] == "junior_automation_specialist"].reset_index(drop=True)
    table_focus_counts = build_table_counts(df_focus, max_rows=10)
    table_focus_share = build_table_share(df_focus, max_rows=10)

    md = f"""---
marp: true
theme: default
paginate: true
style: |
  section {{
    background-color: #FFFFFF;
    color: #000000;
    padding: 38px;
    text-align: left;
    line-height: 1.45;
  }}
  h1, h2, h3 {{
    color: #003366;
    font-weight: 700;
    text-align: center;
    margin-top: 0;
    margin-bottom: 18px;
  }}
  /* Make tables fit in PDF */
  table {{
    font-size: 16px;
  }}
  th, td {{
    padding: 3px 6px;
    vertical-align: top;
  }}
  img {{
    display: block;
    margin: 0 auto;
  }}
---

# BIT DACH AI Automation Market Report
**Generated:** {today}

Период анализа: **последние 6 месяцев (LinkedIn)**  
Метрики: **raw → after_date → dedupe → entry/mid (≤2 years)**

---


- AI Automation Specialist
- Business Transformation Analyst
- Digital Process Analyst
- AI Project Manager

- AI Governance Analyst
- Prompt Engineer

---


{table_all_counts}

---


{table_all_share}

---

# 2. Visualizations — All Roles

## 2.1 Total Jobs
<img src="../data/processed/figures/total_jobs_by_role_country.png" width="55%" />

---

## 2.2 Entry/Mid Jobs
<img src="../data/processed/figures/entry_jobs_by_role_country.png" width="55%" />

---

## 2.3 Entry Share (%)
<img src="../data/processed/figures/entry_share_by_role_country.png" width="55%" />

---

Роль: **Prozessmanager/in – RPA (Junior) / Junior Automation Specialist**

---


{table_focus_counts}

---


{table_focus_share}

---

## 3.3 Visualizations — Junior Automation Specialist

### Total Jobs
<img src="../data/processed/figures/junior_automation_specialist/total_jobs.png" width="55%" />

---

### Entry/Mid Jobs
<img src="../data/processed/figures/junior_automation_specialist/entry_mid_jobs.png" width="55%" />

---

### Entry Share (%)
<img src="../data/processed/figures/junior_automation_specialist/entry_share_pct.png" width="55%" />

---

# 4. Insights

### Germany
- Крупнейший рынок по всем ролям.
- Сильный спрос на automation & project roles.
- Junior доля (entry_share_%): ориентир 3–10% (по данным выборки).

### Austria
- Средний рынок.
- Наиболее стабильный спрос в automation.

### Switzerland
- Меньший по объёму, но зрелый AI-рынок.
- Выше ожидания к навыкам и конкуренция.

---


1. **Закрепить Junior Automation Specialist как основную профессию выхода.**
2. Усилить обучение по:
   - RPA
   - automation workflows
   - process optimization
   - AI-assisted automation
3. Строить карьерные треки под рынок DACH.
4. Добавить проектные кейсы (workflow orchestration + automation cases).

---


- Сводная таблица: `data/processed/summary_linkedin_market.csv`
- Визуализации: `data/processed/figures/`
- Отчёт: `reports/bit_dach_ai_automation_market_report.md`

---
_Auto-generated by BIT Market Analyzer._
"""
    return md


# -----------------------------
# MAIN
# -----------------------------
def main() -> None:
    if not SUMMARY_FILE.exists():
        raise FileNotFoundError(f"Не найден summary файл: {SUMMARY_FILE}")

    df = pd.read_csv(SUMMARY_FILE)

    out_path = REPORTS_DIR / "bit_dach_ai_automation_market_report.md"
    out_path.write_text(generate_markdown(df), encoding="utf-8")

    print("\n✔ FULL MARKET REPORT CREATED:")
    print(out_path)


if __name__ == "__main__":
    main()

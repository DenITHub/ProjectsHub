from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


# -----------------------------
# PATHS (FIXED)
# -----------------------------
SCRIPT_DIR = Path(__file__).resolve().parent          # .../src
PROJECT_ROOT = SCRIPT_DIR.parent                      # .../bit_ai_business_automation_market
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUT_MONTHLY_CSV = PROCESSED_DIR / "monthly_total_vs_entry.csv"
OUT_JOBS_CSV = PROCESSED_DIR / "jobs_all_with_dates_deduped_6m.csv"


# -----------------------------
# CONFIG
# -----------------------------
COUNTRIES = {"DE", "AT", "CH"}

ENTRY_KEYWORDS = [
    r"\bentry\b",
    r"\bjunior\b",
    r"\btrainee\b",
    r"\bintern\b",
    r"\bpraktik\w*\b",
    r"\bberufseinsteiger\w*\b",
    r"\bgraduate\b",
    r"\b0\W*[-–]?\W*2\s*(years|yrs|jahre)\b",
    r"\b1\W*[-–]?\W*2\s*(years|yrs|jahre)\b",
    r"\b(keine|ohne)\s*erfahrung\b",
    r"\b0\s*jahre\b",
    r"\b1\s*jahr\b",
    r"\b2\s*jahre\b",
]

DATE_KEYS = [
    "postedAt",
    "posted_at",
    "datePosted",
    "date_posted",
    "publishedAt",
    "published_at",
    "listedAt",
    "listed_at",
    "postingDate",
    "posting_date",
    "createdAt",
    "created_at",
]


# -----------------------------
# HELPERS
# -----------------------------
def _safe_str(x: Any) -> str:
    return (x or "").strip() if isinstance(x, str) else str(x or "").strip()


def _parse_date_any(val: Any) -> Optional[pd.Timestamp]:
    """
    Поддержка:
    - ISO строки
    - unix timestamp (сек/мс)
    - относительные "3 days ago" (грубо, но лучше чем ничего)
    """
    if val is None:
        return None

    # unix timestamp
    if isinstance(val, (int, float)):
        v = int(val)
        if v > 10_000_000_000:
            return pd.to_datetime(v, unit="ms", utc=True, errors="coerce")
        return pd.to_datetime(v, unit="s", utc=True, errors="coerce")

    s = _safe_str(val)
    if not s:
        return None

    dt = pd.to_datetime(s, utc=True, errors="coerce")
    if pd.notna(dt):
        return dt

    # "x days/weeks/months ago"
    m = re.search(r"(\d+)\s*(day|days|week|weeks|month|months)\s*ago", s.lower())
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        now = pd.Timestamp.utcnow()
        if "day" in unit:
            return now - pd.Timedelta(days=n)
        if "week" in unit:
            return now - pd.Timedelta(weeks=n)
        if "month" in unit:
            return now - pd.DateOffset(months=n)

    return None


def extract_posted_date(obj: Dict[str, Any]) -> Optional[pd.Timestamp]:
    for k in DATE_KEYS:
        if k in obj:
            dt = _parse_date_any(obj.get(k))
            if dt is not None and pd.notna(dt):
                return dt

    for k in ["jobPosting", "job", "posting", "data"]:
        sub = obj.get(k)
        if isinstance(sub, dict):
            for kk in DATE_KEYS:
                if kk in sub:
                    dt = _parse_date_any(sub.get(kk))
                    if dt is not None and pd.notna(dt):
                        return dt

    return None


def is_entry_mid(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(pat, t) for pat in ENTRY_KEYWORDS)


def iter_json_files(raw_dir: Path) -> Iterable[Path]:
    if not raw_dir.exists():
        return []
    return raw_dir.rglob("*.json")


def infer_country_from_path(p: Path) -> Optional[str]:
    parts = {x.upper() for x in p.parts}
    for c in COUNTRIES:
        if c in parts:
            return c
    return None


def infer_role_id_from_path(p: Path) -> str:
    return p.parent.name.strip().lower()


def read_json_any(p: Path):
    text = p.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return []

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("items") or data.get("results") or data.get("data") or []
    return []



def normalize_job(obj: Dict[str, Any], country: str, role_id: str, source_file: str) -> Dict[str, Any]:
    title = _safe_str(obj.get("title") or obj.get("jobTitle") or obj.get("position") or "")
    company = _safe_str(obj.get("companyName") or obj.get("company") or obj.get("company_name") or "")
    location = _safe_str(obj.get("location") or obj.get("jobLocation") or obj.get("city") or "")
    url = _safe_str(obj.get("url") or obj.get("jobUrl") or obj.get("link") or obj.get("applyUrl") or "")
    description = _safe_str(obj.get("description") or obj.get("jobDescription") or obj.get("descriptionText") or "")

    posted_dt = extract_posted_date(obj)

    seniority = _safe_str(obj.get("seniorityLevel") or obj.get("seniority") or obj.get("experienceLevel") or "")
    full_text = " ".join([title, description, seniority])

    return {
        "country": country,
        "role_id": role_id,
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "posted_at": posted_dt.isoformat() if posted_dt is not None and pd.notna(posted_dt) else "",
        "entry_mid": int(is_entry_mid(full_text)),
        "source_file": source_file,
    }


def load_all_jobs() -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for fp in iter_json_files(RAW_DIR):
        country = infer_country_from_path(fp)
        if not country:
            continue
        role_id = infer_role_id_from_path(fp)

        items = read_json_any(fp)
        for obj in items:
            rows.append(normalize_job(obj, country, role_id, source_file=str(fp.relative_to(PROJECT_ROOT))))

    if not rows:
        raise FileNotFoundError(
            f"Не нашёл ни одного JSON в {RAW_DIR}. Проверь, что файлы лежат в data/raw/DE|AT|CH/..."
        )

    df = pd.DataFrame(rows)

    # posted_at -> datetime
    df["posted_at"] = pd.to_datetime(df["posted_at"], utc=True, errors="coerce")
    return df


def filter_last_6_months(df: pd.DataFrame) -> pd.DataFrame:
    now = pd.Timestamp.utcnow()
    cutoff = now - pd.DateOffset(months=6)
    df2 = df[df["posted_at"].notna()].copy()
    return df2[df2["posted_at"] >= cutoff].copy()


def dedupe(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    for c in ["title", "company", "location"]:
        df2[c] = df2[c].fillna("").str.strip().str.lower()

    df2 = df2.drop_duplicates(subset=["country", "title", "company", "location"])
    return df2


def build_monthly(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    df2["month"] = df2["posted_at"].dt.to_period("M").dt.to_timestamp()

    out = (
        df2.groupby(["country", "role_id", "month"], as_index=False)
        .agg(
            total_jobs=("title", "count"),
            entry_mid_jobs=("entry_mid", "sum"),
        )
        .sort_values(["country", "role_id", "month"])
    )
    return out


def main() -> None:
    df_all = load_all_jobs()

    df_6m = filter_last_6_months(df_all)
    df_6m_dedup = dedupe(df_6m)

    df_6m_dedup.to_csv(OUT_JOBS_CSV, index=False, encoding="utf-8")

    monthly = build_monthly(df_6m_dedup)
    monthly.to_csv(OUT_MONTHLY_CSV, index=False, encoding="utf-8")

    print("\n✅ MONTHLY TRENDS CREATED")
    print(f"- Jobs (6m, deduped): {OUT_JOBS_CSV}")
    print(f"- Monthly summary:   {OUT_MONTHLY_CSV}")
    print(f"- Rows monthly:      {len(monthly)}")


if __name__ == "__main__":
    main()

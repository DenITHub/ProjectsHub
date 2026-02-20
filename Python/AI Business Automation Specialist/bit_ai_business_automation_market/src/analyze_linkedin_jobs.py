from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

COUNTRIES = ["DE", "AT", "CH"]

ROLE_CONFIG = {
    "business_transformation_analyst": "Business Transformation Analyst",
    "ai_governance_analyst": "AI Governance Analyst",
    "ai_automation_specialist": "AI Automation Specialist",
    "prompt_engineer": "Prompt Engineer",
    "junior_automation_specialist": "Junior Automation Specialist",
    "digital_process_analyst": "Digital Process Analyst",
    "ai_project_manager": "AI Project Manager",
    "ai_product_manager": "AI Product Manager",
}

CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=183)

ENTRY_INCLUDE = [
    # EN
    "entry level", "entry-level", "junior", "associate", "working student",
    "0-2 years", "0–2 years", "up to 2 years", "no experience required",
    "0-1 years", "0–1 years", "1-2 years", "1–2 years",
    # DE
    "berufseinstieg", "berufseinsteiger", "junior",
    "trainee", "ohne berufserfahrung", "ohne erfahrung",
    "bis 1 jahr erfahrung", "bis 2 jahre erfahrung",
    "0-2 jahre", "0–2 jahre", "0-1 jahr", "1-2 jahre", "1–2 jahre",
]

SENIOR_EXCLUDE = [
    # EN
    "3+ years", "3 years experience", "3-5 years", "5+ years", "7+ years",
    "several years of experience", "many years of experience",
    " senior", "senior ", " lead ", "lead-", "principal", "head of",
    # DE
    "3+ jahre", "3 jahre berufserfahrung", "3-5 jahre", "5+ jahre",
    "mehrjährige berufserfahrung", "langjährige berufserfahrung",
    " senior", "senior ", "leitende position", "teamlead", "team lead", "leitung",
]


def read_json_any(path: Path) -> List[Dict[str, Any]]:
    """
    Считывает файл Apify:
    - JSON-массив
    - или JSONL (по одной вакансии на строку)
    Возвращает список dict.
    """
    if not path.exists() or path.stat().st_size == 0:
        return []

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        if text.lstrip().startswith("["):
            data = json.loads(text)
            return data if isinstance(data, list) else []
        else:
            result: List[Dict[str, Any]] = []
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                result.append(json.loads(line))
            return result
    except json.JSONDecodeError:
        print(f"[WARN] Невозможно распарсить JSON: {path}")
        return []


def get_field(job: Dict[str, Any], keys: List[str], default: str = "") -> str:
    """Берём первое непустое значение из списка ключей."""
    for k in keys:
        val = job.get(k)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return default


def normalize_text(s: str) -> str:
    return (s or "").strip().lower()


def parse_date_safe(value: Any) -> datetime | None:
    """
    Пробуем разобрать дату публикации из разных форматов:
    - timestamp (ms)
    - ISO-строки
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        except Exception:
            return None

    if isinstance(value, str):
        v = value.strip()
        for fmt in ("%Y-%m-%d",
                    "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                    "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(v, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue

    return None


def get_posted_at(job: Dict[str, Any]) -> datetime | None:
    """Ищем дату публикации в возможных полях Apify/LinkedIn."""
    for key in ["listedAt", "publishedAt", "postedAt"]:
        dt = parse_date_safe(job.get(key))
        if dt:
            return dt

    for key in ["listedAtDate", "publishedAtDate", "date"]:
        dt = parse_date_safe(job.get(key))
        if dt:
            return dt

    return None


def is_entry_mid_level(title: str, description: str) -> bool:
    """
    Entry/mid-вакансия, если:
    - содержит хотя бы один include-токен,
    - и НЕ содержит senior-/lead-токены.
    """
    text = f"{title}\n{description}".lower()

    if not any(kw in text for kw in ENTRY_INCLUDE):
        return False

    if any(kw in text for kw in SENIOR_EXCLUDE):
        return False

    return True


def load_raw_jobs_for_country_role(country: str, role_id: str) -> List[Dict[str, Any]]:
    """
    Загружаем ВСЕ вакансии из JSON для страны и роли:
    - без фильтра по дате,
    - без дедупликации.
    Сразу приводим поля к единому формату.
    """
    folder = RAW_DIR / country / role_id
    if not folder.exists():
        print(f"[WARN] Папка не найдена: {folder}")
        return []

    all_jobs: List[Dict[str, Any]] = []

    for path in sorted(folder.glob("*.json")):
        jobs_raw = read_json_any(path)
        if not jobs_raw:
            continue

        for job in jobs_raw:
            posted_at = get_posted_at(job)

            title = get_field(job, ["title", "position", "jobTitle"])
            company = get_field(job, ["companyName", "company", "company_name"])
            location = get_field(job, ["location", "jobLocation", "job_location"])
            description = get_field(
                job,
                ["description", "jobDescription", "descriptionText", "job_description"],
            )
            url = get_field(job, ["url", "jobUrl", "job_url", "link"])

            all_jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description,
                    "url": url,
                    "country": country,
                    "role_id": role_id,
                    "source_file": path.name,
                    "posted_at": posted_at,
                }
            )

    return all_jobs


def dedupe_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Дедупликация по (title, company, location)."""
    seen = set()
    unique: List[Dict[str, Any]] = []
    for job in jobs:
        title = normalize_text(job.get("title", ""))
        company = normalize_text(job.get("company", ""))
        location = normalize_text(job.get("location", ""))

        key = (title, company, location)
        if key in seen:
            continue
        seen.add(key)
        unique.append(job)
    return unique


def main() -> None:
    summary_rows = []

    for country in COUNTRIES:
        for role_id, canonical_en in ROLE_CONFIG.items():
            print(f"\n=== {country} / {role_id} ===")

            raw_jobs = load_raw_jobs_for_country_role(country, role_id)
            raw_total = len(raw_jobs)
            print(f"Сырые данные (до фильтров): {raw_total}")

            date_filtered_jobs = [
                j for j in raw_jobs
                if j["posted_at"] is not None and j["posted_at"] >= CUTOFF_DATE
            ]
            after_date_filter = len(date_filtered_jobs)
            print(f"После фильтра по дате (6 месяцев): {after_date_filter}")

            if after_date_filter == 0:
                summary_rows.append(
                    {
                        "country": country,
                        "role_id": role_id,
                        "canonical_en": canonical_en,
                        "raw_total": raw_total,
                        "after_date_filter": after_date_filter,
                        "total_jobs": 0,
                        "entry_mid_jobs": 0,
                    }
                )
                continue

            jobs_unique = dedupe_jobs(date_filtered_jobs)
            total_jobs = len(jobs_unique)
            print(f"После дедупликации: {total_jobs}")

            for job in jobs_unique:
                job["is_entry_mid"] = is_entry_mid_level(
                    job.get("title", ""), job.get("description", "")
                )

            entry_mid_jobs = sum(1 for j in jobs_unique if j["is_entry_mid"])
            print(f"Entry/mid (<= 2 года): {entry_mid_jobs}")

            out_path = PROCESSED_DIR / f"jobs_{country}_{role_id}.csv"
            df_jobs = pd.DataFrame(jobs_unique)
            if "posted_at" in df_jobs.columns:
                df_jobs["posted_at"] = df_jobs["posted_at"].astype(str)
            df_jobs.to_csv(out_path, index=False)
            print(f"Сохранено в: {out_path}")

            summary_rows.append(
                {
                    "country": country,
                    "role_id": role_id,
                    "canonical_en": canonical_en,
                    "raw_total": raw_total,
                    "after_date_filter": after_date_filter,
                    "total_jobs": total_jobs,
                    "entry_mid_jobs": entry_mid_jobs,
                }
            )

    df_summary = pd.DataFrame(summary_rows)
    summary_path = PROCESSED_DIR / "summary_linkedin_market.csv"
    df_summary.to_csv(summary_path, index=False)
    print(f"\n=== Готово. Сводная таблица: {summary_path} ===")
    print(df_summary)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
catalog_fetcher.py

Скачивает описания официальных профессий из:
- ближайших к роли AI Business Automation Specialist (из role_profile_ai_business_automation.json)
и сохраняет HTML локально в data/raw/catalogs/{country}/.

Использование:
    python -m src.fetching.catalog_fetcher --mode nearest_official_berufe
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List

import requests
from requests.exceptions import RequestException

from ..config import RAW_DIR, ROLE_PROFILE_PATH


CATALOGS_DIR = RAW_DIR / "catalogs"


def load_role_profile(path: Path = ROLE_PROFILE_PATH) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Role profile not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_url(url: str, timeout: int = 15) -> str:
    """
    Простая обёртка над requests.get с минимальной защитой.
    Возвращает текст HTML/JSON (как есть).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AI-Business-Automation-Research/1.0)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch URL {url}: {e}") from e
    return resp.text


def sanitize_filename(name: str) -> str:
    """
    Упрощённая нормализация в имя файла.
    """
    bad_chars = '<>:"/\\|?* '
    out = "".join("_" if c in bad_chars else c for c in name)
    return out[:120]  # ограничим длину на всякий случай


def save_catalog_html(country: str, title_de: str, url: str, html: str) -> Path:
    """
    Сохранить HTML-страницу профессии в:
      data/raw/catalogs/{country}/{sanitized_title}.html
    """
    country = country.lower()
    out_dir = CATALOGS_DIR / country
    out_dir.mkdir(parents=True, exist_ok=True)

    base_name = sanitize_filename(title_de or "unknown_title")
    file_path = out_dir / f"{base_name}.html"
    file_path.write_text(html, encoding="utf-8")

    meta = {
        "country": country,
        "title_de": title_de,
        "url": url,
    }
    meta_path = out_dir / f"{base_name}.meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return file_path


def fetch_nearest_official_berufe() -> List[Path]:
    """
    Берёт из role_profile_ai_business_automation.json список nearest_official_berufe_hypotheses,
    скачивает соответствующие страницы и сохраняет в каталоге data/raw/catalogs.
    """
    profile = load_role_profile()
    berufe = profile.get("nearest_official_berufe_hypotheses", [])

    if not berufe:
        raise ValueError("No 'nearest_official_berufe_hypotheses' entries found in role profile.")

    saved_paths: List[Path] = []

    for entry in berufe:
        country = entry.get("country", "XX")
        title_de = entry.get("title_de", "unknown")
        url = entry.get("url")

        if not url:
            print(f"[WARN] Skipping entry without URL: {entry}")
            continue

        print(f"[INFO] Fetching {country} – {title_de}: {url}")
        try:
            html = fetch_url(url)
        except RuntimeError as e:
            print(f"[ERROR] {e}")
            continue

        path = save_catalog_html(country=country, title_de=title_de, url=url, html=html)
        print(f"[INFO] Saved: {path}")
        saved_paths.append(path)

    return saved_paths


def main():
    parser = argparse.ArgumentParser(
        description="Fetcher für offizielle Berufskataloge (nahe Berufe zu AI Business Automation Specialist)."
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["nearest_official_berufe"],
        default="nearest_official_berufe",
        help="Was soll geladen werden (aktuell: nearest_official_berufe)."
    )

    args = parser.parse_args()

    if args.mode == "nearest_official_berufe":
        paths = fetch_nearest_official_berufe()
        print(f"[INFO] Done. Saved {len(paths)} files.")


if __name__ == "__main__":
    main()

# scripts/inspect_december_collection_window.py
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


# -----------------------------
# Helpers
# -----------------------------

DATE_CANDIDATES_SCRAPE = [
    "scrape_date", "scraped_at", "collected_at", "collected_date",
    "ingested_at", "ingest_date", "run_date", "snapshot_date",
    "created_at", "created_time", "fetched_at", "fetch_date"
]

DATE_CANDIDATES_POSTED = [
    "posted_at", "posted_date", "published_at", "publication_date",
    "date_posted", "job_posted_at", "posted_time"
]

def _find_first_existing(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = set(c.lower() for c in df.columns)
    for c in candidates:
        if c.lower() in cols:
            real = next(col for col in df.columns if col.lower() == c.lower())
            return real
    return None


def _to_datetime_safe(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce", utc=False)


def describe_range(s: pd.Series) -> dict:
    s2 = s.dropna()
    if s2.empty:
        return {"min": None, "max": None, "count": 0}
    return {"min": s2.min(), "max": s2.max(), "count": int(s2.shape[0])}


def print_block(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# -----------------------------
# Main logic
# -----------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Inspect December collection window and posted_at coverage."
    )
    parser.add_argument(
        "--csv",
        type=str,
        required=True,
        help="Path to a CSV file (e.g., data/processed/with_filter_flags.csv or monthly_total_vs_entry.csv)."
    )
    parser.add_argument(
        "--dec_year",
        type=int,
        default=2025,
        help="Year for December slice (default: 2025)."
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    scrape_col = _find_first_existing(df, DATE_CANDIDATES_SCRAPE)
    posted_col = _find_first_existing(df, DATE_CANDIDATES_POSTED)

    print_block("FILE")
    print(f"CSV: {csv_path}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print_block("DETECTED DATE COLUMNS")
    print(f"Scrape-like column: {scrape_col}")
    print(f"Posted-like column: {posted_col}")

    if scrape_col:
        df[scrape_col] = _to_datetime_safe(df[scrape_col])
    if posted_col:
        df[posted_col] = _to_datetime_safe(df[posted_col])

    print_block("OVERALL DATE RANGES")
    if scrape_col:
        r = describe_range(df[scrape_col])
        print(f"[SCRAPE] min={r['min']}  max={r['max']}  non-null={r['count']:,}")
    else:
        print("[SCRAPE] column not found -> cannot compute scrape window.")

    if posted_col:
        r = describe_range(df[posted_col])
        print(f"[POSTED] min={r['min']}  max={r['max']}  non-null={r['count']:,}")
    else:
        print("[POSTED] column not found -> cannot compute posted_at coverage.")

    year = args.dec_year
    dec_start = pd.Timestamp(year=year, month=12, day=1, tz="UTC")
    jan_start = pd.Timestamp(year=year + 1, month=1, day=1, tz="UTC")


    if posted_col:
        dec_df = df[(df[posted_col] >= dec_start) & (df[posted_col] < jan_start)].copy()

        print_block(f"DECEMBER {year} (by {posted_col})")
        print(f"Rows in December: {len(dec_df):,}")

        if len(dec_df) > 0:
            rr = describe_range(dec_df[posted_col])
            print(f"December coverage: min={rr['min']}  max={rr['max']}  non-null={rr['count']:,}")

            dec_df["dec_day"] = dec_df[posted_col].dt.date
            daily = dec_df.groupby("dec_day").size().sort_index()

            print("\nDaily counts (top 20 lines):")
            print(daily.head(20).to_string())

            print("\nDaily counts (last 20 lines):")
            print(daily.tail(20).to_string())

            last_day = pd.to_datetime(daily.index.max())
            print(f"\nLast day present in December postings: {last_day.date()}")

    if scrape_col:
        dec_scrape_df = df[(df[scrape_col] >= dec_start) & (df[scrape_col] < jan_start)].copy()

        print_block(f"DECEMBER {year} (by {scrape_col})")
        print(f"Rows collected in December: {len(dec_scrape_df):,}")

        if len(dec_scrape_df) > 0:
            rr = describe_range(dec_scrape_df[scrape_col])
            print(f"December scrape window: min={rr['min']}  max={rr['max']}  non-null={rr['count']:,}")

            dec_scrape_df["dec_scrape_day"] = dec_scrape_df[scrape_col].dt.date
            daily_scrape = dec_scrape_df.groupby("dec_scrape_day").size().sort_index()

            print("\nDaily scrape counts (top 20 lines):")
            print(daily_scrape.head(20).to_string())

            print("\nDaily scrape counts (last 20 lines):")
            print(daily_scrape.tail(20).to_string())

    print_block("DONE")
    print("Tip: If you don't see posted_at/scrape_date, run on another CSV from your pipeline (raw/processed).")


if __name__ == "__main__":
    main()

# src/inspect_raw_scrape_window_v2_path_mtime.py
from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable, Optional, Tuple

import pandas as pd


# -----------------------------
# -----------------------------
RAW_ROOT = Path("data/raw")

RE_ISO = re.compile(r"(20\d{2})[-_/\.](0[1-9]|1[0-2])[-_/\.](0[1-9]|[12]\d|3[01])")  # YYYY-MM-DD (или с / _ .)
RE_COMPACT = re.compile(r"(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])")            # YYYYMMDD
RE_DMY = re.compile(r"(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(20\d{2})")            # DD.MM.YYYY


def iter_files(root: Path) -> Iterable[Path]:
    exts = {".csv", ".parquet", ".pq", ".jsonl", ".ndjson", ".json"}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def parse_date_from_path(path: Path) -> Optional[pd.Timestamp]:
    s = str(path).replace("\\", "/")

    m = RE_ISO.search(s)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        return pd.Timestamp(f"{y}-{mo}-{d}", tz="UTC")

    m = RE_COMPACT.search(s)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        return pd.Timestamp(f"{y}-{mo}-{d}", tz="UTC")

    m = RE_DMY.search(s)
    if m:
        d, mo, y = m.group(1), m.group(2), m.group(3)
        return pd.Timestamp(f"{y}-{mo}-{d}", tz="UTC")

    return None


def main() -> None:
    if not RAW_ROOT.exists():
        raise FileNotFoundError(f"Folder not found: {RAW_ROOT.resolve()}")

    rows = []
    for p in iter_files(RAW_ROOT):
        mtime_utc = pd.Timestamp(p.stat().st_mtime, unit="s", tz="UTC")
        path_date = parse_date_from_path(p)

        rows.append({
            "file": str(p),
            "path_date_utc": str(path_date) if path_date is not None else "",
            "mtime_utc": str(mtime_utc),
        })

    df = pd.DataFrame(rows)

    df["path_date_dt"] = pd.to_datetime(df["path_date_utc"], errors="coerce", utc=True)
    df["mtime_dt"] = pd.to_datetime(df["mtime_utc"], errors="coerce", utc=True)

    print("\n" + "=" * 90)
    print("RAW SCRAPE WINDOW (heuristics): PATH DATE + FILE MTIME")
    print("=" * 90)
    print(f"Files scanned: {len(df):,}")

    mmin, mmax = df["mtime_dt"].min(), df["mtime_dt"].max()
    print(f"\nGLOBAL window by file mtime (UTC): {mmin}  →  {mmax}")

    with_path_date = df.dropna(subset=["path_date_dt"]).copy()
    print(f"Files with date in path/name: {len(with_path_date):,}")
    if len(with_path_date) > 0:
        pmin, pmax = with_path_date["path_date_dt"].min(), with_path_date["path_date_dt"].max()
        print(f"GLOBAL window by path date (UTC): {pmin}  →  {pmax}")

        print("\nTop 10 files by latest path_date (UTC):")
        print(with_path_date.sort_values("path_date_dt", ascending=False)
              .head(10)[["file", "path_date_utc", "mtime_utc"]].to_string(index=False))
    else:
        print("\nNo dates found in file/folder names. (path_date window unavailable)")

    print("\nTop 10 files by latest mtime (UTC):")
    print(df.sort_values("mtime_dt", ascending=False)
          .head(10)[["file", "mtime_utc", "path_date_utc"]].to_string(index=False))

    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "raw_scrape_window_audit_path_mtime.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\nSaved audit: {out_path.resolve()}")
    print("\nDONE.")


if __name__ == "__main__":
    main()

# src/inspect_raw_scrape_window.py
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


# -----------------------------
# -----------------------------
SCRAPE_COL_CANDIDATES = [
    "scrape_date", "scraped_at", "scraped_date",
    "collected_at", "collected_date",
    "ingested_at", "ingest_date",
    "run_date", "run_at",
    "snapshot_date", "snapshot_at",
    "fetched_at", "fetch_date",
    "crawled_at", "crawl_date",
    "retrieved_at", "retrieved_date",
    "created_at",  # иногда парсеры кладут сюда "время выгрузки"
]

SCRAPE_COL_HINTS = ("scrap", "collect", "ingest", "run", "snapshot", "fetch", "crawl", "retriev")


def _iter_files(root: Path) -> Iterable[Path]:
    exts = {".csv", ".parquet", ".pq", ".jsonl", ".ndjson", ".json"}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def _read_head(path: Path, nrows: int = 5000) -> pd.DataFrame:
    suf = path.suffix.lower()

    if suf == ".csv":
        return pd.read_csv(path, nrows=nrows)

    if suf in {".parquet", ".pq"}:
        df = pd.read_parquet(path)
        if len(df) > nrows:
            return df.head(nrows)
        return df

    if suf in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True, nrows=nrows)

    if suf == ".json":
        df = pd.read_json(path)
        if isinstance(df, pd.Series):
            return df.to_frame().head(nrows)
        return df.head(nrows)

    raise ValueError(f"Unsupported file type: {path}")


def _find_scrape_cols(df: pd.DataFrame) -> list[str]:
    lower_map = {c.lower(): c for c in df.columns}
    found = []
    for cand in SCRAPE_COL_CANDIDATES:
        if cand.lower() in lower_map:
            found.append(lower_map[cand.lower()])

    if found:
        return found

    heuristic = []
    for c in df.columns:
        cl = c.lower()
        if any(h in cl for h in SCRAPE_COL_HINTS):
            heuristic.append(c)
    return heuristic


def _to_dt(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce", utc=True)


def _range(s: pd.Series) -> tuple[Optional[pd.Timestamp], Optional[pd.Timestamp], int]:
    s2 = s.dropna()
    if s2.empty:
        return None, None, 0
    return s2.min(), s2.max(), int(s2.shape[0])


def main() -> None:
    raw_root = Path("data/raw")
    if not raw_root.exists():
        raise FileNotFoundError(f"Folder not found: {raw_root.resolve()}")

    rows = []
    global_mins = []
    global_maxs = []

    for path in _iter_files(raw_root):
        try:
            df = _read_head(path)
        except Exception as e:
            rows.append({
                "file": str(path),
                "status": "read_error",
                "columns_checked": 0,
                "scrape_cols": "",
                "min": "",
                "max": "",
                "non_null": 0,
                "note": repr(e)[:200],
            })
            continue

        scrape_cols = _find_scrape_cols(df)
        if not scrape_cols:
            rows.append({
                "file": str(path),
                "status": "no_scrape_cols",
                "columns_checked": len(df.columns),
                "scrape_cols": "",
                "min": "",
                "max": "",
                "non_null": 0,
                "note": "",
            })
            continue

        best_col = scrape_cols[0]
        dt = _to_dt(df[best_col])
        mn, mx, nn = _range(dt)

        if mn is not None:
            global_mins.append(mn)
        if mx is not None:
            global_maxs.append(mx)

        rows.append({
            "file": str(path),
            "status": "ok",
            "columns_checked": len(df.columns),
            "scrape_cols": ",".join(scrape_cols),
            "chosen_col": best_col,
            "min": str(mn) if mn is not None else "",
            "max": str(mx) if mx is not None else "",
            "non_null": nn,
            "note": "",
        })

    out = pd.DataFrame(rows)
    out_ok = out[out["status"] == "ok"].copy()

    print("\n" + "=" * 90)
    print("RAW SCRAPE WINDOW — SUMMARY")
    print("=" * 90)
    print(f"Files scanned: {len(out):,}")
    print(f"Files with scrape cols: {len(out_ok):,}")

    if global_mins and global_maxs:
        gmin = min(global_mins)
        gmax = max(global_maxs)
        print(f"\nGLOBAL scrape window (UTC): {gmin}  →  {gmax}")
    else:
        print("\nGLOBAL scrape window: not found (no usable scrape columns).")

    if not out_ok.empty:
        out_ok["max_dt"] = pd.to_datetime(out_ok["max"], errors="coerce", utc=True)
        out_ok_sorted = out_ok.sort_values("max_dt", ascending=False).head(10)
        print("\nTop 10 files by latest scrape max (UTC):")
        print(out_ok_sorted[["file", "chosen_col", "min", "max", "non_null"]].to_string(index=False))

    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "raw_scrape_window_audit.csv"
    out.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\nSaved audit: {out_path.resolve()}")

    print("\nDONE.")


if __name__ == "__main__":
    main()

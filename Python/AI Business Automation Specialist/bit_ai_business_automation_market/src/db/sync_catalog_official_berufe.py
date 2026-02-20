# src/db/sync_catalog_official_berufe.py

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
DB_FILE = ROOT / "data" / "database" / "bit_ai.db"
INPUT_FILE = ROOT / "data" / "processed" / "catalog_official_berufe.csv"


def get_engine():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{DB_FILE}")


def load_catalog_df():
    df = pd.read_csv(INPUT_FILE, sep=";", dtype=str).fillna("")
    return df


def sync_catalog():
    df = load_catalog_df()
    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM catalog_official_berufe"))

    df.to_sql(
        "catalog_official_berufe",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )

    print(f"[sync] loaded {len(df)} rows into SQLite → {DB_FILE}")


def main():
    sync_catalog()


if __name__ == "__main__":
    main()

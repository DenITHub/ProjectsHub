from sqlalchemy import create_engine, text
from pathlib import Path

db_path = Path(__file__).resolve().parents[1] / "data" / "database" / "bit_ai.db"
engine = create_engine(f"sqlite:///{db_path}")

schema = """
CREATE TABLE IF NOT EXISTS catalog_official_berufe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    source TEXT NOT NULL,
    official_title TEXT NOT NULL,
    kldb_code TEXT,
    notes TEXT
);
"""

with engine.begin() as conn:
    conn.execute(text(schema))

print("Schema created:", db_path)

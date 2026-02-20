#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

ROOT = Path(r"D:\ICH\Internship\AI Business Automation Specialist\bit_ai_business_automation_market")
CATALOGS_DIR = ROOT / "data" / "raw" / "catalogs"

FILES = [
    ("at_berufe_manual.csv", 4),
    ("ch_berufe_manual.csv", 4),
    ("de_berufe_manual.csv", 5),
]

def check_file(path: Path, expected_fields: int):
    print(f"\n=== Checking {path.name} (expected {expected_fields} fields) ===")
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            # пропускаем пустые строки
            if not line.strip():
                continue
            fields = line.rstrip("\n").split(";")
            if len(fields) != expected_fields:
                print(f"Line {i}: {len(fields)} fields → {line.strip()}")

def main():
    for filename, expected in FILES:
        path = CATALOGS_DIR / filename
        if not path.exists():
            print(f"!!! File not found: {path}")
            continue
        check_file(path, expected)

if __name__ == "__main__":
    main()


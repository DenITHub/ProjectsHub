from __future__ import annotations

from pathlib import Path
import re

CYR = re.compile(r"[\u0400-\u04FF]")     # Cyrillic block
HASH_COMMENT = re.compile(r"^\s*#")      # full-line hash comment

def clean_py_file(path: Path) -> int:
    """
    Remove ONLY full-line hash comments that contain Cyrillic.
    Returns number of removed lines.
    """
    lines = path.read_text(encoding="utf-8", errors="strict").splitlines(True)
    out: list[str] = []
    removed = 0

    for line in lines:
        if HASH_COMMENT.match(line) and CYR.search(line):
            removed += 1
            continue
        out.append(line)

    if removed:
        path.write_text("".join(out), encoding="utf-8")
    return removed

def main() -> None:
    repo = Path(__file__).resolve().parents[1]   # .../bit_ai_business_automation_market
    src = repo / "src"

    if not src.exists():
        raise SystemExit(f"[ERROR] src folder not found: {src}")

    targets = sorted(p for p in src.rglob("*.py") if p.is_file())
    total_removed = 0
    changed_files: list[tuple[Path,int]] = []

    for p in targets:
        removed = clean_py_file(p)
        if removed:
            changed_files.append((p, removed))
            total_removed += removed

    print(f"Scanned: {len(targets)} .py files (src only)")
    print(f"Changed: {len(changed_files)} files")
    print(f"Removed comment lines: {total_removed}")
    for p, n in changed_files[:200]:
        rel = p.relative_to(repo)
        print(f" - {rel.as_posix()}  (removed {n})")

if __name__ == "__main__":
    main()
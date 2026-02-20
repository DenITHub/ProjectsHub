import json
from pathlib import Path

import pandas as pd

from src.classification.skill_extractor import extract_skills
from src.classification.skills_dictionary import HARD_SKILLS, SOFT_SKILLS, TOOLS


RAW_DIR = Path("data/raw")
OUT_FILE = Path("data/processed/job_skills_extracted.csv")


def _to_key_label_map(x) -> dict[str, str]:
    """
    Normalize skills dictionaries to mapping: skill_key -> label.
    Supports:
      - dict: {"skill_sql": "SQL", ...} or {"skill_sql": {"label":"SQL"}, ...}
      - list[str]: ["skill_sql", ...]  (label = key)
      - list[dict]: [{"key":"skill_sql","label":"SQL"}, ...]
      - list[tuple]: [("skill_sql","SQL"), ...]
    """
    if x is None:
        return {}

    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if isinstance(v, str):
                out[k] = v
            elif isinstance(v, dict):
                out[k] = v.get("label") or v.get("name") or k
            else:
                out[k] = k
        return out

    if isinstance(x, list):
        out = {}
        for item in x:
            if isinstance(item, str):
                out[item] = item
            elif isinstance(item, tuple) and len(item) >= 2:
                out[str(item[0])] = str(item[1])
            elif isinstance(item, dict):
                k = item.get("key") or item.get("id") or item.get("name")
                if not k:
                    continue
                out[str(k)] = str(item.get("label") or item.get("title") or k)
        return out

    return {}


HARD_MAP = _to_key_label_map(HARD_SKILLS)
SOFT_MAP = _to_key_label_map(SOFT_SKILLS)
TOOLS_MAP = _to_key_label_map(TOOLS)

ALL_KNOWN_KEYS = set(HARD_MAP) | set(SOFT_MAP) | set(TOOLS_MAP)


def _pick_labels(flags: dict, key_label: dict[str, str]) -> list[str]:
    labels = []
    for k, label in key_label.items():
        if flags.get(k, 0):
            labels.append(label)
    return labels


rows = []

for country_dir in RAW_DIR.iterdir():
    if not country_dir.is_dir():
        continue

    country = country_dir.name

    for role_dir in country_dir.iterdir():
        if not role_dir.is_dir():
            continue

        role_id = role_dir.name

        for json_file in role_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
            except Exception:
                continue

            if not isinstance(data, list) or not data:
                continue

            for job in data:
                if not isinstance(job, dict):
                    continue

                desc = job.get("description", "") or ""
                title = job.get("title", "") or ""
                url = job.get("jobUrl") or job.get("jobURL") or job.get("url")

                if not desc or not url:
                    continue

                flags = extract_skills(desc)

                if not isinstance(flags, dict):
                    continue

                hard = _pick_labels(flags, HARD_MAP)
                soft = _pick_labels(flags, SOFT_MAP)
                tools = _pick_labels(flags, TOOLS_MAP)

                unknown_hits = [k for k, v in flags.items() if v and k not in ALL_KNOWN_KEYS]

                rows.append(
                    {
                        "country": country,
                        "role_id": role_id,
                        "title": title,
                        "url": url,
                        "hard_skills": "; ".join(hard),
                        "soft_skills": "; ".join(soft),
                        "tools": "; ".join(tools),
                        "unknown_skill_keys": "; ".join(unknown_hits),
                        "skill_flags": json.dumps(flags, ensure_ascii=False),
                        "source_json": str(json_file).replace("\\", "/"),
                    }
                )

df = pd.DataFrame(rows)

if df.empty:
    print("❌ No skills extracted (df is empty). Check raw JSON descriptions and extractor rules.")
else:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print(f"✅ Saved {len(df)} rows → {OUT_FILE}")
    print("Columns:", df.columns.tolist())

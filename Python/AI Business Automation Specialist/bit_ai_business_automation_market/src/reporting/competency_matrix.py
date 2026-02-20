import ast
import json
from pathlib import Path

import pandas as pd

from src.classification.skills_dictionary import HARD_SKILLS, SOFT_SKILLS, TOOLS

IN_FILE = Path("data/processed/job_skills_extracted.csv")
OUT_LONG = Path("data/processed/competency_matrix_long.csv")
OUT_PIVOT = Path("data/processed/competency_matrix_pivot_country_role.csv")
OUT_TOP = Path("data/processed/competency_top_by_country_role.csv")


def _to_set(x) -> set[str]:
    """Normalize dictionary/list values from skills_dictionary to a set of skill keys."""
    if x is None:
        return set()
    if isinstance(x, (list, tuple, set)):
        return set(map(str, x))
    if isinstance(x, dict):
        return set(map(str, x.keys()))
    return {str(x)}


HARD_SET = _to_set(HARD_SKILLS)
SOFT_SET = _to_set(SOFT_SKILLS)
TOOLS_SET = _to_set(TOOLS)


def parse_skill_flags(val) -> dict:
    """
    skill_flags can be:
    - dict
    - JSON string
    - python dict string (single quotes) -> literal_eval
    """
    if pd.isna(val) or val is None:
        return {}
    if isinstance(val, dict):
        return val

    s = str(val).strip()
    if not s or s == "{}":
        return {}

    # Try JSON first
    try:
        return json.loads(s)
    except Exception:
        pass

    # Fallback: python-like dict string
    try:
        obj = ast.literal_eval(s)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def skill_category(skill_key: str) -> str:
    TOOLS = {"skill_n8n", "skill_make", "skill_zapier", "skill_power_automate"}
    HARD  = {"skill_python", "skill_sql", "skill_api", "skill_llm", "skill_gdpr", "skill_bpmn"}
    SOFT  = set()  # сейчас у тебя soft-пакет не извлекается (позже расширим)

    if skill_key in TOOLS:
        return "tools"
    if skill_key in HARD:
        return "hard"
    if skill_key in SOFT:
        return "soft"
    return "other"



def main():
    if not IN_FILE.exists():
        raise FileNotFoundError(f"Input not found: {IN_FILE}")

    df = pd.read_csv(IN_FILE)
    needed = {"country", "role_id", "title", "url", "skill_flags"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {IN_FILE}: {sorted(missing)}")

    # Denominator: how many job ads per (country, role_id)
    denom = (
        df.groupby(["country", "role_id"])
        .size()
        .reset_index(name="job_ads")
    )

    rows = []
    for _, r in df.iterrows():
        flags = parse_skill_flags(r.get("skill_flags"))
        if not flags:
            continue

        # active skills only
        for k, v in flags.items():
            try:
                active = int(v) == 1
            except Exception:
                active = bool(v)
            if not active:
                continue

            k = str(k)
            rows.append(
                {
                    "country": r["country"],
                    "role_id": r["role_id"],
                    "skill_key": k,
                    "category": skill_category(k),
                }
            )

    long_df = pd.DataFrame(rows)
    if long_df.empty:
        print("❌ No active skills found in skill_flags.")
        return

    # counts per country-role-skill
    agg = (
        long_df.groupby(["country", "role_id", "category", "skill_key"])
        .size()
        .reset_index(name="mentions")
    )

    # add denominator + share
    agg = agg.merge(denom, on=["country", "role_id"], how="left")
    agg["share"] = agg["mentions"] / agg["job_ads"]

    OUT_LONG.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(OUT_LONG, index=False)

    # Pivot matrix (share) for easy pasting to report: per country-role as rows, skills as columns
    pivot = agg.pivot_table(
        index=["country", "role_id", "category"],
        columns="skill_key",
        values="share",
        aggfunc="max",
        fill_value=0.0,
    ).reset_index()

    pivot.to_csv(OUT_PIVOT, index=False)

    # Top skills per (country, role, category)
    top = (
        agg.sort_values(["country", "role_id", "category", "share"], ascending=[True, True, True, False])
        .groupby(["country", "role_id", "category"], as_index=False)
        .head(20)
    )
    top.to_csv(OUT_TOP, index=False)

    print(f"✅ Saved:\n - {OUT_LONG}\n - {OUT_PIVOT}\n - {OUT_TOP}")
    print(f"Rows (long): {len(agg):,}")
    print(f"Unique skills: {agg['skill_key'].nunique():,}")


if __name__ == "__main__":
    main()

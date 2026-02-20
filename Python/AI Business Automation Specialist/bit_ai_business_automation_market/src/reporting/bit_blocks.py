# src/reporting/bit_blocks.py
from __future__ import annotations

from pathlib import Path
import pandas as pd


PIVOT_FILE = Path("data/processed/competency_matrix_pivot_country_role.csv")
OUT_DIR = Path("data/processed/bit_blocks")

# BIT groups (edit here if you add more skills)
BIT_GROUPS: dict[str, list[str]] = {
    "tools_stack": [
        "skill_n8n",
        "skill_make",
        "skill_zapier",
        "skill_power_automate",
        "skill_api",
    ],
    "hard_skills": [
        "skill_python",
        "skill_sql",
        "skill_llm",
    ],
    "compliance_process": [
        "skill_gdpr",
        "skill_bpmn",
    ],
}

# Friendly labels for presentation-ready CSVs
FRIENDLY: dict[str, str] = {
    "skill_n8n": "n8n",
    "skill_make": "Make",
    "skill_zapier": "Zapier",
    "skill_power_automate": "Power Automate",
    "skill_api": "API",
    "skill_python": "Python",
    "skill_sql": "SQL",
    "skill_llm": "LLM",
    "skill_gdpr": "GDPR",
    "skill_bpmn": "BPMN",
}


def _require_columns(df: pd.DataFrame, cols: list[str], file_hint: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(
            f"Missing columns in {file_hint}: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )


def _to_long_country_role(pivot: pd.DataFrame) -> pd.DataFrame:
    # Expect at least: country, role_id, skill_*
    _require_columns(pivot, ["country", "role_id"], str(PIVOT_FILE))

    skill_cols = [c for c in pivot.columns if c.startswith("skill_")]
    if not skill_cols:
        raise KeyError(
            f"No skill_* columns found in {PIVOT_FILE}. "
            f"Columns: {pivot.columns.tolist()}"
        )

    long_df = pivot.melt(
        id_vars=["country", "role_id"],
        value_vars=skill_cols,
        var_name="skill_key",
        value_name="share",
    )

    # Normalize types
    long_df["share"] = pd.to_numeric(long_df["share"], errors="coerce").fillna(0.0)
    long_df["skill_label"] = long_df["skill_key"].map(FRIENDLY).fillna(long_df["skill_key"])
    return long_df


def _add_bit_group(long_df: pd.DataFrame) -> pd.DataFrame:
    # Map skill_key -> group
    skill_to_group: dict[str, str] = {}
    for g, skills in BIT_GROUPS.items():
        for s in skills:
            skill_to_group[s] = g

    out = long_df.copy()
    out["bit_group"] = out["skill_key"].map(skill_to_group).fillna("other")
    out["bit_group_label"] = out["bit_group"].map(
        {
            "tools_stack": "Tools stack",
            "hard_skills": "Hard skills",
            "compliance_process": "Compliance / Process",
            "other": "Other",
        }
    ).fillna(out["bit_group"])
    return out


def _country_overall_unweighted(long_df: pd.DataFrame) -> pd.DataFrame:
    # Country overall = mean share across roles within each country for each skill
    return (
        long_df.groupby(["country", "skill_key", "skill_label"], as_index=False)
        .agg(share=("share", "mean"))
        .sort_values(["country", "share"], ascending=[True, False])
    )


def _pivot_for_presentation(
    df: pd.DataFrame,
    index_cols: list[str],
    group_name: str,
    out_path: Path,
) -> None:
    # Filter only group skills
    skills = BIT_GROUPS[group_name]
    filtered = df[df["skill_key"].isin(skills)].copy()

    table = (
        filtered.pivot_table(
            index=index_cols,
            columns="skill_label",
            values="share",
            aggfunc="mean",
            fill_value=0.0,
        )
        .reset_index()
    )

    # Keep stable column order: index columns first, then skills in BIT order
    ordered_skill_labels = [FRIENDLY.get(s, s) for s in skills]
    cols = index_cols + [c for c in ordered_skill_labels if c in table.columns]
    table = table[cols]

    table.to_csv(out_path, index=False)


def _topn_by_country_blocks(country_overall: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    # Top N per country within each BIT block
    tmp = _add_bit_group(country_overall)
    tmp = tmp[tmp["bit_group"].isin({"tools_stack", "hard_skills", "compliance_process"})].copy()

    tmp["rank"] = tmp.groupby(["country", "bit_group"])["share"].rank(method="first", ascending=False)
    top = tmp[tmp["rank"] <= top_n].copy()
    top = top.sort_values(["country", "bit_group", "share"], ascending=[True, True, False])

    return top[["country", "bit_group_label", "skill_label", "share"]]


def main() -> None:
    if not PIVOT_FILE.exists():
        raise FileNotFoundError(f"Not found: {PIVOT_FILE}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pivot = pd.read_csv(PIVOT_FILE)
    long_country_role = _add_bit_group(_to_long_country_role(pivot))
    country_overall = _country_overall_unweighted(long_country_role)

    # 1) Universal long tables
    long_country_role_out = OUT_DIR / "bit_blocks_country_role_long.csv"
    long_country_role.to_csv(long_country_role_out, index=False)

    country_overall_out = OUT_DIR / "bit_blocks_country_overall_long.csv"
    country_overall.to_csv(country_overall_out, index=False)

    # 2) Presentation-ready wide tables
    for group in ["tools_stack", "hard_skills", "compliance_process"]:
        # Countries (country × skills)
        out_c = OUT_DIR / f"{group}_-_countries.csv"
        _pivot_for_presentation(
            df=country_overall,
            index_cols=["country"],
            group_name=group,
            out_path=out_c,
        )

        # Country × Role (country, role_id × skills)
        out_cr = OUT_DIR / f"{group}_-_country_x_role.csv"
        _pivot_for_presentation(
            df=long_country_role,
            index_cols=["country", "role_id"],
            group_name=group,
            out_path=out_cr,
        )

    # 3) Top-N bullets per country per block
    topn = _topn_by_country_blocks(country_overall, top_n=5)
    topn_out = OUT_DIR / "bit_blocks_topN_by_country.csv"
    topn.to_csv(topn_out, index=False)

    print("✅ BIT blocks saved:")
    print(f" - {long_country_role_out}")
    print(f" - {country_overall_out}")
    print(f" - {topn_out}")
    print(" - " + "\n - ".join(str(p) for p in sorted(OUT_DIR.glob("*_-_countries.csv"))))
    print(" - " + "\n - ".join(str(p) for p in sorted(OUT_DIR.glob("*_-_country_x_role.csv"))))


if __name__ == "__main__":
    main()

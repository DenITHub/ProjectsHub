from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


IN_FILE = Path("data/processed/competency_matrix_long.csv")
OUT_DIR = Path("data/processed/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def save_bar(df: pd.DataFrame, title: str, out_path: Path, top_n: int = 12) -> None:
    """
    df must contain columns: skill_key, share (0..1)
    """
    if df.empty:
        print(f"Skip (empty): {out_path.name}")
        return

    plot_df = df.sort_values("share", ascending=False).head(top_n).copy()

    plt.figure(figsize=(10, 6))
    plt.barh(plot_df["skill_key"], plot_df["share"])
    plt.gca().invert_yaxis()
    plt.title(title)
    plt.xlabel("Share of job ads mentioning skill")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()

    print(f"Saved: {out_path}")


def main() -> None:
    if not IN_FILE.exists():
        raise FileNotFoundError(f"Missing: {IN_FILE}")

    df = pd.read_csv(IN_FILE)
    required = {"country", "role_id", "skill_key", "mentions", "job_ads", "share"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing columns in {IN_FILE}: {sorted(missing)}")

    # 1) Overall (all countries/roles) — weighted share
    overall = (
        df.groupby("skill_key", as_index=False)
        .agg(mentions=("mentions", "sum"), job_ads=("job_ads", "sum"))
    )
    overall["share"] = (overall["mentions"] / overall["job_ads"]).fillna(0)

    save_bar(
        overall,
        title="Top skills overall (share of job ads)",
        out_path=OUT_DIR / "competency_top_overall_bar.png",
        top_n=12,
    )

    # 2) Per country
    for country in sorted(df["country"].dropna().unique()):
        cdf = df[df["country"] == country]

        by_country = (
            cdf.groupby("skill_key", as_index=False)
            .agg(mentions=("mentions", "sum"), job_ads=("job_ads", "sum"))
        )
        by_country["share"] = (by_country["mentions"] / by_country["job_ads"]).fillna(0)

        save_bar(
            by_country,
            title=f"Top skills in {country} (share of job ads)",
            out_path=OUT_DIR / f"competency_top_{country}_bar.png",
            top_n=12,
        )

    print(f"Done. Bars in: {OUT_DIR}")


if __name__ == "__main__":
    main()

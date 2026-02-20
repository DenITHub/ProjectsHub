from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIG_DIR = PROCESSED_DIR / "figures" / "junior_automation_specialist"
FIG_DIR.mkdir(parents=True, exist_ok=True)

ROLE_ID = "junior_automation_specialist"


def load_summary() -> pd.DataFrame:
    """Загружаем сводный CSV."""
    path = PROCESSED_DIR / "summary_linkedin_market.csv"
    if not path.exists():
        raise FileNotFoundError(f"Не найден summary файл: {path}")
    return pd.read_csv(path)


def plot_total_jobs(df: pd.DataFrame) -> None:
    """Total вакансий по странам."""
    plt.figure(figsize=(6, 4))
    plt.bar(df["country"], df["total_jobs"], color=["#0072B2", "#009E73", "#D55E00"])
    plt.title("Junior Automation Specialist — Total Jobs (after dedupe, 6 months)")
    plt.xlabel("Country")
    plt.ylabel("Total jobs")
    plt.tight_layout()

    out = FIG_DIR / "total_jobs.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")


def plot_entry_jobs(df: pd.DataFrame) -> None:
    """Entry/mid вакансии по странам."""
    plt.figure(figsize=(6, 4))
    plt.bar(df["country"], df["entry_mid_jobs"], color=["#56B4E9", "#F0E442", "#CC79A7"])
    plt.title("Junior Automation Specialist — Entry/Mid Jobs (<=2 years)")
    plt.xlabel("Country")
    plt.ylabel("Entry/Mid jobs")
    plt.tight_layout()

    out = FIG_DIR / "entry_mid_jobs.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")


def plot_entry_share(df: pd.DataFrame) -> None:
    """Доля entry/mid от total (%)."""
    df = df.copy()
    df["entry_share_pct"] = df.apply(
        lambda r: (r["entry_mid_jobs"] / r["total_jobs"] * 100)
        if r["total_jobs"] > 0 else 0.0,
        axis=1,
    )

    plt.figure(figsize=(6, 4))
    plt.bar(df["country"], df["entry_share_pct"], color=["#999999", "#E69F00", "#56B4E9"])
    plt.title("Junior Automation Specialist — Entry Share (%)")
    plt.xlabel("Country")
    plt.ylabel("Entry share (%)")
    plt.tight_layout()

    out = FIG_DIR / "entry_share_pct.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")


def main() -> None:
    df = load_summary()

    df_role = df[df["role_id"] == ROLE_ID].reset_index(drop=True)

    if df_role.empty:
        raise ValueError("В summary нет данных по роли junior_automation_specialist")

    print(df_role)

    plot_total_jobs(df_role)
    plot_entry_jobs(df_role)
    plot_entry_share(df_role)


if __name__ == "__main__":
    main()

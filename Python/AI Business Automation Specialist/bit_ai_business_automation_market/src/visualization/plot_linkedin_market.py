from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIG_DIR = PROCESSED_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_summary() -> pd.DataFrame:
    path = PROCESSED_DIR / "summary_linkedin_market.csv"
    if not path.exists():
        raise FileNotFoundError(f"Не найден summary файл: {path}")
    df = pd.read_csv(path)
    return df


def plot_total_jobs(df: pd.DataFrame) -> None:
    """
    Столбчатая диаграмма: total_jobs по ролям и странам.
    """
    pivot = (
        df.pivot(index="role_id", columns="country", values="total_jobs")
        .fillna(0)
        .astype(int)
    )

    ax = pivot.plot(kind="bar")
    ax.set_title("Total LinkedIn Jobs by Role and Country (after dedupe, 6 months)")
    ax.set_ylabel("Number of jobs")
    ax.set_xlabel("Role")
    ax.legend(title="Country")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_path = FIG_DIR / "total_jobs_by_role_country.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")


def plot_entry_jobs(df: pd.DataFrame) -> None:
    """
    Столбчатая диаграмма: entry_mid_jobs по ролям и странам.
    """
    pivot = (
        df.pivot(index="role_id", columns="country", values="entry_mid_jobs")
        .fillna(0)
        .astype(int)
    )

    ax = pivot.plot(kind="bar")
    ax.set_title("Entry/Mid Jobs (<=2 years) by Role and Country")
    ax.set_ylabel("Number of entry/mid jobs")
    ax.set_xlabel("Role")
    ax.legend(title="Country")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_path = FIG_DIR / "entry_jobs_by_role_country.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")


def plot_entry_share(df: pd.DataFrame) -> None:
    """
    Диаграмма доли entry_mid_jobs / total_jobs в % по ролям и странам.
    """
    df = df.copy()
    df["entry_share_pct"] = df.apply(
        lambda r: (r["entry_mid_jobs"] / r["total_jobs"] * 100) if r["total_jobs"] > 0 else 0.0,
        axis=1,
    )

    pivot = (
        df.pivot(index="role_id", columns="country", values="entry_share_pct")
        .fillna(0.0)
    )

    ax = pivot.plot(kind="bar")
    ax.set_title("Entry/Mid Share (%) by Role and Country")
    ax.set_ylabel("Entry/Mid share (%)")
    ax.set_xlabel("Role")
    ax.legend(title="Country")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_path = FIG_DIR / "entry_share_by_role_country.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")


def main() -> None:
    df = load_summary()
    print(df)

    plot_total_jobs(df)
    plot_entry_jobs(df)
    plot_entry_share(df)


if __name__ == "__main__":
    main()

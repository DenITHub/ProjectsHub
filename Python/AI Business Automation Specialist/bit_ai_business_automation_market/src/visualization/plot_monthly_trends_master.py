from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# PATH RESOLUTION (ROBUST)
# -----------------------------
def find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(10):
        if (cur / "src").exists() and (cur / "requirements.txt").exists():
            return cur
        cur = cur.parent
    raise RuntimeError("Не удалось определить PROJECT_ROOT (ищу src/ и requirements.txt).")


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = find_project_root(SCRIPT_DIR)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
IN_FILE = PROCESSED_DIR / "monthly_total_vs_entry.csv"

FIG_DIR = PROCESSED_DIR / "figures" / "monthly_trends_master"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# PLOTTING
# -----------------------------
def plot_multi_line(df: pd.DataFrame, x: str, y: str, group: str, title: str, out_name: str) -> None:
    d = df.sort_values(x).copy()
    plt.figure()
    for key, g in d.groupby(group):
        g = g.sort_values(x)
        plt.plot(g[x], g[y], label=str(key))
    plt.title(title)
    plt.xlabel("Month")
    plt.ylabel(y)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / out_name, dpi=160)
    plt.close()


def plot_single(df: pd.DataFrame, x: str, y: str, title: str, out_name: str) -> None:
    d = df.sort_values(x).copy()
    plt.figure()
    plt.plot(d[x], d[y])
    plt.title(title)
    plt.xlabel("Month")
    plt.ylabel(y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / out_name, dpi=160)
    plt.close()


def main() -> None:
    if not IN_FILE.exists():
        raise FileNotFoundError(f"Не найден файл: {IN_FILE}. Сначала запусти: python -m src.analyze_monthly_trends")

    df = pd.read_csv(IN_FILE, parse_dates=["month"])

    for col in ["total_jobs", "entry_mid_jobs"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    dach = df.groupby(["month"], as_index=False)[["total_jobs", "entry_mid_jobs"]].sum()
    plot_single(
        dach, "month", "total_jobs",
        "DACH — Total jobs per month (ALL roles, deduped)",
        "dach_total_jobs_by_month.png",
    )
    plot_single(
        dach, "month", "entry_mid_jobs",
        "DACH — Entry/Mid jobs per month (ALL roles, deduped)",
        "dach_entry_mid_jobs_by_month.png",
    )

    by_country = df.groupby(["month", "country"], as_index=False)[["total_jobs", "entry_mid_jobs"]].sum()
    plot_multi_line(
        by_country, "month", "total_jobs", "country",
        "Countries — Total jobs per month (ALL roles, deduped)",
        "country_total_jobs_by_month.png",
    )
    plot_multi_line(
        by_country, "month", "entry_mid_jobs", "country",
        "Countries — Entry/Mid jobs per month (ALL roles, deduped)",
        "country_entry_mid_jobs_by_month.png",
    )

    focus_role = "junior_automation_specialist"
    focus = df[df["role_id"] == focus_role].copy()
    if not focus.empty:
        focus_dach = focus.groupby(["month"], as_index=False)[["total_jobs", "entry_mid_jobs"]].sum()
        plot_single(
            focus_dach, "month", "total_jobs",
            f"Focus ({focus_role}) — DACH total jobs per month (deduped)",
            f"focus_{focus_role}_total.png",
        )
        plot_single(
            focus_dach, "month", "entry_mid_jobs",
            f"Focus ({focus_role}) — DACH entry/mid jobs per month (deduped)",
            f"focus_{focus_role}_entry_mid.png",
        )

        focus_country = focus.groupby(["month", "country"], as_index=False)[["total_jobs", "entry_mid_jobs"]].sum()
        plot_multi_line(
            focus_country, "month", "total_jobs", "country",
            f"Focus ({focus_role}) — Countries total jobs per month (deduped)",
            f"focus_{focus_role}_country_total.png",
        )
        plot_multi_line(
            focus_country, "month", "entry_mid_jobs", "country",
            f"Focus ({focus_role}) — Countries entry/mid jobs per month (deduped)",
            f"focus_{focus_role}_country_entry_mid.png",
        )

    print("\n✅ MASTER MONTHLY PLOTS CREATED")
    print(FIG_DIR)


if __name__ == "__main__":
    main()

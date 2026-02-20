from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def find_project_root(start: Path) -> Path:
    """Поднимаемся вверх и ищем корень проекта по признакам структуры."""
    for p in [start] + list(start.parents):
        if (p / "src").exists() and (p / "data").exists() and (p / "reports").exists():
            return p
    raise RuntimeError(f"Не смог найти корень проекта, старт: {start}")


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = find_project_root(SCRIPT_DIR)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DEFAULT_IN_FILE = PROCESSED_DIR / "monthly_total_vs_entry.csv"

FIG_DIR = PROCESSED_DIR / "figures" / "monthly_trends"
FIG_DIR.mkdir(parents=True, exist_ok=True)

print("SCRIPT_DIR =", SCRIPT_DIR)
print("PROJECT_ROOT =", PROJECT_ROOT)
print("DEFAULT_IN_FILE =", DEFAULT_IN_FILE)
print("DEFAULT_IN_FILE exists =", DEFAULT_IN_FILE.exists())


def plot_country_role(df: pd.DataFrame, country: str, role_id: str) -> None:
    d = (
        df[(df["country"] == country) & (df["role_id"] == role_id)]
        .sort_values("month")
    )
    if d.empty:
        return

    # total jobs
    plt.figure()
    plt.plot(d["month"], d["total_jobs"])
    plt.title(f"Total jobs per month — {country} — {role_id}")
    plt.xlabel("Month")
    plt.ylabel("Jobs")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"{country}_{role_id}_total.png", dpi=180)
    plt.close()

    # entry / mid jobs
    plt.figure()
    plt.plot(d["month"], d["entry_mid_jobs"])
    plt.title(f"Entry/Mid jobs per month — {country} — {role_id}")
    plt.xlabel("Month")
    plt.ylabel("Jobs")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"{country}_{role_id}_entry_mid.png", dpi=180)
    plt.close()


def resolve_input_file() -> Path:
    """Берём файл строго из data/processed проекта."""
    if DEFAULT_IN_FILE.exists():
        return DEFAULT_IN_FILE

    raise FileNotFoundError(
        f"Не найден monthly_total_vs_entry.csv\n"
        f"Ожидаемый путь: {DEFAULT_IN_FILE}\n"
        f"Сначала запусти: python -m src.analyze_monthly_trends"
    )


def main() -> None:
    in_file = resolve_input_file()
    df = pd.read_csv(in_file, parse_dates=["month"])

    for country in sorted(df["country"].unique()):
        for role_id in sorted(df["role_id"].unique()):
            plot_country_role(df, country, role_id)

    print("\n✅ MONTHLY PLOTS CREATED")
    print(FIG_DIR)


if __name__ == "__main__":
    main()

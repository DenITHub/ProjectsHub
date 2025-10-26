import pandas as pd

def build_cohort_table(df, date_col="created_time"):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df["cohort_month"] = df[date_col].dt.to_period("M")
    df["cohort_index"] = (df[date_col].dt.year - df["cohort_month"].dt.year) * 12 + \
                         (df[date_col].dt.month - df["cohort_month"].dt.month)

    grouped = df.groupby(["cohort_month", "cohort_index"]).agg(n_deals=("id", "count")).reset_index()

    cohort_pivot = grouped.pivot(index="cohort_month", columns="cohort_index", values="n_deals").fillna(0).astype(int)
    return cohort_pivot

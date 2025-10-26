import pandas as pd

def analyze_deals_by_city(df):
    df = df.copy()
    df["is_won"] = df["stage"].str.lower().str.strip() == "payment done"

    result = df.groupby("city").agg(
        total_deals=("id", "count"),
        won_deals=("is_won", "sum"),
        revenue=("offer_total_amount", lambda x: x[df["is_won"]].sum())
    )
    result["conversion_rate"] = result["won_deals"] / result["total_deals"]
    return result.sort_values("total_deals", ascending=False)


def analyze_language_effect(df):
    df = df.copy()
    df = df[df["level_of_deutsch"].notna() & df["city"].notna()]
    df["is_won"] = df["stage"].str.lower().str.strip() == "payment done"

    result = df.groupby(["city", "level_of_deutsch"]).agg(
        total_deals=("id", "count"),
        won_deals=("is_won", "sum"),
        revenue=("offer_total_amount", lambda x: x[df["is_won"]].sum())
    )
    result["conversion_rate"] = result["won_deals"] / result["total_deals"]
    return result.reset_index().sort_values(["city", "conversion_rate"], ascending=[True, False])

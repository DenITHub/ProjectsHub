import pandas as pd

def analyze_payment_types(df):
    df = df.copy()
    df["is_won"] = df["stage"].str.lower().str.strip() == "payment done"

    result = df.groupby("payment_type").agg(
        total_deals=("id", "count"),
        won_deals=("is_won", "sum"),
        revenue=("offer_total_amount", lambda x: x[df["is_won"]].sum())
    )
    result["conversion_rate"] = result["won_deals"] / result["total_deals"]
    return result.sort_values("total_deals", ascending=False)

def analyze_products_and_education(df):
    df = df.copy()
    df["is_won"] = df["stage"].str.lower().str.strip() == "payment done"

    product_stats = df.groupby("product").agg(
        total_deals=("id", "count"),
        won_deals=("is_won", "sum"),
        revenue=("offer_total_amount", lambda x: x[df["is_won"]].sum())
    )
    product_stats["conversion_rate"] = product_stats["won_deals"] / product_stats["total_deals"]

    education_stats = df.groupby("education_type").agg(
        total_deals=("id", "count"),
        won_deals=("is_won", "sum"),
        revenue=("offer_total_amount", lambda x: x[df["is_won"]].sum())
    )
    education_stats["conversion_rate"] = education_stats["won_deals"] / education_stats["total_deals"]


    return product_stats.sort_values("total_deals", ascending=False), \
           education_stats.sort_values("total_deals", ascending=False)

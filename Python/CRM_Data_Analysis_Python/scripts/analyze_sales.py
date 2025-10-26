import pandas as pd

def analyze_sales_efficiency(deals_df):
    df = deals_df.copy()

    # успешные сделки
    df["is_won"] = df["stage"].str.lower().str.strip() == "payment done"

    # владельцы сделок
    by_owner = df.groupby("deal_owner_name").agg(
        total_deals=("id", "count"),
        won_deals=("is_won", "sum"),
        total_revenue=("offer_total_amount", lambda x: x[df["is_won"]].sum())
    )
    by_owner["conversion_rate"] = by_owner["won_deals"] / by_owner["total_deals"]
    
    # компании
    by_campaign = df.groupby("campaign").agg(
        total_deals=("id", "count"),
        won_deals=("is_won", "sum"),
        total_revenue=("offer_total_amount", lambda x: x[df["is_won"]].sum())
    )
    by_campaign["conversion_rate"] = by_campaign["won_deals"] / by_campaign["total_deals"]

    return by_owner.sort_values("total_deals", ascending=False), \
           by_campaign.sort_values("total_deals", ascending=False)


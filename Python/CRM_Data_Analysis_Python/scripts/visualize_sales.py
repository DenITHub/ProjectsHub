import plotly.express as px
import pandas as pd

def plot_sales_by_owner(df_owner):
    df = df_owner.reset_index().sort_values(by="total_revenue", ascending=False)
    fig = px.bar(df,
                 x="deal_owner_name",
                 y="total_revenue",
                 color="conversion_rate",
                 title="Sales Revenue by Deal Owner",
                 labels={"deal_owner_name": "Owner", "total_revenue": "Revenue (€)"},
                 text="won_deals")
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def plot_sales_by_campaign(df_campaign):
    df = df_campaign.reset_index().sort_values(by="total_revenue", ascending=False).head(15)
    fig = px.bar(df,
                 x="campaign",
                 y="total_revenue",
                 color="conversion_rate",
                 title="Sales Revenue by Campaign (Top 15)",
                 labels={"campaign": "Campaign", "total_revenue": "Revenue (€)"},
                 text="won_deals")
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

import plotly.express as px
import pandas as pd

def plot_city_conversion(df):
    df = df.reset_index().sort_values("conversion_rate", ascending=False).head(15)
    fig = px.bar(df, x="city", y="conversion_rate",
                 text="total_deals",
                 title="Conversion Rate by City",
                 labels={"conversion_rate": "Conversion Rate", "city": "City"})
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def plot_city_revenue_map(df):
    city_coords = {
        "Berlin": [52.52, 13.405],
        "München": [48.137, 11.575],
        "Hamburg": [53.55, 10.0],
        "Köln": [50.94, 6.96],
        "Frankfurt": [50.11, 8.68],
        "Leipzig": [51.34, 12.37],
        "Dresden": [51.05, 13.74],
        "Nürnberg": [49.45, 11.08],
        "Stuttgart": [48.78, 9.18],
        "Düsseldorf": [51.23, 6.78],
        "Hannover": [52.37, 9.73],
        "Dortmund": [51.51, 7.46],
        "Bremen": [53.08, 8.80],
        "Duisburg": [51.43, 6.76]
    }

    df_plot = df.reset_index()
    df_plot = df_plot[df_plot["city"].isin(city_coords)]
    df_plot["lat"] = df_plot["city"].map(lambda c: city_coords[c][0])
    df_plot["lon"] = df_plot["city"].map(lambda c: city_coords[c][1])

    fig = px.scatter_mapbox(df_plot,
                            lat="lat", lon="lon",
                            size="revenue",
                            hover_name="city",
                            color="conversion_rate",
                            color_continuous_scale="Viridis",
                            size_max=30,
                            zoom=5,
                            title="Revenue by City (Bubble Size)")

    fig.update_layout(mapbox_style="open-street-map")
    fig.show()

def plot_language_conversion(df):
    df = df.copy()
    df = df[df["level_of_deutsch"].notna()]
    grouped = df.groupby("level_of_deutsch").agg(
        total_deals=("id", "count"),
        won_deals=("stage", lambda x: (x.str.lower().str.strip() == "payment done").sum())
    )
    grouped["conversion_rate"] = grouped["won_deals"] / grouped["total_deals"]
    grouped = grouped.reset_index().sort_values("conversion_rate", ascending=False).head(15)

    fig = px.bar(grouped,
                 x="level_of_deutsch",
                 y="conversion_rate",
                 text="total_deals",
                 title="Conversion Rate by Language Level",
                 labels={"level_of_deutsch": "Language Level", "conversion_rate": "Conversion Rate"})
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

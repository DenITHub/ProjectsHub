from dash import Input, Output
import plotly.express as px
import pandas as pd

def register_callbacks(app, deals: pd.DataFrame, contacts: pd.DataFrame, calls: pd.DataFrame):
    """Регистрирует все коллбэки приложения."""

    def _filter(dff, year, product):
        if year is not None and "created_time" in dff.columns:
            dff = dff[dff["created_time"].dt.year == year]
        if product:
            dff = dff[dff["product"] == product]
        return dff

    @app.callback(
        Output("owner-sales-chart", "figure"),
        Input("year-dropdown", "value"),
        Input("product-dropdown", "value"),
    )
    def update_owner_sales(year, product):
        dff = _filter(deals, year, product)
        if dff.empty:
            return px.bar(title="No data for selected filters")
        grouped = (
            dff.groupby("owner")[["id", "offer_total_amount"]]
               .agg(deals=("id","count"), revenue=("offer_total_amount","sum"))
               .reset_index()
               .sort_values("revenue", ascending=False)
        )
        return px.bar(grouped, x="owner", y="revenue", color="deals",
                      title="Sales by Owner")

    @app.callback(
        Output("campaign-performance", "figure"),
        Input("year-dropdown", "value"),
        Input("product-dropdown", "value"),
    )
    def update_campaigns(year, product):
        dff = _filter(deals, year, product)
        if dff.empty:
            return px.bar(title="No data for selected filters")
        grouped = (
            dff.groupby("campaign")[["id", "offer_total_amount"]]
               .agg(deals=("id","count"), revenue=("offer_total_amount","sum"))
               .reset_index()
               .sort_values("revenue", ascending=False)
               .head(20)
        )
        return px.bar(grouped, x="campaign", y="revenue", color="deals",
                      title="Campaign Performance")

    @app.callback(
        Output("payment-types", "figure"),
        Input("year-dropdown", "value"),
        Input("product-dropdown", "value"),
    )
    def update_payment_types(year, product):
        dff = _filter(deals, year, product)
        if dff.empty:
            return px.histogram(title="No data for selected filters")
        return px.histogram(dff, x="payment_type", color="stage",
                            title="Payment Types")

    @app.callback(
        Output("products", "figure"),
        Input("year-dropdown", "value"),
        Input("product-dropdown", "value"),
    )
    def update_products(year, product):
        dff = _filter(deals, year, product)
        if dff.empty:
            return px.histogram(title="No data for selected filters")
        return px.histogram(dff, x="product", color="stage",
                            title="Product Breakdown")

    @app.callback(
        Output("education-types", "figure"),
        Input("year-dropdown", "value"),
        Input("product-dropdown", "value"),
    )
    def update_education_types(year, product):
        dff = _filter(deals, year, product)
        if dff.empty:
            return px.histogram(title="No data for selected filters")
        return px.histogram(dff, x="education_type", color="stage",
                            title="Education Types")

    @app.callback(
        Output("city-bar", "figure"),
        Input("year-dropdown", "value"),
        Input("product-dropdown", "value"),
    )
    def update_city_bar(year, product):
        dff = _filter(deals, year, product)
        if dff.empty:
            return px.bar(title="No data for selected filters")
        grouped = (
            dff.groupby("city")[["id", "offer_total_amount"]]
               .agg(deals=("id","count"), revenue=("offer_total_amount","sum"))
               .reset_index()
               .sort_values("revenue", ascending=False)
        )
        return px.bar(grouped, x="city", y="revenue", color="deals",
                      title="Deals by City")

    @app.callback(
        Output("language-bar", "figure"),
        Input("year-dropdown", "value"),
        Input("product-dropdown", "value"),
    )
    def update_language_bar(year, product):
        dff = _filter(deals, year, product)
        if dff.empty:
            return px.histogram(title="No data for selected filters")
        return px.histogram(dff, x="level_of_deutsch", color="stage",
                            title="Language Levels")





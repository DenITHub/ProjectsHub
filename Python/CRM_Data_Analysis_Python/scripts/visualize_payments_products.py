import plotly.express as px

def plot_payment_types(df):
    df = df.reset_index().sort_values("conversion_rate", ascending=False)
    fig = px.bar(df, x="payment_type", y="conversion_rate",
                 color="revenue", text="won_deals",
                 title="Conversion Rate by Payment Type",
                 labels={"conversion_rate": "Conversion Rate", "payment_type": "Payment Type"})
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def plot_product_revenue(df):
    df = df.reset_index().sort_values("revenue", ascending=False).head(10)
    fig = px.bar(df, x="product", y="revenue",
                 color="conversion_rate", text="won_deals",
                 title="Revenue by Product",
                 labels={"product": "Product", "revenue": "Revenue (€)"})
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

def plot_education_conversion(df):
    df = df.reset_index().sort_values("conversion_rate", ascending=False)
    fig = px.bar(df, x="education_type", y="conversion_rate",
                 color="revenue", text="won_deals",
                 title="Conversion Rate by Education Type",
                 labels={"education_type": "Education Type", "conversion_rate": "Conversion Rate"})
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

from dash import html, dcc

def make_layout(df):
    years = sorted(df["created_time"].dt.year.dropna().unique().tolist())
    products = sorted(df["product"].dropna().unique().tolist())

    return html.Div([
        # Фильтры
        html.Div([
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in years],
                value=years[-1] if years else None,
                clearable=False,
                style={"width": 180, "display": "inline-block", "marginRight": 12}
            ),
            dcc.Dropdown(
                id="product-dropdown",
                options=[{"label": p, "value": p} for p in products],
                value=None,
                placeholder="All products",
                clearable=True,
                style={"width": 260, "display": "inline-block"}
            ),
        ], style={"marginBottom": 16}),

        # Вкладки + графики
        dcc.Tabs([
            dcc.Tab(label="Sales by Owner",
                    children=[dcc.Graph(id="owner-sales-chart")]),
            dcc.Tab(label="Campaigns",
                    children=[dcc.Graph(id="campaign-performance")]),
            dcc.Tab(label="Payment Types",
                    children=[dcc.Graph(id="payment-types")]),
            dcc.Tab(label="Products & Education",
                    children=[dcc.Graph(id="products"),
                              dcc.Graph(id="education-types")]),
            dcc.Tab(label="Geography",
                    children=[dcc.Graph(id="city-bar"),
                              dcc.Graph(id="language-bar")]),
        ])
    ], style={"padding": 16})
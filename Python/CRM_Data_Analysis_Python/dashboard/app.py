from dash import Dash
from data_loader import load_data
from layout import make_layout
from callbacks import register_callbacks

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "CRM Sales Dashboard"

deals, contacts, calls, spend = load_data()

app.layout = make_layout(deals)
register_callbacks(app, deals, contacts, calls)

if __name__ == "__main__":
    app.run(debug=True)





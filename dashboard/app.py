import logging

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output

from components.layout import app_layout
from utils.data_loader import load_dashboard_data

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
LOGGER = logging.getLogger("bankiq")

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="BankIQ Customer Intelligence",
)
server = app.server
app.layout = app_layout


@app.callback(Output("data-health-pill", "children"), Input("url", "pathname"))
def data_health(_):
    try:
        data = load_dashboard_data()
        status = "Verified" if data["row_count_ok"] and data["duplicate_count"] == 0 else "Review"
        return f"{status}: {data['row_count']:,} customers"
    except Exception as exc:
        LOGGER.exception("Data health check failed")
        return f"Data issue: {exc}"


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)

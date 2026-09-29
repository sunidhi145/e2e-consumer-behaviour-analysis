import dash
from dash import ALL, Input, Output, callback, dcc, html

from config import APP_TITLE, PAGE_PATHS


def sidebar():
    items = []
    for label, path in PAGE_PATHS.items():
        items.append(
            dcc.Link(
                label,
                href=path,
                id={"type": "nav-link", "path": path},
                className="nav-link",
            )
        )
    return html.Aside(
        [
            html.Div("BankIQ", className="brand-mark"),
            html.Div("Customer Intelligence", className="brand-subtitle"),
            html.Nav(items, className="nav-stack"),
            html.Div(
                [
                    html.Div("Data Refresh", className="utility-link"),
                    html.Div("Exports", className="utility-link"),
                    html.Div("About Project", className="utility-link"),
                ],
                className="sidebar-footer",
            ),
        ],
        className="sidebar",
    )


def app_layout():
    return html.Div(
        [
            dcc.Location(id="url"),
            dcc.Store(id="selected-customer-store"),
            dcc.Store(id="selected-cluster-store"),
            sidebar(),
            html.Main(
                [
                    html.Div(
                        [
                            html.Div([html.H1(APP_TITLE), html.P("K-Means segmentation command center")], className="topbar-copy"),
                            html.Div(id="data-health-pill", className="health-pill"),
                        ],
                        className="topbar",
                    ),
                    dash.page_container,
                ],
                className="content",
            ),
        ],
        className="app-shell",
    )


@callback(Output({"type": "nav-link", "path": ALL}, "className"), Input("url", "pathname"))
def highlight_active_nav(pathname):
    current_path = pathname or "/"
    return [f"nav-link{' active' if path == current_path else ''}" for path in PAGE_PATHS.values()]

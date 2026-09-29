import dash
import pandas as pd
from dash import Input, Output, State, callback, dcc, html

from components.business_panels import segment_business_panel
from components.cards import feature_card, segment_badge
from components.charts import feature_distribution, radar_for_customer
from components.loaders import empty_state, skeleton_cards, staged_loader
from utils.analytics import nearest_customers, percentile, top_features
from utils.data_loader import load_dashboard_data
from utils.formatting import display_value, humanize_column

dash.register_page(__name__, path="/customer-explorer", name="Customer Explorer", title="BankIQ Customer Explorer")

MESSAGES = [
    "Searching customer records...",
    "Retrieving behavioural features...",
    "Comparing customer with assigned segment...",
    "Computing customer insights...",
    "Generating business recommendations...",
    "Customer profile ready",
]


def layout():
    data = load_dashboard_data()
    ids = data["customers"][data["id_col"]].astype(str).sort_values().tolist()
    return html.Div(
        [
            dcc.Store(id="customer-pending-store"),
            dcc.Store(id="customer-active-store"),
            dcc.Store(id="customer-feature-store"),
            dcc.Interval(id="customer-search-interval", interval=240, n_intervals=0, max_intervals=len(MESSAGES), disabled=True),
            html.Section(
                [
                    html.Div(
                        [
                            html.Label("Customer ID", htmlFor="customer-id-input"),
                            dcc.Dropdown(id="customer-id-input", options=[{"label": i, "value": i} for i in ids], placeholder="Search customer ID", className="dark-dropdown customer-id-dropdown"),
                        ],
                        className="input-wrap",
                    ),
                    html.Button("Search Customer", id="customer-search-button", className="primary-button", n_clicks=0),
                    html.Button("Random Customer", id="customer-random-button", className="secondary-button", n_clicks=0),
                ],
                className="search-strip glass-panel",
            ),
            html.Div(id="customer-warning", className="warning"),
            staged_loader("customer-staged-loader", MESSAGES),
            html.Div(id="customer-empty", children=[empty_state("Select a customer and click Search to begin"), skeleton_cards(3)]),
            html.Div(id="customer-results", className="hidden"),
            dcc.Download(id="customer-download"),
            html.Div(id="metric-modal", className="modal-host"),
        ],
        className="page page-enter",
    )


@callback(Output("customer-id-input", "value"), Input("customer-random-button", "n_clicks"), prevent_initial_call=True)
def random_customer(_):
    data = load_dashboard_data()
    return data["customers"].sample(1, random_state=None)[data["id_col"]].iloc[0]


@callback(
    Output("customer-pending-store", "data"),
    Output("customer-search-interval", "disabled"),
    Output("customer-search-interval", "n_intervals"),
    Output("customer-warning", "children"),
    Output("customer-staged-loader", "className"),
    Input("customer-search-button", "n_clicks"),
    State("customer-id-input", "value"),
    prevent_initial_call=True,
)
def start_search(_, customer_id):
    data = load_dashboard_data()
    if not customer_id or str(customer_id) not in set(data["customers"][data["id_col"]].astype(str)):
        return dash.no_update, True, 0, "Invalid customer ID. Select a customer from the available records.", "staged-loader"
    return str(customer_id), False, 0, "", "staged-loader is-active"


@callback(
    Output("customer-staged-loader-message", "children"),
    Output("customer-staged-loader-bar", "style"),
    Output("customer-active-store", "data"),
    Output("customer-search-interval", "disabled", allow_duplicate=True),
    Output("customer-staged-loader", "className", allow_duplicate=True),
    Input("customer-search-interval", "n_intervals"),
    State("customer-pending-store", "data"),
    prevent_initial_call=True,
)
def progress_search(n, customer_id):
    idx = min(max(n - 1, 0), len(MESSAGES) - 1)
    width = f"{int((n / len(MESSAGES)) * 100)}%"
    if n >= len(MESSAGES):
        return MESSAGES[-1], {"width": "100%"}, customer_id, True, "staged-loader"
    return MESSAGES[idx], {"width": width}, dash.no_update, False, "staged-loader is-active"


@callback(
    Output("customer-empty", "className"),
    Output("customer-results", "children"),
    Output("customer-results", "className"),
    Input("customer-active-store", "data"),
)
def render_customer(customer_id):
    if not customer_id:
        return "", "", "hidden"
    data = load_dashboard_data()
    df = data["customers"]
    id_col, cluster_col, segment_col = data["id_col"], data["cluster_col"], data["segment_col"]
    match = df[df[id_col].astype(str) == str(customer_id)]
    if match.empty:
        return "hidden", html.Div("Invalid customer ID.", className="warning"), ""
    row = match.iloc[0]
    segment = row[segment_col]
    features = top_features(df, data["features"], 6)
    segment_avg = df[df[segment_col] == segment][features].apply(pd.to_numeric, errors="coerce").mean()
    overall_avg = df[features].apply(pd.to_numeric, errors="coerce").mean()
    return (
        "hidden",
        html.Div(
            [
                html.Section(
                    [
                        html.Div([html.Div("Customer ID", className="kpi-label"), html.H2(str(row[id_col])), segment_badge(segment)], className="customer-identity glass-panel"),
                        html.Div([html.Div("Cluster", className="kpi-label"), html.H2(f"Cluster {row[cluster_col]}")], className="glass-panel compact-summary"),
                        html.Div([feature_card(humanize_column(f), row[f], {"type": "metric-card", "feature": f}) for f in features], className="feature-grid"),
                    ],
                    className="customer-summary-grid",
                ),
                html.Section(html.Div([html.H2("Customer vs Segment"), dcc.Graph(figure=radar_for_customer(row, segment_avg, overall_avg, features))], className="glass-panel"), className="single-col"),
                dcc.Tabs(
                    id="customer-tabs",
                    value="profile",
                    className="bankiq-tabs",
                    children=[
                        dcc.Tab(label="Profile", value="profile"),
                        dcc.Tab(label="Business Value", value="business"),
                        dcc.Tab(label="Recommendations", value="recommendations"),
                        dcc.Tab(label="All Features", value="all"),
                        dcc.Tab(label="Similar Customers", value="similar"),
                    ],
                ),
                html.Div(id="customer-tab-content", className="tab-content-region"),
            ]
        ),
        "",
    )


@callback(Output("customer-tab-content", "children"), Input("customer-tabs", "value"), State("customer-active-store", "data"), prevent_initial_call=True)
def render_customer_tab(tab, customer_id):
    data = load_dashboard_data()
    df = data["customers"]
    id_col, cluster_col, segment_col = data["id_col"], data["cluster_col"], data["segment_col"]
    row = df[df[id_col].astype(str) == str(customer_id)].iloc[0]
    segment = row[segment_col]
    if tab == "business":
        return segment_business_panel(segment)
    if tab == "recommendations":
        return segment_business_panel(segment)
    if tab == "all":
        return html.Div(
            [
                html.H2("All Features"),
                html.Table([html.Tr([html.Th("Feature"), html.Th("Value")])] + [html.Tr([html.Td(humanize_column(c)), html.Td(display_value(row[c]))]) for c in df.columns], className="feature-table"),
                html.Button("Download selected customer summary", id="download-customer-summary", className="secondary-button", n_clicks=0),
            ],
            className="glass-panel",
        )
    if tab == "similar":
        similar = nearest_customers(df, customer_id, data["features"], id_col, cluster_col, 5)
        if similar.empty:
            return html.Div("No similar customers found inside this assigned cluster.", className="glass-panel muted")
        cols = [id_col, cluster_col, segment_col, "standardized_feature_distance"] + top_features(df, data["features"], 4)
        return html.Div(
            [
                html.H2("Similar Customers"),
                html.P("Similarity based on standardized feature distance.", className="muted"),
                html.Table([html.Tr([html.Th(humanize_column(c)) for c in cols])] + [html.Tr([html.Td(display_value(r[c])) for c in cols]) for _, r in similar[cols].iterrows()], className="feature-table"),
            ],
            className="glass-panel",
        )
    features = top_features(df, data["features"], 6)
    seg_avg = df[df[segment_col] == segment][features].apply(pd.to_numeric, errors="coerce").mean()
    overall_avg = df[features].apply(pd.to_numeric, errors="coerce").mean()
    return html.Div(
        [
            html.H2("Profile Comparison"),
            html.Table(
                [html.Tr([html.Th("Feature"), html.Th("Customer"), html.Th("Segment Avg"), html.Th("Overall Avg"), html.Th("Percentile")])]
                + [
                    html.Tr(
                        [
                            html.Td(humanize_column(f)),
                            html.Td(display_value(row[f])),
                            html.Td(display_value(seg_avg[f])),
                            html.Td(display_value(overall_avg[f])),
                            html.Td(display_value(percentile(df[f], pd.to_numeric(pd.Series([row[f]]), errors="coerce").iloc[0]))),
                        ]
                    )
                    for f in features
                ],
                className="feature-table",
            ),
        ],
        className="glass-panel",
    )


@callback(
    Output("metric-modal", "children"),
    Input({"type": "metric-card", "feature": dash.ALL}, "n_clicks"),
    State("customer-active-store", "data"),
    prevent_initial_call=True,
)
def metric_modal(clicks, customer_id):
    if not dash.ctx.triggered_id or not customer_id:
        return ""
    feature = dash.ctx.triggered_id["feature"]
    data = load_dashboard_data()
    df = data["customers"]
    id_col, segment_col = data["id_col"], data["segment_col"]
    row = df[df[id_col].astype(str) == str(customer_id)].iloc[0]
    segment = row[segment_col]
    value = pd.to_numeric(pd.Series([row[feature]]), errors="coerce").iloc[0]
    seg_avg = pd.to_numeric(df.loc[df[segment_col] == segment, feature], errors="coerce").mean()
    overall = pd.to_numeric(df[feature], errors="coerce").mean()
    return html.Div(
        [
            html.Div(className="modal-backdrop"),
            html.Div(
                [
                    html.H2(humanize_column(feature)),
                    html.P("Calculating comparison... Computing percentile... Preparing feature insight...", className="muted"),
                    html.Div([feature_card("Customer Value", value), feature_card("Segment Average", seg_avg), feature_card("Overall Average", overall), feature_card("Difference From Segment", value - seg_avg)], className="feature-grid"),
                    dcc.Graph(figure=feature_distribution(df, feature, segment_col, "Box")),
                    html.Button("Close", id="close-metric-modal", className="secondary-button", n_clicks=0),
                ],
                className="modal-panel",
            ),
        ],
        className="modal-shell",
    )


@callback(Output("metric-modal", "children", allow_duplicate=True), Input("close-metric-modal", "n_clicks"), prevent_initial_call=True)
def close_modal(_):
    return ""

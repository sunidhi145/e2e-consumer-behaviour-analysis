import dash
from dash import Input, Output, State, callback, dcc, html

from components.business_panels import segment_business_panel
from components.cards import cluster_card, feature_card, segment_badge
from components.loaders import empty_state, skeleton_cards, staged_loader
from components.tables import customer_grid
from utils.analytics import top_features
from utils.data_loader import load_dashboard_data
from utils.formatting import display_value, humanize_column

dash.register_page(__name__, path="/cluster-explorer", name="Cluster Explorer", title="BankIQ Cluster Explorer")

MESSAGES = [
    "Loading selected cluster...",
    "Analysing customer behaviour...",
    "Summarising key characteristics...",
    "Identifying business opportunities...",
    "Preparing customer records...",
    "Cluster analysis ready",
]


def _cluster_summary(data):
    df = data["customers"]
    cluster_col, segment_col, id_col = data["cluster_col"], data["segment_col"], data["id_col"]
    summary = df.groupby([cluster_col, segment_col], as_index=False)[id_col].count().rename(columns={id_col: "customer_count"})
    summary["percentage"] = summary["customer_count"] / len(df) * 100
    return summary.sort_values(cluster_col)


def layout():
    data = load_dashboard_data()
    clusters = _cluster_summary(data)
    return html.Div(
        [
            dcc.Store(id="cluster-selected-store"),
            dcc.Store(id="cluster-active-store"),
            dcc.Interval(id="cluster-load-interval", interval=180, n_intervals=0, max_intervals=len(MESSAGES), disabled=True),
            html.Section(
                [cluster_card(r[data["cluster_col"]], r[data["segment_col"]], r["customer_count"], r["percentage"]) for _, r in clusters.iterrows()],
                className="cluster-card-grid",
            ),
            html.Div(id="cluster-selected-label", className="selected-label"),
            html.Button("View Cluster Insights", id="view-cluster-button", className="primary-button", n_clicks=0),
            staged_loader("cluster-staged-loader", MESSAGES),
            html.Div(id="cluster-empty", children=[empty_state("Select a cluster and click View Cluster Insights"), skeleton_cards(3)]),
            html.Div(id="cluster-results", className="hidden"),
            dcc.Download(id="cluster-download"),
        ],
        className="page page-enter",
    )


@callback(
    Output("cluster-selected-store", "data"),
    Output("cluster-selected-label", "children"),
    Input({"type": "cluster-card", "cluster": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def select_cluster(_):
    if not dash.ctx.triggered_id:
        return dash.no_update, dash.no_update
    cluster = dash.ctx.triggered_id["cluster"]
    return cluster, f"Selected Cluster {cluster}"


@callback(
    Output("cluster-load-interval", "disabled"),
    Output("cluster-load-interval", "n_intervals"),
    Output("cluster-staged-loader", "className"),
    Input("view-cluster-button", "n_clicks"),
    State("cluster-selected-store", "data"),
    prevent_initial_call=True,
)
def start_cluster_load(_, cluster):
    if not cluster:
        return True, 0, "staged-loader"
    return False, 0, "staged-loader is-active"


@callback(
    Output("cluster-staged-loader-message", "children"),
    Output("cluster-staged-loader-bar", "style"),
    Output("cluster-active-store", "data"),
    Output("cluster-load-interval", "disabled", allow_duplicate=True),
    Output("cluster-staged-loader", "className", allow_duplicate=True),
    Input("cluster-load-interval", "n_intervals"),
    State("cluster-selected-store", "data"),
    prevent_initial_call=True,
)
def progress_cluster(n, cluster):
    idx = min(max(n - 1, 0), len(MESSAGES) - 1)
    if n >= len(MESSAGES):
        return MESSAGES[-1], {"width": "100%"}, cluster, True, "staged-loader"
    return MESSAGES[idx], {"width": f"{int((n / len(MESSAGES)) * 100)}%"}, dash.no_update, False, "staged-loader is-active"


@callback(
    Output("cluster-empty", "className"),
    Output("cluster-results", "children"),
    Output("cluster-results", "className"),
    Input("cluster-active-store", "data"),
)
def render_cluster(cluster):
    if cluster is None:
        return "", "", "hidden"
    data = load_dashboard_data()
    df = data["customers"]
    cluster_col, segment_col = data["cluster_col"], data["segment_col"]
    cluster_df = df[df[cluster_col].astype(str) == str(cluster)]
    if cluster_df.empty:
        return "hidden", html.Div("Empty cluster.", className="warning"), ""
    segment = cluster_df[segment_col].mode().iloc[0]
    features = top_features(df, data["features"], 6)
    averages = cluster_df[features].mean(numeric_only=True)
    return (
        "hidden",
        html.Div(
            [
                html.Section(
                    [
                        html.Div([segment_badge(segment), html.H2(f"Cluster {cluster}")], className="glass-panel compact-summary"),
                        feature_card("Customer Count", len(cluster_df)),
                        feature_card("Percentage", len(cluster_df) / len(df) * 100),
                        *[feature_card(humanize_column(f), averages[f]) for f in features[:4]],
                    ],
                    className="cluster-summary-grid",
                ),
                segment_business_panel(segment),
                dcc.Tabs(
                    id="cluster-tabs",
                    value="customers",
                    className="bankiq-tabs",
                    children=[
                        dcc.Tab(label="Customers", value="customers"),
                        dcc.Tab(label="Feature Summary", value="features"),
                        dcc.Tab(label="Opportunities", value="opportunities"),
                        dcc.Tab(label="Export", value="export"),
                    ],
                ),
                html.Div(id="cluster-tab-content", className="tab-content-region"),
            ]
        ),
        "",
    )


@callback(Output("cluster-tab-content", "children"), Input("cluster-tabs", "value"), State("cluster-active-store", "data"), prevent_initial_call=True)
def render_cluster_tab(tab, cluster):
    data = load_dashboard_data()
    df = data["customers"]
    cluster_col, segment_col, id_col = data["cluster_col"], data["segment_col"], data["id_col"]
    cluster_df = df[df[cluster_col].astype(str) == str(cluster)].copy()
    if cluster_df.empty:
        return html.Div("Empty cluster.", className="warning")
    segment = cluster_df[segment_col].mode().iloc[0]
    if tab == "features":
        features = top_features(df, data["features"], 10)
        averages = cluster_df[features].mean(numeric_only=True)
        return html.Div(
            [
                html.H2("Feature Summary"),
                html.Table([html.Tr([html.Th("Feature"), html.Th("Average")])] + [html.Tr([html.Td(humanize_column(f)), html.Td(display_value(averages[f]))]) for f in features], className="feature-table"),
            ],
            className="glass-panel",
        )
    if tab == "opportunities":
        return segment_business_panel(segment)
    if tab == "export":
        return html.Div([html.H2("Export"), html.Button("Export selected cluster to CSV", id="download-cluster-button", className="primary-button", n_clicks=0)], className="glass-panel")
    visible_cols = [id_col, cluster_col, segment_col] + top_features(df, data["features"], 9)
    return html.Div([html.P("Applying filters... Updating customer records...", className="table-note"), customer_grid(cluster_df[visible_cols], id_col)], className="glass-panel")


@callback(Output("cluster-download", "data"), Input("download-cluster-button", "n_clicks"), State("cluster-active-store", "data"), prevent_initial_call=True)
def download_cluster(_, cluster):
    data = load_dashboard_data()
    df = data["customers"]
    cluster_df = df[df[data["cluster_col"]].astype(str) == str(cluster)]
    return dcc.send_data_frame(cluster_df.to_csv, f"bankiq_cluster_{cluster}_customers.csv", index=False)


@callback(Output("selected-customer-store", "data", allow_duplicate=True), Input("cluster-customer-grid", "selectedRows"), prevent_initial_call=True)
def grid_customer_selected(rows):
    if not rows:
        return dash.no_update
    data = load_dashboard_data()
    return str(rows[0].get(data["id_col"]))

import dash
from dash import Input, Output, callback, dcc, html

from components.charts import cluster_bubble, feature_distribution, parallel_coordinates, profile_heatmap, radar_for_customer
from components.pca_viewer import pca_viewer
from components.loaders import staged_loader
from utils.analytics import top_features
from utils.data_loader import load_dashboard_data
from utils.formatting import humanize_column

dash.register_page(__name__, path="/advanced-analytics", name="Advanced Analytics", title="BankIQ Advanced Analytics")

MESSAGES = [
    "Launching analytics workspace...",
    "Preparing customer matrix...",
    "Computing principal components...",
    "Projecting multidimensional data...",
    "Rendering interactive visualisations...",
    "Analysis ready",
]


def layout():
    data = load_dashboard_data()
    features = data["features"]
    clusters = ["All"] + sorted(data["customers"][data["cluster_col"]].astype(str).unique().tolist())
    return html.Div(
        [
            dcc.Interval(id="advanced-init-interval", interval=250, n_intervals=0, max_intervals=len(MESSAGES), disabled=False),
            dcc.Store(id="advanced-ready-store"),
            staged_loader("advanced-staged-loader", MESSAGES, active=True),
            dcc.Tabs(
                id="advanced-tabs",
                value="3d",
                className="bankiq-tabs",
                children=[
                    dcc.Tab(label="3D Cluster Space", value="3d"),
                    dcc.Tab(label="Feature Explorer", value="feature"),
                    dcc.Tab(label="Comparisons", value="comparisons"),
                    dcc.Tab(label="Distributions", value="distributions"),
                ],
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Cluster Filter"),
                            dcc.Dropdown(id="advanced-cluster-filter", options=[{"label": c, "value": c} for c in clusters], value="All", className="dark-dropdown"),
                        ],
                        className="input-wrap",
                    ),
                    html.Div(
                        [
                            html.Label("Feature"),
                            dcc.Dropdown(id="advanced-feature", options=[{"label": humanize_column(f), "value": f} for f in features], value=features[0], className="dark-dropdown"),
                        ],
                        className="input-wrap",
                    ),
                    html.Div(
                        [
                            html.Label("Chart Type"),
                            dcc.Dropdown(id="advanced-chart-type", options=["Histogram", "Box", "Violin"], value="Histogram", className="dark-dropdown"),
                        ],
                        className="input-wrap",
                    ),
                ],
                className="search-strip glass-panel",
            ),
            html.Div(id="advanced-content", className="tab-content-region"),
        ],
        className="page page-enter",
    )


@callback(
    Output("advanced-staged-loader-message", "children"),
    Output("advanced-staged-loader-bar", "style"),
    Output("advanced-staged-loader", "className"),
    Output("advanced-ready-store", "data"),
    Input("advanced-init-interval", "n_intervals"),
)
def init_progress(n):
    idx = min(max(n - 1, 0), len(MESSAGES) - 1)
    if n >= len(MESSAGES):
        return MESSAGES[-1], {"width": "100%"}, "staged-loader", True
    return MESSAGES[idx], {"width": f"{int((n / len(MESSAGES)) * 100)}%"}, "staged-loader is-active", False


@callback(
    Output("advanced-content", "children"),
    Input("advanced-tabs", "value"),
    Input("advanced-cluster-filter", "value"),
    Input("advanced-feature", "value"),
    Input("advanced-chart-type", "value"),
)
def render_advanced(tab, cluster_filter, feature, chart_type):
    data = load_dashboard_data()
    df = data["customers"]
    if tab == "feature":
        return html.Div([html.H2("Feature Distribution"), html.P("Loading feature distribution... Comparing segment patterns... Updating visualization...", className="muted"), dcc.Graph(figure=feature_distribution(df, feature, data["segment_col"], chart_type))], className="glass-panel")
    if tab == "comparisons":
        profiles = data["profiles"]
        first = df.iloc[0]
        features = top_features(df, data["features"], 6)
        seg_avg = df[df[data["segment_col"]] == first[data["segment_col"]]][features].mean(numeric_only=True)
        overall = df[features].mean(numeric_only=True)
        return html.Div(
            [
                html.Div([html.H2("Radar Comparison"), dcc.Graph(figure=radar_for_customer(first, seg_avg, overall, features))], className="glass-panel"),
                html.Div([html.H2("Parallel Coordinates"), dcc.Graph(figure=parallel_coordinates(profiles, data["cluster_col"], data["segment_col"], data["features"]))], className="glass-panel"),
            ],
            className="two-col",
        )
    if tab == "distributions":
        return html.Div(
            [
                html.Div([html.H2("Standardized Cluster Heatmap"), dcc.Graph(figure=profile_heatmap(data["profiles"], data["cluster_col"], data["segment_col"], data["features"]))], className="glass-panel"),
                html.Div([html.H2("3D Cluster Bubble Chart"), dcc.Graph(figure=cluster_bubble(data["profiles"], data["features"], data["cluster_col"], data["segment_col"]))], className="glass-panel"),
            ],
            className="two-col",
        )
    return html.Div(
        [
            html.H2("3D PCA Cluster Space"),
            html.P("Drag to rotate, scroll to zoom, and hover for customer details. Use Reset view to restore the camera. Centroids are shown with X markers.", className="muted"),
            pca_viewer(data["pca"], data["id_col"], data["cluster_col"], data["segment_col"], cluster_filter),
        ],
        className="glass-panel analytics-3d",
    )

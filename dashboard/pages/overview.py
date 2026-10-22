import dash
from dash import Input, Output, State, callback, dcc, html

from components.business_panels import segment_business_panel
from components.cards import kpi_card
from components.charts import cluster_bar, parallel_coordinates, pca_2d, profile_heatmap, segment_donut
from utils.data_loader import load_dashboard_data
from utils.formatting import format_number, humanize_column

dash.register_page(__name__, path="/", name="Executive Overview", title="BankIQ Overview")


def _silhouette(data):
    eval_df = data["evaluation"]
    if eval_df is None:
        return "N/A"
    metric_col = eval_df.columns[0]
    value_col = eval_df.columns[1]
    mask = eval_df[metric_col].astype(str).str.contains("silhouette", case=False, na=False)
    if mask.any():
        return format_number(eval_df.loc[mask, value_col].iloc[0], 3)
    return "N/A"


def layout():
    data = load_dashboard_data()
    customers = data["customers"]
    cluster_col = data["cluster_col"]
    segment_col = data["segment_col"]
    distribution = data["distribution"]
    largest = distribution.sort_values("customer_count", ascending=False).iloc[0]
    dormant_count = int(distribution.loc[distribution[segment_col].astype(str).eq("Dormant_At_Risk"), "customer_count"].sum()) if segment_col in distribution else 0
    return html.Div(
        [
            html.Section(
                [
                    kpi_card("Total Customers", data["row_count"], "#a855f7", "No duplicates detected" if data["duplicate_count"] == 0 else f"{data['duplicate_count']} duplicate IDs"),
                    kpi_card("Clusters", customers[cluster_col].nunique(), "#3b82f6", "K-Means groups"),
                    kpi_card("Largest Segment", str(largest[segment_col]).replace("_", " "), "#2dd4bf", f"{format_number(largest['customer_count'])} customers"),
                    kpi_card("Dormant At Risk", dormant_count, "#ef4444", "Retention focus"),
                    kpi_card("Silhouette Score", _silhouette(data), "#f59e0b", "Model evaluation"),
                ],
                className="kpi-grid",
            ),
            html.Section(
                [
                    html.Div([html.H2("Segment Mix"), dcc.Graph(figure=segment_donut(distribution, segment_col), config={"displayModeBar": False})], className="glass-panel"),
                    html.Div([html.H2("Cluster Size"), dcc.Graph(figure=cluster_bar(customers, cluster_col, segment_col), config={"displayModeBar": False})], className="glass-panel"),
                ],
                className="two-col",
            ),
            html.Section(
                [
                    html.Div([html.H2("PCA Customer Space"), dcc.Graph(id="overview-pca", figure=pca_2d(data["pca"], data["id_col"], cluster_col, segment_col))], className="glass-panel"),
                ],
                className="single-col",
            ),
            dcc.Tabs(
                id="overview-tabs",
                value="overview",
                className="bankiq-tabs",
                children=[
                    dcc.Tab(label="Overview", value="overview"),
                    dcc.Tab(label="Insights", value="insights"),
                    dcc.Tab(label="Model Evaluation", value="evaluation"),
                    dcc.Tab(label="Downloads", value="downloads"),
                ],
            ),
            html.Div(id="overview-tab-content", className="tab-content-region"),
            dcc.Download(id="overview-download"),
        ],
        className="page page-enter",
    )


@callback(Output("selected-customer-store", "data"), Input("overview-pca", "clickData"), prevent_initial_call=True)
def store_clicked_customer(click_data):
    if not click_data:
        return dash.no_update
    return str(click_data["points"][0]["customdata"][0])


@callback(Output("overview-tab-content", "children"), Input("overview-tabs", "value"))
def render_tab(tab):
    data = load_dashboard_data()
    if tab == "insights":
        panels = []
        for segment in data["distribution"][data["segment_col"]].tolist():
            panels.append(segment_business_panel(segment))
        return html.Div(panels, className="panel-grid")
    if tab == "evaluation":
        eval_df = data["evaluation"]
        if eval_df is None:
            return html.Div("No K-Means evaluation CSV was found.", className="glass-panel muted")
        return html.Div(
            [
                html.H2("Model Evaluation"),
                html.Div(
                    [html.Div([html.Span(str(row[eval_df.columns[0]])), html.Strong(format_number(row[eval_df.columns[1]], 4))], className="metric-row") for _, row in eval_df.iterrows()],
                    className="metric-list",
                ),
            ],
            className="glass-panel",
        )
    if tab == "downloads":
        return html.Div(
            [
                html.H2("Downloads"),
                html.Button("Complete clustered customer data", id="download-customers", className="primary-button", n_clicks=0),
                html.Button("Segment distribution report", id="download-distribution", className="secondary-button", n_clicks=0),
                html.Button("Cluster profile report", id="download-profiles", className="secondary-button", n_clicks=0),
            ],
            className="glass-panel action-row",
        )
    return html.Div(
        [
            html.Div([html.H2("Standardized Segment Profile"), dcc.Graph(figure=profile_heatmap(data["profiles"], data["cluster_col"], data["segment_col"], data["features"]))], className="glass-panel"),
            html.Div([html.H2("Compact Comparison"), dcc.Graph(figure=parallel_coordinates(data["profiles"], data["cluster_col"], data["segment_col"], data["features"]))], className="glass-panel"),
        ],
        className="two-col",
    )


@callback(
    Output("overview-download", "data"),
    Input("download-customers", "n_clicks"),
    Input("download-distribution", "n_clicks"),
    Input("download-profiles", "n_clicks"),
    prevent_initial_call=True,
)
def download_data(n_customers, n_dist, n_profiles):
    triggered = dash.ctx.triggered_id
    data = load_dashboard_data()
    if triggered == "download-customers":
        return dcc.send_data_frame(data["customers"].to_csv, "bankiq_clustered_customers.csv", index=False)
    if triggered == "download-distribution":
        return dcc.send_data_frame(data["distribution"].to_csv, "bankiq_segment_distribution.csv", index=False)
    if triggered == "download-profiles":
        return dcc.send_data_frame(data["profiles"].to_csv, "bankiq_cluster_profiles.csv", index=False)
    return dash.no_update

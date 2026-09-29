from dash import html

from config import SEGMENT_COLORS
from utils.formatting import display_value


def kpi_card(label, value, accent="#a855f7", detail=None):
    return html.Div(
        [
            html.Div(label, className="kpi-label"),
            html.Div(display_value(value), className="kpi-value count-up"),
            html.Div(detail or "", className="kpi-detail"),
        ],
        className="kpi-card card-fade",
        style={"--accent": accent},
    )


def feature_card(feature, value, card_id=None):
    props = {"id": card_id} if card_id is not None else {}
    return html.Button(
        [
            html.Span(feature, className="feature-label"),
            html.Span(display_value(value), className="feature-value"),
        ],
        className="feature-card card-fade",
        n_clicks=0,
        **props,
    )


def segment_badge(segment):
    return html.Span(str(segment), className="segment-badge", style={"--segment": SEGMENT_COLORS.get(str(segment), "#94a3b8")})


def cluster_card(cluster, segment, count, pct, selected=False):
    return html.Button(
        [
            html.Div(segment_badge(segment), className="cluster-card-top"),
            html.Div(f"Cluster {cluster}", className="cluster-id"),
            html.Div(f"{display_value(count)} customers", className="cluster-count"),
            html.Div(f"{display_value(pct)}%", className="cluster-pct"),
        ],
        id={"type": "cluster-card", "cluster": str(cluster)},
        className=f"cluster-card {'selected' if selected else ''}",
        n_clicks=0,
        style={"--segment": SEGMENT_COLORS.get(str(segment), "#94a3b8")},
    )

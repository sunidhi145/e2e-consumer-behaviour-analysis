from dash import html

from components.cards import segment_badge
from utils.segment_metadata import get_metadata


def segment_business_panel(segment):
    metadata = get_metadata(segment)
    return html.Div(
        [
            html.Div([segment_badge(segment), html.H3("Business Strategy")], className="panel-title-row"),
            html.P(metadata["profile"], className="muted"),
            html.H4("Business Value"),
            html.P(metadata["business_value"]),
            html.H4("Recommended Actions"),
            html.Ul([html.Li(action) for action in metadata["actions"]], className="action-list"),
        ],
        className="glass-panel card-fade",
    )

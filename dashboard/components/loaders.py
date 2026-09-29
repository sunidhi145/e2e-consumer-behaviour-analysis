from dash import html


def staged_loader(component_id, messages, active=False):
    return html.Div(
        [
            html.Div(className="loader-ring"),
            html.Div(id=f"{component_id}-message", className="loader-message", children=messages[0] if messages else "Loading..."),
            html.Div(className="progress-track", children=html.Div(id=f"{component_id}-bar", className="progress-fill")),
        ],
        id=component_id,
        className=f"staged-loader {'is-active' if active else ''}",
        **{"data-messages": "|".join(messages)},
    )


def skeleton_cards(count=3):
    return html.Div([html.Div(className="skeleton-card shimmer") for _ in range(count)], className="skeleton-grid")


def inline_loader(text="Loading..."):
    return html.Span([html.Span(className="inline-spinner"), html.Span(text)], className="inline-loader")


def empty_state(message):
    return html.Div(
        [
            html.Div("BIQ", className="empty-mark"),
            html.P(message, className="empty-message"),
        ],
        className="empty-state",
    )

from textwrap import wrap

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import PLOT_TEMPLATE, SEGMENT_COLORS
from utils.formatting import humanize_column


def apply_layout(fig, height=420):
    fig.update_layout(
        template=PLOT_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e5e7eb", "family": "Inter, Segoe UI, sans-serif"},
        margin={"l": 30, "r": 24, "t": 42, "b": 32},
        height=height,
        legend_title_text="",
        transition={"duration": 450, "easing": "cubic-in-out"},
    )
    return fig


def segment_donut(distribution, segment_col="segment"):
    fig = px.pie(
        distribution,
        values="customer_count",
        names=segment_col,
        hole=0.62,
        color=segment_col,
        color_discrete_map=SEGMENT_COLORS,
    )
    fig.update_traces(textposition="inside", textinfo="percent", pull=[0.02] * len(distribution))
    return apply_layout(fig, 360)


def cluster_bar(customers, cluster_col, segment_col):
    data = customers.groupby([cluster_col, segment_col], as_index=False).size().rename(columns={"size": "customer_count"})
    data = data.sort_values("customer_count", ascending=True)
    fig = px.bar(
        data,
        x="customer_count",
        y=cluster_col,
        color=segment_col,
        orientation="h",
        color_discrete_map=SEGMENT_COLORS,
        labels={"customer_count": "Customers", cluster_col: "Cluster"},
    )
    return apply_layout(fig, 360)


def pca_2d(pca_data, id_col, cluster_col, segment_col):
    points = pca_data["points"]
    centroids = pca_data["centroids"]
    fig = px.scatter(
        points,
        x="PC1",
        y="PC2",
        render_mode="svg",
        color=segment_col,
        color_discrete_map=SEGMENT_COLORS,
        custom_data=[id_col, cluster_col, segment_col],
        hover_data={id_col: True, cluster_col: True, segment_col: True, "PC1": ":.2f", "PC2": ":.2f"},
    )
    fig.add_trace(
        go.Scatter(
            x=centroids["PC1"],
            y=centroids["PC2"],
            mode="markers+text",
            marker={"symbol": "x", "size": 18, "color": "#f8fafc", "line": {"width": 2}},
            text=[f"C{c}" for c in centroids[cluster_col]],
            textposition="top center",
            name="Centroids",
        )
    )
    return apply_layout(fig, 440)


def pca_3d(pca_data, id_col, cluster_col, segment_col, cluster_filter="All"):
    points = pca_data["points"].copy()
    if cluster_filter != "All":
        points["_opacity"] = np.where(points[cluster_col].astype(str) == str(cluster_filter), 0.95, 0.12)
    else:
        points["_opacity"] = 0.82
    variance = pca_data["explained_variance"] + [0, 0, 0]
    fig = px.scatter_3d(
        points,
        x="PC1",
        y="PC2",
        z="PC3",
        color=segment_col,
        color_discrete_map=SEGMENT_COLORS,
        custom_data=[id_col, cluster_col, segment_col],
        hover_data={id_col: True, cluster_col: True, segment_col: True, "PC1": ":.2f", "PC2": ":.2f", "PC3": ":.2f", "_opacity": False},
        opacity=0.78,
    )
    centroids = pca_data["centroids"]
    fig.add_trace(
        go.Scatter3d(
            x=centroids["PC1"],
            y=centroids["PC2"],
            z=centroids["PC3"],
            mode="markers+text",
            marker={"symbol": "x", "size": 9, "color": "#f8fafc", "line": {"width": 4, "color": "#a855f7"}},
            text=[f"C{c}" for c in centroids[cluster_col]],
            name="Centroids",
        )
    )
    fig.update_layout(
        scene={
            "xaxis_title": f"PC1 ({variance[0] * 100:.1f}%)",
            "yaxis_title": f"PC2 ({variance[1] * 100:.1f}%)",
            "zaxis_title": f"PC3 ({variance[2] * 100:.1f}%)",
            "camera": {"eye": {"x": 1.6, "y": 1.5, "z": 0.9}},
        }
    )
    return apply_layout(fig, 620)


def radar_for_customer(customer, segment_average, overall_average, features):
    labels = [humanize_column(f) for f in features]
    values = [float(pd.to_numeric(pd.Series([customer.get(f)]), errors="coerce").fillna(0).iloc[0]) for f in features]
    seg = [float(segment_average.get(f, 0)) for f in features]
    overall = [float(overall_average.get(f, 0)) for f in features]
    rows = np.array([values, seg, overall], dtype=float)
    mins = np.nanmin(rows, axis=0)
    maxs = np.nanmax(rows, axis=0)
    scaled = np.divide(rows - mins, maxs - mins, out=np.zeros_like(rows), where=(maxs - mins) != 0)
    fig = go.Figure()
    for name, vals, color in [
        ("Customer", scaled[0], "#a855f7"),
        ("Segment Avg", scaled[1], "#2dd4bf"),
        ("Overall Avg", scaled[2], "#94a3b8"),
    ]:
        fig.add_trace(go.Scatterpolar(r=list(vals) + [vals[0]], theta=labels + [labels[0]], fill="toself", name=name, line_color=color))
    fig.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 1]}}, showlegend=True)
    return apply_layout(fig, 360)


def profile_heatmap(profiles, cluster_col, segment_col, features):
    use_features = [f for f in features if f in profiles.columns]
    data = profiles[[cluster_col, segment_col] + use_features].copy()
    matrix = data[use_features].apply(pd.to_numeric, errors="coerce")
    z = (matrix - matrix.mean()) / matrix.std(ddof=0).replace(0, 1)
    fig = px.imshow(
        z,
        x=[humanize_column(c) for c in use_features],
        y=[f"C{c} {s}" for c, s in zip(data[cluster_col], data[segment_col])],
        color_continuous_scale="RdBu",
        aspect="auto",
    )
    return apply_layout(fig, 460)


def feature_distribution(customers, feature, segment_col, chart_type="Histogram"):
    if chart_type == "Box":
        fig = px.box(customers, x=segment_col, y=feature, color=segment_col, color_discrete_map=SEGMENT_COLORS)
    elif chart_type == "Violin":
        fig = px.violin(customers, x=segment_col, y=feature, color=segment_col, color_discrete_map=SEGMENT_COLORS, box=True)
    else:
        fig = px.histogram(customers, x=feature, color=segment_col, color_discrete_map=SEGMENT_COLORS, marginal="box", opacity=0.78)
    fig.update_layout(xaxis_title=humanize_column(feature), yaxis_title="Customers")
    return apply_layout(fig, 520)


def parallel_coordinates(profiles, cluster_col, segment_col, features):
    use_features = [f for f in features if f in profiles.columns][:8]
    data = profiles[[cluster_col, segment_col] + use_features].copy()
    for col in use_features:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    # Plotly's Parcoords trace requires WebGL. Draw the same per-feature
    # min/max projection with SVG scatter lines so every browser can show it.
    values = data[use_features]
    spans = values.max() - values.min()
    scaled = ((values - values.min()) / spans.replace(0, np.nan)).fillna(0.5)
    fig = go.Figure()
    for index, row in data.iterrows():
        segment = str(row[segment_col])
        color = SEGMENT_COLORS.get(segment, "#94a3b8")
        fig.add_trace(go.Scatter(
            x=list(range(len(use_features))),
            y=scaled.loc[index].tolist(),
            mode="lines+markers",
            name=f"C{row[cluster_col]} {segment.replace('_', ' ')}",
            line={"color": color, "width": 2},
            marker={"color": color, "size": 6},
            text=[humanize_column(f) for f in use_features],
            customdata=[[str(row[cluster_col]), segment.replace("_", " "), float(row[f])] for f in use_features],
            hovertemplate="%{text}<br>Cluster %{customdata[0]} · %{customdata[1]}<br>Value: %{customdata[2]:.3g}<br>Relative position: %{y:.2f}<extra></extra>",
        ))
    for axis in range(len(use_features)):
        fig.add_shape(type="line", x0=axis, x1=axis, y0=0, y1=1, line={"color": "rgba(148,163,184,.25)", "width": 1}, layer="below")
    apply_layout(fig, 500)
    fig.update_layout(
        xaxis={"tickmode": "array", "tickvals": list(range(len(use_features))), "ticktext": ["<br>".join(wrap(humanize_column(f), 14)) for f in use_features], "tickangle": -35, "tickfont": {"size": 10}, "showgrid": False, "zeroline": False},
        yaxis={"title": "Relative position (min → max)", "range": [-0.05, 1.05], "tickvals": [0, 0.5, 1], "zeroline": False},
        legend={"orientation": "h", "yanchor": "top", "y": -0.32, "x": 0, "font": {"size": 10}},
        margin={"l": 55, "r": 15, "t": 24, "b": 160},
    )
    return fig


def cluster_bubble(profiles, features, cluster_col, segment_col):
    wealth = next((f for f in ["avg_monthly_balance", "log_avg_monthly_balance"] if f in profiles.columns), features[0])
    freq = next((f for f in ["txn_frequency_per_month", "log_txn_frequency_per_month"] if f in profiles.columns), features[min(1, len(features)-1)])
    amount = next((f for f in ["avg_txn_amount", "log_avg_txn_amount"] if f in profiles.columns), features[min(2, len(features)-1)])
    size_col = "customer_count" if "customer_count" in profiles.columns else None
    fig = px.scatter_3d(
        profiles,
        x=wealth,
        y=freq,
        z=amount,
        size=size_col,
        color=segment_col,
        color_discrete_map=SEGMENT_COLORS,
        hover_data=[cluster_col, segment_col],
    )
    return apply_layout(fig, 560)

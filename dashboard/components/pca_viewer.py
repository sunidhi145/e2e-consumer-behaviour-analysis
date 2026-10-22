"""Interactive PCA viewer using Canvas 2D, including browsers without WebGL."""

import json
from pathlib import Path

from dash import html

from config import SEGMENT_COLORS


def pca_viewer(pca_data, id_col, cluster_col, segment_col, cluster_filter="All"):
    def records(frame, centroid=False):
        result = []
        for _, row in frame.iterrows():
            segment = str(row[segment_col])
            result.append({
                "xyz": [float(row[axis]) for axis in ("PC1", "PC2", "PC3")],
                "id": "Centroid" if centroid else str(row[id_col]),
                "cluster": str(row[cluster_col]),
                "segment": segment,
                "color": SEGMENT_COLORS.get(segment, "#94a3b8"),
                "centroid": centroid,
            })
        return result

    payload = {
        "points": records(pca_data["points"]),
        "centroids": records(pca_data["centroids"], centroid=True),
        "variance": pca_data["explained_variance"],
        "filter": str(cluster_filter or "All"),
    }
    # Escape HTML delimiters so dataset strings cannot close the JSON script tag.
    encoded = json.dumps(payload, allow_nan=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    template = Path(__file__).with_name("pca_viewer.html").read_text(encoding="utf-8")
    return html.Iframe(
        id="advanced-pca-viewer",
        title="Interactive 3D PCA customer clusters",
        srcDoc=template.replace("__PCA_DATA__", encoded),
        sandbox="allow-scripts",
        className="pca-viewer",
    )

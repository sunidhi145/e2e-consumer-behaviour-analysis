from functools import lru_cache
from pathlib import Path

import pandas as pd

from config import DATA_SEARCH_ROOT, EXPECTED_CUSTOMER_ROWS
from utils.analytics import compute_pca, numeric_feature_columns
from utils.data_validation import (
    DashboardDataError,
    detect_cluster_column,
    detect_customer_id_column,
    detect_segment_column,
)


PURPOSE_PATTERNS = {
    "customers": [
        "final_customer_clusters.csv",
        "customers_with_clusters_and_segments.csv",
    ],
    "profiles": [
        "final_cluster_profiles.csv",
        "cluster_profiles.csv",
        "segment_profiles.csv",
    ],
    "distribution": [
        "final_segment_distribution.csv",
        "segment_distribution.csv",
    ],
    "evaluation": [
        "kmeans_evaluation_results.csv",
    ],
    "training": [
        "ml_training_features.csv",
    ],
}


def _csv_candidates():
    return [p for p in DATA_SEARCH_ROOT.rglob("*.csv") if ".venv" not in p.parts and "dashboard" not in p.parts]


def _find_file(patterns):
    candidates = _csv_candidates()
    by_name = {p.name.lower(): p for p in candidates}
    for pattern in patterns:
        exact = by_name.get(pattern.lower())
        if exact:
            return exact
    for pattern in patterns:
        stem = pattern.lower().replace(".csv", "")
        matches = [p for p in candidates if stem in p.stem.lower()]
        if matches:
            matches.sort(key=lambda p: (not p.name.lower().startswith("final_"), len(p.parts)))
            return matches[0]
    return None


def _safe_read(path):
    if not path:
        return None
    return pd.read_csv(path)


def _maybe_numeric(series):
    converted = pd.to_numeric(series, errors="coerce")
    return converted if converted.notna().sum() else series


@lru_cache(maxsize=1)
def load_dashboard_data():
    selected_files = {purpose: _find_file(patterns) for purpose, patterns in PURPOSE_PATTERNS.items()}
    if selected_files["customers"] is None:
        raise DashboardDataError(
            "Missing customer-level CSV. Expected a file similar to final_customer_clusters.csv "
            "or customers_with_clusters_and_segments.csv."
        )

    customers = _safe_read(selected_files["customers"])
    id_col = detect_customer_id_column(customers)
    cluster_col = detect_cluster_column(customers)
    segment_col = detect_segment_column(customers)

    customers[id_col] = customers[id_col].astype(str)
    customers[cluster_col] = _maybe_numeric(customers[cluster_col])
    customers[segment_col] = customers[segment_col].astype(str)

    duplicate_count = int(customers[id_col].duplicated().sum())
    row_count = len(customers)
    row_count_ok = row_count == EXPECTED_CUSTOMER_ROWS

    features = numeric_feature_columns(customers, id_col, cluster_col, segment_col)
    pca = compute_pca(customers, features, id_col, cluster_col, segment_col)

    profiles = _safe_read(selected_files["profiles"])
    if profiles is None:
        profiles = customers.groupby([cluster_col, segment_col], as_index=False)[features].mean(numeric_only=True)
        profiles["customer_count"] = customers.groupby([cluster_col, segment_col])[id_col].transform("count")
    else:
        for col in profiles.columns:
            if col not in {cluster_col, segment_col}:
                profiles[col] = _maybe_numeric(profiles[col])

    distribution = _safe_read(selected_files["distribution"])
    if distribution is None:
        distribution = customers.groupby(segment_col, as_index=False).size().rename(columns={"size": "customer_count"})
        distribution["percentage"] = distribution["customer_count"] / len(customers) * 100

    evaluation = _safe_read(selected_files["evaluation"])
    training = _safe_read(selected_files["training"])

    return {
        "customers": customers,
        "profiles": profiles,
        "distribution": distribution,
        "evaluation": evaluation,
        "training": training,
        "selected_files": selected_files,
        "id_col": id_col,
        "cluster_col": cluster_col,
        "segment_col": segment_col,
        "features": features,
        "pca": pca,
        "row_count": row_count,
        "row_count_ok": row_count_ok,
        "duplicate_count": duplicate_count,
    }


def clear_data_cache():
    load_dashboard_data.cache_clear()

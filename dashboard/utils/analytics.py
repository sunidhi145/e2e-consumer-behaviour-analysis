import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def numeric_feature_columns(df, id_col, cluster_col, segment_col):
    excluded = {id_col, cluster_col, segment_col}
    cols = []
    for col in df.columns:
        if col in excluded:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        if series.notna().sum() > 0:
            cols.append(col)
    return cols


def standardized_matrix(df, features):
    numeric = df[features].apply(pd.to_numeric, errors="coerce")
    filled = numeric.fillna(numeric.median(numeric_only=True)).fillna(0)
    scaler = StandardScaler()
    return scaler.fit_transform(filled), scaler, filled


def compute_pca(df, features, id_col, cluster_col, segment_col):
    if len(features) < 2:
        raise ValueError("At least two numeric feature columns are required for PCA.")
    matrix, scaler, filled = standardized_matrix(df, features)
    n_components = min(3, matrix.shape[1])
    pca = PCA(n_components=n_components, random_state=42)
    pcs = pca.fit_transform(matrix)
    out = pd.DataFrame(
        {
            id_col: df[id_col].astype(str),
            cluster_col: df[cluster_col],
            segment_col: df[segment_col],
            "PC1": pcs[:, 0],
            "PC2": pcs[:, 1] if n_components > 1 else 0,
            "PC3": pcs[:, 2] if n_components > 2 else 0,
        }
    )
    centroids = out.groupby([cluster_col, segment_col], as_index=False)[["PC1", "PC2", "PC3"]].mean()
    return {
        "points": out,
        "centroids": centroids,
        "explained_variance": pca.explained_variance_ratio_.tolist(),
        "matrix": matrix,
        "filled_features": filled,
        "scaler": scaler,
    }


def top_features(df, features, limit=6):
    preferred = [
        "avg_monthly_balance",
        "log_avg_monthly_balance",
        "txn_frequency_per_month",
        "log_txn_frequency_per_month",
        "avg_txn_amount",
        "log_avg_txn_amount",
        "account_tenure_months",
        "log_account_tenure_months",
        "num_active_products",
        "overdraft_month_count",
        "log_overdraft_month_count",
        "days_since_last_txn",
        "log_days_since_last_txn",
    ]
    picked = [col for col in preferred if col in features]
    picked.extend([col for col in features if col not in picked])
    return picked[:limit]


def percentile(series, value):
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return None
    return float((clean <= value).mean() * 100)


def nearest_customers(df, customer_id, features, id_col, cluster_col, limit=5):
    row_mask = df[id_col].astype(str) == str(customer_id)
    if not row_mask.any():
        return pd.DataFrame()
    target = df.loc[row_mask].iloc[0]
    cluster_value = target[cluster_col]
    cluster_df = df[df[cluster_col] == cluster_value].copy()
    if len(cluster_df) <= 1:
        return pd.DataFrame()
    matrix, _, _ = standardized_matrix(cluster_df, features)
    target_idx = cluster_df.index.get_loc(target.name)
    distances = np.linalg.norm(matrix - matrix[target_idx], axis=1)
    cluster_df["standardized_feature_distance"] = distances
    return (
        cluster_df[cluster_df[id_col].astype(str) != str(customer_id)]
        .sort_values("standardized_feature_distance")
        .head(limit)
    )

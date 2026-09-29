ID_CANDIDATES = ["customer_id", "customerid", "cust_id", "id", "client_id", "account_id"]
CLUSTER_CANDIDATES = ["cluster_id", "cluster", "kmeans_cluster", "Cluster"]
SEGMENT_CANDIDATES = ["segment", "segment_name", "customer_segment", "Segment"]


class DashboardDataError(RuntimeError):
    pass


def _find_column(columns, candidates, contains=None):
    normalized = {str(col).lower().replace(" ", "").replace("-", "_"): col for col in columns}
    for candidate in candidates:
        key = candidate.lower().replace(" ", "").replace("-", "_")
        if key in normalized:
            return normalized[key]
    if contains:
        for col in columns:
            low = str(col).lower()
            if all(part in low for part in contains):
                return col
    return None


def detect_customer_id_column(df):
    column = _find_column(df.columns, ID_CANDIDATES, contains=["customer", "id"])
    if not column:
        raise DashboardDataError("Missing customer ID column in customer-level CSV.")
    return column


def detect_cluster_column(df):
    column = _find_column(df.columns, CLUSTER_CANDIDATES, contains=["cluster"])
    if not column:
        raise DashboardDataError("Missing cluster ID column in customer-level CSV.")
    return column


def detect_segment_column(df):
    column = _find_column(df.columns, SEGMENT_CANDIDATES, contains=["segment"])
    if not column:
        raise DashboardDataError("Missing segment column in customer-level CSV.")
    return column

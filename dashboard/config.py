from pathlib import Path

APP_TITLE = "BankIQ Customer Intelligence"
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_SEARCH_ROOT = PROJECT_ROOT

SEGMENT_COLORS = {
    "VIP_Wealth_Builders": "#2dd4bf",
    "Active_Spenders": "#a855f7",
    "Dormant_At_Risk": "#ef4444",
    "Young_Savers": "#f59e0b",
    "Business_Owners": "#3b82f6",
}

PAGE_PATHS = {
    "Executive Overview": "/",
    "Customer Explorer": "/customer-explorer",
    "Cluster Explorer": "/cluster-explorer",
    "Advanced Analytics": "/advanced-analytics",
}

PLOT_TEMPLATE = "plotly_dark"
EXPECTED_CUSTOMER_ROWS = 2869

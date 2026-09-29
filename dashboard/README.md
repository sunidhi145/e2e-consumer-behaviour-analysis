# BankIQ Customer Intelligence

BankIQ Customer Intelligence is a dark-mode Dash dashboard for the K-Means customer-segmentation college project in this workspace. It reads the existing clustering CSV files, detects the actual ID, cluster, and segment columns, computes PCA from real numeric feature columns, and never edits the source datasets.

## Pages

- Executive Overview: KPI cards, segment donut, cluster-size bar chart, 2D PCA customer space, segment heatmap, model evaluation, and downloads.
- Customer Explorer: starts empty, then reveals a searched customer after staged loading. Includes profile comparison, business value, recommendations, all features, similar customers, and metric deep dives.
- Cluster Explorer: five selectable cluster cards, staged analysis loading, cluster summary, business panels, AG Grid customer records, feature summary, opportunities, and selected-cluster export.
- Advanced Analytics: technical workspace with 3D PCA, feature distributions, comparison plots, standardized heatmap, and 3D cluster bubble chart.

## Folder Structure

```text
dashboard/
  app.py
  config.py
  requirements.txt
  README.md
  run_dashboard.ps1
  pages/
  components/
  utils/
  assets/
```

## Required CSV Files

The dashboard searches the project root recursively, excluding `.venv` and `dashboard`, and prefers final verified files:

- Customer-level clusters: `final_customer_clusters.csv`
- Cluster profiles: `final_cluster_profiles.csv`
- Segment distribution: `final_segment_distribution.csv`
- K-Means evaluation: `kmeans_evaluation_results.csv`
- Training features: `ml_training_features.csv`

If the customer-level file is missing, the app shows a clear data error instead of fabricating records.

## Installation

Open Windows PowerShell:

```powershell
cd "C:\Users\sunid\OneDrive\Desktop\ML Project"
& ".\.venv\Scripts\Activate.ps1"
python -m pip install -r dashboard\requirements.txt
```

## Run

```powershell
python dashboard\app.py
```

Or use:

```powershell
.\dashboard\run_dashboard.ps1
```

Expected dashboard address:

```text
http://127.0.0.1:8050
```

## Customer Search

The Customer Explorer initially shows only a customer ID dropdown, Search Customer, Random Customer, an empty state, and skeleton cards. Results appear only after Search Customer is clicked and the staged loader completes.

## Cluster Filtering

The Cluster Explorer requires selecting a cluster card and then clicking View Cluster Insights. The Customers tab uses Dash AG Grid with sorting, filters, pagination, resizing, and a pinned Customer ID column.

## PCA And 3D Visualisation

PCA uses standardized numeric feature columns only. The loader excludes customer ID, cluster ID, segment, and nonnumeric metadata. PC1, PC2, PC3, explained variance, and centroids are cached for responsiveness. The Advanced Analytics 3D chart supports rotate, zoom, pan, hover, reset camera, and cluster filtering.

## Exports

- `bankiq_clustered_customers.csv`: complete clustered customer records.
- `bankiq_segment_distribution.csv`: segment counts and percentages.
- `bankiq_cluster_profiles.csv`: cluster profile data.
- `bankiq_cluster_<id>_customers.csv`: selected cluster customer records.

## Animation Behaviour

The app includes page fade/slide entrance, card fade-up, hover lift, active navigation glow, button scale/glow, Plotly transitions, skeleton shimmer, staged loaders, progress bars, modal slide-in, table row animation, and KPI count-up styling. Reduced-motion preferences are respected in CSS.

## Troubleshooting

- Missing customer CSV: confirm `kmeans_ml_proj\final_customer_clusters.csv` or a similar customer-level cluster file exists.
- Missing ID/cluster/segment column: check the customer-level CSV headers.
- PCA failure: confirm at least two numeric feature columns exist.
- Import error: activate `.venv` and reinstall `dashboard\requirements.txt`.
- Port conflict: edit `app.py` and change the port from `8050` to another available local port.

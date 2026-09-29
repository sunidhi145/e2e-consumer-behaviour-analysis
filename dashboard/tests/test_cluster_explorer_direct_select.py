import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClusterExplorerDirectSelectTest(unittest.TestCase):
    def test_view_cluster_button_removed(self):
        source = (ROOT / "pages" / "cluster_explorer.py").read_text()

        self.assertNotIn("view-cluster-button", source)
        self.assertNotIn("View Cluster Insights", source)

    def test_cluster_click_sets_active_cluster_directly(self):
        source = (ROOT / "pages" / "cluster_explorer.py").read_text()

        self.assertIn('Output("cluster-active-store", "data")', source)
        self.assertIn('Input({"type": "cluster-card", "cluster": dash.ALL}, "n_clicks")', source)
        self.assertIn("return cluster, cluster", source)

    def test_selected_cluster_card_style_exists(self):
        css = (ROOT / "assets" / "styles.css").read_text()

        self.assertIn(".cluster-card.selected", css)


if __name__ == "__main__":
    unittest.main()

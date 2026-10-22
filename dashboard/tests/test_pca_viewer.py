import json
import unittest

import pandas as pd

from components.pca_viewer import pca_viewer


class PcaViewerTest(unittest.TestCase):
    def test_actual_coordinates_and_filter_survive_safe_embedding(self):
        points = pd.DataFrame({
            "customer": ['</script><script>alert("x")</script>', "second"],
            "cluster": [0, 1], "segment": ["VIP_Wealth_Builders", "Young_Savers"],
            "PC1": [-2.5, 3.5], "PC2": [0.0, 2.0], "PC3": [1.0, -1.0],
        })
        pca = {"points": points, "centroids": points.groupby(["cluster", "segment"], as_index=False)[["PC1", "PC2", "PC3"]].mean(), "explained_variance": [0.5, 0.3, 0.1]}
        viewer = pca_viewer(pca, "customer", "cluster", "segment", "1")
        encoded = viewer.srcDoc.split('<script id="pca-data" type="application/json">')[1].split('</script>')[0]
        payload = json.loads(encoded)
        self.assertEqual(payload["points"][0]["xyz"], [-2.5, 0.0, 1.0])
        self.assertEqual(payload["points"][0]["id"], points.iloc[0]["customer"])
        self.assertNotIn("<", encoded)
        self.assertEqual(payload["filter"], "1")
        self.assertTrue(all(p["centroid"] for p in payload["centroids"]))
        self.assertEqual(payload["variance"], [0.5, 0.3, 0.1])


if __name__ == "__main__":
    unittest.main()

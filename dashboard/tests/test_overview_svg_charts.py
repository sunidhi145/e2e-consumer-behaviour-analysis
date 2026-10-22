import unittest

import numpy as np
import pandas as pd

from components.charts import parallel_coordinates, pca_2d


class OverviewSvgChartsTest(unittest.TestCase):
    def test_large_pca_stays_svg_and_keeps_customer_click_data(self):
        points = pd.DataFrame({
            "customer": [str(i) for i in range(1500)],
            "cluster": [0] * 1500, "segment": ["Young_Savers"] * 1500,
            "PC1": np.linspace(-2, 2, 1500), "PC2": np.linspace(2, -2, 1500),
        })
        centroids = points.groupby("cluster", as_index=False)[["PC1", "PC2"]].mean()
        figure = pca_2d({"points": points, "centroids": centroids}, "customer", "cluster", "segment")
        self.assertTrue(all(trace.type == "scatter" for trace in figure.data))
        self.assertEqual(sum(len(trace.x) for trace in figure.data[:-1]), 1500)
        self.assertEqual(figure.data[0].customdata[42][0], "42")
        self.assertEqual(figure.data[-1].name, "Centroids")

    def test_comparison_uses_svg_with_per_feature_scaling_and_raw_hover(self):
        profiles = pd.DataFrame({"cluster": [0, 1, 2], "segment": ["Young_Savers", "Active_Spenders", "Dormant_At_Risk"], "balance": [10.0, 20.0, 30.0], "frequency": [30.0, 20.0, 10.0], "constant": [5.0] * 3})
        figure = parallel_coordinates(profiles, "cluster", "segment", ["balance", "frequency", "constant"])
        self.assertTrue(all(trace.type == "scatter" for trace in figure.data))
        self.assertEqual(len(figure.data), 3)
        self.assertEqual(list(figure.data[0].y), [0.0, 1.0, 0.5])
        self.assertEqual(list(figure.data[2].y), [1.0, 0.0, 0.5])
        self.assertEqual(figure.data[0].customdata[0][2], 10.0)
        self.assertEqual(len(figure.layout.shapes), 3)


if __name__ == "__main__":
    unittest.main()

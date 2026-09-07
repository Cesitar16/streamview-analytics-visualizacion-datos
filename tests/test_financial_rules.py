import unittest

import pandas as pd

from src.financial_rules import build_financial_analysis


class FinancialAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.movies = pd.DataFrame(
            {
                "show_id": ["1", "2", "3", "4"],
                "title": ["Alpha", "Beta", "Gamma", "Delta"],
                "budget": [100, 10, 50, 20],
                "revenue": [200, 100, 75, 20],
            }
        )

    def test_builds_case_roi_kpis_rankings_and_segment(self) -> None:
        result = build_financial_analysis(self.movies, total_movies=8)
        financial = result["financial_movies"].set_index("title")
        self.assertEqual(financial.loc["Beta", "roi_approx"], 10.0)
        self.assertEqual(result["top_revenue"].iloc[0]["title"], "Alpha")
        self.assertEqual(result["top_roi"].iloc[0]["title"], "Beta")
        self.assertEqual(result["low_budget_high_return"].iloc[0]["title"], "Beta")
        kpis = result["financial_kpis"].set_index("kpi")
        self.assertEqual(kpis.loc["Cobertura financiera", "value"], 50.0)
        self.assertEqual(kpis.loc["Ingresos totales", "value"], 395)
        self.assertAlmostEqual(result["financial_association"].iloc[0]["spearman_rho"], 0.4)

    def test_does_not_mutate_the_prepared_view(self) -> None:
        before = self.movies.copy(deep=True)
        build_financial_analysis(self.movies)
        pd.testing.assert_frame_equal(self.movies, before)

    def test_rejects_invalid_financial_rows(self) -> None:
        invalid = self.movies.copy()
        invalid.loc[0, "budget"] = 0
        with self.assertRaises(ValueError):
            build_financial_analysis(invalid)


if __name__ == "__main__":
    unittest.main()

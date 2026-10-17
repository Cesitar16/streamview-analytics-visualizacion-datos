"""Integration checks against the two official CSVs used for the EP2 delivery."""

import unittest

from src.dashboard_data import (
    category_counts,
    financial_selection,
    financial_summary,
    load_views,
    select_catalog,
)


class DashboardDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.views = load_views()

    def test_default_selection_reconciles_with_ep1_entities(self):
        selected = select_catalog(self.views)
        self.assertEqual(len(selected), 31_991)
        self.assertEqual(int(selected["type"].eq("Movie").sum()), 16_000)
        self.assertEqual(selected["content_id"].nunique(), len(selected))
        self.assertEqual(len(category_counts(selected, self.views["catalogo_generos"], "genre")), 28)

    def test_multivalue_filters_keep_unique_contents_and_intersect(self):
        selected = select_catalog(
            self.views, genres=["Drama"], countries=["Japan"], types=["Movie"]
        )
        self.assertGreater(len(selected), 0)
        self.assertTrue(selected["type"].eq("Movie").all())
        self.assertEqual(selected["content_id"].nunique(), len(selected))
        ids = set(selected["content_id"])
        self.assertTrue(ids.issubset(set(self.views["catalogo_generos"].loc[
            self.views["catalogo_generos"]["genre"].eq("Drama"), "content_id"])))
        self.assertTrue(ids.issubset(set(self.views["catalogo_paises"].loc[
            self.views["catalogo_paises"]["country"].eq("Japan"), "content_id"])))

    def test_all_available_acquisition_filters_intersect(self):
        selected = select_catalog(
            self.views,
            types=["Movie"], years=(2020, 2023), genres=["Action"],
            countries=["United States of America"], languages=["en"],
            rating_range=(5.0, 8.0),
        )
        self.assertEqual(len(selected), 416)
        self.assertEqual(selected["content_id"].nunique(), len(selected))
        self.assertTrue(selected["type"].eq("Movie").all())
        self.assertTrue(selected["release_year"].between(2020, 2023).all())
        self.assertTrue(selected["language"].eq("en").all())
        self.assertTrue(selected["vote_average"].between(5.0, 8.0).all())

    def test_finance_reconciles_to_source_and_obeys_type_filter(self):
        all_finance = financial_selection(select_catalog(self.views), self.views)
        summary = financial_summary(all_finance)
        self.assertEqual(summary["eligible_movies"], 3_540)
        self.assertEqual(summary["total_budget"], 125_960_767_278)
        self.assertEqual(summary["total_revenue"], 367_371_433_138)
        self.assertAlmostEqual(summary["portfolio_multiple"], 2.916554424658258)
        self.assertAlmostEqual(summary["gross_roi_approx"], 1.916554424658258)
        self.assertAlmostEqual(summary["gross_roi_approx"], summary["portfolio_multiple"] - 1)
        tv_only = select_catalog(self.views, types=["TV Show"])
        empty_summary = financial_summary(financial_selection(tv_only, self.views))
        self.assertEqual(empty_summary["eligible_movies"], 0)
        self.assertIsNone(empty_summary["gross_roi_approx"])


if __name__ == "__main__":
    unittest.main()

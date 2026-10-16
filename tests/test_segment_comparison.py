"""Checks for the temporal series and genre comparator."""

import unittest

import pandas as pd

from src.dashboard_data import load_views, select_catalog
from src.segment_comparison import (
    annual_content_trend,
    compare_segments,
    segment_selection,
)


class SegmentComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.views = load_views()
        cls.selected = select_catalog(cls.views)

    def test_annual_trend_reconciles_unique_entities_by_type(self):
        trend = annual_content_trend(self.selected)
        self.assertEqual(int(trend["titles"].sum()), len(self.selected))
        self.assertEqual(set(trend["type"]), {"Movie", "TV Show"})
        self.assertEqual(set(trend["release_year"]), set(range(2010, 2026)))

    def test_segment_selection_uses_unique_ids_for_multivalue_genres(self):
        drama = segment_selection(self.selected, self.views, dimension="genre", category="Drama")
        self.assertEqual(drama["content_id"].nunique(), len(drama))
        bridge_ids = set(self.views["catalogo_generos"].loc[
            self.views["catalogo_generos"]["genre"].eq("Drama"), "content_id"
        ])
        self.assertTrue(set(drama["content_id"]).issubset(bridge_ids))

    def test_comparison_respects_global_filters_and_reliable_metric_rules(self):
        filtered = select_catalog(self.views, types=["Movie"], years=(2020, 2023))
        comparison = compare_segments(
            filtered,
            self.views,
            dimension="genre",
            left_category="Drama",
            right_category="Comedy",
        ).set_index("metric")
        self.assertTrue((comparison[["left", "right"]].loc[["titles", "movies", "tv_shows", "rated_titles"]] >= 0).all().all())
        self.assertEqual(comparison.loc["tv_shows", "left"], 0)
        self.assertEqual(comparison.loc["tv_shows", "right"], 0)
        self.assertTrue(comparison.loc["mean_rating", ["left", "right"]].between(0, 10).all())
        self.assertEqual(
            comparison.loc["titles", "difference"],
            comparison.loc["titles", "left"] - comparison.loc["titles", "right"],
        )

    def test_empty_segment_reports_zero_counts_and_missing_averages(self):
        empty = self.selected.iloc[0:0]
        comparison = compare_segments(
            empty,
            self.views,
            dimension="genre",
            left_category="Drama",
            right_category="Comedy",
        ).set_index("metric")
        self.assertEqual(comparison.loc["titles", "left"], 0)
        self.assertEqual(comparison.loc["rated_titles", "right"], 0)
        self.assertTrue(pd.isna(comparison.loc["median_popularity", "left"]))
        self.assertTrue(pd.isna(comparison.loc["mean_rating", "right"]))


if __name__ == "__main__":
    unittest.main()

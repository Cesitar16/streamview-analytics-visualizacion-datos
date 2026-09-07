import unittest

import pandas as pd

from src.business_rules import build_lucas_analysis


class LucasAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalogo_general = pd.DataFrame(
            {
                "content_id": ["Movie_1", "Movie_2", "Movie_3", "TV Show_1", "TV Show_2"],
                "title": ["M1", "M2", "M3", "T1", "T2"],
                "type": ["Movie", "Movie", "Movie", "TV Show", "TV Show"],
                "release_year": [2010, 2010, 2011, 2010, 2011],
                "date_added": pd.to_datetime(
                    ["2011-01-01", "2011-02-01", "2012-01-01", "2011-03-01", "2012-02-01"]
                ),
                "popularity": [10.0, 20.0, 30.0, 40.0, 80.0],
                "vote_average": [5.0, 0.0, 9.0, 6.0, 9.0],
                "vote_count": [10, 0, 30, 10, 20],
            }
        )
        self.catalogo_popularity = self.catalogo_general.loc[
            self.catalogo_general["content_id"] != "Movie_2"
        ].copy()
        self.catalogo_generos = pd.DataFrame(
            {
                "content_id": ["Movie_1", "Movie_2", "Movie_3", "TV Show_1", "TV Show_2"],
                "genre": ["Action", "Comedy", "Action", "Drama", "Drama"],
            }
        )

    def test_builds_reproducible_tables_without_treating_no_votes_as_a_score(self) -> None:
        result = build_lucas_analysis(
            self.catalogo_general, self.catalogo_popularity, self.catalogo_generos
        )

        popularity = result["popularity_comparison"].set_index("type")
        self.assertEqual(popularity.loc["Movie", "titles"], 2)
        self.assertEqual(popularity.loc["Movie", "median_popularity"], 20.0)
        self.assertEqual(popularity.loc["TV Show", "median_popularity"], 60.0)

        rating = result["rating_summary"].set_index("type")
        self.assertEqual(rating.loc["Movie", "rated_titles"], 2)
        self.assertAlmostEqual(rating.loc["Movie", "rating_coverage_pct"], 200 / 3)
        self.assertEqual(rating.loc["Movie", "median_vote_average"], 7.0)
        self.assertEqual(rating.loc["Movie", "mean_vote_average"], 7.0)
        self.assertEqual(rating.loc["Movie", "median_vote_count"], 20.0)
        self.assertEqual(rating.loc["Movie", "weighted_vote_average"], 8.0)

        history = result["historical_evolution"]
        movie_2010 = history.loc[
            (history["type"] == "Movie") & (history["release_year"] == 2010)
        ].iloc[0]
        self.assertEqual(movie_2010["titles"], 2)
        self.assertEqual(movie_2010["rated_titles"], 1)
        self.assertEqual(movie_2010["rating_coverage_pct"], 50.0)
        self.assertEqual(movie_2010["median_vote_average"], 5.0)

        timeline = result["catalog_timeline"]
        movie_added_2011 = timeline.loc[
            (timeline["type"] == "Movie")
            & (timeline["year"] == 2011)
            & (timeline["event"] == "Incorporaciones")
        ].iloc[0]
        self.assertEqual(movie_added_2011["titles"], 2)

        temporal_alignment = result["temporal_alignment"].set_index("type")
        self.assertEqual(temporal_alignment.loc["Movie", "same_year_titles"], 0)
        self.assertEqual(temporal_alignment.loc["Movie", "same_year_pct"], 0.0)

    def test_uses_only_the_popularity_view_for_popularity_metrics(self) -> None:
        result = build_lucas_analysis(
            self.catalogo_general, self.catalogo_popularity, self.catalogo_generos
        )

        popularity = result["popularity_comparison"].set_index("type")
        self.assertEqual(popularity.loc["Movie", "titles"], 2)

        history = result["historical_evolution"]
        movie_2010 = history.loc[
            (history["type"] == "Movie") & (history["release_year"] == 2010)
        ].iloc[0]
        self.assertEqual(movie_2010["popularity_titles"], 1)
        self.assertEqual(movie_2010["median_popularity"], 10.0)

    def test_reports_spearman_association_on_titles_with_votes(self) -> None:
        result = build_lucas_analysis(
            self.catalogo_general, self.catalogo_popularity, self.catalogo_generos
        )
        association = result["popularity_rating_association"].set_index("scope")

        self.assertEqual(association.loc["Overall", "titles"], 4)
        self.assertAlmostEqual(association.loc["Movie", "spearman_rho"], 1.0)
        self.assertAlmostEqual(association.loc["TV Show", "spearman_rho"], 1.0)

    def test_does_not_mutate_prepared_views(self) -> None:
        general_before = self.catalogo_general.copy(deep=True)
        popularity_before = self.catalogo_popularity.copy(deep=True)
        genres_before = self.catalogo_generos.copy(deep=True)

        build_lucas_analysis(
            self.catalogo_general, self.catalogo_popularity, self.catalogo_generos
        )

        pd.testing.assert_frame_equal(self.catalogo_general, general_before)
        pd.testing.assert_frame_equal(self.catalogo_popularity, popularity_before)
        pd.testing.assert_frame_equal(self.catalogo_generos, genres_before)

    def test_builds_case_rankings_and_popularity_by_genre(self) -> None:
        result = build_lucas_analysis(
            self.catalogo_general, self.catalogo_popularity, self.catalogo_generos
        )

        self.assertEqual(result["top_popularity"].iloc[0]["title"], "T2")
        self.assertEqual(result["top_rated"].iloc[0]["title"], "M3")
        self.assertEqual(result["top_voted"].iloc[0]["title"], "M3")

        genre = result["popularity_by_genre"].set_index("genre")
        self.assertEqual(genre.loc["Action", "titles"], 2)
        self.assertEqual(genre.loc["Action", "median_popularity"], 20.0)
        self.assertEqual(genre.loc["Drama", "mean_popularity"], 60.0)


if __name__ == "__main__":
    unittest.main()

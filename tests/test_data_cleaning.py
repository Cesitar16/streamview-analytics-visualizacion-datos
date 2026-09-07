from pathlib import Path
import unittest

from src.data_cleaning import build_catalog_views


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MOVIES_PATH = PROJECT_ROOT / "data" / "raw" / "netflix_movies_detailed_up_to_2025.csv"
TV_SHOWS_PATH = PROJECT_ROOT / "data" / "raw" / "netflix_tv_shows_detailed_up_to_2025.csv"


class BuildCatalogViewsTests(unittest.TestCase):
    def test_reconstructs_approved_entity_and_multivalue_views(self) -> None:
        """A broken preparation rule must not silently change approved metrics."""
        views = build_catalog_views(MOVIES_PATH, TV_SHOWS_PATH)

        catalogo_general = views["catalogo_general"]
        catalogo_generos = views["catalogo_generos"]
        catalogo_paises = views["catalogo_paises"]
        catalogo_popularity = views["catalogo_popularity"]
        movies_financial_valid = views["movies_financial_valid"]
        catalogo_directores = views["catalogo_directores"]
        catalogo_cast = views["catalogo_cast"]

        self.assertEqual(len(catalogo_general), 31_991)
        self.assertTrue(catalogo_general["content_id"].is_unique)
        self.assertEqual(int(catalogo_general["popularity_conflict"].sum()), 9)
        self.assertEqual(len(catalogo_popularity), 31_982)
        self.assertEqual(len(movies_financial_valid), 3_540)
        self.assertEqual(len(catalogo_generos), 65_888)
        self.assertEqual(len(catalogo_paises), 37_628)
        self.assertEqual(len(catalogo_directores), 24_763)
        self.assertEqual(len(catalogo_cast), 140_367)
        self.assertEqual(catalogo_generos.duplicated(["content_id", "genre"]).sum(), 0)
        self.assertEqual(catalogo_paises.duplicated(["content_id", "country"]).sum(), 0)

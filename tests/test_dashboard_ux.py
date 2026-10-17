"""UI behavior with a small in-memory catalog; official CSVs are not required."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def sample_views():
    catalog = pd.DataFrame(
        {
            "content_id": ["Movie_m1", "Movie_m2", "TV Show_s1"],
            "show_id": ["m1", "m2", "s1"],
            "title": ["Ejemplo A", "Ejemplo B", "Ejemplo C"],
            "type": ["Movie", "Movie", "TV Show"],
            "release_year": [2020, 2021, 2022],
            "language": ["es", "en", "es"],
            "popularity": [12.0, 8.0, 6.0],
            "vote_average": [8.0, 7.0, 6.0],
            "vote_count": [200, 150, 120],
        }
    )
    return {
        "catalogo_general": catalog,
        "catalogo_popularity": catalog.copy(),
        "catalogo_generos": pd.DataFrame(
            {
                "content_id": ["Movie_m1", "Movie_m1", "Movie_m2", "TV Show_s1", "TV Show_s1"],
                "genre": ["Drama", "Acción", "Drama", "Comedia", "Género de área pequeña"],
            }
        ),
        "catalogo_paises": pd.DataFrame(
            {
                "content_id": ["Movie_m1", "Movie_m2", "TV Show_s1"],
                "country": ["Chile", "United States of America", "Chile"],
            }
        ),
        "catalogo_directores": pd.DataFrame(
            {"content_id": ["Movie_m1", "Movie_m2"], "director": ["Directora A", "Director B"]}
        ),
        "catalogo_cast": pd.DataFrame(
            {"content_id": ["Movie_m1", "Movie_m2"], "actor": ["Actriz A", "Actor B"]}
        ),
        "movies_financial_valid": pd.DataFrame(
            {
                "show_id": ["m1", "m2"],
                "title": ["Ejemplo A", "Ejemplo B"],
                "budget": [100.0, 200.0],
                "revenue": [300.0, 400.0],
            }
        ),
    }


class DashboardUxTests(unittest.TestCase):
    def setUp(self):
        import streamlit as st

        st.cache_data.clear()
        self.data_patch = patch("src.dashboard_data.load_views", return_value=sample_views())
        self.data_patch.start()
        self.addCleanup(self.data_patch.stop)
        self.app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=60).run()
        self.assertEqual(len(self.app.exception), 0)

    def test_treemap_base_filters_and_empty_recovery(self):
        frame = self.app.get("iframe")[0].proto.srcdoc
        payload = json.loads(frame.split("const payload = ", 1)[1].split(";", 1)[0])
        self.assertEqual(payload["selectedTitles"], 3)
        self.assertEqual(sum(row["value"] for row in payload["records"]), 5)
        self.assertIn("los porcentajes no suman 100 %", frame)
        self.assertTrue(any("Filtros aplicados: ninguno" in item.value for item in self.app.caption))

        self.app.multiselect[0].set_value(["Movie"])
        self.app.multiselect[1].set_value(["Comedia"])
        self.app.run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertTrue(any("No hay contenidos" in item.value for item in self.app.warning))
        self.assertTrue(any("Tipo: Película" in item.value for item in self.app.caption))
        self.assertTrue(any("Género: Comedia" in item.value for item in self.app.caption))

        self.app.button[1].click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.app.metric[0].value, "3")
        self.assertEqual(self.app.multiselect[0].value, [])
        self.assertEqual(self.app.multiselect[1].value, [])

    def test_acquisition_uses_same_filter_feedback(self):
        self.app.segmented_control[0].set_value("Contenidos y adquisición").run()
        self.assertEqual(len(self.app.exception), 0)
        self.app.multiselect[0].set_value(["Movie"])
        self.app.multiselect[1].set_value(["Drama"])
        self.app.multiselect[2].set_value(["Chile"])
        self.app.run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.app.metric[0].value, "1")
        self.assertTrue(any("País: Chile" in item.value for item in self.app.caption))
        frame = self.app.get("iframe")[0].proto.srcdoc
        payload = json.loads(frame.split("const payload = ", 1)[1].split(";", 1)[0])
        self.assertEqual(payload["selectedTitles"], 1)
        self.assertEqual(sum(row["value"] for row in payload["records"]), 2)


if __name__ == "__main__":
    unittest.main()

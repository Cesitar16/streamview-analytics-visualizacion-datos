"""End-to-end smoke checks of both Streamlit perspectives."""

import json
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


def chart_types(app):
    return [
        [trace["type"] for trace in json.loads(chart.proto.spec)["data"]]
        for chart in app.get("plotly_chart")
    ]


def metrics(app):
    return {item.label: item.value for item in app.metric}


class DashboardAppTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(
            str(Path(__file__).resolve().parents[1] / "dashboard" / "app.py"),
            default_timeout=90,
        ).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_executive_filters_map_notes_and_reset(self):
        app = self.app()
        self.assertEqual(metrics(app)["Títulos"], "31.991")
        self.assertEqual(metrics(app)["Películas"], "16.000")
        self.assertEqual(metrics(app)["Series"], "15.991")
        self.assertEqual(len(app.get("iframe")), 1)
        self.assertIn("Drama", app.get("iframe")[0].proto.srcdoc)
        self.assertEqual(len(app.get("download_button")), 1)
        self.assertIn(["choropleth"], chart_types(app))
        maps = [json.loads(chart.proto.spec)["data"][0] for chart in app.get("plotly_chart")
                if json.loads(chart.proto.spec)["data"][0]["type"] == "choropleth"]
        self.assertEqual(len(maps[0]["locations"]), 147)
        self.assertTrue(any("No permite inferir altas reales" in note.value for note in app.caption))
        self.assertTrue(any("Diferencia: 9 títulos" in note.value for note in app.caption))
        self.assertEqual(chart_types(app)[0], ["scatter", "scatter"])
        self.assertEqual(len(app.selectbox), 2)

        app.multiselect[0].set_value(["Movie"])
        app.multiselect[1].set_value(["Drama"])
        app.slider[0].set_value((2020, 2023))
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(metrics(app)["Series"], "0")
        self.assertGreater(int(metrics(app)["Títulos"].replace(".", "")), 0)
        self.assertIn(["choropleth"], chart_types(app))

        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(metrics(app)["Títulos"], "31.991")
        self.assertEqual(app.multiselect[0].value, [])
        self.assertEqual(app.multiselect[1].value, [])
        self.assertEqual(app.slider[0].value, (2010, 2025))

    def test_acquisition_cross_filters_finance_map_thresholds_and_reset(self):
        app = self.app()
        app.segmented_control[0].set_value("Contenidos y adquisición").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(metrics(app)["Títulos"], "31.991")
        self.assertEqual(metrics(app)["Películas elegibles"], "3.540")
        self.assertEqual(len(app.get("download_button")), 2)
        self.assertIn(["choropleth"], chart_types(app))
        maps = [json.loads(chart.proto.spec)["data"][0] for chart in app.get("plotly_chart")
                if json.loads(chart.proto.spec)["data"][0]["type"] == "choropleth"]
        self.assertEqual(len(maps[0]["locations"]), 35)
        self.assertTrue(any("Eje acotado" in note.value for note in app.caption))
        self.assertTrue(any("muestra parcial" in item.value for item in app.get("markdown")))
        self.assertTrue(any("clasificación etaria" in note.value.lower() for note in app.caption))

        app.multiselect[0].set_value(["Movie"])
        app.multiselect[1].set_value(["Action"])
        app.multiselect[2].set_value(["United States of America"])
        app.multiselect[3].set_value(["en"])
        app.slider[0].set_value((2020, 2023))
        app.slider[1].set_value((5.0, 8.0))
        app.slider[2].set_value(250)
        app.slider[3].set_value(200)
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(metrics(app)["Títulos"], "416")
        self.assertEqual(metrics(app)["Películas elegibles"], "128")
        self.assertEqual(app.slider[2].value, 250)
        self.assertEqual(app.slider[3].value, 200)
        self.assertIn(["choropleth"], chart_types(app))

        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(metrics(app)["Títulos"], "31.991")
        self.assertEqual(metrics(app)["Películas elegibles"], "3.540")
        self.assertEqual(app.slider[2].value, 100)
        self.assertEqual(app.slider[3].value, 100)

        app.multiselect[0].set_value(["TV Show"]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(metrics(app)["Títulos"], "15.991")
        self.assertEqual(metrics(app)["Películas elegibles"], "0")
        self.assertTrue(any("no contiene películas" in note.value for note in app.info))
        self.assertIn(["choropleth"], chart_types(app))
        self.assertEqual(len(app.get("download_button")), 2)


if __name__ == "__main__":
    unittest.main()

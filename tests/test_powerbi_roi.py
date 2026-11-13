"""Check that the ROI card references a measure present in both model sources."""

import json
import unittest
from pathlib import Path

from scripts.build_powerbi_model import MEASURES

ROOT = Path(__file__).resolve().parents[1]


class PowerBiRoiTests(unittest.TestCase):
    def test_roi_card_has_documented_measure_in_model_and_generator(self):
        report = ROOT / "powerbi/StreamView_EP2.Report/definition/pages/f5a580efa104354849b6/visuals/516c60f7de7557f1a8b0/visual.json"
        model = ROOT / "powerbi/StreamView_EP2.SemanticModel/definition/tables/catalogo.tmdl"
        card = json.loads(report.read_text(encoding="utf-8"))
        field = card["visual"]["query"]["queryState"]["Data"]["projections"][0]["field"]["Measure"]["Property"]
        formula = "DIVIDE([Ingresos totales] - [Presupuesto total], [Presupuesto total])"
        self.assertEqual(field, "ROI bruto aproximado")
        self.assertEqual(MEASURES[field], (formula, "0.00%"))
        self.assertIn(f"measure '{field}' = {formula}\n\t\tformatString: 0.00%", model.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

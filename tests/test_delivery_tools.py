"""Focused checks for portable Power BI data paths."""

import tempfile
import unittest
from pathlib import Path

from scripts.rebase_powerbi_sources import SOURCE, TABLES, rebase


class RebasePowerBISourcesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.project = root / "powerbi"
        self.data = self.project / "data"
        self.tables = self.project / "StreamView_EP2.SemanticModel/definition/tables"
        self.data.mkdir(parents=True)
        self.tables.mkdir(parents=True)
        for name in TABLES:
            (self.data / f"{name}.csv").write_text("content_id\n", encoding="utf-8")
            (self.tables / f"{name}.tmdl").write_text(
                f'table {name}\n\tmeasure Test = DISTINCTCOUNT(catalogo[content_id])\n'
                f'\tFile.Contents("C:\\old\\{name}.csv")\n',
                encoding="utf-8",
            )

    def test_rebases_all_six_sources_without_changing_measures(self):
        self.assertEqual(rebase(self.project, self.data), 6)
        self.assertEqual(rebase(self.project, self.data), 0)
        for name in TABLES:
            text = (self.tables / f"{name}.tmdl").read_text(encoding="utf-8")
            self.assertEqual(SOURCE.findall(text), [str((self.data / f"{name}.csv").resolve())])
            self.assertIn("measure Test = DISTINCTCOUNT(catalogo[content_id])", text)

    def test_missing_data_prevents_partial_rewrite(self):
        (self.data / "finanzas.csv").unlink()
        with self.assertRaises(FileNotFoundError):
            rebase(self.project, self.data)
        self.assertIn("C:\\old\\catalogo.csv", (self.tables / "catalogo.tmdl").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

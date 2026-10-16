"""Export the approved EP1 views to a compact, Power BI-ready relational model."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard_data import load_views  # noqa: E402


DESTINATION = ROOT / "powerbi/data"


def export() -> dict[str, int]:
    views = load_views()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    catalog = views["catalogo_general"].copy()
    # Power BI agrupa categorías de texto iguales. El identificador visible evita
    # fusionar películas/series homónimas en tablas y rankings financieros.
    repeated = catalog.duplicated(["title", "release_year"], keep=False)
    catalog["display_title"] = (
        catalog["title"].astype("string")
        + " (" + catalog["release_year"].astype("string")
        + catalog["content_id"].where(repeated, "").radd(", ").where(repeated, "")
        + ")"
    )
    language_labels = json.loads(
        (Path(__file__).with_name("language_labels.json")).read_text(encoding="utf-8")
    )
    catalog["language_label"] = catalog["language"].map(language_labels)
    if catalog["language_label"].isna().any():
        raise ValueError("Falta una etiqueta para un código de idioma del catálogo")
    catalog_columns = [
        "content_id", "show_id", "type", "title", "display_title", "release_year", "date_added",
        "language", "language_label", "popularity", "popularity_conflict", "vote_average", "vote_count",
    ]
    tables = {
        "catalogo": catalog[catalog_columns],
        "generos": views["catalogo_generos"][["content_id", "genre"]],
        "paises": views["catalogo_paises"][["content_id", "country"]],
        "directores": views["catalogo_directores"][["content_id", "director"]],
        "actores": views["catalogo_cast"][["content_id", "actor"]],
    }
    finance = views["movies_financial_valid"][["show_id", "title", "budget", "revenue"]].copy()
    finance.insert(0, "content_id", "Movie_" + finance["show_id"].astype("string"))
    finance["return_multiple"] = finance["revenue"] / finance["budget"]
    tables["finanzas"] = finance.drop(columns=["show_id", "title"])
    for name, table in tables.items():
        table.to_csv(DESTINATION / f"{name}.csv", index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
    return {name: len(table) for name, table in tables.items()}


if __name__ == "__main__":
    for name, rows in export().items():
        print(f"{name}: {rows:,} filas")

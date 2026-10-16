"""Apply the final readability changes to an existing EP2 PBIR report.

Run with Power BI Desktop closed, then reopen and refresh the PBIP.
"""

from __future__ import annotations

import json

from build_powerbi_report import col, ident, mea, projection, save
from build_powerbi_model import MEASURES
from refine_powerbi_report import (
    CONTEXT_MEASURES,
    PAGES,
    add_measure,
    clear_slicers_button,
    context_card,
    literal,
    normalize_layer_order,
    polish_visual_labels,
    scatter_minimum_votes,
    textbox,
    update_visual,
)


def main() -> None:
    executive, analytical = json.loads(
        (PAGES / "pages.json").read_text(encoding="utf-8")
    )["pageOrder"]

    for name, dax in CONTEXT_MEASURES.items():
        add_measure(name, dax, None)
    coverage_dax, coverage_format = MEASURES["Resumen cobertura financiera"]
    add_measure("Resumen cobertura financiera", coverage_dax, coverage_format)

    update_visual(executive, "page_title", position={"width": 720})
    update_visual(analytical, "page_title", position={"width": 720})
    context_card(executive, "context_main", "Contexto principal", 1050, 20, 830, 55)
    add_measure(
        "Diferencia entre tipos",
        'VAR m = CALCULATE([Total contenidos], KEEPFILTERS(catalogo[type] = "Movie")) '
        'VAR s = CALCULATE([Total contenidos], KEEPFILTERS(catalogo[type] = "TV Show")) '
        'RETURN IF(m > 0 && s > 0, "Diferencia entre tipos: " & FORMAT(ABS(m - s), "#,0") & " títulos", '
        '"Un solo tipo visible")',
        None,
    )
    context_card(executive, "type_difference", "Diferencia entre tipos", 1090, 677, 790, 26)
    textbox(executive, "year_source_note",
            "Año de incorporación = año de estreno en la fuente; no representa altas reales.",
            310, 677, 760, 26, 15, "#43566B")
    context_card(analytical, "context_main", "Contexto principal", 1050, 8, 830, 36)
    context_card(analytical, "context_detail", "Contexto secundario", 1050, 45, 830, 35)
    context_card(analytical, "finance_coverage", "Resumen cobertura financiera",
                 310, 1201, 1550, 28)
    clear_slicers_button(executive)
    clear_slicers_button(analytical)
    textbox(analytical, "finance_note",
            "Finanzas: verde = ingresos ≥ presupuesto; coral = por debajo. M = millones; el cociente bruto no es utilidad neta.",
            310, 1650, 1550, 45, 18, "#43566B")

    for key, title in {
        "releases": "Distribución por año de estreno registrado · ≈2.000/año sin filtros",
        "countries": "Países con más producciones · hasta 10",
        "genres": "Géneros más frecuentes · hasta 10, solapados",
    }.items():
        update_visual(executive, key, title=title)
    update_visual(executive, "releases", visual_type="clusteredColumnChart")
    update_visual(executive, "languages", title="Idiomas con más títulos · hasta 10",
                  roles={"Category": [col("catalogo", "language_label")],
                         "Y": [mea("Top 10 idiomas")]})

    for key, title in {
        "pop_rating": "Popularidad y calificación · ≥250 votos; escala log",
        "genre_rating": "Géneros mejor valorados · hasta 10; ≥100 títulos",
        "genre_volume": "Géneros con más títulos · hasta 10, solapados",
        "top_rated": "Títulos mejor valorados · hasta 10; ≥100 votos",
        "revenue_titles": "Películas con mayores ingresos · hasta 10",
    }.items():
        update_visual(analytical, key, title=title)
    update_visual(analytical, "filter_language",
                  roles={"Values": [col("catalogo", "language_label")]})
    scatter_minimum_votes(analytical)

    # Preserve bubble area for title count and use a sequential color scale for rating.
    map_path = PAGES / analytical / "visuals" / ident(analytical + "/country_map") / "visual.json"
    map_data = json.loads(map_path.read_text(encoding="utf-8"))
    map_visual = map_data["visual"]
    map_visual["visualContainerObjects"]["title"][0]["properties"]["text"] = literal(
        "'Países (≥30): tamaño = títulos · tono = nota'"
    )
    map_controls = map_visual.setdefault("objects", {}).setdefault(
        "mapControls", [{"properties": {}}]
    )
    map_controls[0]["properties"]["defaultStyle"] = literal("'grayscale_light'")
    map_visual.setdefault("objects", {})["bubbleLayer"] = [
        {"properties": {"show": literal("true"),
                        "markerType": literal("'icon'"),
                        "sizeByValue": literal("true")}},
        {"properties": {"fillColor": {"solid": {"color": {"expr": {"FillRule": {
            "Input": {"Measure": {"Expression": {"SourceRef": {"Entity": "catalogo"}},
                                  "Property": "Calificación promedio"}},
            "FillRule": {"linearGradient2": {
                "min": {"color": {"Literal": {"Value": "'#65B8E8'"}}},
                "max": {"color": {"Literal": {"Value": "'#123B7A'"}}},
                "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}},
            }},
        }}}}}},
         "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}},
    ]
    save(map_path, map_data)

    scatter_path = PAGES / analytical / "visuals" / ident(analytical + "/budget_revenue") / "visual.json"
    scatter_data = json.loads(scatter_path.read_text(encoding="utf-8"))
    scatter_visual = scatter_data["visual"]
    scatter_visual["visualContainerObjects"]["title"][0]["properties"]["text"] = literal(
        "'Presupuesto e ingresos · verde: cubre presupuesto'"
    )
    scatter_visual["query"]["queryState"]["Tooltips"] = {"projections": [
        projection(*col("catalogo", "display_title")),
        projection(*mea("Ingresos / presupuesto")),
    ]}
    ratio = {"Measure": {"Expression": {"SourceRef": {"Entity": "catalogo"}},
                         "Property": "Ingresos / presupuesto"}}
    scatter_visual.setdefault("objects", {})["dataPoint"] = [{
        "properties": {"fill": {"solid": {"color": {"expr": {"Conditional": {
            "Cases": [
                {"Condition": {"Comparison": {"ComparisonKind": 2, "Left": ratio,
                                              "Right": {"Literal": {"Value": "1D"}}}},
                 "Value": {"Literal": {"Value": "'#187A75'"}}},
                {"Condition": {"Comparison": {"ComparisonKind": 3, "Left": ratio,
                                              "Right": {"Literal": {"Value": "1D"}}}},
                 "Value": {"Literal": {"Value": "'#D76B5C'"}}},
            ],
        }}}}}},
        "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]},
    }]
    save(scatter_path, scatter_data)

    for page in (executive, analytical):
        polish_visual_labels(page)
        for path in (PAGES / page / "visuals").glob("*/visual.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data["visual"]["visualType"] == "slicer":
                data["visual"]["visualContainerObjects"]["title"][0]["properties"]["show"] = literal("false")
                save(path, data)
        normalize_layer_order(page)


if __name__ == "__main__":
    main()

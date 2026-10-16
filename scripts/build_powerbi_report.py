"""Populate the Desktop-created enhanced PBIR report with two EP2 pages."""

from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(os.environ.get("EP2_PROJECT_DIR", ROOT / "powerbi"))
DEFINITION = PROJECT_ROOT / "StreamView_EP2.Report/definition"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json"


def ident(name: str) -> str:
    return uuid5(NAMESPACE_URL, "streamview-ep2/visual/" + name).hex[:20]


def save(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def projection(table: str, field: str, kind: str = "Column") -> dict:
    return {
        "field": {kind: {"Expression": {"SourceRef": {"Entity": table}}, "Property": field}},
        "queryRef": f"{table}.{field}", "nativeQueryRef": field,
    }


def visual(page: str, key: str, visual_type: str, x: int, y: int, w: int, h: int,
           roles: dict[str, list[tuple[str, str, str]]], title: str | None = None,
           sort_by: tuple[str, str, str] | None = None) -> None:
    page_dir = DEFINITION / "pages" / page
    name = ident(page + "/" + key)
    query_state = {role: {"projections": [projection(*entry) for entry in entries]}
                   for role, entries in roles.items()}
    num = len(list((page_dir / "visuals").glob("*/visual.json"))) + 1
    query: dict = {"queryState": query_state}
    if sort_by:
        query["sortDefinition"] = {"sort": [{"field": projection(*sort_by)["field"],
                                              "direction": "Descending"}],
                                   "isDefaultSort": False}
    v: dict = {"visualType": visual_type, "query": query,
               "drillFilterOtherVisuals": True}
    if title:
        v["visualContainerObjects"] = {"title": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": "'" + title.replace("'", "''") + "'"}}},
        }}]}
    if visual_type == "slicer" and key in {"filter_release_year", "filter_vote_average"}:
        v["objects"] = {"data": [{"properties": {
            "mode": {"expr": {"Literal": {"Value": "'Between'"}}}
        }}]}
    if visual_type == "cardVisual" and roles["Data"][0][1] in {
        "Total contenidos", "Total películas", "Total series",
        "Países representados", "Idiomas disponibles", "Géneros",
        "Películas financieras",
    }:
        v["objects"] = {"value": [{"properties": {
            "labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}}
        }, "selector": {"id": "default"}}]}
    if key == "releases":
        v["objects"] = {"valueAxis": [{"properties": {
            "start": {"expr": {"Literal": {"Value": "0D"}}}
        }}]}
    save(page_dir / "visuals" / name / "visual.json", {
        "$schema": SCHEMA, "name": name,
        "position": {"x": x, "y": y, "z": num * 1000, "height": h,
                     "width": w, "tabOrder": num * 1000},
        "visual": v,
    })


def col(table: str, field: str) -> tuple[str, str, str]:
    return table, field, "Column"


def mea(field: str) -> tuple[str, str, str]:
    return "catalogo", field, "Measure"


def slicers(page: str, analytical: bool = False) -> None:
    fields = [("Tipo", "catalogo", "type"), ("Año de estreno", "catalogo", "release_year"),
              ("Género", "generos", "genre")]
    if analytical:
        fields += [("País", "paises", "country"), ("Idioma", "catalogo", "language"),
                   ("Calificación", "catalogo", "vote_average")]
    for i, (label, table, field) in enumerate(fields):
        visual(page, "filter_" + field, "slicer", 25, 90 + i * 150, 255, 125,
               {"Values": [col(table, field)]}, label)


def card(page: str, key: str, title: str, measure: str, x: int, y: int, w: int = 365) -> None:
    visual(page, key, "cardVisual", x, y, w, 115, {"Data": [mea(measure)]}, title)


def chart(page: str, key: str, title: str, vtype: str, x: int, y: int,
          w: int, h: int, roles: dict[str, list[tuple[str, str, str]]],
          sort_by: tuple[str, str, str] | None = None) -> None:
    visual(page, key, vtype, x, y, w, h, roles, title, sort_by)


def main() -> None:
    pages_dir = DEFINITION / "pages"
    original = pages_dir / "0ba758a715996c4bb135"
    if not original.is_dir():
        raise FileNotFoundError("Save a blank Power BI project first")
    executive = original.name
    analytical = "f" + ident("page-analytical")[:19]
    schema = json.loads((original / "page.json").read_text(encoding="utf-8"))["$schema"]
    save(original / "page.json", {"$schema": schema, "name": executive,
         "displayName": "01 | Dirección ejecutiva", "displayOption": "FitToWidth",
         "height": 1320, "width": 1920})
    save(pages_dir / analytical / "page.json", {"$schema": schema, "name": analytical,
         "displayName": "02 | Contenidos y adquisición", "displayOption": "FitToWidth",
         "height": 1740, "width": 1920})
    metadata = json.loads((pages_dir / "pages.json").read_text(encoding="utf-8"))
    metadata["pageOrder"] = [executive, analytical]
    metadata["activePageName"] = executive
    save(pages_dir / "pages.json", metadata)

    slicers(executive)
    for i, (title, measure) in enumerate([
        ("Contenidos", "Total contenidos"), ("Películas", "Total películas"),
        ("Series", "Total series"), ("Países", "Países representados"),
        ("Idiomas", "Idiomas disponibles"), ("Géneros", "Géneros"),
        ("Popularidad media", "Popularidad promedio"),
        ("Calificación media", "Calificación promedio"),
    ]):
        card(executive, "kpi_" + measure, title, measure,
             310 + (i % 4) * 395, 95 + (i // 4) * 130)
    chart(executive, "releases", "Estrenos por año (la incorporación coincide en estas fuentes)",
          "lineChart", 310, 385, 760, 290,
          {"Category": [col("catalogo", "release_year")], "Y": [mea("Total contenidos")]})
    chart(executive, "types", "Películas y series", "clusteredBarChart", 1090, 385, 790, 290,
          {"Category": [col("catalogo", "type")], "Y": [mea("Total contenidos")]})
    chart(executive, "countries", "Producciones asociadas por país", "clusteredBarChart",
          310, 705, 500, 540,
          {"Category": [col("paises", "country")], "Y": [mea("Total contenidos")]},
          mea("Total contenidos"))
    chart(executive, "genres", "Géneros por volumen (categorías solapadas)", "treemap",
          835, 705, 500, 540,
          {"Group": [col("generos", "genre")], "Values": [mea("Total contenidos")]})
    chart(executive, "languages", "Idiomas del catálogo", "clusteredBarChart",
          1360, 705, 520, 540,
          {"Category": [col("catalogo", "language")], "Y": [mea("Total contenidos")]},
          mea("Total contenidos"))

    slicers(analytical, analytical=True)
    for i, (title, measure) in enumerate([
        ("Contenidos", "Total contenidos"), ("Popularidad mediana", "Popularidad mediana"),
        ("Calificación media", "Calificación promedio"),
        ("Películas financieras", "Películas financieras"),
    ]):
        card(analytical, "kpi_" + measure, title, measure, 310 + i * 395, 95)
    chart(analytical, "pop_rating", "Popularidad y calificación por título",
          "scatterChart", 310, 240, 760, 410,
          {"Category": [col("catalogo", "content_id")],
           "Series": [col("catalogo", "type")],
           "X": [mea("Popularidad por título")],
           "Y": [mea("Calificación por título")],
           "Size": [mea("Votos totales")]})
    chart(analytical, "genre_rating", "Calificación media por género",
          "clusteredBarChart", 1090, 240, 790, 410,
          {"Category": [col("generos", "genre")], "Y": [mea("Calificación promedio")]},
          mea("Calificación promedio"))
    chart(analytical, "genre_volume", "Géneros por volumen", "treemap",
          310, 680, 760, 380,
          {"Group": [col("generos", "genre")], "Values": [mea("Total contenidos")]})
    chart(analytical, "top_rated", "Títulos y valoración (ordenar por votos y nota)",
          "tableEx", 1090, 680, 790, 380,
          {"Values": [col("catalogo", "title"), col("catalogo", "type"),
                      col("catalogo", "vote_average"), col("catalogo", "vote_count")]})
    for i, (title, measure) in enumerate([
        ("Presupuesto medio", "Presupuesto promedio"),
        ("Presupuesto total", "Presupuesto total"),
        ("Ingresos totales", "Ingresos totales"),
        ("Ingresos/presupuesto", "Ingresos / presupuesto"),
    ]):
        card(analytical, "finance_" + measure, title, measure, 310 + i * 395, 1085)
    chart(analytical, "budget_revenue", "Presupuesto e ingresos por película elegible",
          "scatterChart", 310, 1230, 760, 420,
          {"Category": [col("finanzas", "content_id")],
           "X": [mea("Presupuesto total")], "Y": [mea("Ingresos totales")]})
    chart(analytical, "revenue_titles", "Ingresos por título (subconjunto elegible)",
          "clusteredBarChart", 1090, 1230, 790, 420,
          {"Category": [col("catalogo", "title")], "Y": [mea("Ingresos totales")]},
          mea("Ingresos totales"))
    print("PBIR escrito: 2 páginas, 9 segmentadores y 36 visualizaciones")


if __name__ == "__main__":
    main()

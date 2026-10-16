"""Improve the EP2 PBIR pages after build_powerbi_report.py has run.

Set EP2_PROJECT_DIR to a copy of powerbi when reviewing changes while Desktop
still has the original PBIP open.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from build_powerbi_report import DEFINITION, PROJECT_ROOT, SCHEMA, chart, col, ident, mea, save


REPORT = DEFINITION / "report.json"
PAGES = DEFINITION / "pages"
MODEL = PROJECT_ROOT / "StreamView_EP2.SemanticModel" / "definition" / "tables" / "catalogo.tmdl"
THEME = Path(__file__).resolve().parents[1] / "powerbi" / "StreamView-theme.json"

CONTEXT_MEASURES = {
    "Contexto principal": (
        'VAR t = IF(HASONEVALUE(catalogo[type]), SWITCH(SELECTEDVALUE(catalogo[type]), "Movie", "Películas", "TV Show", "Series", SELECTEDVALUE(catalogo[type])), IF(ISFILTERED(catalogo[type]), "Varios", "Todos")) '
        'VAR g = IF(HASONEVALUE(generos[genre]), SELECTEDVALUE(generos[genre]), IF(ISFILTERED(generos[genre]), "Varios", "Todos")) '
        'VAR p = IF(HASONEVALUE(paises[country]), SELECTEDVALUE(paises[country]), IF(ISFILTERED(paises[country]), "Varios", "Todos")) '
        'RETURN "Tipo: " & t & "  ·  Género: " & g & "  ·  País: " & p'
    ),
    "Contexto secundario": (
        'VAR i = IF(HASONEVALUE(catalogo[language_label]), SELECTEDVALUE(catalogo[language_label]), IF(ISFILTERED(catalogo[language_label]), "Varios", "Todos")) '
        'RETURN "Años: " & FORMAT(MIN(catalogo[release_year]), "0") & "–" & FORMAT(MAX(catalogo[release_year]), "0") & '
        '"  ·  Idioma: " & i & "  ·  Nota: " & FORMAT(MIN(catalogo[vote_average]), "0.0") & "–" & FORMAT(MAX(catalogo[vote_average]), "0.0")'
    ),
}


def literal(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


FIELD_NAMES = {
    "catalogo.type": "Tipo", "catalogo.release_year": "Año de estreno",
    "catalogo.display_title": "Título", "catalogo.vote_average": "Calificación",
    "catalogo.vote_count": "Votos", "catalogo.language_label": "Idioma",
    "catalogo.content_id": "Título", "finanzas.content_id": "Película",
    "generos.genre": "Género", "paises.country": "País",
    "directores.director": "Director", "actores.actor": "Intérprete",
}


def update_visual(page: str, key: str, *, title: str | None = None,
                  visual_type: str | None = None, roles: dict | None = None,
                  sort_by: tuple[str, str, str] | None = None,
                  position: dict | None = None) -> Path:
    path = PAGES / page / "visuals" / ident(page + "/" + key) / "visual.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    visual = data["visual"]
    if title is not None:
        visual["visualContainerObjects"]["title"][0]["properties"]["text"] = literal(
            "'" + title.replace("'", "''") + "'"
        )
    if visual_type is not None:
        visual["visualType"] = visual_type
    if roles is not None:
        from build_powerbi_report import projection
        visual["query"]["queryState"] = {
            role: {"projections": [projection(*field) for field in fields]}
            for role, fields in roles.items()
        }
    if sort_by is not None:
        from build_powerbi_report import projection
        visual["query"]["sortDefinition"] = {
            "sort": [{"field": projection(*sort_by)["field"], "direction": "Descending"}],
            "isDefaultSort": False,
        }
    if position is not None:
        data["position"].update(position)
    save(path, data)
    return path


def add_measure(name: str, dax: str, fmt: str | None = "#,0") -> None:
    from build_powerbi_model import guid
    content = MODEL.read_text(encoding="utf-8")
    if f"\tmeasure '{name}' =" in content:
        return
    insertion = f"\tmeasure '{name}' = {dax}\n"
    if fmt is not None:
        insertion += f"\t\tformatString: {fmt}\n"
    insertion += f"\t\tlineageTag: {guid('measure/' + name)}\n\n"
    content = content.replace("\tpartition catalogo = m", insertion + "\tpartition catalogo = m")
    MODEL.write_text(content, encoding="utf-8")


def register_theme() -> None:
    target = PROJECT_ROOT / "StreamView_EP2.Report" / "StaticResources" / "RegisteredResources" / "StreamView-EP2.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(THEME, target)
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    data["themeCollection"]["customTheme"] = {
        "name": target.name,
        "reportVersionAtImport": data["themeCollection"]["baseTheme"]["reportVersionAtImport"],
        "type": "RegisteredResources",
    }
    data["resourcePackages"] = [p for p in data["resourcePackages"] if p["name"] != "RegisteredResources"]
    data["resourcePackages"].append({
        "name": "RegisteredResources", "type": "RegisteredResources",
        "items": [{"name": target.name, "path": target.name, "type": "CustomTheme"}],
    })
    save(REPORT, data)


def page_background(page: str) -> None:
    path = PAGES / page / "page.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["objects"] = {"background": [{"properties": {
        "color": {"solid": {"color": literal("'#F3F6FA'")}},
        "transparency": literal("0D"),
    }}]}
    save(path, data)


def top_rated_filters(page: str) -> None:
    path = PAGES / page / "visuals" / ident(page + "/top_rated") / "visual.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    source = {"Name": "c", "Entity": "catalogo", "Type": 0}
    def field(name: str, alias: bool = False) -> dict:
        return {"Column": {"Expression": {"SourceRef": {
            "Source" if alias else "Entity": "c" if alias else "catalogo"
        }}, "Property": name}}
    existing = [f for f in data.get("filterConfig", {}).get("filters", [])
                if f.get("name") not in {"FilterTopRatedTen", "FilterMinimumVotes"}]
    data["filterConfig"] = {"filters": [
        {
            "name": "FilterTopRatedTen", "field": field("display_title"), "type": "TopN",
            "filter": {"Version": 2, "From": [
                {"Name": "subquery", "Expression": {"Subquery": {"Query": {
                    "Version": 2, "From": [source],
                    "Select": [{**field("display_title", True), "Name": "field"}],
                    "Where": [{"Condition": {"Comparison": {
                        "ComparisonKind": 2, "Left": field("vote_count", True),
                        "Right": {"Literal": {"Value": "100L"}},
                    }}}],
                    "OrderBy": [{"Direction": 2, "Expression": {"Aggregation": {
                        "Expression": field("vote_average", True), "Function": 4,
                    }}}, {"Direction": 2, "Expression": {"Aggregation": {
                        "Expression": field("vote_count", True), "Function": 4,
                    }}}, {"Direction": 1, "Expression": field("display_title", True)}],
                    "Top": 10,
                }}}, "Type": 2},
                source,
            ], "Where": [{"Condition": {"In": {
                "Expressions": [field("display_title", True)],
                "Table": {"SourceRef": {"Source": "subquery"}},
            }}}]}, "howCreated": "User",
        },
        {
            "name": "FilterMinimumVotes", "field": field("vote_count"),
            "type": "Advanced", "filter": {"Version": 2, "From": [source],
                "Where": [{"Condition": {"Comparison": {
                    "ComparisonKind": 2, "Left": field("vote_count", True),
                    "Right": {"Literal": {"Value": "100L"}},
                }}}]}, "howCreated": "User",
        },
    ] + existing}
    save(path, data)


def scatter_minimum_votes(page: str, minimum: int = 250) -> None:
    path = PAGES / page / "visuals" / ident(page + "/pop_rating") / "visual.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    existing = [f for f in data.get("filterConfig", {}).get("filters", [])
                if f.get("name") != "FilterScatterMinimumVotes"]
    data["filterConfig"] = {"filters": existing + [{
        "name": "FilterScatterMinimumVotes",
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "catalogo"}},
                              "Property": "vote_count"}},
        "type": "Advanced", "filter": {"Version": 2,
            "From": [{"Name": "c", "Entity": "catalogo", "Type": 0}],
            "Where": [{"Condition": {"Comparison": {
                "ComparisonKind": 2,
                "Left": {"Column": {"Expression": {"SourceRef": {"Source": "c"}},
                                   "Property": "vote_count"}},
                "Right": {"Literal": {"Value": f"{minimum}L"}},
            }}}]}, "howCreated": "User",
    }]}
    save(path, data)


def polish_visual_labels(page: str) -> None:
    for path in (PAGES / page / "visuals").glob("*/visual.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        visual = data["visual"]
        for role in visual.get("query", {}).get("queryState", {}).values():
            for item in role.get("projections", []):
                caption = FIELD_NAMES.get(item.get("queryRef"))
                if caption:
                    item["displayName"] = caption
        kind = visual.get("visualType")
        if kind in {"lineChart", "clusteredBarChart", "scatterChart", "treemap",
                    "azureMap", "tableEx"}:
            visual.setdefault("visualContainerObjects", {})["subTitle"] = [
                {"properties": {"show": literal("false")}}
            ]
        if kind == "cardVisual":
            visual.setdefault("objects", {})["label"] = [
                {"properties": {"show": literal("false")}, "selector": {"id": "default"}}
            ]
        save(path, data)


def context_card(page: str, key: str, measure: str, x: int, y: int,
                 width: int, height: int) -> None:
    from build_powerbi_report import projection
    name = ident(page + "/" + key)
    save(PAGES / page / "visuals" / name / "visual.json", {
        "$schema": SCHEMA, "name": name,
        "position": {"x": x, "y": y, "z": 1000, "width": width,
                     "height": height, "tabOrder": 1000},
        "visual": {"visualType": "cardVisual", "query": {"queryState": {
            "Data": {"projections": [projection(*mea(measure))]}
        }}, "objects": {
            "value": [{"properties": {"fontSize": literal("15D"),
                                      "fontColor": {"solid": {"color": literal("'#43566B'")}}},
                       "selector": {"id": "default"}}],
            "label": [{"properties": {"show": literal("false")},
                       "selector": {"id": "default"}}],
        }, "visualContainerObjects": {
            "title": [{"properties": {"show": literal("false")}}],
            "background": [{"properties": {"show": literal("false")}}],
            "border": [{"properties": {"show": literal("false")}}],
        }},
    })


def clear_slicers_button(page: str) -> None:
    name = ident(page + "/clear_slicers")
    save(PAGES / page / "visuals" / name / "visual.json", {
        "$schema": SCHEMA, "name": name,
        "position": {"x": 25, "y": 20, "z": 1000, "width": 255,
                     "height": 50, "tabOrder": 1000},
        "visual": {"visualType": "actionButton", "objects": {
            "fill": [{"properties": {"show": literal("true"),
                                     "fillColor": {"solid": {"color": literal("'#2778C7'")}}},
                      "selector": {"id": "default"}}],
            "text": [{"properties": {"show": literal("true"),
                                     "text": literal("'Borrar segmentadores'"),
                                     "fontSize": literal("16D"),
                                     "fontColor": {"solid": {"color": literal("'#FFFFFF'")}}},
                      "selector": {"id": "default"}}],
        }, "visualContainerObjects": {
            "visualLink": [{"properties": {
                "show": literal("true"),
                "type": literal("'ClearAllSlicers'"),
                "enabledTooltip": literal("'Borra los segmentadores de esta página'"),
            }}],
            "border": [{"properties": {"show": literal("false")}}],
        }},
    })


def normalize_layer_order(page: str) -> None:
    paths = list((PAGES / page / "visuals").glob("*/visual.json"))
    visuals = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in paths]
    visuals.sort(key=lambda item: (item[1]["position"]["y"], item[1]["position"]["x"]))
    for index, (path, data) in enumerate(visuals, 1):
        data["position"]["z"] = index * 1000
        data["position"]["tabOrder"] = index * 1000
        save(path, data)


def textbox(page: str, key: str, value: str, x: int, y: int,
            width: int, height: int, size: int, color: str = "#223247") -> None:
    name = ident(page + "/" + key)
    save(PAGES / page / "visuals" / name / "visual.json", {
        "$schema": SCHEMA, "name": name,
        "position": {"x": x, "y": y, "z": 1000, "width": width,
                     "height": height, "tabOrder": 1000},
        "visual": {"visualType": "textbox", "objects": {"general": [{"properties": {
            "paragraphs": [{"textRuns": [{"value": value, "textStyle": {
                "fontFamily": "Segoe UI Semibold" if size >= 24 else "Segoe UI",
                "fontSize": f"{size}px", "color": color,
            }}], "horizontalTextAlignment": "left"}],
        }}]}, "visualContainerObjects": {
            "background": [{"properties": {"show": literal("false")}}],
            "border": [{"properties": {"show": literal("false")}}],
        }},
    })


def main() -> None:
    pages = json.loads((PAGES / "pages.json").read_text(encoding="utf-8"))["pageOrder"]
    executive, analytical = pages
    register_theme()
    for page in pages:
        page_background(page)
    textbox(executive, "page_title", "STREAMVIEW  /  Panorama del catálogo",
            310, 15, 720, 70, 30)
    textbox(analytical, "page_title", "STREAMVIEW  /  Contenidos y adquisición",
            310, 15, 720, 70, 30)
    textbox(analytical, "finance_note",
            "Finanzas: películas con presupuesto e ingresos positivos. M = millones; ingresos/presupuesto es múltiplo bruto.",
            310, 1650, 1550, 45, 18, "#43566B")

    for name, dax in {
        "Top 10 países": "IF(RANKX(ALLSELECTED(paises[country]), CALCULATE([Total contenidos]),, DESC, DENSE) <= 10, [Total contenidos])",
        "Top 10 idiomas": "IF(RANKX(ALLSELECTED(catalogo[language_label]), CALCULATE([Total contenidos]),, DESC, DENSE) <= 10, [Total contenidos])",
        "Top 10 géneros": "IF(RANKX(ALLSELECTED(generos[genre]), CALCULATE([Total contenidos]),, DESC, DENSE) <= 10, [Total contenidos])",
        "Top 10 calificación géneros": "IF([Total contenidos] >= 100 && RANKX(FILTER(ALLSELECTED(generos[genre]), CALCULATE([Total contenidos]) >= 100), CALCULATE([Calificación promedio]),, DESC, DENSE) <= 10, [Calificación promedio])",
        "Contenidos por director": "DISTINCTCOUNT(directores[content_id])",
        "Contenidos por actor": "DISTINCTCOUNT(actores[content_id])",
        "Top 10 directores": "IF(RANKX(ALLSELECTED(directores[director]), CALCULATE([Contenidos por director]),, DESC, DENSE) <= 10, [Contenidos por director])",
        "Top 10 actores": "IF(RANKX(ALLSELECTED(actores[actor]), CALCULATE([Contenidos por actor]),, DESC, DENSE) <= 10, [Contenidos por actor])",
        "Top 10 ingresos": "IF(RANKX(ALLSELECTED(catalogo[display_title]), CALCULATE([Ingresos totales]),, DESC, DENSE) <= 10, [Ingresos totales])",
        "Cobertura país mínimo 30": "IF([Total contenidos] >= 30, [Total contenidos])",
        "Popularidad escala log": "IF(NOT ISBLANK([Popularidad por título]), LOG(1 + [Popularidad por título], 10))",
        **CONTEXT_MEASURES,
    }.items():
        add_measure(name, dax, "0.00" if name in {
            "Popularidad escala log", "Top 10 calificación géneros"
        } else None if name.startswith("Contexto ") else "#,0")

    context_card(executive, "context_main", "Contexto principal", 1050, 20, 830, 55)
    context_card(analytical, "context_main", "Contexto principal", 1050, 8, 830, 36)
    context_card(analytical, "context_detail", "Contexto secundario", 1050, 45, 830, 35)
    clear_slicers_button(executive)
    clear_slicers_button(analytical)

    update_visual(executive, "kpi_Total contenidos", title="Contenidos seleccionados")
    update_visual(executive, "releases", title="Títulos por año · ≈2.000/año en el catálogo completo")
    update_visual(executive, "countries", title="Países con más producciones · hasta 10",
                  roles={"Category": [col("paises", "country")], "Y": [mea("Top 10 países")]},
                  sort_by=mea("Top 10 países"))
    update_visual(executive, "genres", title="Géneros más frecuentes · hasta 10, solapados",
                  visual_type="clusteredBarChart",
                  roles={"Category": [col("generos", "genre")], "Y": [mea("Top 10 géneros")]},
                  sort_by=mea("Top 10 géneros"))
    update_visual(executive, "languages", title="Idiomas con más títulos · hasta 10",
                  roles={"Category": [col("catalogo", "language_label")], "Y": [mea("Top 10 idiomas")]},
                  sort_by=mea("Top 10 idiomas"))

    update_visual(analytical, "kpi_Total contenidos", title="Contenidos seleccionados")
    update_visual(analytical, "filter_language",
                  roles={"Values": [col("catalogo", "language_label")]})
    update_visual(analytical, "pop_rating", title="Popularidad y calificación · ≥250 votos; escala log",
                  roles={"Category": [col("catalogo", "content_id")],
                         "Series": [col("catalogo", "type")],
                         "X": [mea("Popularidad escala log")],
                         "Y": [mea("Calificación por título")],
                         "Size": [mea("Votos totales")],
                         "Tooltips": [mea("Popularidad por título")]})
    scatter_minimum_votes(analytical)
    update_visual(analytical, "genre_rating", title="Géneros mejor valorados · hasta 10; ≥100 títulos",
                  roles={"Category": [col("generos", "genre")],
                         "Y": [mea("Top 10 calificación géneros")]},
                  sort_by=mea("Top 10 calificación géneros"))
    update_visual(analytical, "genre_volume", title="Géneros con más títulos · hasta 10, solapados",
                  roles={"Group": [col("generos", "genre")],
                         "Values": [mea("Top 10 géneros")]})
    update_visual(analytical, "top_rated", title="Títulos mejor valorados · hasta 10; ≥100 votos",
                  roles={"Values": [col("catalogo", "display_title"), col("catalogo", "type"),
                                    col("catalogo", "vote_average"), col("catalogo", "vote_count")]},
                  sort_by=col("catalogo", "vote_average"))
    top_rated_filters(analytical)
    update_visual(analytical, "revenue_titles", title="Películas con mayores ingresos · hasta 10",
                  roles={"Category": [col("catalogo", "display_title")], "Y": [mea("Top 10 ingresos")]},
                  sort_by=mea("Top 10 ingresos"))

    # The extra row keeps the main analysis and the financial section readable
    # at normal Power BI zoom while adding the talent views required by EP2.
    page_path = PAGES / analytical / "page.json"
    page = json.loads(page_path.read_text(encoding="utf-8"))
    page["height"] = 2200
    save(page_path, page)
    chart(analytical, "director_top", "Directores con más títulos · incluye empates",
          "clusteredBarChart", 310, 1710, 490, 400,
          {"Category": [col("directores", "director")], "Y": [mea("Top 10 directores")]},
          mea("Top 10 directores"))
    chart(analytical, "actor_top", "Intérpretes con más títulos · incluye empates",
          "clusteredBarChart", 820, 1710, 490, 400,
          {"Category": [col("actores", "actor")], "Y": [mea("Top 10 actores")]},
          mea("Top 10 actores"))
    chart(analytical, "country_map", "Mapa de países · mínimo 30 títulos",
          "azureMap", 1330, 1710, 550, 400,
          {"Category": [col("paises", "country")],
           "Size": [mea("Cobertura país mínimo 30")],
           "Tooltips": [mea("Calificación promedio")]})
    for page_name in pages:
        polish_visual_labels(page_name)
        normalize_layer_order(page_name)
    print("Diseño EP2 refinado: paleta, rankings y talento")


if __name__ == "__main__":
    main()

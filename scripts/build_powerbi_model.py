"""Write the EP2 semantic model into a blank Power BI Desktop PBIP project.

Run only while the PBIP is closed in Power BI Desktop. The six CSV exports must
already exist. Power BI performs the actual data refresh when the project opens.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
import os


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(os.environ.get("EP2_PROJECT_DIR", ROOT / "powerbi"))
MODEL = PROJECT_ROOT / "StreamView_EP2.SemanticModel/definition"
DATA = ROOT / "powerbi/data"

TABLES = {
    "catalogo": {
        "content_id": "string", "show_id": "string", "type": "string",
        "title": "string", "display_title": "string", "release_year": "int64", "date_added": "dateTime",
        "language": "string", "language_label": "string", "popularity": "double",
        "popularity_conflict": "boolean", "vote_average": "double",
        "vote_count": "int64",
    },
    "generos": {"content_id": "string", "genre": "string"},
    "paises": {"content_id": "string", "country": "string"},
    "directores": {"content_id": "string", "director": "string"},
    "actores": {"content_id": "string", "actor": "string"},
    "finanzas": {
        "content_id": "string", "budget": "int64", "revenue": "int64",
        "return_multiple": "double",
    },
}

M_TYPES = {
    "string": "type text", "int64": "Int64.Type", "dateTime": "type date",
    "double": "type number", "boolean": "type logical",
}

MEASURES = {
    "Total contenidos": ("DISTINCTCOUNT(catalogo[content_id])", "#,0"),
    "Total películas": ("COALESCE(CALCULATE([Total contenidos], KEEPFILTERS(catalogo[type] = \"Movie\")), 0)", "#,0"),
    "Total series": ("COALESCE(CALCULATE([Total contenidos], KEEPFILTERS(catalogo[type] = \"TV Show\")), 0)", "#,0"),
    "Países representados": ("DISTINCTCOUNT(paises[country])", "#,0"),
    "Idiomas disponibles": ("DISTINCTCOUNT(catalogo[language])", "#,0"),
    "Géneros": ("DISTINCTCOUNT(generos[genre])", "#,0"),
    "Popularidad promedio": ("AVERAGE(catalogo[popularity])", "#,0.0"),
    "Popularidad mediana": ("MEDIAN(catalogo[popularity])", "#,0.0"),
    "Calificación promedio": (
        "CALCULATE(AVERAGE(catalogo[vote_average]), catalogo[vote_count] > 0)", "0.00"),
    "Votos totales": ("SUM(catalogo[vote_count])", "#,0"),
    "Popularidad por título": ("AVERAGE(catalogo[popularity])", "#,0.0"),
    "Calificación por título": (
        "IF([Votos totales] > 0, AVERAGE(catalogo[vote_average]))", "0.00"),
    "Películas financieras": ("DISTINCTCOUNT(finanzas[content_id])", "#,0"),
    "Resumen cobertura financiera": (
        'VAR elegibles = COALESCE([Películas financieras], 0) '
        'VAR peliculas = CALCULATE([Total películas], REMOVEFILTERS(finanzas)) '
        'RETURN IF(peliculas = 0, "Cobertura financiera: sin películas en la selección", '
        '"Cobertura financiera: " & FORMAT(elegibles, "#,0", "es-CL") & " de " & '
        'FORMAT(peliculas, "#,0", "es-CL") & " películas (" & '
        'FORMAT(DIVIDE(elegibles, peliculas), "0.0%", "es-CL") & '
        '") con presupuesto e ingresos positivos")', None),
    "Presupuesto promedio": ("AVERAGE(finanzas[budget])", "#,0"),
    "Presupuesto total": ("SUM(finanzas[budget])", "#,0"),
    "Ingresos totales": ("SUM(finanzas[revenue])", "#,0"),
    "Ingresos / presupuesto": (
        "DIVIDE([Ingresos totales], [Presupuesto total])", "0.00"),
    "Retorno mediano por título": ("MEDIAN(finanzas[return_multiple])", "0.00"),
}


def guid(name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"streamview-ep2/{name}"))


def table_tmdl(name: str, columns: dict[str, str]) -> str:
    path = (DATA / f"{name}.csv").resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    # M string literals escape double quotes by doubling them.
    m_path = str(path).replace('"', '""')
    lines = [f"table {name}", f"\tlineageTag: {guid(name)}", ""]
    for column, kind in columns.items():
        lines.extend([
            f"\tcolumn {column}",
            f"\t\tdataType: {kind}",
            f"\t\tlineageTag: {guid(name + '/' + column)}",
            "\t\tsummarizeBy: none",
            f"\t\tsourceColumn: {column}",
            "",
        ])
    if name == "catalogo":
        for measure, (dax, fmt) in MEASURES.items():
            lines.extend([
                f"\tmeasure '{measure}' = {dax}",
                *([f"\t\tformatString: {fmt}"] if fmt is not None else []),
                f"\t\tlineageTag: {guid('measure/' + measure)}",
                "",
            ])
    types = ", ".join(f'{{"{c}", {M_TYPES[k]}}}' for c, k in columns.items())
    lines.extend([
        f"\tpartition {name} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\tlet",
        f'\t\t\t\tSource = Csv.Document(File.Contents("{m_path}"), '
        f'[Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        "\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
        f"\t\t\t\tTyped = Table.TransformColumnTypes(Headers, {{{types}}}, \"en-US\")",
        "\t\t\tin",
        "\t\t\t\tTyped",
        "",
        "\tannotation PBI_NavigationStepName = Navigation",
        "\tannotation PBI_ResultType = Table",
        "",
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    if not (MODEL / "model.tmdl").is_file():
        raise FileNotFoundError("Save the blank PBIP in Power BI Desktop first")
    tables_dir = MODEL / "tables"
    tables_dir.mkdir(exist_ok=True)
    for name, columns in TABLES.items():
        (tables_dir / f"{name}.tmdl").write_text(
            table_tmdl(name, columns), encoding="utf-8"
        )
    relationships = []
    for table in ("generos", "paises", "directores", "actores", "finanzas"):
        relationships.extend([
            f"relationship {guid('relationship/' + table)}",
            f"\tfromColumn: {table}.content_id",
            "\ttoColumn: catalogo.content_id",
        ])
        relationships.append("\tcrossFilteringBehavior: bothDirections")
        relationships.append("")
    (MODEL / "relationships.tmdl").write_text("\n".join(relationships).rstrip() + "\n", encoding="utf-8")
    model_path = MODEL / "model.tmdl"
    text = model_path.read_text(encoding="utf-8-sig")
    text = text.split("ref table ")[0].rstrip() + "\n\n"
    text += "\n".join(f"ref table {name}" for name in TABLES) + "\n"
    model_path.write_text(text, encoding="utf-8")
    print(f"Modelo TMDL escrito: 6 tablas, 5 relaciones y {len(MEASURES)} medidas")


if __name__ == "__main__":
    main()

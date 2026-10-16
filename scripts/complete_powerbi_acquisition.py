"""Finish the acquisition page with a filterable low-budget, high-revenue shortlist.

Run after the other PBIR refinement scripts, with Power BI Desktop closed.
The thresholds use the full eligible financial sample so filters change the titles
shown without silently changing the definition of "low" and "high".
"""

from __future__ import annotations

import json

from build_powerbi_report import chart, col, ident, mea, projection, save
from refine_powerbi_report import (
    FIELD_NAMES, PAGES, add_measure, context_card, normalize_layer_order,
    polish_visual_labels, textbox,
)


def candidate_filter() -> dict:
    field = projection(*mea("Candidata: presupuesto bajo e ingresos altos"))["field"]
    return {
        "name": "FilterLowBudgetHighRevenue",
        "field": field,
        "type": "Advanced",
        "filter": {
            "Version": 2,
            "From": [{"Name": "c", "Entity": "catalogo", "Type": 0}],
            "Where": [{"Condition": {"Comparison": {
                "ComparisonKind": 2,
                "Left": {"Measure": {"Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Candidata: presupuesto bajo e ingresos altos"}},
                "Right": {"Literal": {"Value": "0D"}},
            }}}],
        },
        "howCreated": "User",
    }


def main() -> None:
    analytical = json.loads((PAGES / "pages.json").read_text(encoding="utf-8"))["pageOrder"][1]
    add_measure(
        "Umbral presupuesto reducido",
        "CALCULATE(PERCENTILEX.INC(finanzas, finanzas[budget], 0.25), "
        "REMOVEFILTERS(catalogo), REMOVEFILTERS(finanzas))",
        "#,0",
    )
    add_measure(
        "Umbral ingresos altos",
        "CALCULATE(PERCENTILEX.INC(finanzas, finanzas[revenue], 0.75), "
        "REMOVEFILTERS(catalogo), REMOVEFILTERS(finanzas))",
        "#,0",
    )
    add_measure(
        "Candidata: presupuesto bajo e ingresos altos",
        "VAR presupuesto = SELECTEDVALUE(finanzas[budget]) "
        "VAR ingresos = SELECTEDVALUE(finanzas[revenue]) "
        "RETURN IF(NOT ISBLANK(presupuesto) && NOT ISBLANK(ingresos) && "
        "presupuesto <= [Umbral presupuesto reducido] && "
        "ingresos >= [Umbral ingresos altos], 1)",
        "0",
    )
    add_measure(
        "Criterio candidatas",
        '"Presupuesto ≤ P25 (US$ " & FORMAT([Umbral presupuesto reducido] / 1000000, '
        '"0.0", "es-CL") & " M) · ingresos ≥ P75 (US$ " & '
        'FORMAT([Umbral ingresos altos] / 1000000, "0.0", "es-CL") & '
        '" M). Umbrales de las 3.540 películas elegibles; los filtros acotan la lista."',
        None,
    )
    add_measure(
        "Top 10 popularidad géneros",
        "IF([Total contenidos] >= 100 && "
        "RANKX(FILTER(ALLSELECTED(generos[genre]), "
        "CALCULATE([Total contenidos]) >= 100), "
        "CALCULATE([Popularidad mediana]),, DESC, DENSE) <= 10, "
        "[Popularidad mediana])",
        "0.0",
    )

    page_path = PAGES / analytical / "page.json"
    page = json.loads(page_path.read_text(encoding="utf-8"))
    page["height"] = 2680
    save(page_path, page)

    chart(
        analytical, "genre_popularity",
        "Popularidad mediana por género · hasta 10; ≥100 títulos",
        "clusteredBarChart", 310, 2160, 760, 400,
        {"Category": [col("generos", "genre")],
         "Y": [mea("Top 10 popularidad géneros")]},
        mea("Top 10 popularidad géneros"),
    )

    # Both amounts stay visible beside the multiple, so tiny budgets cannot
    # masquerade as strong evidence merely through an extreme ratio.
    chart(
        analytical, "low_budget_high_revenue",
        "Películas de bajo presupuesto y altos ingresos · muestra financiera",
        "tableEx", 1090, 2160, 790, 400,
        {"Values": [col("catalogo", "display_title"), col("finanzas", "budget"),
                    col("finanzas", "revenue"), col("finanzas", "return_multiple")]},
        col("finanzas", "revenue"),
    )
    path = PAGES / analytical / "visuals" / ident(analytical + "/low_budget_high_revenue") / "visual.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    existing_table = PAGES / analytical / "visuals" / ident(analytical + "/top_rated") / "visual.json"
    data["$schema"] = json.loads(existing_table.read_text(encoding="utf-8"))["$schema"]
    data["filterConfig"] = {"filters": [candidate_filter()]}
    save(path, data)

    context_card(analytical, "candidate_criterion", "Criterio candidatas",
                 310, 2564, 1570, 42)
    textbox(
        analytical, "age_unavailable",
        "Clasificación etaria no disponible: la columna rating replica la nota numérica.",
        25, 1050, 255, 110, 16, "#43566B",
    )
    FIELD_NAMES.update({
        "finanzas.budget": "Presupuesto · USD",
        "finanzas.revenue": "Ingresos · USD",
        "finanzas.return_multiple": "Ingresos / presupuesto",
    })
    polish_visual_labels(analytical)
    normalize_layer_order(analytical)
    print("Página analítica: popularidad por género y candidatas financieras agregadas")


if __name__ == "__main__":
    main()

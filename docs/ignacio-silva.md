# Implementación de Ignacio Silva - Integrante 3

## Alcance y regla de datos

Este bloque implementa el análisis financiero de Movies para EP1. Recibe exclusivamente `movies_financial_valid`, reconstruida por `build_catalog_views`; no lee ni modifica los CSV RAW desde el notebook o las reglas financieras.

La vista aplica la regla aprobada `budget > 0 AND revenue > 0`. Contiene 3.540 de 16.000 películas (22,125 %), con `show_id` único y ambos valores positivos. Los ceros permanecen en la fuente y no se interpretan como valores financieros reales.

La definición oficial del caso es **ROI aproximado = revenue / budget**. Se expresa como multiplicador (por ejemplo, `3,0x`) y no como ROI porcentual clásico ni utilidad neta.

## Implementación

- `src/financial_rules.py`: validación de contrato, ROI, KPIs, Spearman, rankings y segmentación reproducible.
- `src/visualizations.py`: cuatro gráficos financieros con títulos orientados al hallazgo, unidades y escalas explícitas.
- `notebooks/05_analisis_financiero.ipynb`: análisis ejecutable, evidencia, narrativa y tablas auditables.
- `tests/test_financial_rules.py`: pruebas de fórmula, reglas, ranking, segmento y no mutación de la vista preparada.

## Resultados reproducibles

| Métrica | Resultado |
|---|---:|
| Presupuesto total | USD 125.960.770.871 |
| Presupuesto promedio / mediano | USD 35.582.421 / USD 15.000.000 |
| Ingresos totales | USD 367.371.370.178 |
| Ingresos promedio / medianos | USD 103.777.223 / USD 23.800.000 |
| ROI aproximado promedio / mediano | 781,55x / 1,70x |
| Asociación budget-revenue (Spearman) | 0,710 |

El promedio de ROI queda dominado por bases de presupuesto extremadamente pequeñas; por esa razón se informa también la mediana y el ranking siempre muestra presupuesto e ingresos junto al multiplicador.

`Avengers: Endgame` lidera los ingresos absolutos con USD 2.799.439.100. El Top ROI es encabezado por `The Beatles: Eight Days a Week - The Touring Years` (2.456.760x), pero sobre un presupuesto registrado de USD 5; esto evidencia por qué retorno relativo e ingreso absoluto deben leerse por separado.

## Bajo presupuesto y alto retorno

La regla no usa una cifra arbitraria:

- presupuesto reducido: `budget <= P25` = USD 5.903.050,25;
- alto retorno: `ROI aproximado >= P75` = 3,76x.

La intersección contiene 295 películas. Es un segmento para priorizar evaluación de adquisiciones, no una relación causal ni una garantía de retorno futuro.

## Storytelling y decisiones

| Visual | Audiencia | Hallazgo y uso |
|---|---|---|
| Presupuesto vs ingresos | Directorio y Adquisición | La asociación positiva es alta, pero hay dispersión; una mayor inversión no determina por sí sola el resultado. |
| Top ingresos | Gerencia General y Finanzas | Prioriza contenidos por magnitud de ingreso absoluto. |
| Top ROI | Finanzas y Adquisición | Expone retornos relativos junto con la base para evitar rankings engañosos. |
| Bajo presupuesto y alto retorno | Adquisición y Dirección | Identifica 295 candidatos relativos para revisión editorial y financiera. |

Los scatter usan ejes logarítmicos porque `budget`, `revenue` y ROI son muy asimétricos. Los KPIs se calculan siempre con los valores originales. No se eliminan outliers solo por ser extremos y no se infiere causalidad desde la asociación.

## Reproducción

Desde la raíz del repositorio:

```powershell
uv sync --locked
uv run python -m unittest discover -s tests -v
uv run python -m jupyter nbconvert --to notebook --execute --inplace notebooks/05_analisis_financiero.ipynb --ExecutePreprocessor.kernel_name=python3 --ExecutePreprocessor.timeout=180
```

Las cuatro figuras generadas son `ignacio_budget_vs_revenue.png`, `ignacio_top_ingresos.png`, `ignacio_top_roi.png` e `ignacio_bajo_presupuesto_alto_retorno.png`.

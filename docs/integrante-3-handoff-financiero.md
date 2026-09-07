# Traspaso al Integrante 3 — análisis financiero

## Propósito

Este documento deja preparado el contexto técnico para que el Integrante 3 implemente
el bloque financiero sin volver a limpiar los archivos RAW ni alterar el trabajo de
los integrantes anteriores. **No atribuye al Integrante 3 código financiero que aún no
ha sido desarrollado.**

## Punto de partida obligatorio

La vista aprobada ya es construida por `build_catalog_views`, función implementada por
el Integrante 1 en `src/data_cleaning.py`:

```python
from pathlib import Path

from src.data_cleaning import build_catalog_views

views = build_catalog_views(
    Path("data/raw/netflix_movies_detailed_up_to_2025.csv"),
    Path("data/raw/netflix_tv_shows_detailed_up_to_2025.csv"),
)
movies_financial_valid = views["movies_financial_valid"]
```

Todo cálculo de presupuesto, ingresos o ROI debe comenzar desde
`movies_financial_valid`. No se debe volver a leer, unir o filtrar los RAW dentro del
bloque financiero.

## Contrato de la vista financiera

Regla reproducible ya implementada:

```text
budget > 0 AND revenue > 0
```

Estado verificado con los datasets actuales:

| Propiedad | Resultado |
|---|---:|
| Movies originales | 16.000 |
| Películas elegibles | 3.540 |
| Cobertura financiera | 22,125 % |
| Películas excluidas | 12.460 |
| Clave única disponible | `show_id` (3.540 valores únicos) |
| Tipo de `budget` y `revenue` | `int64` |

La vista conserva, entre otras, las columnas `show_id`, `title`, `release_year`,
`genres`, `language`, `popularity`, `vote_average`, `vote_count`, `budget`, `revenue`
y `financial_complete`. Actualmente no contiene `content_id`; para este subconjunto
exclusivo de Movies se debe usar `show_id` como clave, sin modificar la preparación
solo para renombrar el identificador.

Los ceros se excluyen del análisis financiero por la regla aprobada, pero no se afirma
que sean costos o ingresos reales iguales a cero ni se modifican sus valores en la
fuente general.

## Objetivos específicos del Integrante 3

| # | Objetivo | Evidencia mínima esperada |
|---:|---|---|
| 1 | Trabajar sobre la vista financiera aprobada | Notebook y funciones reciben `movies_financial_valid`; no contienen `pd.read_csv`. |
| 2 | Formalizar el filtrado financiero | Se documenta y comprueba `budget > 0 AND revenue > 0`, con 3.540 filas elegibles. |
| 3 | Construir KPIs financieros | Presupuesto promedio, ingresos totales, presupuesto total, ROI y rankings reproducibles. |
| 4 | Analizar presupuesto vs ingresos | Tabla, scatter, medida de asociación e interpretación. |
| 5 | Analizar ROI | Fórmula explícita, cálculo reproducible y lectura contextualizada. |
| 6 | Identificar películas de mayor ingreso | Top 10 por `revenue`, con título y magnitud. |
| 7 | Identificar películas de mayor ROI | Top 10 por ROI con presupuesto e ingresos visibles y advertencia sobre bases pequeñas. |
| 8 | Evaluar bajo presupuesto y alto retorno | Regla cuantitativa documentada, tabla/visual e interpretación. |
| 9 | Resolver escalas visuales | Diagnóstico de asimetría y escalas log justificadas para `budget`/`revenue`. |
| 10 | Entregar storytelling financiero | Cada gráfico cierra con audiencia, propósito, hallazgo, interpretación e implicación. |

## Definiciones recomendadas

### ROI

Salvo que el caso oficial indique otra convención, utilizar y documentar:

```text
ROI (%) = ((revenue - budget) / budget) × 100
```

También puede conservarse `revenue / budget` como múltiplo de retorno, pero debe tener
otro nombre y no sustituir silenciosamente al ROI porcentual.

Precauciones:

- no calcular ROI fuera de `movies_financial_valid`;
- no eliminar valores extremos solo por IQR;
- mostrar `budget` y `revenue` junto al Top 10 de ROI;
- un ROI muy alto sobre presupuesto pequeño no equivale al mayor ingreso absoluto;
- asociación entre presupuesto e ingresos no demuestra causalidad.

### Presupuesto reducido y alto retorno

Regla inicial recomendada, reproducible y adaptada a la distribución:

```text
presupuesto reducido: budget <= percentil 25 de movies_financial_valid
alto retorno: ROI >= percentil 75 de movies_financial_valid
```

La intersección de ambas condiciones define el segmento a estudiar. Los percentiles,
el número de películas resultante y la sensibilidad de la regla deben mostrarse; no se
debe presentar esta segmentación como una definición universal de la industria.

## KPIs mínimos sugeridos

| KPI | Fórmula o regla |
|---|---|
| Películas elegibles | `nunique(show_id)` |
| Cobertura financiera | `3.540 / 16.000 × 100` |
| Presupuesto promedio | `mean(budget)` |
| Presupuesto mediano | `median(budget)` como contexto ante asimetría |
| Presupuesto total | `sum(budget)` |
| Ingresos totales | `sum(revenue)` |
| Ingreso promedio/mediano | `mean(revenue)` y `median(revenue)` |
| ROI promedio/mediano | sobre ROI por película; informar ambas medidas |
| Correlación presupuesto–ingresos | Spearman como medida principal; Pearson puede quedar como contraste si se justifica |
| Top ingresos | ordenar `revenue` descendente y tomar 10 |
| Top ROI | ordenar ROI descendente y tomar 10, mostrando presupuesto e ingresos |

No calcular un “ROI global” como promedio sin aclarar su definición. El ROI de la
cartera, `((sum(revenue) - sum(budget)) / sum(budget)) × 100`, responde una pregunta
distinta del promedio o mediana de ROI por película.

## Visualizaciones y audiencia

| Visual | Selección recomendada | Audiencia principal | Mensaje que debe responder |
|---|---|---|---|
| Presupuesto vs ingresos | Scatter con ambos ejes log si la asimetría lo justifica | Finanzas / Adquisición | ¿Mayor presupuesto se asocia con mayores ingresos? |
| Top 10 ingresos | Barras horizontales ordenadas | Gerencia General / Finanzas | ¿Qué películas generan mayor ingreso absoluto? |
| Top 10 ROI | Barras horizontales con presupuesto e ingreso accesibles | Finanzas / Adquisición | ¿Qué retornos relativos destacan y con qué base? |
| Bajo presupuesto y alto retorno | Scatter o cuadrantes con umbrales explícitos | Adquisición / Contenidos | ¿Qué películas cumplen simultáneamente ambas reglas? |

Mantener títulos orientados al hallazgo, unidades monetarias claras, separadores de
miles, nota de escala logarítmica y una paleta consistente. Cada figura debe poder
entenderse sin inspeccionar el código.

## Estructura sugerida de implementación

- Desarrollar reglas reutilizables en un módulo financiero independiente o en el
  módulo acordado por el equipo, evitando mezclar la autoría con el bloque de Lucas.
- Crear un notebook propio del Integrante 3 o completar el archivo que el equipo le
  haya asignado; no sobrescribir el notebook 03 de Lucas.
- Añadir pruebas sintéticas para fórmula de ROI, filtro, rankings, percentiles,
  asociación y no mutación de la vista.
- Guardar figuras con un prefijo identificable del Integrante 3.
- Crear documentación de autoría propia y actualizar el README al completar el bloque.

## Comprobaciones antes de entregar

1. No aparece `pd.read_csv` en el notebook financiero.
2. Todos los cálculos parten de `movies_financial_valid`.
3. Se verifican 3.540 `show_id` únicos y `budget/revenue > 0` en todas las filas.
4. La fórmula y unidad de ROI están visibles.
5. Los Top 10 son deterministas y muestran las variables de contexto.
6. Las escalas logarítmicas están etiquetadas y no reemplazan el dato original.
7. Cada gráfico declara audiencia, propósito y narrativa.
8. El notebook se ejecuta de principio a fin y las pruebas pasan.

## Límites de autoría

- La exploración, calidad, preparación y creación de `movies_financial_valid`
  corresponden al Integrante 1.
- El análisis de popularidad, valoración y evolución documentado en
  `docs/lucas-moncada.md` corresponde a Lucas Moncada, Integrante 2.
- El futuro código, notebook, pruebas, figuras y hallazgos financieros corresponderán
  al Integrante 3 cuando los implemente.

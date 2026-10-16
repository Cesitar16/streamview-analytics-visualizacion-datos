# Guion de defensa técnica · StreamView Analytics EP2

Duración objetivo: **10 minutos de exposición y hasta 5 minutos de preguntas**. El reparto organiza los turnos de César, Lucas e Ignacio. Los tres deben poder explicar la preparación de datos, ambas herramientas y las limitaciones del análisis. Este guion acompaña `output/pdf/StreamView_EP2_Presentacion.pdf` y sirve para ensayar la demostración.

| Expositor | Tramo | Láminas y demostración | Tiempo |
|---|---|---|---:|
| **César** | Apertura, datos y dashboard ejecutivo | 1–4 | 3 min 25 s |
| **Lucas** | Modelo Power BI, análisis y primera parte de la demo | 5–6; lámina 7, Streamlit | 3 min 05 s |
| **Ignacio** | Finanzas, límites y cierre | Lámina 7, página 02 de Power BI; 8–10 | 3 min 30 s |

## Recorrido oral de 10 minutos

| Tiempo | Habla | Lámina | Qué decir y mostrar |
|---|---|---|---|
| 0:00–0:30 | César | 1. Portada | «Partimos del catálogo trabajado en EP1 y construimos dos dashboards para preguntas distintas. Uno resume la oferta para dirección y el otro permite explorar señales para contenidos y adquisición». |
| 0:30–1:15 | César | 2. Problema y audiencias | «La dirección necesita ver composición y concentración; adquisición necesita comparar títulos con su valoración y costos. Son datos de catálogo: no tenemos reproducciones ni comportamiento de usuarios». Señalar la comparación de películas y series. |
| 1:15–2:35 | César | 3. Preparación de datos | «Leemos dos CSV originales de 16.000 filas cada uno. La función `build_catalog_views` convierte fechas, limpia espacios de borde y conserva los originales. Nueve identificadores de series están repetidos con distinta popularidad: mantenemos una entidad por serie, pero anulamos esa popularidad solo para las métricas que la usan. `show_id` colisiona 397 veces entre las dos fuentes, por eso la clave analítica añade el tipo: `content_id = type + '_' + show_id`. Separar géneros, países y créditos en tablas relacionadas evita perder valores múltiples. El resultado son 31.991 títulos únicos; las finanzas cubren 3.540 películas con presupuesto e ingresos positivos». Mostrar `src/data_cleaning.py` solo si piden evidencia de código. |
| 2:35–3:25 | César | 4. Dashboard 1 | «Streamlit carga esas vistas en memoria. Al elegir tipo, años o género, primero cambia el conjunto de `content_id`; luego se recalculan las tarjetas y gráficos. Plotly dibuja barras y mapa coroplético; D3 dibuja el treemap. Usamos barras para comparar cantidades exactas y el treemap para ver proporciones generales. Un título puede pertenecer a más de un género o país, por lo que esas barras no se suman para obtener 31.991». Ceder la palabra a Lucas: «Ahora veremos cómo se reutilizan las vistas en Power BI». |
| 3:25–4:20 | Lucas | 5. Dashboard 2 | «El script de exportación genera seis CSV derivados de las mismas vistas. En Power BI, `catalogo` tiene una fila por `content_id` y se relaciona con géneros, países, directores, actores y finanzas. Las medidas DAX usan `DISTINCTCOUNT` para que un título con varios géneros no se duplique. Los segmentadores y las selecciones de gráficos propagan el contexto a tarjetas, rankings y mapa». Mostrar el modelo de relaciones en Desktop solo si la profesora pide detalle. |
| 4:20–5:15 | Lucas | 6. Contenidos y adquisición | «Aquí cruzamos popularidad, nota y votos. Popularidad es un índice de la fuente, no visualizaciones. La dispersión revela variación que un promedio ocultaría. El Top 10 exige votos mínimos; el mapa de calificación exige cobertura mínima por país. Los umbrales se ajustan en Streamlit y son fijos y visibles en Power BI». |
| 5:15–6:30 | Lucas | 7. Demostración, parte 1 | Mostrar el panorama de Streamlit según el recorrido de abajo. Narrar qué recalculan los filtros y señalar la navegación hacia adquisición. Ceder el control a Ignacio: «Veamos qué ocurre con el subconjunto financiero en Power BI». |
| 6:30–7:15 | Ignacio | 7. Demostración, parte 2 | En la página 02 de Power BI, mostrar la nota de cobertura, seleccionar **TV Show** y señalar que las finanzas quedan vacías. Restablecer filtros. |
| 7:15–8:05 | Ignacio | 8. Finanzas | «Solo 3.540 de 16.000 películas tienen presupuesto e ingresos positivos. La razón agregada ingresos/presupuesto es 2,9166 veces: es un múltiplo bruto, no utilidad neta ni retorno después de costos. La dispersión permite observar valores extremos; los candidatos requieren revisar derechos y costos ausentes». |
| 8:05–9:05 | Ignacio | 9. Calidad y límites | «No construimos un filtro de edad porque `rating` replica la nota numérica. El año de incorporación coincide con el de estreno y no permite narrar altas reales. La cobertura financiera es 22,1 % de las películas. Las pruebas automáticas y la revisión interactiva comprobaron filtros, cálculos, mapas y restablecimiento». |
| 9:05–10:00 | Ignacio | 10. Conclusiones | «Para dirección, la evidencia permite detectar concentración. Para adquisición, combinaríamos popularidad, valoración y votos para formar una lista corta. Antes de invertir, faltaría confirmar derechos, costos completos y datos reales de audiencia». Cerrar sin atribuir demanda o rentabilidad a estos CSV. |

## Demostración en vivo: secuencia de dos minutos

1. **Lucas · Streamlit, panorama (1 min 15 s):** abrir `http://127.0.0.1:8501` sin filtros. Señalar 31.991 títulos, 16.000 películas y 15.991 series. Elegir **Película** y después **Drama**. Indicar que cambian las tarjetas, las barras, el treemap D3 y el mapa de países. Pulsar **Restablecer filtros** y señalar la navegación a la otra perspectiva.
2. **Ignacio · Power BI, página 02 (45 s):** mostrar la nota de cobertura financiera y el mapa. Seleccionar **TV Show**: los indicadores financieros quedan vacíos porque solo hay finanzas de películas elegibles. Pulsar **Borrar segmentadores**. Una selección hecha directamente sobre una barra, punto o burbuja se desmarca en ese mismo gráfico.

Si hay margen, Lucas puede abrir la página 01 de Power BI y mostrar cómo un género cambia sus tarjetas; Ignacio puede enseñar el control de votos de la perspectiva analítica de Streamlit. Estas ampliaciones no forman parte de los dos minutos obligatorios.

Si falta tiempo, demostrar un filtro en cada herramienta y explicar verbalmente el resto. Dejar ambas herramientas abiertas y sin filtros antes de comenzar. Power BI puede tardar al cambiar de página o filtrar; esperar a que terminen de actualizarse las tarjetas antes de narrar el resultado.

## Preguntas probables y respuestas breves

**¿Por qué 31.991 y no 32.000?** Los dos archivos traen 32.000 filas. Nueve identificadores de series aparecen dos veces; se conserva una entidad por identificador y tipo. Las nueve entidades siguen en el catálogo.

**¿Por qué `content_id` y no `show_id`?** Hay 397 valores de `show_id` presentes tanto en películas como en series. Anteponer el tipo evita unir contenidos distintos.

**¿Dónde están los datos procesados?** EP1 definió una función reproducible que reconstruye vistas en memoria desde `data/raw/`; no dejó un CSV persistente en `data/processed/`. EP2 reutiliza esa función. Solo para Power BI se exportan seis CSV derivados a `powerbi/data/`.

**¿Cómo evita el modelo inflar los conteos?** `catalogo` tiene una fila por `content_id`. Las tablas de género, país y talento representan relaciones múltiples; la medida de títulos usa `DISTINCTCOUNT(catalogo[content_id])`.

**¿Por qué excluir nueve valores de popularidad?** Esos IDs tienen dos valores incompatibles. Se conserva cada título para conteos y demás métricas, pero no se inventa una popularidad escogiendo una fila arbitraria.

**¿Por qué no hay filtro etario?** La columna `rating` coincide con la nota numérica `vote_average`; no identifica edades. La ausencia queda informada en ambas herramientas.

**¿Es ROI o rentabilidad?** El cociente mostrado es ingresos divididos por presupuesto, sobre películas con ambas cifras positivas. No incluye derechos, distribución, marketing, impuestos ni otros costos; se comunica como múltiplo bruto aproximado.

**¿Qué diferencias hay entre los dashboards?** Streamlit integra Python, Plotly y D3, permite ajustar umbrales y descargar la selección. Power BI usa un modelo de seis tablas, medidas DAX, segmentadores y cruces nativos entre visuales. Ambos parten de las mismas vistas preparadas.

**¿Qué se verificó?** Se conciliaron los totales con los CSV, pasaron 17 pruebas automáticas y se recorrieron ambas herramientas con filtros y restablecimiento. La evidencia de escenarios está en `docs/verificacion_demostracion_ep2.md`.

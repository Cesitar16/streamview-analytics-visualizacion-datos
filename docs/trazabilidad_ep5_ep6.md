# Matriz de evidencia y trazabilidad — EP5

Esta matriz acompaña el informe ejecutivo y la presentación de StreamView Analytics. Relaciona hallazgos con decisiones y permite ubicar la evidencia solicitada en la pauta **EP5: Encargo** de ADY1104 (2026). Las cifras se calcularon a partir de los dos CSV oficiales, conservados sin modificaciones en `data/raw/`; estos archivos no se publican en Git.

## Recomendación → evidencia → decisión

| Recomendación y audiencia | Hallazgo, KPI o visual | Decisión que habilita | Impacto esperado en el proceso | Límite y control |
|---|---|---|---|---|
| Revisar concentración de la oferta; dirección | 31.991 títulos únicos; Drama 14.769, Comedia 9.105 y EE. UU. 10.955. Tarjetas, barras y treemap de Panorama. | Seleccionar segmentos para una revisión editorial de variedad, aplicando tipo y año. | Priorizar preguntas concretas sobre composición antes de definir objetivos. | Géneros y países se solapan; usar `content_id` único y no sumar categorías. No hay demanda observada. |
| Construir lista corta de títulos; contenidos y adquisición | Dispersión popularidad–nota con tamaño por votos; Top 10 con mínimo de 100 votos en Power BI y umbral ajustable en Streamlit. | Pedir evaluación editorial de candidatos con tres señales y cobertura de votos. | Evitar que una nota alta con pocos votos domine la exploración. | Popularidad no son reproducciones; votos y nota no prueban preferencia de usuarios ni causalidad. |
| Revisar cobertura geográfica antes de comparar; ambas audiencias | Mapa de nota con mínimo predeterminado de 100 títulos valorados por país; Japón: 2.647 títulos y media aproximada 7,17/10. Ranking tabular contiguo. | Escoger países para un análisis posterior solo tras revisar tamaño de muestra y valores exactos. | Reducir comparaciones basadas en muestras pequeñas o áreas del mapa. | País indica asociación de producción, no consumo local; el geocodificador puede reconocer nombres de forma ambigua. |
| Evaluar títulos con información financiera; adquisición | 3.540/16.000 películas elegibles (22,125 %); dispersión presupuesto–ingresos y detalle individual; múltiplo agregado bruto 2,9166×. | Solicitar derechos, divisa confirmada y costos completos antes de discutir una compra. | Ordenar la revisión de casos con datos financieros observables. | No extrapolar al resto del catálogo; ingresos/presupuesto no son utilidad neta ni predicción. |

## Evaluación crítica: riesgo → efecto → tratamiento

| Riesgo o decisión visual | Efecto posible | Tratamiento y evidencia |
|---|---|---|
| `rating` reproduce la nota numérica, no una edad. | Falso segmento etario. | Omitir filtro etario; documentado en informe §8 y lámina 9. Incorporar clasificación solo con fuente verificada. |
| `date_added.year = release_year` y distribución anual artificialmente regular. | Interpretar años registrados como altas o tendencia del mercado. | Rotular la línea como distribución por año registrado; no inferir incorporaciones. Informe §§5 y 8, lámina 9. |
| Géneros y países multivalor. | Sumar categorías infla el total. | Tablas puente y conteos únicos; aviso en treemap y barras. `src/data_cleaning.py`, informe §§3 y 8. |
| Popularidad relativa y nota con cobertura de votos desigual. | Confundir índice con reproducciones o confiar en notas débiles. | Leyendas y umbrales de votos; dispersión con tamaño por votos. Informe §§6 y 8, láminas 6 y 9. |
| Reconocimiento geográfico y cobertura desigual. | Ubicación errónea o comparación de medias inestables. | Ranking tabular, mínimo de títulos y nota metodológica. Informe §§4, 6 y 8. |
| Finanzas parciales y costos/divisa incompletos. | Extrapolación y falsa rentabilidad neta. | Mostrar 3.540/16.000 y denominador; tratar 2,9166× como múltiplo bruto. Informe §§7–9, láminas 8–10. |

Las fortalezas se apoyan en hechos comprobables: la clave compuesta resuelve 397 colisiones entre fuentes; nueve identificadores de series se consolidan sin eliminar sus entidades; filtros y estados vacíos tienen pruebas automatizadas; el treemap conserva lista, porcentajes con base explícita y acceso por teclado. Véanse `tests/`, `docs/verificacion_demostracion_ep2.md` y `docs/evaluacion_usabilidad_dashboard_ux.md`. Las pruebas con datos sintéticos demuestran el comportamiento de la aplicación; las cifras del catálogo se verifican con los CSV oficiales.

## Trazabilidad de la pauta EP5

Los indicadores se resumen a partir de la pauta EP5. Las secciones corresponden al informe ejecutivo y las láminas al PDF de presentación de esta entrega.

| Indicador | Tema comprobable | Informe | Lámina o demostración |
|---|---|---|---|
| IE25 | Técnicas y representaciones acordes al dato, uso y objetivo | §§4–8 | 4, 6, 8–9; barras, treemap, dispersión y mapa |
| IE27 | Coherencia entre visual, análisis y decisión | §§4–9; matriz de recomendaciones | 4, 6, 8–10; filtros en vivo |
| IE28 | Diseño visual, jerarquía y organización | §§4–8 | 4–9; contraste treemap/barras y dispersión |
| IE29 | Legibilidad, acceso y comunicación visual | §§5, 6, 8; `docs/evaluacion_usabilidad_dashboard_ux.md` | 4, 6, 9; lista y teclado del treemap |
| IE30 | Comunicación clara de hallazgos mediante visualizaciones | §§4–9 | 4, 6, 8–10; demostración de filtros |
| IE34 | Solución visual alineada al problema de negocio | §§1–2, 5–6, 9 | 1–2, 4–6, 10 |

## Preparación para el examen posterior

El equipo puede reutilizar esta evidencia en la defensa EP6. Esta correspondencia sirve para planificar la exposición y deberá cotejarse con la pauta del examen cuando se entregue. **IE34 corresponde a EP5 y no se incluye entre los indicadores EP6.**

| Indicador de planificación | Evidencia disponible | Ubicación sugerida |
|---|---|---|
| IE26 | Problema, fuentes e integración | Informe §§1–3; láminas 1–5 |
| IE31 | Fortalezas y limitaciones de la solución | Informe §8; lámina 9 |
| IE32 | Justificación y evaluación de decisiones de diseño | Informe §§4–8; lámina 9 y demostración |
| IE33 | Oportunidades de mejora priorizadas y fundamentadas | Informe §8; `docs/plan_mejoras_ep6.md`; lámina 9 por actualizar |
| IE35 | Recomendaciones sustentadas en hallazgos | Informe §9; lámina 10 y matriz anterior |
| IE36 | Impacto esperado de las recomendaciones en las decisiones | Informe §9; lámina 10 y matriz anterior |

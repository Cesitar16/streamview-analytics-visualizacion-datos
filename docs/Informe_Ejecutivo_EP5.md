# StreamView Analytics — Informe ejecutivo EP5

**ADY1104 · Visualización de datos · Tercera evaluación · Noviembre de 2026**

**Audiencias:** dirección ejecutiva y equipo de contenidos/adquisición.
**Fuente:** dos CSV oficiales de películas y series, corte 2025, en `data/raw/`.

## 1. Problema, objetivo y continuidad del proyecto

En EP1 se definieron la limpieza, las claves y las vistas analíticas del catálogo. En EP2 se construyeron dos tableros interactivos. Este informe EP5 reúne la solución, revisa sus decisiones visuales y explica qué hallazgos pueden apoyar a cada audiencia. El tablero ejecutivo resume composición, cobertura geográfica e idiomas. El de contenidos combina valoración, popularidad, talento y finanzas para explorar oportunidades de adquisición. Ambos trabajan sobre 31.991 contenidos únicos y conservan los CSV originales sin modificación.

**Problema de negocio:** las áreas necesitan una lectura común del catálogo para orientar una revisión de la oferta y de posibles adquisiciones. Los recuentos por categorías solapadas, la calidad de fechas y la cobertura financiera parcial pueden producir conclusiones equivocadas. **Objetivo de comunicación:** mostrar a dirección el tamaño y la concentración de la oferta y presentar al equipo de contenidos señales de popularidad, valoración y costos con sus límites visibles. Los archivos no incluyen usuarios, reproducciones ni retención; por ello no permiten describir el comportamiento de la audiencia.

## 2. Arquitectura y herramientas

`data/raw/` → función de preparación aprobada en EP1 (`src/data_cleaning.py`) → vistas analíticas en memoria → aplicación Python (`dashboard/app.py`) y seis exportaciones CSV locales (`powerbi/data/`) para el informe Power BI (`powerbi/StreamView_EP2.pbip`). EP1 no generó un CSV persistente en `data/processed/`; EP2 reconstruye las mismas vistas desde los originales sin alterarlos. El treemap de géneros se dibuja con D3 dentro de la aplicación. Plotly aporta líneas, barras, dispersión y mapas; Streamlit aporta navegación, filtros, comparador de géneros y descarga; Power BI aporta modelo tabular, medidas DAX y una versión de los paneles para escritorio.

Se eligió Python por la limpieza trazable y el análisis de datos; D3 por el treemap con interacción específica; Power BI por el modelo de datos y la experiencia de exploración de negocio. Esta combinación cumple el requisito de integración sin atribuir a una herramienta cálculos que realiza otra.

Las **dos fuentes** son `netflix_movies_detailed_up_to_2025.csv` (16.000 filas) y `netflix_tv_shows_detailed_up_to_2025.csv` (16.000 filas). Comparten identificador, tipo, título, fecha, año, género, país, idioma, popularidad, votos y nota. Solo películas aporta presupuesto e ingresos. La integración se realiza por una clave compuesta de tipo e identificador, y las categorías multivalor pasan a tablas relacionadas. Las seis exportaciones de Power BI son derivados de estas mismas vistas; no constituyen fuentes independientes.

## 3. Reglas del modelo

La clave es `content_id = type + '_' + show_id`: `show_id` por sí solo colisiona entre películas y series. `catalogo` tiene una fila por contenido. Géneros, países, directores y actores usan tablas de puente, porque un contenido puede tener varios valores. Los conteos de estas dimensiones no se suman para obtener el total de títulos. `finanzas` contiene únicamente 3.540 películas con `budget > 0` y `revenue > 0`. Los indicadores de valoración usan títulos con `vote_count > 0`. Nueve identificadores de series con popularidad en conflicto se excluyen de esa métrica.

Los filtros se aplican al conjunto de contenidos antes de calcular indicadores. Se ofrecen tipo, periodo y género en ambas vistas; la vista de adquisición agrega país, idioma, calificación y umbrales de votos/cobertura.

## 4. Exploración y representación visual

La primera lectura compara la cantidad de películas y series. Las barras muestran el equilibrio entre ambas; la diferencia exacta de nueve títulos se indica aparte porque es casi imperceptible visualmente. Las barras ordenadas muestran concentración por género y país; sus etiquetas advierten que un contenido puede pertenecer a varias categorías. El mapa ofrece contexto espacial, mientras que las barras quedan como referencia cuantitativa exacta cuando el reconocimiento geográfico es ambiguo.

![Distribución del catálogo por tipo; las películas y series tienen volúmenes cercanos.](outputs/figures/peliculas_vs_series.png)

![Los géneros predominantes; las categorías se solapan.](outputs/figures/generos_predominantes.png)

La dispersión resulta apropiada para estudiar relaciones entre dos variables continuas sin esconder la variabilidad detrás de un promedio. La escala logarítmica de popularidad reduce el efecto visual de valores extremos; el tipo separa formatos distintos. Para elegir títulos se añade el número de votos, porque una nota alta con pocos votos es evidencia débil.

![La relación entre popularidad y nota es débil dentro de cada formato.](outputs/figures/lucas_popularidad_vs_valoracion.png)

## 5. Tablero ejecutivo

Al abrir sin filtros muestra **31.991 contenidos**: 16.000 películas y 15.991 series. Hay **147 países**, **83 idiomas** y **28 géneros** representados. Drama aparece en 14.769 títulos y Comedia en 9.105. Estados Unidos está asociado a 10.955 títulos, Japón a 2.869 y Reino Unido a 2.608. Inglés (`en`) aparece en 13.969 títulos. Estos números describen amplitud del catálogo, no audiencia ni reproducciones.

Las tarjetas KPI permiten ver el efecto de cada filtro. La serie de líneas por tipo muestra la distribución anual registrada en la fuente; `date_added.year = release_year` para todos los registros, por lo que **no es válido inferir una política real de incorporación**. El gráfico de tipo, las barras de países e idiomas, el treemap D3 de géneros y el mapa muestran composiciones complementarias. El mapa se interpreta como países asociados a producciones, no como consumo local.

La navegación comienza con esta vista general y pasa a la página analítica solo cuando se necesita evaluar candidatos. El treemap muestra participación relativa de géneros y permite explorar sus etiquetas; se complementa con barras porque las áreas son menos precisas para comparar valores cercanos. El comparador estratégico enfrenta dos géneros dentro de los filtros vigentes y comunica títulos únicos, formatos, popularidad mediana, calificación media y cobertura de votos. Como los géneros se solapan, sus segmentos no se suman para reconstruir el catálogo. Las tarjetas y gráficos responden a los filtros de tipo, intervalo de años y género.

## 6. Tablero de contenidos y adquisición

La dispersión cruza popularidad relativa y calificación, con tamaño de punto ligado a votos y transparencia para reducir la superposición; así evita equiparar una nota alta con pocos votos a una evidencia sólida. En Streamlit, la popularidad mediana y la calificación media por género se muestran por separado; un gráfico de puntos con eje acotado permite comparar notas cercanas sin ocultar sus valores. El Top 10 de títulos exige un umbral de votos configurable. Los rankings de directores y actores representan solamente créditos informados; la cobertura de directores es parcial, especialmente en series.

Para comparación geográfica de calificación, el mapa exige al menos 100 títulos valorados por país de forma predeterminada. Un ranking de puntos junto al mapa permite distinguir medias cercanas y consultar la cantidad de títulos valorados. Bajo ese umbral, Japón registra 2.647 títulos valorados y una media aproximada de 7,17/10; la cifra es descriptiva y no controla diferencias en composición del catálogo. Los filtros permiten volver a calcular estas vistas para un segmento concreto.

El recorrido de interacción es: acotar tipo, año, género, país, idioma y nota; inspeccionar la dispersión; subir el umbral de votos del Top 10; y comprobar la cobertura mínima antes de comparar países. La vista ofrece descarga CSV de la selección para auditoría. Power BI también incluye Top 10 con mínimo fijo de 100 votos, rankings de talento y un mapa de burbujas con mínimo fijo de 30 títulos. Streamlit permite ajustar ambos umbrales y muestra mapas coropléticos. Las dos herramientas usan las vistas preparadas de EP1, aunque sus controles y representaciones no son idénticos.

## 7. Módulo financiero

El subconjunto elegible es **3.540 de 16.000 películas (22,125 %)**. El presupuesto acumulado es **125.960.767.278** y los ingresos acumulados **367.371.433.138**. La razón agregada ingresos/presupuesto es **2,9166×**; el **ROI bruto aproximado agregado** es **191,66 %**, calculado como `(ingresos - presupuesto) / presupuesto`. El múltiplo y el porcentaje son indicadores distintos. El ROI no representa utilidad neta: no incluye costos adicionales. La convención USD proviene del informe anterior; los CSV no incluyen una columna que confirme divisa. La dispersión presupuesto–ingresos, el Top 10 de ingresos y las tarjetas contextualizan la variación por título.

La documentación de la evaluación 1 contiene totales ligeramente diferentes. Para esta entrega se prioriza el cálculo repetible desde los dos CSV presentes, con detalle en `docs/conciliacion_financiera_ep2.md`. No se mezclan ambas series de cifras.

![Presupuesto e ingresos presentan asociación positiva y amplia dispersión entre películas elegibles.](outputs/figures/ignacio_budget_vs_revenue.png)

La escala logarítmica en ambos ejes permite ver películas pequeñas y grandes en la misma dispersión; en Streamlit, la diagonal ingresos = presupuesto y dos colores muestran qué títulos superan esa referencia bruta. El múltiplo exacto permanece en el detalle del punto, sin dejar que valores extremos dominen una escala continua. La asociación positiva observada no implica que aumentar presupuesto cause ingresos mayores. El Top 10 de ingresos es útil para localizar extremos, pero una recomendación de adquisición exige revisar derechos y costos ausentes de estos CSV. La aplicación permite exportar el subconjunto financiero filtrado.

## 8. Evaluación crítica y límites

**Fortalezas:** ambos tableros comparten reglas y claves, los KPI se reconcilian con los CSV oficiales, los filtros actualizan el conjunto de entidades antes de agregarlo y el análisis financiero muestra su población elegible. La versión Power BI permite explorar medidas y relaciones en escritorio; la versión Python añade controles de umbral, descarga, serie temporal por formato y comparación de géneros.

La evidencia de estas fortalezas es concreta: la clave compuesta evita 397 colisiones de `show_id` entre fuentes; el catálogo conserva 31.991 títulos únicos tras resolver nueve identificadores repetidos de series; y las tablas de géneros y países permiten contar títulos sin duplicarlos. Las pruebas de `tests/` comprueban reglas y filtros con muestras controladas. La verificación de la interacción está documentada en la guía de demostración y en la evaluación de usabilidad. Estas pruebas respaldan el funcionamiento de la solución, no el resultado comercial de una decisión.

**Riesgos y decisiones adoptadas:**

- `rating` replica `vote_average`; usarlo como edad produciría segmentos incorrectos. Se omite el filtro etario hasta disponer de una fuente verificada.
- `date_added.year` coincide con `release_year`, y cada año de 2010 a 2024 tiene exactamente 2.000 títulos. Llamarlo «fecha de incorporación» sugeriría altas que el archivo no registra. La serie se presenta como distribución por año registrado.
- Un título puede tener varios géneros y países; sumar esas categorías inflaría el catálogo. Se cuentan títulos únicos y se advierte el solapamiento.
- `popularity` es un índice, no reproducciones. La nota también depende de cuántos votos recibió cada título. Ambas son señales para explorar y se muestran con umbrales de cobertura.
- El mapa depende del reconocimiento de nombres geográficos. El ranking tabular y el mínimo de títulos por país sirven como control para comparar valores.
- Las finanzas cubren 3.540 de 16.000 películas (22,125 %). No se extrapolan al resto ni se interpretan como utilidad neta: faltan derechos, otros costos y confirmación de divisa.

**Evaluación del diseño:** las barras y tablas permiten comparar cantidades exactas; el treemap muestra la composición y ofrece una lista para las áreas pequeñas. La dispersión conserva la variación entre títulos y usa los votos para contextualizar cada nota. La escala logarítmica financiera hace visibles montos de distinto tamaño, pero requiere explicar sus ejes y la diagonal de igualdad. El mapa orienta la exploración; el ranking entrega el valor preciso. Los filtros y el restablecimiento permiten repetir el recorrido. La matriz complementaria de evidencia y trazabilidad indica dónde se presenta cada criterio EP5.

**Oportunidades de mejora:** priorizar la reproducción en otro equipo y los controles de cobertura y reconocimiento geográfico; posteriormente, si se autorizan fuentes fiables, incorporar clasificación etaria, fechas reales de incorporación y completar créditos y finanzas. El anexo `output/pdf/StreamView_EP6_Anexo_Mejoras.pdf`, con fuente en `docs/plan_mejoras_ep6.md`, explica el orden, las dependencias y los beneficios esperados. La información ausente no se simula con los CSV actuales.

## 9. Conclusiones y recomendaciones para las dos audiencias

El análisis permite ordenar una revisión del catálogo para dos audiencias. Estas recomendaciones indican la evidencia observada, la acción que habilita y el límite de esa lectura:

- **Dirección, concentración:** Drama figura en 14.769 títulos y Comedia en 9.105; Estados Unidos se asocia a 10.955. Comparar estos segmentos con filtros y conteos únicos antes de revisar la variedad del catálogo. Esto ayuda a elegir qué segmentos estudiar primero, pero no demuestra un aumento de audiencia; géneros y países se solapan.
- **Adquisición, lista corta:** la dispersión de popularidad frente a nota muestra variación y cada punto indica votos; el Top 10 aplica un mínimo de 100 votos en Power BI y un umbral ajustable en Streamlit. Pedir una lista de títulos con nota, popularidad y respaldo de votos antes de una evaluación editorial. Mejora la selección para revisión, pero ninguna de esas variables mide consumo, preferencia de usuarios o causalidad.
- **Comparación por país:** el mapa de calificación de Streamlit requiere por defecto 100 títulos valorados por país; Japón reúne 2.647 y una media aproximada de 7,17/10 bajo ese criterio. Revisar el ranking tabular y la cobertura antes de elegir mercados para estudio. Se evita comparar medias de muestras pequeñas; las asociaciones de país y el reconocimiento del mapa no prueban demanda local.
- **Finanzas, revisión individual:** 3.540 de 16.000 películas (22,125 %) tienen cifras válidas. Revisar cada candidata y pedir derechos, divisa y costos faltantes antes de invertir. El múltiplo bruto de 2,9166× y el ROI aproximado no se extrapolan al resto del catálogo.

## 10. Reproducción y verificación

Para repetir la solución en otro equipo:

- Obtener los dos CSV oficiales por el canal autorizado y copiarlos, sin modificarlos, en `data/raw/`.
- Desde la raíz del repositorio, ejecutar `uv sync --locked` y luego `uv run --locked python -m unittest discover -s tests -v`. Con las fuentes de esta entrega pasaron 25 pruebas.
- Ejecutar `uv run --locked python scripts/export_powerbi.py`. Abrir `powerbi/StreamView_EP2.pbip` en Power BI Desktop y actualizar las rutas de las seis tablas derivadas según la guía de reproducción.
- Ejecutar `uv run --locked streamlit run dashboard/app.py` para explorar las dos perspectivas del tablero interactivo.

Los controles de referencia son 31.991 contenidos, 16.000 películas, 15.991 series y 3.540 películas con datos financieros elegibles. Los CSV originales y las exportaciones para Power BI no se publican en Git; el código, la documentación y el proyecto PBIP sí están versionados.

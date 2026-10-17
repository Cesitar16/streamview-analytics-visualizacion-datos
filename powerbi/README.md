# Power BI · Evaluación 2

Abrir `StreamView_EP2.pbip` **después de cerrar cualquier ventana anterior del mismo proyecto**. El proyecto contiene dos páginas PBIR, seis tablas de importación, cinco relaciones y medidas DAX. La primera apertura puede pedir confirmar el origen local de los CSV y actualizar los datos. Las rutas de las consultas apuntan a esta ubicación del repositorio en el equipo; si se mueve la carpeta, ejecutar `uv run --locked python scripts/rebase_powerbi_sources.py` desde la raíz del repositorio con Power BI cerrado. Ese script cambia únicamente las seis rutas locales y conserva las medidas y los visuales actuales. Para reconstruir el diseño completo desde cero, ejecutar en este orden `uv run --locked python scripts/build_powerbi_model.py`, `uv run --locked python scripts/build_powerbi_report.py`, `uv run --locked python scripts/refine_powerbi_report.py`, `uv run --locked python scripts/polish_powerbi_clarity.py` y `uv run --locked python scripts/complete_powerbi_acquisition.py`.

El diseño refinado se abrió, actualizó y guardó en Power BI Desktop. Si se editan los archivos PBIR/TMDL externamente con el proyecto abierto, cerrar esa ventana y volver a abrir el `.pbip` antes de guardar desde Desktop.

La carpeta `data/` contiene localmente seis tablas CSV reproducibles exportadas desde las vistas aprobadas de EP1. Se ignoran en Git porque el repositorio es público; en otro equipo hay que generarlas a partir de los dos CSV oficiales de `data/raw/`. No deben reemplazarse por los datos inmobiliarios de práctica. Para regenerarlas:

```powershell
uv run --locked python scripts/export_powerbi.py
```

## Modelo

Importar en Power BI Desktop los seis CSV de `powerbi/data/` con codificación UTF-8, usando la primera fila como encabezado. Comprobar que `content_id`, `show_id`, `type`, `title`, `display_title`, `language`, `language_label`, `genre`, `country`, `director` y `actor` sean texto; `release_year` y `vote_count`, entero; `date_added`, fecha; `popularity`, `vote_average`, `budget`, `revenue` y `return_multiple`, número decimal. No crear una relación por `show_id`: hay colisiones entre películas y series.

| Tabla | Filas esperadas | Clave y relación |
|---|---:|---|
| `catalogo` | 31.991 | `content_id` único, centro del modelo; `display_title` distingue títulos homónimos |
| `generos` | 65.888 | `catalogo[content_id]` 1 → * `generos[content_id]` |
| `paises` | 37.628 | `catalogo[content_id]` 1 → * `paises[content_id]` |
| `directores` | 24.763 | `catalogo[content_id]` 1 → * `directores[content_id]` |
| `actores` | 140.367 | `catalogo[content_id]` 1 → * `actores[content_id]` |
| `finanzas` | 3.540 | `catalogo[content_id]` 1 → 1 `finanzas[content_id]` (solo Movies elegibles) |

Las cinco relaciones del caso propagan filtros en **ambas direcciones**. Esto permite que los segmentadores y las selecciones de géneros, países, directores, intérpretes y películas financieras actualicen los KPI del catálogo. Comprobar con una selección que el total de contenidos cambia y que cada `content_id` se cuenta una sola vez. Desactivar relaciones automáticas incorrectas.

## Medidas DAX sugeridas

Usar `catalogo` como tabla de medidas. Las medidas toman el contexto de filtros activo:

```dax
Total contenidos = DISTINCTCOUNT(catalogo[content_id])
Total películas = COALESCE(CALCULATE([Total contenidos], KEEPFILTERS(catalogo[type] = "Movie")), 0)
Total series = COALESCE(CALCULATE([Total contenidos], KEEPFILTERS(catalogo[type] = "TV Show")), 0)
Países representados = DISTINCTCOUNT(paises[country])
Idiomas disponibles = DISTINCTCOUNT(catalogo[language])
Géneros = DISTINCTCOUNT(generos[genre])
Popularidad promedio = AVERAGE(catalogo[popularity])
Calificación promedio = CALCULATE(AVERAGE(catalogo[vote_average]), catalogo[vote_count] > 0)
Películas financieras = DISTINCTCOUNT(finanzas[content_id])
Presupuesto promedio = AVERAGE(finanzas[budget])
Presupuesto total = SUM(finanzas[budget])
Ingresos totales = SUM(finanzas[revenue])
Ingresos / presupuesto = DIVIDE([Ingresos totales], [Presupuesto total])
ROI bruto aproximado = DIVIDE([Ingresos totales] - [Presupuesto total], [Presupuesto total])
Retorno mediano por título = MEDIAN(finanzas[return_multiple])
```

`Ingresos / presupuesto` es un múltiplo bruto expresado en veces. `ROI bruto aproximado` es una razón decimal formateada como porcentaje y se calcula sobre los importes agregados, no como el promedio de retornos individuales. Ninguno representa utilidad neta ni confirma moneda. El promedio de `popularity` excluye los nueve identificadores de series conflictivos porque sus valores quedaron nulos en la vista de EP1. La calificación se limita a títulos con votos.

## Páginas incluidas y alcance

1. **Dirección ejecutiva:** ocho tarjetas KPI, resumen visible del contexto, botón para borrar segmentadores, distribución anual de la fuente, comparación de películas y series, rankings de países, géneros e idiomas, y segmentadores de tipo, año y género. El título del gráfico temporal aclara que la regularidad de aproximadamente 2.000 contenidos por año corresponde al catálogo completo, antes de filtrar.
2. **Contenidos y adquisición:** resumen visible del contexto y botón para borrar segmentadores; dispersión popularidad–calificación con escala logarítmica y mínimo de 250 votos (6.820 títulos sin filtros), conservando la popularidad original en el tooltip; barras separadas de calificación media y popularidad mediana por género, más treemap de volumen; tabla de hasta 10 títulos mejor valorados con al menos 100 votos, aplicando ese mínimo antes del ranking y distinguiendo homónimos; tarjetas y gráficos financieros; directores, intérpretes y mapa de países con al menos 30 títulos. Los controles de año y calificación son intervalos («Between»). La cobertura financiera dinámica indica películas elegibles / películas seleccionadas (3.540 / 16.000 = 22,1 % sin filtros). La dispersión financiera colorea en verde los títulos cuyos ingresos alcanzan el presupuesto y en coral los demás; el tooltip incluye título y cociente bruto. La lista de candidatas muestra películas con presupuesto ≤ P25 e ingresos ≥ P75 de las 3.540 películas elegibles: 18 títulos sin filtros. Estos umbrales permanecen fijos para que los segmentadores acoten la lista sin cambiar su definición. En el mapa el tamaño indica número de títulos y el azul más oscuro, mayor calificación media entre los países representados. Las notas metodológicas permanecen visibles.

La aplicación `dashboard/app.py` complementa estas páginas con un umbral de votos ajustable para el Top 10 y mapas coropléticos de producción y valoración por país. El mapa nativo de Power BI representa cobertura con burbujas y valoración por color y tooltip; la vista coroplética ejecutiva permanece en la aplicación. Los rankings nativos de talento incluyen empates en la décima posición.

El segmentador de clasificación etaria solicitado por el documento del docente **no se puede construir con los datos entregados**: en los 32.000 registros originales, `rating` coincide exactamente con `vote_average` y no contiene categorías de edad. La página analítica de Power BI y la aplicación advierten esta ausencia. No imputar ni inventar esa variable.

## Tema y verificación

El tema claro `StreamView-theme.json` ya está incorporado al proyecto PBIR. Al probarlo, la vista sin filtros debe mostrar 31.991 contenidos, 16.000 películas, 15.991 series, 147 países, 83 idiomas, 28 géneros y 3.540 películas financieras. Los totales financieros reproducibles están en `docs/conciliacion_financiera_ep2.md`. Tras editar el modelo fuera de Desktop, cerrar cualquier ventana anterior del proyecto, abrir de nuevo el `.pbip` y usar **Actualizar** para cargar `language_label`, la cobertura financiera y los demás resúmenes. Comprobar visualmente los colores del mapa y de la dispersión financiera en Desktop. «Borrar segmentadores» limpia los controles de la página; una selección hecha al pulsar una barra, burbuja o punto se quita desde ese mismo gráfico. La validación de archivos no sustituye esa prueba interactiva.

# Implementación de Lucas Moncada — Integrante 2

## 1. Identificación y alcance

| Campo | Detalle |
|---|---|
| Responsable | Lucas Moncada |
| Rol | Integrante 2 |
| Proyecto | StreamView Analytics |
| Evaluación | Evaluación Parcial 1 (EP1) |
| Fecha de documentación | 7 de septiembre de 2026 |
| Bloque implementado | Popularidad, valoración, rankings, género, relación popularidad–calificación, evolución temporal y KPIs |
| Notebook principal | `notebooks/03_reglas_negocio_kpis.ipynb` |

El bloque de Lucas transforma las vistas preparadas en indicadores, tablas, gráficos y
hallazgos orientados a decisión. No modifica los CSV RAW, no repite la limpieza y no
crea métricas predictivas ni financieras.

## 2. Límite explícito de autoría

Este documento **no atribuye a Lucas Moncada el trabajo previo del integrante 1**.
Ese trabajo se menciona únicamente como dependencia técnica.

| Elemento heredado | Autoría correcta | Uso en este bloque |
|---|---|---|
| Estructura del repositorio, `pyproject.toml`, `uv.lock` y configuración base | Integrante 1 | Entorno utilizado por Lucas. |
| `notebooks/01_exploracion_datos.ipynb` | Integrante 1 | Contexto inicial de los datasets. |
| `notebooks/02_limpieza_preparacion.ipynb` | Integrante 1 | Preparación y reglas de calidad reutilizadas. |
| `src/data_cleaning.py`, `build_catalog_views` y `explode_multivalue_column` | Integrante 1 | Construcción de vistas; Lucas no reimplementó estas funciones. |
| Documentación previa de exploración, calidad y preparación | Integrante 1 | Antecedentes técnicos. |
| `notebooks/04_visualizaciones_storytelling.ipynb` y figuras sin prefijo `lucas_` | Integrante 1 | Caracterización previa; fuera de la autoría de Lucas. |
| `tests/test_data_cleaning.py` | Integrante 1 | Prueba heredada de reconstrucción de vistas. |
| Esqueleto original de `notebooks/03_reglas_negocio_kpis.ipynb` | Integrante 1 | Lucas desarrolló el contenido, pero no creó el archivo base. |
| Placeholders originales de `src/business_rules.py` y `src/visualizations.py` | Integrante 1 | Lucas reemplazó los placeholders por las funciones documentadas aquí. |

La contribución atribuible a Lucas es:

- el contenido analítico incorporado y ejecutado en el notebook 03;
- las reglas y KPIs añadidos a `src/business_rules.py`;
- las seis funciones gráficas añadidas a `src/visualizations.py`;
- `tests/test_business_rules.py`;
- las seis imágenes cuyo nombre comienza con `lucas_`;
- este documento y las actualizaciones puntuales del README que describen el bloque.

## 3. Objetivos y criterio de cumplimiento

| # | Objetivo | Implementación |
|---:|---|---|
| 1 | Trabajar sobre vistas preparadas | Las funciones reciben `catalogo_general`, `catalogo_popularity` y la vista auxiliar preparada `catalogo_generos`; no leen RAW. |
| 2 | Comparar popularidad Movie/TV Show | Tabla de distribución, gráfico comparativo y narrativa ejecutiva. |
| 3 | Analizar valoración | Media, mediana, valoración ponderada, cobertura y volumen de votos se estudian por separado. |
| 4 | Relacionar popularidad y calificación | Rho de Spearman global y por formato, más dispersión estratificada. |
| 5 | Analizar evolución histórica | Series 2010–2025 por año de estreno y auditoría separada del año de incorporación. |
| 6 | Implementar KPIs | Funciones reutilizables, catálogo de KPIs y rankings reproducibles. |
| 7 | Resolver escalas | Diagnóstico de asimetría y ejes logarítmicos, sin cambiar los datos originales. |
| 8 | Entregar storytelling | Cada visual incluye audiencia, propósito, hallazgo, interpretación e implicación. |

Como refuerzo a las preguntas explícitas del caso también se implementaron:

- Top 10 por `popularity`;
- Top 10 por `vote_average`, mostrando además `vote_count`;
- Top 10 por `vote_count`;
- popularidad media y mediana por género;
- popularidad promedio y calificación promedio dentro del catálogo de KPIs.

## 4. Archivos creados y modificados

### 4.1 Archivos creados por Lucas

| Archivo | Propósito |
|---|---|
| `docs/lucas-moncada.md` | Registro completo de implementación, decisiones, resultados y autoría. |
| `tests/test_business_rules.py` | Pruebas unitarias con datos sintéticos. |
| `outputs/figures/lucas_popularidad_movies_vs_tv.png` | Comparación de popularidad por formato. |
| `outputs/figures/lucas_top_10_popularidad.png` | Ranking ejecutivo de contenidos más populares. |
| `outputs/figures/lucas_valoracion_y_votos.png` | Calidad de valoración, cobertura y votos. |
| `outputs/figures/lucas_popularidad_vs_valoracion.png` | Asociación popularidad–calificación. |
| `outputs/figures/lucas_popularidad_por_genero.png` | Géneros líderes por popularidad mediana. |
| `outputs/figures/lucas_evolucion_2010_2025.png` | Evolución anual por formato. |

### 4.2 Archivos preexistentes modificados por Lucas

| Archivo | Cambio realizado |
|---|---|
| `notebooks/03_reglas_negocio_kpis.ipynb` | El placeholder heredado se convirtió en un análisis ejecutable, con tablas, seis gráficos y narrativa. |
| `src/business_rules.py` | Se implementaron validación, resúmenes, rankings, agregación por género, temporalidad, asociación y KPIs. |
| `src/visualizations.py` | Se incorporaron seis funciones visuales reutilizables y una paleta común. |
| `README.md` | Solo se actualizó el alcance del bloque y el enlace a esta documentación. |

## 5. Contexto heredado de datos y vistas

La auditoría y preparación de esta sección corresponden al integrante 1. Lucas consume
sus resultados sin atribuirse su creación.

Fuentes RAW locales:

- `data/raw/netflix_movies_detailed_up_to_2025.csv`;
- `data/raw/netflix_tv_shows_detailed_up_to_2025.csv`.

El notebook no contiene `pd.read_csv`. Entrega las rutas a `build_catalog_views` y
trabaja desde las vistas preparadas:

### 5.1 `catalogo_general`

- 31.991 contenidos únicos: 16.000 Movies y 15.991 TV Shows.
- Conserva valoración y votos incluso cuando la popularidad de un identificador fue
  clasificada como conflictiva.
- Se utiliza para valoración, rankings de puntaje/votos y análisis temporal.

### 5.2 `catalogo_popularity`

- 31.982 contenidos: 16.000 Movies y 15.982 TV Shows.
- Excluye nueve TV Shows con valores conflictivos de `popularity`.
- Es la única fuente para cualquier KPI, ranking o gráfico que use popularidad.

### 5.3 `catalogo_generos`

- Vista normalizada a una fila por `content_id` y género.
- Se une con `catalogo_popularity` mediante `content_id` con validación `many_to_one`.
- Permite comparar géneros sin volver a separar ni limpiar la columna RAW.

## 6. Decisiones metodológicas

### 6.1 Media, mediana y valores extremos

El caso solicita promedios, por lo que se calculan y documentan. Sin embargo,
`popularity` y `vote_count` tienen fuerte asimetría positiva: la mediana se adopta como
medida principal de contenido típico y la media se conserva como KPI complementario.

| Variable | Tipo | Asimetría original | Asimetría con `log1p` |
|---|---|---:|---:|
| popularity | Movie | 31,130 | 1,792 |
| popularity | TV Show | 16,839 | 0,857 |
| vote_count | Movie | 6,662 | -0,454 |
| vote_count | TV Show | 17,864 | 0,875 |

La transformación logarítmica se usa solo en ejes visuales. No se reemplazan
`popularity` ni `vote_count`, y todos los KPIs se calculan sobre valores originales.

### 6.2 Calidad de valoración frente a cantidad de evidencia

- `vote_average` es el puntaje promedio del título.
- `vote_count` cuantifica el respaldo de ese puntaje.
- Solo se interpreta una valoración cuando `vote_count > 0`.
- `vote_average = 0` junto con `vote_count = 0` se trata como ausencia de evidencia,
  no como mala calidad.
- El Top 10 de valoración es literal y no aplica un umbral arbitrario de votos; por
  ello siempre muestra `vote_count`, se titula **“Top 10 por calificación bruta —
  interpretar junto con vote_count”** y advierte que sus líderes tienen evidencia baja.

### 6.3 Asociación mediante Spearman

Se usa rho de Spearman porque no presupone linealidad y es más apropiado ante la
asimetría observada. Se calcula como Pearson sobre rangos promedio, sin añadir SciPy.
El resultado global se informa como referencia, pero la lectura principal se realiza
por formato para evitar confundir diferencias entre poblaciones con una relación
dentro de ellas.

### 6.4 Dos conceptos temporales

- `release_year`: año de estreno del contenido.
- `date_added.year`: año de incorporación al catálogo.

Se implementaron ambos conteos y una auditoría de brecha. En estos archivos los dos
años coinciden en el 100 % de Movies y TV Shows, con brecha mínima, mediana y máxima
igual a cero. Por tanto, no existe información independiente para describir una
tendencia de incorporación distinta a los estrenos. Se presenta la tabla comparativa
y la limitación, pero no un gráfico redundante con líneas exactamente superpuestas.

## 7. Implementación en `src/business_rules.py`

### 7.1 Contrato y filtros internos

`REQUIRED_COLUMNS` exige:

```text
content_id, title, type, release_year, date_added,
popularity, vote_average, vote_count
```

`_validate_view` produce un `KeyError` informativo si falta una columna. `_rated_rows`
retorna una copia con `vote_count > 0` y `vote_average` no nulo, sin alterar la vista.

### 7.2 Funciones públicas

| Función | Entrada | Resultado |
|---|---|---|
| `popularity_comparison` | `catalogo_popularity` | Títulos, media, mediana, Q1, Q3 y máximo por formato. |
| `rating_summary` | `catalogo_general` | Cobertura, media/mediana, media ponderada, votos medianos y totales. |
| `popularity_rating_association` | `catalogo_popularity` | Títulos elegibles y rho global/Movie/TV Show. |
| `content_rankings` | vistas general y popularidad | Top 10 de popularidad, puntaje y votos con desempates reproducibles. |
| `popularity_by_genre` | vistas popularidad y géneros | Títulos únicos, media y mediana por género. |
| `historical_evolution` | vistas general y popularidad | Serie 2010–2025 de popularidad, valoración, votos y cobertura. |
| `catalog_timeline` | `catalogo_general` | Conteos largos de estrenos e incorporaciones por año y formato. |
| `temporal_alignment_summary` | `catalogo_general` | Coincidencia y brecha entre estreno e incorporación. |
| `kpi_summary` | tablas calculadas | Catálogo auditable `kpi`, `scope`, `value`, `unit`, `definition`. |

Fórmulas principales:

```text
cobertura (%) = títulos con vote_count > 0 / títulos totales × 100

valoración ponderada = Σ(vote_average × vote_count) / Σ(vote_count)

brecha temporal = year(date_added) - release_year
```

### 7.3 Punto de entrada reproducible

```python
analysis = build_lucas_analysis(
    catalogo_general,
    catalogo_popularity,
    catalogo_generos,
)
```

Retorna once tablas:

```text
popularity_comparison         rating_summary
popularity_rating_association historical_evolution
popularity_by_genre           catalog_timeline
temporal_alignment            top_popularity
top_rated                     top_voted
kpi_summary
```

## 8. Implementación en `src/visualizations.py`

La identidad cromática se mantiene en todo el bloque: Movie azul `#2F6690` y TV Show
naranja `#D17A22`. Los títulos comunican la conclusión, las escalas logarítmicas están
etiquetadas y las leyendas solo se mantienen cuando aportan identificación.

| Función | Selección visual | Decisión de diseño |
|---|---|---|
| `plot_popularity_comparison` | Barras con intervalo Q1–Q3 | Facilita comparar dos medianas y muestra dispersión; eje log explícito. |
| `plot_top_popular_contents` | Barras horizontales ordenadas | Permite leer títulos largos, posición y magnitud en segundos. |
| `plot_rating_comparison` | Dos paneles de barras | Separa puntaje/cobertura de cantidad de votos; votos en escala log. |
| `plot_popularity_rating_relationship` | Dispersión facetada | Muestra forma, densidad y asociación por formato; transparencia reduce solapamiento. |
| `plot_genre_popularity` | Barras horizontales Top 10 | Prioriza categorías líderes y explica en una nota al pie que `Unknown` se elimina solo de la presentación. |
| `plot_historical_evolution` | Líneas 2010–2025 | Es adecuada para cambios en el tiempo y conserva la comparación Movie/TV. |

`Unknown` permanece en la tabla completa de géneros para no ocultar calidad de datos;
solo se excluye del Top 10 visual, porque no es una categoría accionable.

## 9. Desarrollo del notebook 03

El notebook contiene 29 celdas, 17 de código. Su flujo es:

1. importa funciones y reconstruye las vistas preparadas;
2. calcula las once tablas con `build_lucas_analysis`;
3. diagnostica asimetría y justifica escalas;
4. compara popularidad por formato;
5. presenta los tres rankings y grafica el Top 10 de popularidad;
6. separa calidad de valoración, cobertura y votos;
7. calcula y visualiza popularidad frente a calificación;
8. compara popularidad por género;
9. estudia la evolución 2010–2025 por año de estreno;
10. contrasta estreno e incorporación y documenta su coincidencia;
11. presenta una tabla ejecutiva compacta con popularidad promedio, calificación
    promedio, cobertura y votos medianos por formato, seguida del catálogo técnico
    completo de KPIs, cumplimiento y limitaciones.

Cada bloque visual declara **audiencia principal**, **propósito**, **hallazgo**,
**interpretación** e **implicación de negocio**. El notebook queda ejecutado y guarda
sus resultados y seis PNG reproducibles.

## 10. Resultados principales

### 10.1 Popularidad por formato

| Tipo | Títulos | Media | Mediana | Q1 | Q3 | Máximo |
|---|---:|---:|---:|---:|---:|---:|
| Movie | 16.000 | 20,3847 | 10,9135 | 7,8408 | 17,3365 | 3.876,006 |
| TV Show | 15.982 | 64,9065 | 36,2140 | 24,9098 | 62,2528 | 6.421,923 |

La mediana de TV Shows es 3,32 veces la de Movies.

### 10.2 Rankings

- Mayor popularidad: *The Late Show with Stephen Colbert* (TV Show), 6.421,923.
- Segundo lugar: *The Tonight Show Starring Jimmy Fallon* (TV Show), 4.925,253.
- Tercer lugar: *The Gorge* (Movie), 3.876,006.
- Composición del Top 10 de popularidad: 7 TV Shows y 3 Movies.
- Mayor cantidad de votos: *Inception* (Movie), 37.119 votos.
- El Top 10 literal de `vote_average` presenta puntajes 10,0 respaldados por solo
  3–5 votos; no debe usarse como ranking robusto sin mostrar ese contexto.

### 10.3 Valoración y evidencia

| Tipo | Cobertura | Promedio | Mediana | Ponderada | Votos medianos | Votos totales |
|---|---:|---:|---:|---:|---:|---:|
| Movie | 94,4125 % | 6,3089 | 6,40 | 6,8381 | 154 | 11.498.498 |
| TV Show | 77,0746 % | 7,0237 | 7,20 | 7,8593 | 9 | 1.712.228 |

TV Shows obtiene mejor valoración típica, pero Movies reúne mucha más evidencia.

### 10.4 Popularidad y valoración

| Alcance | Títulos | Rho de Spearman | Lectura |
|---|---:|---:|---|
| Global | 27.430 | 0,3225 | Positiva débil/moderada, influida por mezclar formatos. |
| Movie | 15.106 | 0,2153 | Positiva débil. |
| TV Show | 12.324 | 0,0355 | Prácticamente nula. |

### 10.5 Popularidad por género

Los líderes por mediana son Soap (88,398), News (53,556), Talk (51,283), Kids
(40,972) y Reality (40,789). La tabla también conserva media y cantidad de títulos
para evitar comparar categorías sin contexto de cobertura.

### 10.6 Evolución y temporalidad

- Movies alcanza su máxima popularidad mediana en 2024: 27,6770.
- TV Shows alcanza su máxima popularidad mediana en 2018: 46,7550.
- En 2025 la cobertura de valoración cae a 26,5 % en Movies y 37,1342 % en TV Shows.
- `release_year` y `date_added.year` coinciden en el 100 % de los registros de ambos
  formatos; los conteos de estrenos e incorporaciones son idénticos en la fuente.

## 11. Storytelling y audiencia

| Bloque | Audiencia principal | Hallazgo e implicación respaldada |
|---|---|---|
| Popularidad por formato | Marketing / Contenidos | Las series tienen una mediana 3,32 veces mayor. Los resultados sugieren evaluar umbrales de comparación o priorización por formato, porque las distribuciones son distintas. |
| Top 10 popularidad | Marketing / Contenidos | Siete de diez líderes son series; conviene contextualizar campañas y rankings por formato. |
| Valoración y votos | Contenidos / Adquisición | Las series puntúan más alto, pero las películas tienen más respaldo; un ranking debe mostrar ambas dimensiones. |
| Popularidad–valoración | Contenidos / Marketing | La asociación interna es débil o nula; popularidad y valoración deben mantenerse como dimensiones separadas. |
| Géneros | Contenidos / Adquisición | Soap lidera la mediana; el resultado orienta exploración editorial, no demuestra demanda causal. |
| Evolución histórica | Gerencia General / Contenidos | Las trayectorias difieren por formato y los máximos de popularidad mediana ocurren en años distintos; además, 2025 tiene menor cobertura. |
| Estreno vs incorporación | Gerencia General / Contenidos | La fuente duplica ambos conceptos temporales; no permite inferir una estrategia real de incorporación. |

## 12. Alineación con la pauta EP1

| Criterio evaluado | Evidencia del bloque |
|---|---|
| IE4 — percepción visual y jerarquía | Títulos orientados al hallazgo, orden de lectura claro y ranking ordenado por posición. |
| IE5 — atributos visuales | Paleta Movie/TV consistente, color categórico y etiquetas directas. |
| IE6 — claridad y carga cognitiva | Seis gráficos focalizados, paneles separados cuando las unidades cambian, KPIs ejecutivos antes del detalle técnico y ausencia de adornos innecesarios. |
| IE7 — selección de gráficos | Barras para comparación/ranking, dispersión para asociación y líneas para tiempo. |
| IE9 — audiencia y propósito | Cada sección identifica destinatario y decisión que puede informar. |
| IE10 — narrativa visual | Secuencia Hallazgo → Interpretación → Implicación, con límites explícitos para no sobreafirmar. |

## 13. Pruebas y reproducibilidad

`tests/test_business_rules.py` usa DataFrames sintéticos; no depende de los CSV RAW.
Cubre:

1. popularidad, promedio/mediana de valoración y evolución;
2. exclusión de títulos sin votos del puntaje analítico;
3. uso de `catalogo_popularity` en métricas de popularidad;
4. Spearman global y por formato;
5. rankings, agregación por género y desempates;
6. diferencia entre `release_year` y `date_added.year`;
7. no mutación de las tres vistas recibidas.

La suite completa incluye además `tests/test_data_cleaning.py`, que sigue atribuida al
integrante 1.

Reproducción desde la raíz:

```powershell
uv sync
uv run python -m unittest discover -s tests -v
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/03_reglas_negocio_kpis.ipynb --ExecutePreprocessor.kernel_name=python3 --ExecutePreprocessor.timeout=180
```

## 14. Matriz final de cumplimiento

| # | Evidencia concreta | Estado |
|---:|---|---|
| 1 | Notebook sin `pd.read_csv`; tres vistas preparadas como entradas. | Cumplido |
| 2 | `popularity_comparison`, tabla, PNG y narrativa. | Cumplido |
| 3 | `rating_summary`, rankings, cobertura, promedio, mediana, ponderada y votos. | Cumplido |
| 4 | Spearman global/por tipo y dispersión facetada. | Cumplido |
| 5 | `historical_evolution`, PNG 2010–2025, `catalog_timeline` y auditoría de fechas. | Cumplido |
| 6 | `kpi_summary`, rankings y `build_lucas_analysis`. | Cumplido |
| 7 | Diagnóstico de asimetría y ejes log sin modificar datos. | Cumplido |
| 8 | Audiencia, propósito y narrativa en cada bloque. | Cumplido |

## 15. Limitaciones y pendientes de alcance

- `popularity` es un índice relativo, no reproducciones reales.
- Los metadatos de catálogo no miden campañas ni satisfacción directa del usuario.
- Asociación no implica causalidad.
- Un puntaje perfecto con pocos votos no demuestra calidad consolidada.
- `Unknown` se conserva en resultados tabulares aunque se omita del Top 10 visual.
- La menor cobertura de 2025 exige cautela al comparar esa cohorte.
- La igualdad exacta entre estreno e incorporación impide estudiar tendencias reales
  de ingreso al catálogo con estas fuentes.
- Popularidad/calificación por país e idioma no se añadieron a este refuerzo mínimo;
  pueden incorporarse en otro bloque si la distribución grupal los asigna a Lucas.
- No se implementaron dashboard interactivo, integración final del informe ni análisis
  financiero/ROI, porque pertenecen a etapas o responsables distintos.

## 16. Estado de entrega

El bloque de Lucas queda implementado, documentado y preparado para revisión e
integración mediante su rama de trabajo. Este estado no reasigna a Lucas ninguna pieza
previa del integrante 1 ni incluye la futura implementación financiera del Integrante 3.

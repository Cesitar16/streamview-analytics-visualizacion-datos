# StreamView Analytics

Proyecto académico de **Data Science y Visual Analytics** para la asignatura Visualización de Datos. El repositorio prepara un flujo reproducible para estudiar un catálogo audiovisual simulado y apoyar decisiones estratégicas.

## Contexto y objetivo

StreamView Analytics representa una empresa de streaming que busca transformar la información de su catálogo en conocimiento útil. El objetivo semestral será construir una solución de Visual Analytics sobre composición del catálogo, películas versus series, géneros, países, idiomas, popularidad, valoración, evolución temporal y —solo para películas— presupuesto, ingresos y ROI.

## Alcance original: EP1

El proyecto contiene exploración, auditoría de calidad, preparación reproducible, caracterización del catálogo y el bloque analítico de popularidad, valoración, rankings, género, asociación y evolución histórica. Las transformaciones se realizan en memoria sin sobrescribir los CSV originales.

## Evaluación 2

Los dos CSV oficiales están disponibles localmente en `data/raw/`. La evaluación 2 reutiliza las vistas y reglas anteriores para construir dos dashboards: **Ejecutivo** y **Contenidos y adquisición**. La aplicación interactiva se ejecuta con Python y Streamlit e incluye un treemap en D3. `powerbi/StreamView_EP2.pbip` es el proyecto nativo de Power BI; los CSV preparados, el tema y las notas del modelo están en esa carpeta.

En EP1 no se guardó un CSV final en `data/processed/`: esa carpeta contiene solo `.gitkeep`. El procesamiento aprobado quedó en `src/data_cleaning.py` mediante `build_catalog_views`, usado también por los notebooks de EP1. En EP2, `src/dashboard_data.py` llama esa misma función sobre los dos CSV originales; Streamlit consume sus vistas en memoria y `scripts/export_powerbi.py` exporta esas mismas vistas a seis CSV locales para Power BI. La perspectiva ejecutiva de Streamlit incorpora una serie temporal por tipo y un comparador de géneros que mantiene conteos únicos aun cuando las categorías se solapan. Así se reutilizan las reglas de EP1 sin mantener dos versiones independientes de datos preparados.

```powershell
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python scripts/export_powerbi.py
uv run --locked streamlit run dashboard/app.py
```

La aplicación se abre localmente en `http://localhost:8501`. Los filtros recalculan los indicadores desde las vistas de EP1; los CSV RAW no se reescriben. `dashboard/d3.v7.min.js` se incluye para que el treemap no dependa de una CDN. Véanse `powerbi/README.md` y `docs/conciliacion_financiera_ep2.md` antes de presentar cifras financieras.

El informe escrito y las diapositivas se encuentran en `output/pdf/`. Sus fuentes editables son `docs/Informe_Ejecutivo_EP2.md` y `scripts/build_ep2_pdfs.py`. Para regenerar ambos PDF: `uv run --locked python scripts/build_ep2_pdfs.py`. El [guion de defensa técnica](docs/guion_defensa_tecnica_ep2.md) organiza una exposición de 10 minutos, la demostración en vivo y posibles preguntas. La aplicación ofrece exportación CSV del catálogo filtrado y del subconjunto financiero. La [matriz de cumplimiento](docs/matriz_cumplimiento_ep2.md) indica dónde se encuentra cada elemento solicitado y qué debe comprobarse antes de entregar.

Los CSV de `powerbi/data/` se generan localmente con `scripts/export_powerbi.py` y quedan fuera de Git, igual que los archivos originales de `data/raw/`. Para el encargo, `uv run --locked python scripts/package_ep2_data.py` crea `output/entrega/StreamView_EP2_Datos.zip` con las dos fuentes y las seis tablas derivadas; el ZIP se adjunta por la plataforma y no se publica en Git. En otro equipo, extraerlo en la raíz y ejecutar `scripts/rebase_powerbi_sources.py` con Power BI Desktop cerrado antes de abrir el `.pbip`. La [guía de reproducción](docs/reproduccion_ep2.md) describe el proceso completo; [equipo y evidencia](docs/equipo_y_evidencia_ep2.md) recoge los antecedentes verificables del proyecto grupal.

Limitaciones visibles en los dashboards: `rating` no contiene una clasificación etaria utilizable; `date_added.year` coincide con `release_year` en las fuentes; el análisis financiero solo cubre 3.540 películas con presupuesto e ingresos positivos. Los importes se muestran como USD por la convención del informe EP1, ya que los CSV no incluyen una columna de divisa.

El notebook 03 y `src/business_rules.py` implementan los KPIs de Lucas Moncada sobre `catalogo_general`, `catalogo_popularity` y la vista preparada `catalogo_generos`. El notebook 05 y `src/financial_rules.py` implementan el bloque financiero de Ignacio Silva sobre `movies_financial_valid`.

## Fuentes de datos

El trabajo utilizará exclusivamente los archivos proporcionados por la asignatura:

- `netflix_movies_detailed_up_to_2025.csv`
- `netflix_tv_shows_detailed_up_to_2025.csv`

Colócalos en `data/raw/`. Los CSV originales no deben editarse ni sobrescribirse desde los notebooks o módulos del proyecto. Por precaución de tamaño, los CSV de esa carpeta están ignorados por Git; no se incluyen en el repositorio.

### Movies y TV Shows

Cada fila representa un contenido audiovisual. Las películas y las series se compararán únicamente en variables equivalentes. Campos como título, director, actores, país, idioma, género, clasificación, duración, año, fecha de ingreso, popularidad, valoración y votos pueden requerir revisión antes de compararse.

`budget` y `revenue` son exclusivos de las películas. Por tanto, cualquier indicador financiero o ROI se calculará solo sobre películas con valores válidos. `vote_average` usa una escala de 0 a 10 y `popularity` es un índice relativo, no un conteo de reproducciones.

## Estructura del repositorio

```text
streamview-analytics-visualizacion-datos/
├── .streamlit/              # configuración de la aplicación
├── dashboard/               # Streamlit, treemap D3 y licencia
├── data/
│   ├── raw/                  # CSV originales locales (no versionados)
│   └── processed/            # reservado; la preparación actual ocurre en memoria
├── docs/                     # fuentes y documentación de EP1 y EP2
├── notebooks/                # exploración y análisis de EP1 (01–05)
├── output/
│   ├── pdf/                  # informe y presentación finales de EP2
│   └── entrega/              # ZIP local de datos (no versionado)
├── outputs/
│   └── figures/              # figuras generadas para EP1
├── powerbi/                  # proyecto PBIP, modelo, informe y tema de EP2
│   └── data/                 # CSV derivados locales (no versionados)
├── reports/                  # directorio reservado desde EP1
├── scripts/                  # exportación, reproducción y generación de entregables
├── src/                      # limpieza, reglas, vistas y datos del dashboard
├── tests/                    # comprobaciones de datos, dashboards y entrega
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

`output/` reúne los entregables de EP2; `outputs/figures/` conserva las figuras de EP1. `reports/` y `data/processed/` son directorios reservados de EP1 y solo contienen `.gitkeep`. Los CSV originales, los CSV exportados para Power BI y el ZIP de entrega se mantienen localmente fuera de Git. Las vistas previas de PDF, `tmp/` y `superpowers/` también se excluyen del repositorio.

## Preparación del entorno

El proyecto usa [uv](https://docs.astral.sh/uv/) para gestionar Python, el entorno virtual y las dependencias. Se requiere Python 3.13.

### Instalar uv

Si todavía no tienes `uv`, puedes instalarlo en Windows con PowerShell:

```powershell
winget install --id=astral-sh.uv -e
```

También están disponibles otros métodos en la documentación oficial de uv.

### Sincronizar dependencias

Desde la raíz del repositorio, ejecuta:

```powershell
uv sync
```

Esto crea o actualiza `.venv/` a partir de `pyproject.toml` y `uv.lock`. `uv.lock` debe versionarse; `.venv/` no.

Para ejecutar Python sin activar manualmente el entorno:

```powershell
uv run python
```

Si prefieres activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Iniciar Jupyter

Ejecuta desde la raíz:

```powershell
uv run jupyter lab
```

Selecciona el kernel **Python (StreamView Analytics)**. Si no aparece después de recrear el entorno, regístralo de nuevo:

```powershell
uv run python -m ipykernel install --user --name streamview-analytics --display-name "Python (StreamView Analytics)"
```

## Notebooks

- **01_exploracion_datos:** inspección inicial y comprensión de ambos datasets.
- **02_limpieza_preparacion:** calidad, nulos, duplicados, tipos, formatos y outliers.
- **03_reglas_negocio_kpis:** reglas del caso, variables derivadas y KPIs.
- **04_visualizaciones_storytelling:** visualizaciones requeridas y narrativa.

Los notebooks 01, 02 y 04, junto con la preparación de datos, corresponden al trabajo previo del integrante 1. El notebook 03 corresponde al bloque de Lucas Moncada y reconstruye sus tablas y figuras desde esas vistas preparadas.

La implementación completa, metodología, KPIs, hallazgos y matriz de cumplimiento del bloque están documentados en `docs/lucas-moncada.md`.

## Bloque financiero

El equipo analizó el desempeño financiero de las películas usando
`movies_financial_valid`, una vista preparada con la regla
`budget > 0 AND revenue > 0`.

El bloque incluye KPIs financieros, el múltiplo individual `revenue / budget` y el
ROI bruto agregado `((SUM(revenue) - SUM(budget)) / SUM(budget))`, la relación entre
presupuesto e ingresos, los Top 10 por ingresos y por múltiplo, y el grupo de
películas con bajo presupuesto y alto retorno. La implementación se encuentra en
`notebooks/05_analisis_financiero.ipynb`, `src/financial_rules.py` y
`docs/ignacio-silva.md`; las figuras quedan en `outputs/figures/` con el prefijo
`ignacio_` y las pruebas en `tests/test_financial_rules.py`.

## Tecnologías

- Python 3.13
- uv
- pandas y NumPy
- Matplotlib y Seaborn
- Jupyter e ipykernel
- Git y GitHub

No se incluyen librerías de Machine Learning porque el proyecto no contempla modelos predictivos.

## Flujo de trabajo con Git y GitHub

Se utilizará GitHubFlow con `main` como rama principal. Para trabajo posterior, crea ramas cortas y descriptivas, por ejemplo:

```text
feature/exploracion-datos
feature/limpieza-datos
feature/reglas-negocio-kpis
feature/visualizaciones
docs/informe-ep1
```

Mantén los cambios enfocados, revisa el notebook o código antes de integrarlo y evita subir datos RAW o credenciales. Este repositorio no configura remoto ni realiza pushes automáticamente.

## Estado del proyecto

EP1 está conservada como base analítica. EP2 dispone de dos vistas interactivas en Python/D3, un proyecto nativo de Power BI con dos páginas, un informe ejecutivo PDF y una presentación PDF. La conciliación financiera de EP2 usa los CSV actuales y documenta una pequeña diferencia frente a los importes transcritos en EP1. Los archivos de datos originales y las tablas exportadas permanecen solo en el equipo local; para una entrega reproducible en otro equipo, se deben proporcionar los dos CSV oficiales por el canal autorizado de la asignatura.

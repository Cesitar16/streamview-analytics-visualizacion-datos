# StreamView Analytics

Proyecto académico de **Data Science y Visual Analytics** para la asignatura Visualización de Datos. El repositorio prepara un flujo reproducible para estudiar un catálogo audiovisual simulado y apoyar decisiones estratégicas.

## Contexto y objetivo

StreamView Analytics representa una empresa de streaming que busca transformar la información de su catálogo en conocimiento útil. El objetivo semestral será construir una solución de Visual Analytics sobre composición del catálogo, películas versus series, géneros, países, idiomas, popularidad, valoración, evolución temporal y —solo para películas— presupuesto, ingresos y ROI.

## Alcance actual: EP1

El proyecto contiene exploración, auditoría de calidad, preparación reproducible, caracterización del catálogo y el bloque analítico de popularidad, valoración, rankings, género, asociación y evolución histórica. Las transformaciones se realizan en memoria sin sobrescribir los CSV originales.

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
├── data/
│   ├── raw/                  # CSV originales locales (no versionados)
│   └── processed/            # datos derivados futuros
├── notebooks/
│   ├── 01_exploracion_datos.ipynb
│   ├── 02_limpieza_preparacion.ipynb
│   ├── 03_reglas_negocio_kpis.ipynb
│   └── 04_visualizaciones_storytelling.ipynb
├── outputs/
│   └── figures/              # figuras reproducibles de los análisis
├── reports/                  # informes y entregables futuros
├── src/
│   ├── data_cleaning.py      # preparación reutilizable futura
│   ├── business_rules.py     # KPIs y reglas analíticas reproducibles
│   └── visualizations.py     # funciones visuales reutilizables
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

Los directorios vacíos usan `.gitkeep` para que Git los conserve. Los resultados futuros en `data/processed/`, `outputs/figures/` y `reports/` no se ignoran de forma global: decide qué entregables versionar cuando existan.

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

El bloque incluye KPIs financieros, ROI aproximado (`revenue / budget`), la relación
entre presupuesto e ingresos, los Top 10 por ingresos y por ROI, y el grupo de
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

**EP1 en desarrollo avanzado.** Están implementadas la exploración, calidad y preparación del catálogo, cuatro visualizaciones de composición y el bloque de popularidad, valoración, rankings, género, asociación y evolución. Queda pendiente integrar los demás bloques del equipo y consolidar el informe final.

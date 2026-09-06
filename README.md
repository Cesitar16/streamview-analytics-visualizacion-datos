# StreamView Analytics

Proyecto académico de **Data Science y Visual Analytics** para la asignatura Visualización de Datos. El repositorio prepara un flujo reproducible para estudiar un catálogo audiovisual simulado y apoyar decisiones estratégicas.

## Contexto y objetivo

StreamView Analytics representa una empresa de streaming que busca transformar la información de su catálogo en conocimiento útil. El objetivo semestral será construir una solución de Visual Analytics sobre composición del catálogo, películas versus series, géneros, países, idiomas, popularidad, valoración, evolución temporal y —solo para películas— presupuesto, ingresos y ROI.

## Alcance actual: EP1

El proyecto está en **Configuración inicial / preparación para EP1**. Esta fase solo establece el entorno, la estructura, la documentación y los puntos de extensión del código. No se han realizado análisis, limpieza, KPIs, visualizaciones, storytelling ni transformaciones de datos.

En las siguientes etapas se documentarán y justificarán el tratamiento de nulos, duplicados, tipos, formatos, categóricas, outliers, fechas y coherencia de los campos financieros.

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
│   └── figures/              # figuras futuras
├── reports/                  # informes y entregables futuros
├── src/
│   ├── data_cleaning.py      # preparación reutilizable futura
│   ├── business_rules.py     # reglas y variables derivadas futuras
│   └── visualizations.py     # funciones visuales futuras
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

Actualmente todos contienen solo una introducción Markdown; se desarrollarán en ese orden cuando comience EP1.

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

**Configuración inicial / preparación para EP1.** Los CSV deben añadirse manualmente a `data/raw/` antes de iniciar la exploración.


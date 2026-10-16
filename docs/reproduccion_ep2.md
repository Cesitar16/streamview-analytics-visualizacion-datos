# Reproducción de StreamView Analytics · EP2

La entrega requiere **dos piezas**: el repositorio del proyecto y el archivo `StreamView_EP2_Datos.zip`, preparado para adjuntarlo por separado en el encargo de la asignatura. El ZIP conserva las rutas `data/raw/` y `powerbi/data/`. Los CSV no se incluyen en el repositorio público. No se necesita editar código ni los CSV para reproducir la solución.

## Preparar el proyecto en otro equipo

1. Obtener el repositorio correspondiente a EP2 y colocar `StreamView_EP2_Datos.zip` en su raíz.
2. Extraer el ZIP en esa raíz, **conservando las carpetas**. En PowerShell:

   ```powershell
   Expand-Archive -LiteralPath .\StreamView_EP2_Datos.zip -DestinationPath . -Force
   ```

3. Confirmar que existen los dos archivos `data/raw/netflix_*_detailed_up_to_2025.csv` y las seis tablas `powerbi/data/*.csv`. `MANIFEST.sha256` dentro del ZIP registra la huella de cada archivo; los originales no deben editarse.
4. Instalar Python 3.13 y `uv`. Desde la raíz del repositorio:

   ```powershell
   uv sync --locked
   uv run --locked python -m unittest discover -s tests -v
   uv run --locked python scripts/export_powerbi.py
   uv run --locked streamlit run dashboard/app.py
   ```

   La aplicación se abre en `http://localhost:8501`. La exportación vuelve a generar las seis tablas de Power BI desde los dos originales; no cambia `data/raw/`.

5. Con **Power BI Desktop cerrado**, ajustar únicamente las rutas locales de las seis consultas a esta carpeta y abrir el proyecto:

   ```powershell
   uv run --locked python scripts/rebase_powerbi_sources.py
   ```

   Abrir `powerbi/StreamView_EP2.pbip` en Power BI Desktop y pulsar **Actualizar**. Si Desktop solicita confirmar el origen de los CSV, seleccionar los archivos locales extraídos. El script cambia solo las rutas `File.Contents` de las seis tablas; conserva medidas DAX, relaciones, páginas y visuales.

## Cifras de control

| Comprobación | Valor esperado sin filtros |
|---|---:|
| Contenidos únicos | 31.991 |
| Películas / series | 16.000 / 15.991 |
| Países / idiomas / géneros | 147 / 83 / 28 |
| Películas con presupuesto e ingresos positivos | 3.540 |
| Presupuesto / ingresos de la muestra elegible | 125.960.767.278 / 367.371.433.138 |

La aplicación y Power BI deben responder al tipo y género seleccionados. En la perspectiva analítica, elegir **TV Show** deja la sección financiera sin películas elegibles. `docs/verificacion_demostracion_ep2.md` registra las comprobaciones realizadas.

## Archivos de entrega y límites

- `output/pdf/StreamView_EP2_Informe.pdf`: informe ejecutivo.
- `output/pdf/StreamView_EP2_Presentacion.pdf`: presentación de diez láminas.
- `docs/guion_defensa_tecnica_ep2.md`: exposición y preguntas.
- `powerbi/StreamView_EP2.pbip`: proyecto de Power BI con dos páginas.
- `dashboard/app.py`: aplicación Streamlit con dos perspectivas.
- `StreamView_EP2_Datos.zip`: dos fuentes originales y seis exportaciones; **debe adjuntarse al encargo y no publicarse en Git**.

`data/processed/` no contiene un dataset final de EP1: `src/data_cleaning.py` reconstruye las vistas en memoria. La popularidad de nueve series conflictivas se excluye solo de métricas que requieren popularidad; `rating` no permite clasificación etaria; `date_added` no demuestra incorporaciones reales; las finanzas cubren solo una muestra de películas. El README y el informe explican estas restricciones.

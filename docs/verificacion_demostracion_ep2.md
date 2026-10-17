# Verificación de la demostración · EP2

Fecha: 16 de octubre de 2026. Se comprobaron la aplicación Streamlit y las dos páginas del proyecto Power BI.

| Escenario | Resultado y evidencia |
|---|---|
| Streamlit, panorama inicial | 31.991 títulos, 16.000 películas, 15.991 series; serie temporal de líneas por tipo, mapa coroplético con 147 países y treemap D3 incorporado. Prueba `test_executive_filters_map_notes_and_reset`. |
| Streamlit, filtros ejecutivos | Película + Drama + 2020–2023 cambia cifras y mantiene mapa. Restablecer devuelve los 31.991 títulos y los tres controles a sus valores iniciales. Misma prueba. |
| Streamlit, evolución y comparador | La serie temporal concilia títulos únicos por año y tipo. El comparador Drama/Comedy conserva títulos únicos, respeta filtros globales, excluye popularidad no confiable y comunica conjuntos vacíos. Pruebas `test_segment_comparison.py`. |
| Streamlit, adquisición inicial | 3.540 películas financieras; mapa analítico con 35 países que cumplen el mínimo de 100 títulos valorados; aparecen las notas de cobertura y clasificación etaria. Prueba `test_acquisition_cross_filters_finance_map_thresholds_and_reset`. |
| Streamlit, cruces analíticos | Película + Action + Estados Unidos + inglés + 2020–2023 + nota 5–8 produce 416 títulos únicos y 128 películas financieras elegibles. Mismos resultados en `src.dashboard_data`. |
| Streamlit, umbrales y reinicio | Votos mínimos 250 y títulos mínimos por país 200 se aplican; Restablecer los devuelve a 100 y restaura cifras y demás filtros. Prueba automatizada. |
| Streamlit, solo series | 15.991 títulos, cero películas financieras, aviso explicativo, mapa disponible y ambas descargas CSV presentes. Prueba automatizada. |
| Streamlit, revisión visual | Treemap y mapa cargan en navegador; al seleccionar solo series aparece el aviso financiero sin errores. |
| Power BI, página 01 | En Desktop se observaron las cifras iniciales, los gráficos de tipo, países, géneros e idiomas, el cruce de tipo y género, y el restablecimiento sin errores. |
| Power BI, página 02 | En Desktop se observaron las cifras iniciales y las notas visibles. Al seleccionar series la sección financiera queda vacía y Restablecer devuelve el estado inicial. La tabla de candidatas responde a los filtros de tipo y género. El visual Azure Maps se mantiene como complemento y puede requerir una sesión habilitada; no se usa como evidencia principal de la demostración. |
| Sitio local | El servidor Streamlit responde HTTP 200 en `http://127.0.0.1:8501/_stcore/health`. |

La suite completa se ejecutó con `uv run --locked python -m unittest discover -s tests -v`: **23 pruebas correctas**. Las cifras financieras completas concilian con 3.540 películas, US$ 125.960.767.278 de presupuesto y US$ 367.371.433.138 de ingresos. El mapa, el treemap, la serie temporal, el comparador, la exportación y las reglas financieras se comprobaron mediante pruebas de contenido y revisión visual.

Para la defensa conviene iniciar sin filtros, mostrar un cruce que cambie tarjetas y gráficos, explicar la superposición de fechas y géneros, seleccionar solo series para demostrar la cobertura financiera parcial y cerrar restableciendo los filtros. El mapa de países usa nombres reconocidos por Plotly; cualquier país no reconocido se explica mediante la nota visible en la aplicación.

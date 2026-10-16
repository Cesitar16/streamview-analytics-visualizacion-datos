# Evaluación 2 · matriz de cumplimiento y revisión final

Fuentes de esta revisión: `evaluacion-ea2/REQUERIMIENTOS ENTREGA EXPERIENCIA 2.pdf`, pauta EP3 (encargo) y pauta EP4 (presentación y defensa), ubicadas en la carpeta superior del proyecto. Para la demostración principal se asigna el dashboard ejecutivo a Python/Streamlit/D3 y el analítico a Power BI. Ambas herramientas incluyen vistas complementarias. La cobertura de un elemento en una herramienta no implica que esté también en la otra.

| Solicitud | Evidencia preparada | Estado y observación |
|---|---|---|
| Dos audiencias y KPI ejecutivos | Vistas «Ejecutiva» y «Contenidos y adquisición» en `dashboard/app.py` y dos páginas en `powerbi/StreamView_EP2.pbip` | Cubierto; la vista ejecutiva muestra los ocho indicadores pedidos. |
| Distribución por año, tipo, géneros, países e idiomas | Columnas anuales, gráficos y treemap D3 en la aplicación; columnas y rankings nativos en Power BI | Cubierto. La fuente equipara incorporación y estreno; ambas herramientas muestran solo la distribución por año registrado y advierten que no representa altas reales. Power BI muestra las categorías principales y el mapa coroplético queda en la aplicación. |
| Filtros ejecutivos | Tipo, rango de año y género en la aplicación; segmentadores de tipo, intervalo de año y género en Power BI | Cubierto. |
| Popularidad frente a calificación; género; treemap | Dispersión con tamaño por votos, barras y treemap D3 en la aplicación; dispersión con popularidad en escala log, barras separadas de popularidad mediana y calificación media por género, y treemap en Power BI | Cubierto. La escala de Power BI distribuye los valores extremos y conserva el valor original en el tooltip. |
| Top 10 de valoración con mínimo de votos | Tabla Top 10 con umbral ajustable en la aplicación y tabla nativa con umbral fijo de 100 votos | Cubierto. El umbral de Power BI es fijo; el de la aplicación se puede variar. |
| Top directores y actores | Tablas Top 10 en la aplicación y barras nativas de talento | Cubierto, con aviso sobre créditos faltantes en la aplicación. Los rankings nativos incluyen empates. |
| Mapa analítico por país con mínimo de títulos | Mapa de calificación media con control de mínimo en la aplicación; mapa de burbujas Power BI con mínimo fijo de 30 títulos, tamaño por volumen y color por calificación media | Cubierto en conjunto. La aplicación conserva el ajuste del umbral; el mapa nativo muestra el valor exacto en el tooltip. |
| Finanzas | Subconjunto elegible, tarjetas, dispersión, Top 10 de ingresos y candidatos de bajo presupuesto en la aplicación; tarjetas, cobertura dinámica, dispersión coloreada por ingreso/presupuesto, barras de principales ingresos, lista de bajo presupuesto y altos ingresos y nota metodológica en Power BI | Cubierto en ambas vistas analíticas. La nueva lista Power BI usa presupuesto ≤ P25 e ingresos ≥ P75 de la muestra financiera completa, para que el criterio no cambie al filtrar. El carácter aproximado del múltiplo se explica en la aplicación y el informe. |
| Filtros analíticos | Tipo, género, país, idioma, intervalo de años y calificación en ambas herramientas; controles adicionales de votos y cobertura en la aplicación | Cubierto salvo clasificación etaria: en las 32.000 filas originales `rating` reproduce `vote_average`, por lo que no existe una categoría de edad que se pueda seleccionar. La ausencia queda visible en Power BI y en el pie de la aplicación. |
| Python, D3 y Power BI | `src/`, `dashboard/`, `powerbi/` | Cubierto. Los datos preparados son comunes y su generación está documentada. |
| Informe y presentación | `output/pdf/StreamView_EP2_Informe.pdf`, `output/pdf/StreamView_EP2_Presentacion.pdf`, `docs/guion_defensa_tecnica_ep2.md` | Preparados. Las diapositivas explican preparación, construcción e interacción en ambas herramientas; el guion organiza la defensa oral de 10 minutos y preguntas individuales. |
| Exportación, organización y reproducción | Descarga CSV en la aplicación; `docs/reproduccion_ep2.md`; proyecto PBIP y PDF; ZIP local en `output/entrega/` | Preparado localmente. El ZIP con dos fuentes y seis tablas derivadas debe adjuntarse al encargo por la plataforma y no publicarse en Git. En otro equipo se extrae y se ajustan las rutas del PBIP mediante script, sin editar código ni CSV. |
| Participación del equipo | `docs/equipo_y_evidencia_ep2.md`, historial Git de EP1, `docs/guion_defensa_tecnica_ep2.md` | El historial documenta la base analítica de EP1; el guion organiza la exposición individual de EP2. |
| URL de repositorio y entrega en plataforma | Repositorio del proyecto y paquete de datos | Incluir la URL del repositorio y adjuntar el ZIP de datos en el encargo. |

## Comprobaciones para la demostración

1. Abrir la aplicación y alternar las dos vistas. Mostrar que los filtros recalculan los 31.991 contenidos y sus desgloses.
2. En la vista analítica, variar el mínimo de votos y el mínimo de títulos por país; explicar por qué ambos evitan comparaciones débiles.
3. Mostrar los 3.540 registros financieros elegibles y la advertencia de cobertura. Explicar que ingresos/presupuesto es un múltiplo bruto aproximado, no utilidad neta.
4. Abrir el `.pbip` y recorrer sus dos páginas. Verificar 31.991 contenidos, 16.000 películas, 15.991 series, 147 países, 83 idiomas, 28 géneros y 3.540 películas financieras.
5. Presentar el informe PDF y la presentación PDF. Preparar respuestas sobre calidad de datos, unión mediante `content_id`, representaciones elegidas, límites del mapa, edad, fechas, moneda y cobertura financiera.

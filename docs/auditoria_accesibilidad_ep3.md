# Informe de trabajo · DUO-42: accesibilidad y legibilidad

**Responsable:** Lucas Moncada

**Fecha de registro:** 13 de noviembre de 2026

**Tarjeta:** [DUO-42 en Linear](https://linear.app/duoc2026/issue/DUO-42/auditar-accesibilidad-y-legibilidad-de-dashboards-y-entregables)

**Estado del trabajo:** en curso; quedan pendientes para cumplir todos los criterios de la tarjeta.

## Objetivo y alcance

Revisar la legibilidad, accesibilidad y comunicación visual de Streamlit, Power BI, el informe y la presentación para el cierre de EP5/EP6, especialmente los indicadores IE28 e IE29. Se consideran propósito y datos, representación, interpretación, legibilidad y navegación. El trabajo no equivale a una certificación de accesibilidad ni a una evaluación formal con usuarios.

Los datos disponibles describen el catálogo; no permiten medir directamente usuarios, reproducciones, retención o engagement. Esta restricción guía las correcciones de lenguaje e interpretación.

## Hallazgos y acciones

| Herramienta / página | Hallazgo y riesgo | Acción o decisión | Evidencia / estado |
|---|---|---|---|
| Streamlit · ambas vistas | El subtítulo mencionaba «señales de audiencia» y adquisición hablaba de «interés», aunque las fuentes no miden consumo de usuarios. | Se nombran popularidad relativa y valoración, sin cambiar cálculos. | Inspección de la aplicación con los CSV oficiales; cambio en `dashboard/app.py`. |
| Streamlit · panorama | Las series de películas y series se distinguían por color. | Se añade estilo de línea por tipo; se conserva la leyenda. | Cambio en `dashboard/app.py`; pendiente comprobar visualmente en pantalla de presentación. |
| Streamlit · adquisición y finanzas | Las categorías en las dispersiones dependían del color. | Se añade forma por tipo de contenido y por cobertura de presupuesto. | Cambio en `dashboard/app.py`; pendiente verificar legibilidad con datos oficiales y filtros. |
| Streamlit · treemap | Los géneros pequeños no caben necesariamente como etiquetas; categorías se solapan. | Se conserva la lista con etiquetas y valores, selección por teclado y explicación del denominador. | Revisión de árbol accesible y documentación `docs/evaluacion_usabilidad_dashboard_ux.md`; falta prueba completa con lector de pantalla. |
| Streamlit · panorama | La distribución anual podría confundirse con incorporaciones reales o evolución de mercado. | Se conserva la nota explícita de la limitación. | Texto de la aplicación revisado con datos oficiales. |
| Presentación EP2 · láminas 2, 4, 6 y 8 | Las figuras ocupan una parte reducida de la lámina y los ejes y etiquetas resultan pequeños a escala de presentación. | Pendiente rediseñar o sustituir figuras para la versión final y probar en proyector. | Revisión visual del PDF de 10 páginas; no se afirma una prueba en proyector. |
| Informe EP2 · páginas 2–4 | Las figuras tienen etiquetas pequeñas y el texto del PDF financiero no coincide con la fuente Markdown actual, que ya incorpora ROI bruto. | Revisar la figura y regenerar el informe final desde fuentes verificadas al integrar el trabajo del equipo. | Revisión visual del PDF y comparación con `docs/Informe_Ejecutivo_EP2.md`; pendiente integrar. |
| Power BI y Streamlit · ambas vistas | Lucas informó que revisó ambas aplicaciones y las encontró en orden. | Conservar esta revisión como antecedente, sin atribuirle pruebas específicas no detalladas. | Revisión comunicada por Lucas; no sustituye una prueba documentada de contraste o tecnologías de asistencia. |

## Corrección adicional en Power BI

Lucas detectó una tarjeta con error en la sección financiera de Contenidos y adquisición. La definición de la tarjeta solicitaba `ROI bruto aproximado`, pero esa medida no existía en el modelo guardado. Se agregó al modelo y a `scripts/build_powerbi_model.py` con la fórmula documentada:

`DIVIDE([Ingresos totales] - [Presupuesto total], [Presupuesto total])`

La medida se presenta como porcentaje y corresponde a ROI bruto aproximado agregado, no a utilidad neta. Se agregó `tests/test_powerbi_roi.py` para comprobar que la tarjeta y ambas fuentes del modelo mantienen la misma medida. La corrección se verificó mediante pruebas automáticas; no se registró una comprobación independiente del valor de esa tarjeta en Power BI Desktop después del cambio.

## Revisión de los PDF de EP2

- La presentación tiene 10 láminas y el informe 5 páginas. Se revisaron las páginas renderizadas de ambos archivos; los textos de los gráficos en las láminas 2, 4, 6 y 8 son pequeños respecto del resto de la diapositiva. También requieren atención las figuras del informe, en particular sus ejes y etiquetas. La revisión no equivale a una prueba de proyección.
- El PDF del informe describe el múltiplo de ingresos/presupuesto, pero no incorpora el ROI bruto agregado que sí aparece en la sección 7 de `docs/Informe_Ejecutivo_EP2.md`. Debe regenerarse desde la versión acordada cuando el equipo integre los cambios del informe.
- La presentación se identifica como experiencia 2 y menciona 21 pruebas; no debe presentarse como versión final de EP5/EP6 sin actualizar su contenido y verificar la evidencia vigente.
- La figura de géneros del PDF muestra porcentajes distintos a los del treemap actual. Sus denominadores deben verificarse y explicarse antes de reutilizar ambas representaciones juntas; las categorías pueden solaparse.

## Verificación inicial

- `uv run --locked python -m unittest discover -s tests -v`: 25 pruebas aprobadas con los datos locales disponibles.
- Después de corregir la medida, `uv run --locked python -m unittest tests.test_powerbi_roi tests.test_financial_rules -v`: seis pruebas aprobadas. La ejecución completa de 25 pruebas se realizó antes de añadir la prueba de la tarjeta.
- La revisión inicial en Streamlit mostró 31.991 títulos, 16.000 películas y 15.991 series en la vista ejecutiva. Las pruebas comprueban filtros y reglas existentes; no sustituyen una prueba visual o de tecnologías de asistencia.
- Las capturas históricas de `docs/evidence/dashboard-ux/` usan datos sintéticos. No se presentan como evidencia visual del estado actual con datos oficiales.

## Pendiente para cerrar DUO-42

- Mejorar y volver a inspeccionar los gráficos de la presentación y el informe finales; conciliar sus cifras y denominadores con las fuentes y con el trabajo del equipo.
- Regenerar y revisar los PDF cuando estén integradas y acordadas las fuentes definitivas de EP5/EP6. Los PDF de EP2 no se modificaron en esta revisión.
- Registrar la comprobación de la tarjeta de ROI en Power BI Desktop después de reabrir el proyecto.
- Completar la evidencia por artefacto, probar la presentación en una pantalla de proyección y documentar las comprobaciones de contraste, teclado y tecnologías de asistencia que se realicen o queden pendientes.

Los cambios están en el proyecto local y no se ha registrado el cierre de la tarjeta en Linear.

# Plan priorizado de mejoras · StreamView Analytics

**Criterio:** IE33 de EP6: oportunidades de mejora viables, priorizadas y fundamentadas. El anexo distingue las mejoras ya incorporadas de las acciones futuras propuestas.

## Mejoras incorporadas durante el proyecto

La siguiente síntesis se basa en commits integrados hasta `7f3e6a7` y en los archivos actuales. Los nombres corresponden al autor registrado por Git: un commit puede reunir trabajo colaborativo y no demuestra por sí solo toda la participación de cada integrante.

| Etapa y mejora | Aporte incorporado y beneficio | Evidencia y autor registrado |
|---|---|---|
| EP1 · exploración y calidad | Se exploraron las fuentes y se documentaron nulos, duplicados, conflictos y limitaciones como el campo `rating`. Esto permite fundamentar qué variables pueden usarse y cuáles no. | `760cd8f` y `defe9b8`, Cesitar16; `docs/hallazgos_exploracion_inicial_ep1.md`, `docs/calidad_datos_decisiones.md`. |
| EP1 · preparación del catálogo | Se prepararon vistas y categorías multivalor sin sobrescribir los CSV originales. La clave y las tablas auxiliares permiten contar contenidos y categorías con reglas explícitas. | `ac543a6`, Cesitar16; `src/data_cleaning.py`, `tests/test_data_cleaning.py`. |
| EP1 · popularidad y valoración | Se incorporaron KPI, comparaciones, rankings y reglas para votos y popularidad, con pruebas. Esto permite explorar señales del catálogo sin tratarlas como reproducciones. | `89809fc`, LucasMoncadaCL; `src/business_rules.py`, `tests/test_business_rules.py`. |
| EP1 · finanzas | Se incorporó un análisis de películas con presupuesto e ingresos elegibles, con indicadores, visualizaciones y pruebas. La selección evita tratar automáticamente los valores no válidos como evidencia financiera. | `92200bb`, ign00; `src/financial_rules.py`, `docs/ignacio-silva.md`. |
| EP2 · dashboards y reproducción | Se integraron Streamlit/D3 y Power BI, filtros, KPI, exportaciones y guías. Esto facilita explorar el catálogo y preparar su ejecución en otro equipo. | `eb6a71b`, LucasMoncadaCL; `dashboard/app.py`, `powerbi/`, `docs/reproduccion_ep2.md`. La verificación en un entorno limpio sigue pendiente. |
| EP2 · comparaciones analíticas | Se añadieron la distribución anual por tipo y un comparador de géneros con conteos únicos, evitando sumar segmentos que pueden solaparse. | `d8b437f`, Cesitar16; `src/segment_comparison.py`, `docs/comparacion_segmentos.md`. |
| EP2 · usabilidad | Se mejoraron la información de filtros, los estados vacíos y la exploración del treemap, incluida una lista para categorías pequeñas; se documentaron pruebas y capturas. | `b982e19` y `7d15298`, ign00; `docs/evaluacion_usabilidad_dashboard_ux.md`. |
| EP2 · lectura financiera | Se añadió el ROI bruto aproximado y se distinguió del múltiplo ingresos/presupuesto; también se ajustó la presentación financiera de Power BI. | `b9a27d8`, `ef458fc` y `fd42006`, Cesitar16; `src/financial_rules.py`, `powerbi/README.md`. |
| EP5/EP6 · evidencia y comunicación | Se prepararon el informe EP5 y una matriz que relaciona hallazgos, decisiones y límites; se ajustó la trazabilidad posterior. | `cb3e0ac` y `73e1d12`, ign00; `docs/Informe_Ejecutivo_EP5.md`, `docs/trazabilidad_ep5_ep6.md`. |
| Cierre · legibilidad y corrección | Se aclaró el lenguaje sobre popularidad, se añadieron estilos y formas a gráficos y se incorporó al modelo la medida usada por la tarjeta de ROI. | `2bc8510`, LucasMoncadaCL; `dashboard/app.py`, `tests/test_powerbi_roi.py`, `docs/auditoria_accesibilidad_ep3.md`. La auditoría conserva pendientes para los entregables finales. |

Estas mejoras son antecedentes verificables del trabajo realizado. Su existencia no demuestra que se hayan completado las acciones futuras descritas a continuación.

## Oportunidades futuras: criterio de priorización

El orden considera primero el riesgo para la interpretación y la entrega, luego la factibilidad en el proyecto actual y, finalmente, las dependencias externas. Una prioridad alta indica que conviene atenderla antes; no supone que sea fácil ni que exista una fecha comprometida. Los plazos y responsables se acuerdan con el equipo.

| Prioridad | Mejora y problema | Propuesta técnica | Dependencia y viabilidad | Beneficio esperado y justificación |
|---|---|---|---|---|
| 1 | **Reproducción de la entrega.** Los CSV y derivados están fuera de Git y Power BI usa rutas locales. | Verificar el ZIP, sus huellas, extracción, exportación y ajuste de rutas; ejecutar pruebas y abrir ambos tableros en otro equipo. Documentar los pasos y el resultado. | Se cuenta con scripts, guía y paquete local; requiere un entorno limpio y Power BI Desktop. Coordinar con DUO-46 de César. | Permite detectar fallas que impedirían ejecutar la solución completa. Se prioriza por ser condición de entrega y no requerir una nueva fuente. |
| 2 | **Cobertura de créditos y finanzas.** Los rankings omiten créditos no informados; solo 3.540 de 16.000 películas tienen presupuesto e ingresos positivos. | Añadir o reforzar indicadores de cobertura y avisos por segmento en las vistas que los utilicen; mantener las reglas de elegibilidad y contrastar los totales con las fuentes. | Factible con los CSV y vistas actuales. Completar registros, en cambio, requiere una fuente adicional autorizada y reglas de conciliación. | Ayuda a interpretar rankings y cifras parciales sin extrapolarlos al catálogo completo. Se prioriza por su efecto directo sobre las conclusiones y su factibilidad. |
| 3 | **Reconocimiento geográfico.** Los nombres de país pueden no coincidir con los reconocidos por el mapa. | Comparar nombres presentes con un catálogo geográfico adecuado, registrar coincidencias y excepciones, y mantener una tabla alternativa con valores y cobertura. Validar manualmente las correspondencias ambiguas antes de aplicarlas. | La auditoría puede comenzar con los países existentes; una tabla de equivalencias o catálogo externo requiere selección y validación. La herramienta de mapas y su disponibilidad condicionan la comprobación. | Reduce el riesgo de ubicar u omitir países incorrectamente; no convierte país de producción en consumo local. Se prioriza después de cobertura porque existe una alternativa tabular, aunque aún debe comprobarse. |
| 4 | **Fecha real de incorporación.** El año de `date_added` coincide con el de estreno; no permite sostener análisis de altas reales. | Solicitar datos de incorporación con definición, fecha y clave de título; validar cobertura y unión antes de construir una vista temporal separada. Conservar la serie actual rotulada como año registrado. | Depende de una fuente de eventos autorizada y compatible; no es recuperable desde los CSV actuales. | Podría permitir analizar incorporaciones verificadas. Se posterga frente a controles factibles hoy; no implica inferir tendencias de audiencia. |
| 5 | **Clasificación etaria.** `rating` reproduce la nota y no identifica edades. | Solo si se autoriza una fuente, documentar su procedencia y jurisdicción, asociarla por identificadores fiables y medir coincidencias y valores sin clasificar antes de ofrecer un filtro. | Requiere fuente externa autorizada, cobertura adecuada y revisión del contexto territorial; no imputar edades desde la nota. | Haría posible segmentar por clasificación conocida, con sus límites. Se ubica después de las acciones realizables con datos actuales por depender de información ausente. |

El orden entre fechas y clasificación puede cambiar si la audiencia define una necesidad prioritaria y se dispone de una fuente fiable para ella. La priorización no afirma causalidad ni beneficios comerciales medidos.

## Separación por dependencia

- **Con el proyecto y las fuentes actuales:** verificar reproducción y cobertura; iniciar controles de nombres geográficos y mantener la alternativa tabular.
- **Con fuentes adicionales autorizadas:** completar créditos o finanzas, obtener fechas reales y añadir clasificación etaria. La conciliación debe conservar los originales, identificar valores sin correspondencia y documentar cobertura y procedencia.

La solución actual no contiene datos de usuarios, reproducciones ni retención. Ninguna mejora anterior, por sí sola, permite medir o prometer mejoras de retención o engagement.

## Evidencia de partida

- `docs/Informe_Ejecutivo_EP5.md`, secciones 5–8: límites temporales, geográficos y financieros.
- `docs/calidad_datos_decisiones.md`: `rating`, cobertura de créditos y ceros financieros.
- `docs/reproduccion_ep2.md` y `scripts/package_ep2_data.py`: procedimiento y paquete de datos.
- `docs/trazabilidad_ep5_ep6.md`: relación de los riesgos y la planificación de la defensa.

## Regeneración de los PDF

Desde la raíz del proyecto, `uv run --locked python scripts/build_ep5_mejoras_pdfs.py` genera el anexo PDF y actualiza el informe EP5 a partir de sus fuentes Markdown. Requiere Arial instalada y las dependencias del proyecto. Revisar ambos PDF después de modificar sus fuentes.

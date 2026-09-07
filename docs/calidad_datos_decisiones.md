# StreamView Analytics — Decisiones de calidad de datos

## Propósito

Esta matriz registra las decisiones propuestas por la auditoría del notebook
02_limpieza_preparacion.ipynb. Distingue una observación de calidad de una
transformación: las fuentes RAW no se modifican aquí.

| Variable / alcance | Problema | Evidencia | Impacto | Decisión propuesta | Justificación | Branch donde se aplica |
|---|---|---|---|---|---|---|
| rating | Inconsistencia con el diccionario | Es numérica y coincide 100 % con vote_average en ambas fuentes. | No permite análisis de clasificación etaria. | No usar como clasificación etaria ni completarla con fuentes externas. Usar vote_average solo para valoración. | La semántica observada contradice la declarada; inferir edades produciría información no sustentada. | Calidad: documentar. Preparación/visualización: excluir de análisis etario. |
| duration | Disponibilidad no analítica | Movies: 100 % nula; TV Shows: un único valor no nulo (1 Seasons). | No existen duraciones comparables ni variabilidad útil. | Conservar tal como llega y excluir de análisis de duración. | Imputar o inventar temporadas alteraría la fuente. | Calidad: documentar. Visualización: excluir. |
| show_id | Tipo semántico y conflicto de popularity en TV Shows | Se carga como entero, aunque el diccionario lo describe como texto. TV Shows tiene 15.991 IDs únicos; 9 IDs forman 18 filas y cada par difiere solo en popularity. | Puede afectar conteos y análisis dependientes de popularity. | Para conteos: una entidad por show_id. Para popularity: excluir ambos registros de los 9 IDs conflictivos. No borrar RAW ni crear un valor sintético. | La fuente no indica qué popularity es correcta y no contiene temporalidad de actualización. | Calidad: documentar. Preparación: detección, flag y aplicación de filtro. |
| Duplicados exactos | Posibles repeticiones completas | El conteo duplicated(keep=False) es 0 en Movies y 0 en TV Shows. | No hay evidencia de filas idénticas que eliminar. | Conservar todos los registros; no aplicar deduplicación automática. | La ausencia de duplicados exactos no resuelve la repetición de identificadores. | Calidad: decisión. Preparación: aplicar solo si se aprueba. |
| director y cast | Cobertura parcial | director tiene 132 nulos en Movies y 10.965 (68,531 %) en TV Shows; cast tiene 204 y 1.157, respectivamente. | Rankings y análisis de créditos pueden representar una fracción del catálogo. | Conservar nulos; excluir solo del análisis que requiera el campo e informar cobertura. | Sin información no debe contarse como persona real. | Calidad: documentar. Preparación/visualización: regla de presentación explícita. |
| country, genres, director, cast | Valores multivalor | Existen celdas separadas por coma; la auditoría mide espacios, vacíos, repeticiones y tamaños de lista. | Contar cadenas completas crea categorías artificiales. | Mantener la columna original y, posteriormente, separar por coma, aplicar strip() y crear tablas auxiliares explotadas. | Preserva trazabilidad y permite frecuencias individuales correctas. | Calidad: definir regla. Preparación: aplicar. |
| language | Calidad categórica por verificar | No hubo señal inicial de coma; la auditoría revisa espacios, vacíos, placeholders y variantes. | Podrían existir categorías inconsistentes. | No tratarla como multivalor sin evidencia; normalizar solo si la auditoría demuestra una regla segura. | Evita suposiciones por analogía con otros campos. | Calidad: documentar. Preparación: solo si procede. |
| date_added | Tipo de fecha almacenado como texto | Los 32.000 valores son parseables; Movies abarca 2010-01-01 a 2025-12-25 y TV Shows 2010-01-01 a 2025-12-31. No hay casos anteriores a release_year. | Requiere preparación para análisis temporal. | Mantener RAW sin cambios y convertir una copia con pd.to_datetime en preparación. Los casos anteriores al año de estreno se documentan, no se corrigen automáticamente. | La conversión es semántica y reproducible; la coherencia depende de la definición del campo. | Calidad: validar. Preparación: aplicar. |
| release_year | Validación temporal | Entero, completo y dentro del rango observado 2010–2025. | Apto estructuralmente para análisis temporal. | Conservar; documentar cualquier incoherencia frente a date_added sin reescritura automática. | No hay evidencia previa de una conversión necesaria. | Calidad: validar. |
| vote_average | Regla de dominio | Escala declarada 0–10; la auditoría cuenta valores fuera de rango. | Sustenta análisis de valoración. | Conservar los valores dentro del dominio; investigar solo excepciones reales. | Cumple la regla conocida y no requiere limpieza preventiva. | Calidad: validar. |
| popularity y vote_count | Magnitud, ceros y extremos | No hay negativos. vote_count tiene 894 ceros en Movies y 3.674 en TV Shows; popularity no tiene ceros. IQR marca extremos en ambas variables. | Los extremos pueden dominar escalas y los ceros afectan interpretación. | Conservar valores; no interpretar popularity como reproducciones; definir filtros o escalas solo por análisis. | Un outlier estadístico no prueba un error. | Calidad: documentar. Visualización: decidir escala/filtro. |
| budget y revenue (Movies) | Disponibilidad, ceros, negativos y extremos | No hay nulos ni negativos. budget tiene 11.153 ceros, revenue 10.355; 9.048 filas tienen ambos en cero y solo 3.540 ambos positivos. | Afecta futuros indicadores financieros. | No calcular ROI aquí. Tratar cero como estado incierto salvo evidencia adicional; excluir solo mediante una regla financiera explícita. | El caso exige excluir información financiera no válida, pero el origen de los ceros no puede inferirse con certeza. | Calidad: documentar. Preparación/KPI: aplicar filtros aprobados. |

## Clasificación por resolubilidad

| Problema | Qué ocurre y evidencia | Clasificación | ¿Puede solucionarse técnicamente? | Política antes de actuar | Branch de aplicación |
|---|---|---|---|---|---|
| date_added | Los 32.000 valores son parseables y no hay incoherencias frente a release_year. | A. Resolvable mediante preparación | Sí: una copia puede convertirse a datetime de forma reproducible. | Conservar RAW y documentar formato, errores coercionados y columnas derivadas. | cesar/feature/preparacion-catalogo |
| Tipo de show_id | El CSV se carga como entero aunque es un identificador y el diccionario lo describe como texto. | A. Resolvable mediante preparación | Sí: conversión semántica de una copia a string. | Preservar la columna RAW y no usar el ID como medida numérica. | cesar/feature/preparacion-catalogo |
| Campos multivalor y espacios | country, genres, director y cast contienen comas; la auditoría detectó pocos espacios de borde en director/cast. | A. Resolvable mediante preparación | Sí, mediante separación por coma y strip() sobre copias trazables. | Definir la tabla auxiliar por variable y conservar la cadena original. | cesar/feature/preparacion-catalogo |
| rating | Replica vote_average en 100 % de filas comparables y no existe otra columna explícitamente etaria. | B. Limitación permanente de la fuente | No: falta la información original de clasificación etaria. | No inferir, imputar ni buscar una sustitución externa; declarar la limitación. | Calidad: documentar; visualización: excluir del análisis etario. |
| duration | Movies no tiene valores y TV Shows solo contiene 1 Seasons. | B. Limitación permanente de la fuente | No: no hay duración ni variabilidad que recuperar. | No imputar ni fabricar minutos o temporadas; excluir del análisis de duración. | Calidad: documentar; visualización: excluir. |
| director en TV Shows | 10.965 valores nulos (68,531 %). | B. Limitación permanente de la fuente | No para los nulos originales: no se pueden inventar directores. | Mantener nulos y comunicar la cobertura de cualquier análisis de créditos. | Calidad: documentar; preparación/visualización: aplicar regla de cobertura. |
| show_id repetidos | 9 IDs forman 18 filas, con igual título y todas las columnas coincidentes salvo popularity. | D. Decisión metodológica definida — aplicación pendiente | No puede recuperarse el valor verdadero de popularity con las fuentes disponibles. | Detectar los IDs programáticamente, marcar popularity_conflict, evitar doble conteo de entidad y excluir ambos registros solo de análisis dependientes de popularity. | cesar/feature/preparacion-catalogo |
| Ceros financieros | budget tiene 11.153 ceros y revenue 10.355; 9.048 filas tienen ambos en cero. | C. Requiere decisión antes de transformar | No sin una política que interprete los ceros y la validez financiera. | Mantener los valores; definir criterios de inclusión antes de KPI o ROI. | cesar/feature/preparacion-catalogo y cesar/feature/reglas-negocio-kpis |
| Nulos y extremos en análisis específicos | La cobertura y los valores IQR extremos dependen de la variable y del análisis posterior. | C. Requiere decisión antes de transformar | Sí técnicamente, pero no debe hacerse de forma global. | Definir exclusión o presentación por análisis y conservar los datos originales. | cesar/feature/preparacion-catalogo y visualización |

## Política definida para show_id con conflicto de popularity

La auditoría confirma un conflicto de atributo para una misma entidad identificada por
show_id; no son duplicados exactos. La detección programática identifica 9 IDs y 18
filas: 9 de 15.991 entidades únicas de TV Shows (0,056 %). Esta distinción exige
separar dos usos:

- **Conteo del catálogo:** un show_id repetido no debe representar dos contenidos. La
  etapa de preparación debe conservar una única entidad conceptual por show_id y evitar
  doble conteo, sin borrar las filas RAW.
- **Análisis de popularity:** no existe evidencia para determinar cuál valor es correcto.
  Se excluyen ambos registros de esos 9 IDs de promedios, comparaciones, relaciones,
  rankings, KPIs y gráficos que dependan directamente de popularity. Se mantienen para
  análisis que no usen popularity.

La futura etapa de preparación debe detectar los conflictos desde los datos, crear el
flag booleano popularity_conflict, conservar la trazabilidad de ambas filas RAW y
documentar cuántas entidades se excluyen. El máximo popularity conflictivo es 24,577,
muy inferior al umbral aproximado del Top 10 de TV Shows (2.379,884); el diagnóstico
indica que la exclusión no alcanza ese umbral de rankings altos.

## Alternativas evaluadas para resolver el conflicto de popularity

| Alternativa | Decisión | Justificación |
|---|---|---|
| Conservar el primer registro | Rechazada | El orden del CSV no demuestra temporalidad ni validez. |
| Conservar el último registro | Rechazada | El orden del CSV no demuestra temporalidad ni validez. |
| Conservar el valor máximo | Rechazada | Mayor popularity no demuestra que sea más reciente ni correcta. |
| Conservar el valor mínimo | Rechazada | Tampoco existe una justificación de calidad para preferirlo. |
| Promediar ambos valores | Rechazada | Generaría un valor sintético no observado directamente en la fuente. |
| Excluir los IDs de todos los análisis | Rechazada | Es innecesariamente destructiva: los demás atributos son consistentes. |
| Excluir los IDs solo de análisis dependientes de popularity | Seleccionada | Minimiza pérdida de información, evita una regla arbitraria y no inventa datos. |

La selección se justifica porque date_added y release_year coinciden en cada par y no
existe una marca temporal de actualización de popularity. Elegir primero, último,
máximo o mínimo sería arbitrario; promediar no representa necesariamente una
observación real.

## Extremos estadísticos, inválidos y sospechosos

- **Extremo estadístico:** un valor fuera de 1,5 × IQR. Indica una posición extrema,
  no un error; popularity, vote_count, budget y revenue pueden ser altos y plausibles.
- **Valor inválido por dominio:** viola una regla conocida, como un negativo no permitido,
  vote_average fuera de 0–10 o una fecha no interpretable. Requiere investigación.
- **Valor sospechoso:** necesita más evidencia, pero todavía no puede declararse erróneo.

La política es conservar los extremos plausibles y no eliminarlos automáticamente.
Las escalas logarítmicas, límites visuales o filtros analíticos se decidirán después,
por visualización y con justificación. Ningún valor fue transformado en esta rama.

## Limitaciones no resolubles con las fuentes entregadas

- No existe una clasificación etaria confiable mediante rating.
- duration no permite estudiar duración de Movies ni número de temporadas de TV Shows.
- La naturaleza real de un cero financiero no puede demostrarse solo con estos CSV.

## Handoff a cesar/feature/preparacion-catalogo

La siguiente etapa debe implementar únicamente reglas ya aprobadas: copia semántica de
show_id como texto, conversión definitiva de date_added, normalización segura de
espacios, separación de campos multivalor y tablas auxiliares explotadas. También debe
mantener una regla explícita para cobertura de nulos y para la inclusión financiera.
Además, debe detectar programáticamente los IDs con conflicto de popularity, crear
popularity_conflict, evitar doble conteo de entidad y construir la versión apta para
análisis de popularity excluyendo esos IDs. No debe modificar data/raw ni decidir que
los ceros de budget/revenue representan datos faltantes sin evidencia adicional.

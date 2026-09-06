# StreamView Analytics — Hallazgos de la exploración inicial y plan de calidad de datos

**Proyecto:** StreamView Analytics  
**Asignatura:** ADY1104 — Visualización de Datos  
**Evaluación:** Evaluación Parcial 1 (EP1)  
**Branch documentada:** `feature/exploracion-datos`  
**Siguiente branch recomendada:** `feature/calidad-datos`  
**Notebook de referencia:** `notebooks/01_exploracion_datos.ipynb`

---

## 1. Objetivo de este documento

Este documento registra de forma trazable los hallazgos obtenidos durante la exploración inicial de las dos fuentes oficiales del proyecto y los contrasta con lo establecido en:

- `Caso_Semestral_STREAMVIEW_ANALYTICS.pdf`
- `REQUERIMIENTOS ENTREGA EXPERIENCIA 1.pdf`
- `netflix_movies_detailed_up_to_2025.csv`
- `netflix_tv_shows_detailed_up_to_2025.csv`
- `notebooks/01_exploracion_datos.ipynb`

La finalidad es que la exploración inicial no quede únicamente dentro del notebook, sino que exista una documentación técnica comprensible que explique:

1. qué esperaba encontrar el caso;
2. qué se encontró realmente en los datasets;
3. qué aspectos son consistentes con la documentación;
4. qué inconsistencias o limitaciones fueron detectadas;
5. qué impacto pueden tener sobre los análisis de la EP1;
6. qué debe investigarse en `feature/calidad-datos`;
7. qué transformaciones deberán quedar para `feature/preparacion-catalogo`.

> **Principio de trabajo:** los archivos de `data/raw/` se consideran fuentes originales y no deben modificarse. Las decisiones de limpieza o transformación deben realizarse sobre copias o datos derivados y quedar documentadas y justificadas.

---

# 2. Relación con los requerimientos de la EP1

El documento de requerimientos de la Entrega 1 exige explícitamente trabajar sobre los siguientes aspectos de calidad y preparación:

- tratamiento de valores nulos;
- registros duplicados;
- inconsistencias de tipos y formatos;
- manejo de outliers / valores atípicos;
- implementación de reglas de negocio;
- filtrado financiero;
- normalización / escalas;
- cálculo de variables derivadas / KPI;
- primeras visualizaciones;
- storytelling inicial;
- documentación técnica y uso de GitHub con GitFlow o GitHubFlow.

El Caso Semestral complementa lo anterior indicando que, antes de construir las visualizaciones, debe revisarse la calidad considerando:

- valores nulos;
- registros duplicados;
- formatos inconsistentes;
- variables categóricas;
- fechas;
- valores atípicos;
- coherencia entre presupuesto e ingresos;
- disponibilidad parcial de variables según el tipo de contenido.

Además, todas las transformaciones realizadas deben quedar **documentadas y justificadas**.

Por esta razón, `feature/exploracion-datos` se utilizó solamente para **observar, validar y documentar**, mientras que `feature/calidad-datos` deberá profundizar sistemáticamente en los problemas detectados.

---

# 3. Fuentes analizadas

El caso define dos fuentes oficiales para todo el proyecto:

| Fuente | Registros observados | Variables observadas | Referencia del caso |
|---|---:|---:|---|
| Movies | 16.000 | 18 | Aproximadamente 16.000 registros y 18 variables |
| TV Shows | 16.000 | 16 | Aproximadamente 16.000 registros y 16 variables |

## Conclusión

Las dimensiones reales coinciden con la estructura general descrita por el caso.

Se identificaron:

- **16 variables compartidas** entre Movies y TV Shows;
- **2 variables exclusivas de Movies:** `budget` y `revenue`;
- **0 variables exclusivas adicionales de TV Shows**.

Esto es coherente con la documentación, que establece que presupuesto e ingresos están disponibles únicamente para contenidos cinematográficos.

---

# 4. Variables compartidas y exclusivas

Las variables estructuralmente compartidas son:

- `show_id`
- `type`
- `title`
- `director`
- `cast`
- `country`
- `date_added`
- `release_year`
- `rating`
- `duration`
- `genres`
- `language`
- `description`
- `popularity`
- `vote_count`
- `vote_average`

Exclusivas de Movies:

- `budget`
- `revenue`

> **Importante:** que una variable esté presente en ambos datasets **no significa automáticamente que sea comparable**. También debe validarse su significado, tipo, disponibilidad, formato y calidad.

El hallazgo de `duration` demuestra precisamente esta diferencia entre **presencia estructural** y **utilidad real**.

---

# 5. Matriz resumida de hallazgos

| Aspecto | Resultado observado | Clasificación | Impacto | Siguiente acción |
|---|---|---|---|---|
| Dimensiones | Movies 16.000×18; TV Shows 16.000×16 | Conforme | La estructura coincide con el caso | Sin acción inmediata |
| Variables compartidas | 16 variables comunes | Conforme estructuralmente | Permite plantear análisis conjuntos después de validar cada variable | Validar calidad/comparabilidad |
| `budget` / `revenue` | Solo Movies | Conforme | Finanzas y ROI deben restringirse a películas | Análisis financiero posterior |
| `type` | 16.000 `Movie` y 16.000 `TV Show` | Conforme | Identificación principal consistente | Sin acción inmediata |
| `date_added` | Completa, texto, 100% interpretable como fecha | Requiere preparación | Puede utilizarse después de conversión documentada | `feature/preparacion-catalogo` |
| `release_year` | `int64`, sin nulos, 2010–2025 | Conforme | Disponible para análisis temporal | Sin acción inmediata |
| `vote_average` | 0–10, sin valores fuera de rango | Conforme | Respeta regla de negocio | Sin acción inmediata |
| `rating` | Numérica y 100% igual a `vote_average` | Inconsistencia | No representa clasificación etaria como indica el caso | `feature/calidad-datos` |
| Clasificación etaria | No hay variable confiable mediante `rating` | Limitación funcional | No se puede reproducir correctamente ese análisis | Documentar limitación |
| `duration` Movies | 16.000 nulos | Limitación severa | No puede analizarse duración de películas | `feature/calidad-datos` |
| `duration` TV Shows | 16.000 veces `1 Seasons` | Limitación severa | No posee variabilidad analítica | `feature/calidad-datos` |
| `show_id` tipo | `int64` en ambas fuentes | Inconsistencia documental | Es identificador, no medida numérica | Definir representación |
| `show_id` unicidad Movies | 16.000 registros / 16.000 IDs | Conforme | No hay señal preliminar de duplicidad por ID | Validar duplicados completos |
| `show_id` unicidad TV | 16.000 registros / 15.991 IDs | Señal de calidad | Existen 9 diferencias registro-ID único | Investigar duplicados |
| `director` Movies | 132 nulos (0,825%) | Disponibilidad parcial | Puede afectar rankings/análisis de producción | Evaluar política de nulos |
| `director` TV | 10.965 nulos (68,531%) | Limitación importante | Un análisis de directores en series tendría cobertura muy incompleta | Evaluar/explicitar |
| `cast` Movies | 204 nulos (1,275%) | Disponibilidad parcial | Afecta análisis de actores | Evaluar política de nulos |
| `cast` TV | 1.157 nulos (7,231%) | Disponibilidad parcial | Afecta análisis de actores | Evaluar política de nulos |
| `country` | Señales de valores múltiples | Requiere preparación | Contar cadenas completas produciría categorías artificiales | Separar/normalizar después |
| `genres` | Señales de valores múltiples | Requiere preparación | Fundamental para géneros predominantes | Separar/normalizar después |
| `director` | Señales de valores múltiples | Requiere preparación | Un contenido puede tener múltiples directores | Separar si el análisis lo requiere |
| `cast` | Señales de valores múltiples | Requiere preparación | Un contenido contiene múltiples actores | Separar para frecuencias |
| `language` | Sin señal de coma en diagnóstico | Sin evidencia de multivalor con ese separador | No debe tratarse como multivalor sin nueva evidencia | Revisar formato/categorías |

---

# 6. Hallazgo 1 — Estructura general coherente con el caso

El caso describe aproximadamente 16.000 registros en cada dataset, con 18 variables para Movies y 16 para TV Shows.

La ejecución real confirmó exactamente:

- Movies: **16.000 registros, 18 variables**.
- TV Shows: **16.000 registros, 16 variables**.

Esto aporta confianza respecto de que las fuentes cargadas corresponden a las fuentes esperadas por el caso.

No obstante, la coincidencia estructural no implica que todas las variables posean la calidad o semántica descrita en el diccionario.

---

# 7. Hallazgo 2 — `budget` y `revenue` correctamente restringidas a Movies

El caso establece explícitamente que:

- `budget` corresponde al presupuesto de producción;
- `revenue` corresponde a los ingresos generados;
- ambas variables están disponibles únicamente para películas.

La estructura real coincide:

- Movies contiene `budget` y `revenue`;
- TV Shows no contiene dichas columnas.

## Implicación

Los siguientes análisis de la EP1 deben realizarse **solo con Movies**:

- presupuesto vs. ingresos;
- presupuesto promedio;
- ingresos totales;
- ROI;
- películas con mayor retorno;
- películas con mayor ingreso.

## Recomendación para etapas posteriores

Antes del análisis financiero deberá investigarse:

- nulos;
- ceros;
- valores negativos;
- valores extremos;
- coherencia entre presupuesto e ingresos;
- interpretación de `0` en caso de que se use como marcador de información no disponible.

No debe asumirse automáticamente que un valor `0` significa un presupuesto o ingreso real de cero sin validación.

---

# 8. Hallazgo 3 — `type` es consistente

Se encontró:

- Movies: 16.000 registros con `type = Movie`.
- TV Shows: 16.000 registros con `type = TV Show`.

Esto coincide con el diccionario, que define `type` como una variable categórica con los valores `Movie` y `TV Show`.

## Implicación

Esta variable puede utilizarse posteriormente para construir la visualización requerida:

**Distribución de películas vs. series.**

---

# 9. Hallazgo 4 — `date_added` está completa, pero almacenada como texto

Según el caso, `date_added` debe representar una **fecha**.

Resultados observados:

| Fuente | Tipo actual | No nulos | Nulos | Interpretables como fecha | No interpretables |
|---|---|---:|---:|---:|---:|
| Movies | `str` | 16.000 | 0 | 16.000 | 0 |
| TV Shows | `str` | 16.000 | 0 | 16.000 | 0 |

Ejemplos:

- `2010-05-16`
- `2010-07-15`
- `2010-11-17`

## Interpretación

No existe un problema de disponibilidad y el formato observado parece consistente.

La única diferencia respecto del diccionario es que Pandas la carga como texto y no como `datetime`.

## Recomendación

En `feature/preparacion-catalogo`:

1. convertir `date_added` mediante `pd.to_datetime`;
2. conservar intacta la fuente RAW;
3. verificar nuevamente valores inválidos después de la conversión;
4. documentar el formato utilizado;
5. opcionalmente derivar `year_added`, `month_added`, etc., solo si esos campos son necesarios para el análisis.

No es recomendable sobrescribir los CSV originales.

---

# 10. Hallazgo 5 — `release_year` está correctamente disponible

Resultados en ambas fuentes:

- tipo: `int64`;
- nulos: **0**;
- valores únicos: **16**;
- mínimo: **2010**;
- máximo: **2025**.

## Contraste con el caso

El diccionario define `release_year` como el año oficial de estreno y el caso solicita análisis temporal de:

- estrenos por año;
- evolución del catálogo;
- tendencias.

La variable está estructuralmente disponible para estos fines.

## Observación metodológica

Todavía no se debe concluir que el catálogo "crece" o "disminuye" por año hasta realizar el análisis temporal correspondiente. En la exploración solo se comprobó la disponibilidad y rango.

---

# 11. Hallazgo 6 — `vote_average` cumple la regla 0–10

El caso define formalmente:

- `vote_average`: calificación promedio de los usuarios;
- escala: **0–10**.

Resultados:

| Fuente | Mínimo | Máximo | Nulos | Fuera de 0–10 |
|---|---:|---:|---:|---:|
| Movies | 0,0 | 10,0 | 0 | 0 |
| TV Shows | 0,0 | 10,0 | 0 | 0 |

## Conclusión

La variable cumple la regla de negocio documentada y está estructuralmente disponible para:

- calificación promedio;
- comparación de valoración;
- relación popularidad-calificación;
- contenidos mejor evaluados;
- valoración por género/país, una vez preparadas esas categorías.

## Nota

`vote_average` debe diferenciarse de `vote_count`:

- `vote_average` = promedio de calificación;
- `vote_count` = cantidad de evaluaciones recibidas.

---

# 12. Hallazgo 7 — Inconsistencia crítica en `rating`

Este es uno de los hallazgos más importantes de la exploración.

## Lo que dice el caso

El diccionario define:

- variable: `rating`;
- tipo: categoría;
- significado: **clasificación por edad**;
- ejemplos: `TV-MA`, `PG-13`, `R`, `TV-14`, `PG`.

Por otro lado:

- `vote_average` corresponde a la calificación promedio;
- debe estar en escala 0–10.

## Lo que contienen los datos

En ambas fuentes:

- `rating` es `float64`;
- `vote_average` es `float64`;
- los 16.000 registros comparables de Movies coinciden;
- los 16.000 registros comparables de TV Shows coinciden;
- porcentaje de coincidencia: **100%** en ambos datasets.

Por tanto:

**`rating` replica exactamente a `vote_average`.**

## Clasificación del problema

### Inconsistencia diccionario-datos

La variable `rating` no posee el significado que el diccionario declara.

### Limitación funcional

El caso solicita análisis por clasificación etaria, pero con la información entregada **no existe mediante `rating` una variable confiable que permita realizar ese análisis**.

## Recomendación

En `feature/calidad-datos`:

1. comprobar nuevamente la igualdad `rating == vote_average` como test reproducible;
2. documentar formalmente la inconsistencia;
3. no utilizar `rating` como clasificación etaria;
4. no inferir artificialmente clasificaciones;
5. no sustituir la variable con datos externos, dado que el caso indica trabajar con las fuentes proporcionadas;
6. mantener la limitación explícita en el informe ejecutivo y en cualquier visualización donde la clasificación etaria hubiera sido relevante.

### Decisión sugerida

Para análisis de valoración:

- utilizar `vote_average`.

Para clasificación etaria:

- indicar **"No disponible de forma confiable en las fuentes entregadas"**.

---

# 13. Hallazgo 8 — `duration` no es utilizable en su estado actual

El diccionario define `duration` como duración del contenido y entrega ejemplos como:

- `120 min`
- `3 Seasons`

## Movies

- total: 16.000;
- nulos: **16.000**;
- no nulos: **0**;
- porcentaje nulo: **100%**;
- valores únicos no nulos: **0**.

## TV Shows

- total: 16.000;
- nulos: **0**;
- no nulos: **16.000**;
- valores únicos no nulos: **1**;
- único valor observado: `1 Seasons`.

## Interpretación

Aunque la columna existe en ambos datasets, no posee utilidad analítica real:

- Movies: ausencia total de información;
- TV Shows: ausencia total de variabilidad.

## Recomendación

En `feature/calidad-datos`:

- clasificar `duration` como variable no apta para análisis comparativo;
- no imputar duración de películas;
- no inventar número de temporadas para series;
- documentar la limitación;
- excluir `duration` de KPIs o conclusiones donde la información no sea representativa.

Este hallazgo ejemplifica por qué **"columna presente" no equivale a "variable utilizable"**.

---

# 14. Hallazgo 9 — `show_id` tiene una diferencia de tipo respecto del diccionario

## Documentación

El caso define:

- `show_id`
- tipo: texto
- uso: clave primaria / identificador único.

## Datos observados

En ambas fuentes:

- tipo actual: `int64`.

## Interpretación

No necesariamente se trata de un dato incorrecto, pero su significado es de identificador, no de medida numérica.

## Recomendación

En `feature/calidad-datos` decidir explícitamente si se normalizará como texto en el dataset procesado.

La conversión a texto es razonable si:

- nunca se realizan operaciones matemáticas sobre el ID;
- se desea reforzar semánticamente su rol de identificador;
- se busca consistencia con el diccionario.

La decisión debe quedar documentada.

---

# 15. Hallazgo 10 — Señal de duplicidad de `show_id` en TV Shows

Resultados:

| Fuente | Registros | IDs únicos | Diferencia |
|---|---:|---:|---:|
| Movies | 16.000 | 16.000 | 0 |
| TV Shows | 16.000 | 15.991 | 9 |

## Contraste con el caso

El caso establece como regla:

**Cada registro representa un único contenido audiovisual.**

También define `show_id` como identificador único.

La diferencia detectada en TV Shows constituye una señal que debe investigarse antes de realizar conteos definitivos.

## Importante

La diferencia de 9 **no implica automáticamente que deban eliminarse 9 filas**.

Debe investigarse:

1. qué IDs se repiten;
2. cuántas veces se repite cada uno;
3. si las filas son idénticas;
4. si el mismo ID tiene títulos diferentes;
5. si existen diferencias en metadatos;
6. si puede tratarse de registros realmente duplicados o de una inconsistencia de identificación.

## Recomendación

No aplicar `drop_duplicates()` ciegamente.

Primero construir una tabla de auditoría de duplicados.

---

# 16. Hallazgo 11 — Nulos relevantes en `director` y `cast`

## Director

| Fuente | Nulos | Porcentaje |
|---|---:|---:|
| Movies | 132 | 0,825% |
| TV Shows | 10.965 | 68,531% |

## Cast

| Fuente | Nulos | Porcentaje |
|---|---:|---:|
| Movies | 204 | 1,275% |
| TV Shows | 1.157 | 7,231% |

## Contraste con el caso

El caso plantea preguntas como:

- ¿Qué directores poseen mayor cantidad de contenidos?
- ¿Qué actores aparecen con mayor frecuencia?

La disponibilidad de `director` en TV Shows es particularmente limitada.

## Implicación

Un ranking de directores de TV Shows basado únicamente en los registros no nulos describiría solo una fracción del catálogo.

No debe comunicarse como si representara al 100% de las series.

## Recomendación para calidad

Para `director` y `cast`:

- medir cobertura;
- no imputar nombres;
- conservar nulos cuando la información realmente falta;
- decidir si los nulos se muestran como "Sin información" solamente para visualización, sin convertirlos en una persona/categoría real;
- acompañar rankings con información de cobertura cuando sea relevante.

---

# 17. Hallazgo 12 — Variables potencialmente multivalor

Se utilizó la presencia de comas como señal diagnóstica. Este método no transforma los datos ni prueba por sí solo todos los casos posibles, pero evidencia que varias columnas contienen listas dentro de una misma celda.

## Resultados

| Variable | Movies: nulos | Movies: celdas con coma | TV Shows: nulos | TV Shows: celdas con coma |
|---|---:|---:|---:|---:|
| `country` | 466 | 4.058 | 1.797 | 1.307 |
| `genres` | 107 | 12.116 | 974 | 8.696 |
| `language` | 0 | 0 | 0 | 0 |
| `director` | 132 | 1.286 | 10.965 | 1.321 |
| `cast` | 204 | 15.632 | 1.157 | 13.353 |

## Implicación para `genres`

No sería correcto calcular géneros predominantes directamente con:

```python
df["genres"].value_counts()
```

porque cadenas como:

- `Action, Adventure`
- `Drama, Comedy`
- `Comedy, Drama`

se tratarían como categorías completas diferentes.

## Implicación para `country`

El caso define `country` como "país o países asociados a la producción".

Por tanto, múltiples países en una celda son esperables y deben tratarse correctamente antes del análisis geográfico.

## Implicación para `director` y `cast`

Un contenido puede incluir:

- múltiples directores;
- múltiples actores.

Para contar presencia individual será necesario separar los valores.

## `language`

No se detectaron comas con el separador analizado.

Esto **no debe interpretarse como una garantía absoluta de que nunca exista otra forma de multivalor**, pero no existe evidencia actual que justifique separarlo como lista.

---

# 18. Hallazgo 13 — Variables necesarias para EP1 están estructuralmente presentes

Se comprobó la presencia de:

- `type`
- `country`
- `release_year`
- `genres`
- `language`
- `popularity`
- `vote_average`
- `vote_count`
- `budget`
- `revenue`

Esto cubre estructuralmente las principales áreas solicitadas:

### Caracterización

- películas vs. series;
- géneros;
- países;
- idiomas.

### Popularidad y valoración

- popularidad;
- calificación;
- cantidad de votos.

### Temporal

- año de estreno;
- fecha de incorporación.

### Financiero

- presupuesto;
- ingresos.

No obstante:

> La presencia estructural de una variable no garantiza su disponibilidad, calidad ni comparabilidad.

La clasificación etaria y `duration` son ejemplos claros de esta limitación.

---

# 19. Consideraciones importantes provenientes del caso

## `popularity`

El caso indica que `popularity`:

- es un índice relativo;
- no representa cantidad de reproducciones.

Por tanto, en gráficos e informe debe evitarse lenguaje como:

> "esta película tuvo X reproducciones"

si el dato utilizado es `popularity`.

Debe hablarse de:

> "índice de popularidad".

## `vote_average`

Se interpreta en escala 0–10.

## Finanzas

Los contenidos sin información válida de presupuesto o ingresos no deben formar parte de los indicadores financieros.

## Movies vs. TV Shows

Solo deben compararse cuando las variables sean realmente equivalentes.

## Variables no disponibles

Cuando una variable no esté disponible o sea insuficiente para un tipo de contenido, debe:

- excluirse del análisis correspondiente; o
- indicarse explícitamente la limitación.

Esto respalda directamente la decisión de no inventar información para `rating` o `duration`.

---

# 20. Impacto sobre las visualizaciones obligatorias de EP1

## 20.1 Películas vs. series

Estado:

**Viable.**

La variable `type` es consistente.

---

## 20.2 Géneros predominantes

Estado:

**Viable después de preparación.**

Antes deben separarse los géneros multivalor.

---

## 20.3 Análisis geográfico

Estado:

**Viable después de preparación.**

Debe tratarse correctamente `country` cuando contiene múltiples países y considerar sus nulos.

---

## 20.4 Idiomas

Estado:

**Viable preliminarmente.**

`language` está completa y no muestra señal de coma en la exploración actual.

Aun así, en calidad deben revisarse:

- códigos;
- mayúsculas/minúsculas;
- valores inesperados;
- categorías equivalentes.

---

## 20.5 Popularidad

Estado:

**Estructuralmente viable.**

Debe revisarse en calidad:

- nulos;
- valores negativos;
- outliers;
- distribución.

Nunca interpretar como reproducciones.

---

## 20.6 Popularidad vs. calificación

Estado:

**Estructuralmente viable.**

`vote_average` cumple 0–10.

Debe revisarse:

- outliers de `popularity`;
- distribución de `vote_count`;
- posibles registros con `vote_count = 0`;
- interpretación responsable.

---

## 20.7 Evolución histórica

Estado:

**Viable.**

`release_year` está completo entre 2010–2025.

`date_added` es completa e interpretable, pero debe convertirse a fecha en la preparación.

---

## 20.8 Presupuesto vs. ingresos

Estado:

**Solo Movies.**

Antes debe realizarse control de calidad financiero.

---

## 20.9 ROI

Estado:

**Solo Movies.**

Debe realizarse después del filtrado financiero y evitando divisiones por presupuesto no válido o cero.

---

## 20.10 Clasificación etaria

Estado:

**No reproducible de forma confiable con `rating`.**

Debe documentarse como limitación de la fuente.

---

# 21. Riesgos de calidad identificados

| Riesgo | Severidad sugerida | Motivo |
|---|---|---|
| `rating` no corresponde al diccionario | Alta | Bloquea análisis de clasificación etaria |
| `duration` inutilizable | Alta para análisis de duración | 100% nula en Movies y constante en TV |
| IDs repetidos en TV Shows | Alta | Puede alterar conteos y KPIs |
| `director` nulo en 68,531% de TV Shows | Alta para análisis de directores | Cobertura insuficiente |
| Multivalor sin normalizar en `genres` | Alta | Afecta visualización obligatoria |
| Multivalor sin normalizar en `country` | Alta | Afecta análisis geográfico obligatorio |
| Multivalor en `cast` | Media | Afecta análisis de actores posterior |
| Multivalor en `director` | Media | Afecta conteos individuales |
| `show_id` como entero | Baja/Media | Problema semántico, no necesariamente de contenido |
| `date_added` como texto | Baja | Es completa y convertible |

---

# 22. Siguiente branch propuesta — `feature/calidad-datos`

## Objetivo

Realizar una auditoría completa y reproducible de calidad de ambos datasets, definiendo decisiones justificadas sin alterar las fuentes RAW.

La branch debe responder:

> ¿Qué problemas reales de calidad existen y cuál será la política de tratamiento para cada uno?

No debe convertirse todavía en la branch de visualizaciones ni storytelling.

---

# 23. Orden recomendado para `feature/calidad-datos`

## Fase 1 — Perfil general de calidad

Para cada dataset generar un resumen por columna con:

- tipo;
- total de registros;
- nulos;
- porcentaje de nulos;
- cantidad de valores únicos;
- ejemplos;
- mínimo/máximo para numéricas;
- cardinalidad para categóricas.

### Producto

Una tabla de auditoría central que permita identificar rápidamente qué variables requieren tratamiento.

---

## Fase 2 — Auditoría de valores nulos

El requerimiento de EP1 exige tratamiento de valores nulos.

### Revisar todas las columnas

No limitarse a `director`, `cast` y `duration`.

Clasificar variables por nivel de impacto:

### Críticas para EP1

- `type`
- `country`
- `genres`
- `language`
- `release_year`
- `date_added`
- `popularity`
- `vote_average`
- `vote_count`
- `budget`
- `revenue`

### Complementarias

- `director`
- `cast`
- `description`
- `duration`

### Para cada variable decidir

- conservar nulo;
- excluir registro únicamente del análisis donde sea necesario;
- utilizar etiqueta "Sin información" para fines visuales, si procede;
- no imputar cuando no existe una base razonable.

### Recomendación

Evitar imputaciones artificiales como:

```python
director = "Director desconocido"
```

si luego esa categoría será contada como si fuera un director real.

Una etiqueta de presentación puede ser válida, pero debe distinguirse de una imputación analítica.

---

# 24. Fase 3 — Duplicados

El requerimiento exige revisar registros duplicados.

Deben realizarse **dos auditorías distintas**.

## 24.1 Duplicados exactos

```python
df.duplicated()
```

## 24.2 Duplicados por identificador

```python
df["show_id"].duplicated()
```

Para los IDs repetidos en TV Shows construir una tabla que permita comparar:

- `show_id`;
- `title`;
- `type`;
- `release_year`;
- `director`;
- `country`;
- `genres`;
- `popularity`;
- `vote_average`;
- demás campos relevantes.

### Decisión

Solo eliminar cuando exista una justificación.

Casos posibles:

1. filas completamente idénticas → candidato fuerte a deduplicación;
2. mismo ID con diferencias menores → investigar;
3. mismo ID con títulos diferentes → inconsistencia de identificación;
4. mismo contenido con IDs distintos → requiere una regla diferente.

---

# 25. Fase 4 — Tipos y formatos

El requerimiento exige revisar inconsistencias de tipos y formatos.

## `show_id`

Decidir si el dataset procesado lo almacenará como texto.

## `date_added`

Validar formalmente conversión a fecha, pero aplicar la conversión definitiva en `feature/preparacion-catalogo`.

## `rating`

Marcar como inconsistente con el diccionario.

## `release_year`

Verificar que todos los valores sean enteros válidos dentro del rango observado.

## Texto/categorías

Revisar:

- espacios al inicio/final;
- mayúsculas/minúsculas;
- cadenas vacías;
- valores equivalentes con distintas escrituras;
- separadores;
- codificación.

No normalizar categorías sin dejar la regla documentada.

---

# 26. Fase 5 — Variables categóricas y multivalor

En calidad debe determinarse **cómo están representadas**, sin realizar todavía todos los conteos finales.

Revisar:

- `country`
- `genres`
- `language`
- `director`
- `cast`

Preguntas:

- ¿el separador es siempre coma?
- ¿existen espacios inconsistentes?
- ¿hay categorías vacías?
- ¿hay duplicados dentro de una misma celda?
- ¿hay variantes ortográficas evidentes?
- ¿existen valores inesperados?

### Resultado esperado

Definir reglas para `feature/preparacion-catalogo`, por ejemplo:

1. separar por coma;
2. aplicar `strip()`;
3. mantener una tabla explotada por variable;
4. conservar también la versión original para trazabilidad.

---

# 27. Fase 6 — Fechas

Aunque `date_added` pasó la validación preliminar, el Caso Semestral exige revisar fechas.

Validar:

- formato;
- fechas inválidas;
- rango temporal;
- coherencia respecto de `release_year`.

Una validación útil sería comprobar si existen casos donde:

`date_added` sea anterior al año de estreno.

No debe asumirse que esto es imposible sin revisar el significado del campo, pero cualquier caso debe documentarse.

---

# 28. Fase 7 — Outliers / valores atípicos

El requerimiento de EP1 los exige explícitamente.

Revisar como mínimo:

- `popularity`
- `vote_average`
- `vote_count`
- `budget`
- `revenue`

## Metodología sugerida

Combinar:

- estadísticas descriptivas;
- percentiles;
- IQR;
- boxplots diagnósticos;
- validaciones de dominio.

## Importante

**Outlier no significa error.**

Una película extremadamente popular o con ingresos muy elevados puede ser perfectamente válida.

No eliminar automáticamente valores porque estén fuera de:

`Q1 - 1.5 × IQR` o `Q3 + 1.5 × IQR`.

Cada tratamiento debe justificar:

- por qué se considera error;
- por qué se conserva;
- si se limita solo la escala visual;
- si se utiliza transformación logarítmica para visualizar;
- si se excluye de un cálculo específico.

---

# 29. Fase 8 — Coherencia financiera

El Caso Semestral exige revisar coherencia entre presupuesto e ingresos.

Solo Movies.

Validar:

- nulos en `budget`;
- nulos en `revenue`;
- valores negativos;
- valores cero;
- frecuencia de ceros;
- valores extremos;
- relación general budget/revenue;
- registros donde no exista información financiera útil.

## Regla del caso

Los contenidos sin información de presupuesto o ingresos no deben considerarse en indicadores financieros.

## Punto crítico

Debe definirse si `0` representa realmente:

- valor financiero cero; o
- información no disponible codificada como cero.

No decidirlo sin evidencia.

Esta decisión impactará directamente:

- presupuesto promedio;
- ingresos totales;
- presupuesto vs. ingresos;
- ROI.

---

# 30. Fase 9 — Registro de decisiones de calidad

Crear una tabla/documento del estilo:

| Variable | Problema | Evidencia | Decisión propuesta | Justificación | Branch donde se aplica |
|---|---|---|---|---|---|
| `rating` | Semántica incorrecta | Igual a vote_average | Excluir de clasificación etaria | Contradice diccionario | calidad/preparación |
| `show_id` | Tipo entero | Diccionario: texto | Convertir a string | Es identificador | preparación |
| `date_added` | Texto | 100% parseable | Convertir a datetime | Campo temporal | preparación |
| `duration` | Sin información útil | Movies nulo; TV constante | Excluir de análisis | No representa variación | calidad |
| `genres` | Multivalor | Comas en miles de registros | Separar y explotar | Necesario para conteos | preparación |

Este registro es especialmente valioso porque la documentación del caso exige **justificar las transformaciones realizadas**.

---

# 31. Qué NO hacer en `feature/calidad-datos`

No:

- modificar `data/raw/`;
- inventar datos faltantes;
- reconstruir clasificación etaria;
- buscar fuentes externas para completar `rating`;
- eliminar outliers automáticamente;
- eliminar IDs repetidos sin inspeccionarlos;
- calcular KPIs definitivos;
- hacer storytelling;
- generar los gráficos finales de EP1;
- producir conclusiones estratégicas antes de preparar los datos.

---

# 32. Artefactos recomendados para `feature/calidad-datos`

## Notebook

`notebooks/02_limpieza_preparacion.ipynb`

Durante esta branch puede utilizarse principalmente para:

- auditoría;
- diagnóstico;
- documentación de decisiones.

La aplicación sistemática de transformaciones puede terminarse en `feature/preparacion-catalogo`.

## Código reutilizable

`src/data_cleaning.py`

Posibles funciones:

```python
def quality_profile(df):
    ...

def null_summary(df):
    ...

def duplicate_summary(df, id_column="show_id"):
    ...

def validate_numeric_range(series, min_value=None, max_value=None):
    ...

def outlier_iqr_summary(series):
    ...

def categorical_quality_summary(series):
    ...
```

No hace falta sobreingeniería. Las funciones deben existir solo si reducen duplicación entre Movies y TV Shows.

## Documentación

Recomendado:

`docs/calidad_datos_decisiones.md`

para registrar políticas finales de tratamiento.

---

# 33. Criterios de salida de `feature/calidad-datos`

La branch puede considerarse terminada cuando:

- [ ] se haya generado un perfil completo de nulos para ambos datasets;
- [ ] se hayan revisado duplicados exactos;
- [ ] se hayan investigado los `show_id` repetidos;
- [ ] se hayan documentado inconsistencias de tipos;
- [ ] se hayan revisado formatos categóricos;
- [ ] se haya validado la calidad de fechas;
- [ ] se hayan detectado outliers en variables numéricas relevantes;
- [ ] se haya evaluado la coherencia financiera de Movies;
- [ ] exista una decisión explícita para `rating`;
- [ ] exista una decisión explícita para `duration`;
- [ ] exista una decisión para el tipo de `show_id`;
- [ ] exista una política para nulos de `director` y `cast`;
- [ ] se hayan documentado las variables multivalor;
- [ ] ninguna fuente RAW haya sido modificada;
- [ ] las decisiones de tratamiento estén justificadas;
- [ ] quede claro qué transformaciones se aplicarán en `feature/preparacion-catalogo`.

---

# 34. Handoff esperado a `feature/preparacion-catalogo`

Una vez cerrada calidad, la siguiente branch debería ejecutar las transformaciones aprobadas.

Posibles tareas:

- conversión de `date_added`;
- conversión semántica de `show_id` a texto;
- estandarización de strings;
- tratamiento acordado de nulos;
- separación de `country`;
- separación de `genres`;
- preparación de `director`;
- preparación de `cast`;
- construcción de tablas auxiliares explotadas;
- consolidación de columnas comunes Movies/TV Shows;
- generación de datasets procesados reproducibles.

La regla debe ser:

**primero decidir y justificar en calidad → luego transformar en preparación.**

---

# 35. Handoff posterior a visualizaciones

Después de preparar correctamente los datos, podrán construirse de forma confiable las visualizaciones obligatorias:

- películas vs. series;
- géneros predominantes;
- análisis geográfico;
- idiomas;
- comparación de popularidad;
- popularidad vs. calificación;
- evolución histórica;
- presupuesto vs. ingresos;
- ROI.

Cada gráfico deberá apoyar preguntas de negocio, no existir solo porque "se podía graficar".

---

# 36. Implicaciones para el informe ejecutivo y storytelling

La EP1 requiere que el storytelling responda:

1. ¿Qué está ocurriendo?
2. ¿Por qué ocurre?
3. ¿Qué evidencia lo demuestra?
4. ¿Qué decisiones deben tomarse?

Los hallazgos de calidad no constituyen todavía el storytelling central de negocio, pero sí deben influir en la interpretación.

Ejemplos:

- no presentar análisis de clasificación etaria como si fuera válido;
- no comparar duración Movies vs. TV Shows;
- explicar cobertura limitada si se presenta un ranking de directores de TV Shows;
- no interpretar `popularity` como reproducciones;
- no incluir películas sin información financiera válida en ROI;
- documentar cuándo una visualización excluye registros por falta de información.

La transparencia respecto de estas limitaciones fortalece el informe, porque evita conclusiones engañosas.

---

# 37. Trazabilidad contra los documentos del proyecto

## Caso Semestral — Sección 14: Diccionario de Datos

Usada para contrastar:

- `show_id`;
- `rating`;
- `date_added`;
- `release_year`;
- `duration`;
- `popularity`;
- `vote_average`;
- `budget`;
- `revenue`.

## Caso Semestral — Sección 15: Calidad de los Datos

Sustenta la revisión de:

- nulos;
- duplicados;
- formatos;
- categorías;
- fechas;
- outliers;
- coherencia financiera;
- disponibilidad parcial.

## Caso Semestral — Sección 16: KPIs

Orienta las variables que deben quedar utilizables para análisis posteriores.

## Caso Semestral — Sección 17: Preguntas de Negocio

Justifica la necesidad de preparar correctamente:

- géneros;
- países;
- idiomas;
- popularidad;
- valoración;
- directores;
- actores;
- finanzas.

## Caso Semestral — Sección 18: Reglas de Negocio

Relevante para:

- comparabilidad Movies vs. TV Shows;
- uso exclusivo de budget/revenue en Movies;
- escala 0–10 de vote_average;
- interpretación de popularity;
- exclusión de información financiera no disponible;
- declaración explícita de limitaciones.

## Caso Semestral — Etapa 1 / EP1

La primera evaluación corresponde a:

**Comprensión del Negocio y Exploración Visual**

y espera:

- comprensión del contexto;
- stakeholders;
- objetivos de comunicación;
- exploración;
- primeras visualizaciones;
- storytelling inicial;
- informe ejecutivo con narrativa visual.

## Requerimientos Entrega 1

Exigen específicamente:

- preparación de datos;
- tratamiento de nulos;
- duplicados;
- tipos/formatos;
- outliers;
- reglas de negocio;
- visualizaciones;
- storytelling;
- GitHub;
- documentación técnica;
- informe;
- presentación.

---

# 38. Conclusión general

La exploración inicial demuestra que las fuentes poseen una estructura suficiente para continuar con gran parte de la EP1, pero también revela diferencias importantes entre la documentación y los datos reales.

Los principales puntos que deben considerarse antes de cualquier análisis definitivo son:

1. **`rating` no representa clasificación etaria** y replica `vote_average`.
2. **La clasificación etaria solicitada por el caso no puede reproducirse confiablemente con las fuentes entregadas.**
3. **`duration` carece de utilidad analítica** en su estado actual.
4. **TV Shows presenta una señal de duplicidad de `show_id`** que debe investigarse.
5. **`director` posee una disponibilidad extremadamente baja en TV Shows.**
6. **`country`, `genres`, `director` y `cast` requieren una estrategia de variables multivalor.**
7. **`date_added` es usable, pero requiere conversión documentada.**
8. **`release_year` y `vote_average` cumplen las validaciones preliminares realizadas.**
9. **Los análisis financieros deben limitarse a Movies y requieren auditoría específica.**
10. **Todas las decisiones de tratamiento deben quedar justificadas antes de construir visualizaciones y KPIs.**

Por tanto, el paso siguiente no debería ser generar gráficos inmediatamente, sino ejecutar una auditoría completa en:

`feature/calidad-datos`

y dejar allí definido, con evidencia, **qué se corrige, qué se conserva, qué se excluye y qué limitaciones deben comunicarse**.

---

# 39. Estado de trazabilidad

**Exploración inicial:** completada.  
**Datos RAW modificados:** no.  
**Datos procesados generados:** no.  
**Transformaciones definitivas:** no.  
**Siguiente etapa:** `feature/calidad-datos`.  
**Etapa posterior:** `feature/preparacion-catalogo`.

---

## Referencias documentales

1. **Caso_Semestral_STREAMVIEW_ANALYTICS.pdf**
   - Descripción de fuentes y diccionario de datos: secciones 13–14.
   - Calidad de datos: sección 15.
   - KPIs: sección 16.
   - Preguntas de negocio: sección 17.
   - Reglas de negocio: sección 18.
   - Evaluación Parcial 1: sección 21.
   - Requerimientos técnicos y storytelling: sección 23.

2. **REQUERIMIENTOS ENTREGA EXPERIENCIA 1.pdf**
   - Codificación y preparación de datos.
   - Reglas de negocio.
   - Visualizaciones requeridas.
   - Storytelling.
   - GitHub / GitFlow / GitHubFlow.
   - Informe ejecutivo y presentación.

3. **notebooks/01_exploracion_datos.ipynb**
   - Evidencia reproducible de los hallazgos documentados en este archivo.

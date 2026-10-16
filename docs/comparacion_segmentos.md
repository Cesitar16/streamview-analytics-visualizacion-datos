# Mejoras analíticas: evolución temporal y comparador de géneros

## Propósito

Estas mejoras fortalecen la lectura ejecutiva del catálogo sin cambiar las reglas de preparación de EP1. La serie temporal permite contrastar películas y series para cada año registrado; el comparador ayuda a evaluar dos géneros bajo la misma selección global.

## Evolución temporal

La visualización de líneas usa una fila por combinación de `release_year` y `type`, con conteo de `content_id` únicos. Se eligió una línea con marcadores porque facilita comparar ambos tipos de contenido a lo largo de los años y permite inspeccionar el valor puntual mediante el tooltip.

La fuente disponible equipara el año de incorporación con `release_year`. Por ello el título y la nota del gráfico hablan de **distribución anual registrada**: no se interpreta como historial real de altas del catálogo ni como una tendencia de mercado.

## Comparador de géneros

El componente se ubica en **Panorama del catálogo** y responde a los filtros generales de tipo, año y género. Sus dos selectores comparan géneros y muestran:

- títulos únicos;
- películas y series;
- popularidad mediana, solo cuando el contenido pertenece a `catalogo_popularity`;
- calificación media y cantidad de contenidos con votos; y
- variación de Género A menos Género B.

Un contenido puede tener más de un género. Cada segmento se selecciona mediante una semi-unión por `content_id`, por lo que no duplica títulos. Los segmentos pueden superponerse y sus totales no deben sumarse para inferir el total del catálogo.

## Verificación

Ejecutar desde la raíz:

```powershell
uv run --locked python -m unittest tests.test_segment_comparison -v
uv run --locked python -m unittest discover -s tests -v
```

Las pruebas comprueban conciliación anual, ausencia de duplicados por campos multivalor, respeto de filtros globales, exclusión de popularidad no confiable, escala de calificación y conjuntos vacíos.

# Conciliación financiera para EP2

Los dos CSV oficiales ubicados en `data/raw/` son la fuente de cálculo de esta etapa. Se mantienen intactos. La regla usada en EP1 y EP2 es `budget > 0 AND revenue > 0`, aplicada solo a Movies. El cálculo se verificó mediante `build_catalog_views` y, de manera independiente, con una suma directa sobre el CSV de películas.

| Medida | Recalculada desde RAW para EP2 | Escrita en la documentación EP1 | Diferencia EP2 − EP1 |
|---|---:|---:|---:|
| Películas elegibles | 3.540 | 3.540 | 0 |
| Presupuesto total | 125.960.767.278 | 125.960.770.871 | −3.593 |
| Ingresos totales | 367.371.433.138 | 367.371.370.178 | +62.960 |

La nota final del informe EP1 reconoce una discrepancia entre reconstrucción local y valor documentado, y opta por el valor versionado. Para EP2 se emplea el cálculo reproducible de los CSV presentes, no la cifra transcrita en el documento anterior. La causa histórica de la discrepancia no puede determinarse con el repositorio actual; no se modifica el informe EP1.

**Alcance:** las sumas corresponden al subconjunto elegible de 3.540 de 16.000 películas (22,125 %). El multiplicador de cartera `sum(revenue) / sum(budget)` es aproximadamente 2,9166×. El **ROI bruto aproximado agregado** es `((sum(revenue) - sum(budget)) / sum(budget))`, equivalente a **191,6554 %**. Son indicadores relacionados, pero tienen unidades distintas: el primero se expresa en veces y el segundo en porcentaje. Ninguno representa utilidad neta.

**Limitación de moneda:** los CSV contienen números sin una columna de divisa. La documentación EP1 presenta `budget` y `revenue` como USD; EP2 conserva esa convención y debe declararla como supuesto de presentación.

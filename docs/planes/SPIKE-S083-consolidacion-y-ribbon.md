# SPIKE S083 — Factibilidad de las 2 piezas riesgosas del Eje 2 (antes de tocar el CORE)

> **Qué es:** Paso 0 (de-risking) del arranque del ESQUELETO-FABLE. Análisis de factibilidad anclado al código real de `SMC-Visual.pine` (3790 líneas), NO producción. Objetivo: confirmar que los pasos 5–6 del §11.2 no van a descubrir un muro DESPUÉS de construir el motor strength en el CORE (pasos 1–2).
> **Método:** inspección del modelo de objetos Pine ya usado en el archivo + los caps reales del `indicator()`.
> **Veredicto global:** ✅ ambas piezas FACTIBLES. La preocupación de perf se DEGRADA (no es riesgo de perf; es costo de refactor). Un hallazgo reordena el plan (§4).

---

## §1 — Hallazgo base que cambia la evaluación

**Todo el dibujo de Visual ya corre bajo el patrón `if i_show* and barstate.islast:` → borrar objetos previos → reconstruir desde arrays.** (Verificado: ~40 bloques con `barstate.islast` + `for x in SMC_*Labels: label.delete(x)` seguido de `array.push`.)

Consecuencia directa sobre el gate de 20k barras (§10-11):
- El dibujo **NO se ejecuta 20.000 veces.** Corre UNA vez por barra en tiempo real (y una al terminar de cargar el histórico). El costo pesado de 20k barras es la **detección** (`f_detect*` en el CORE), que YA pasó el gate de perf en S057.
- Por lo tanto, cualquier post-proceso de dibujo (consolidación, presupuesto global, ribbon) se paga **una vez por render**, acotado por el cap de 500 objetos — no por la profundidad del histórico.

**Esto degrada la preocupación #2 de la revisión** ("perf de la consolidación llega tarde"): la consolidación no multiplica contra las 20k barras. El riesgo real no es perf; es el **refactor** (§2.3).

Caps actuales (línea 5): `max_labels_count = 500, max_lines_count = 500, max_boxes_count = 500`. El presupuesto global del esqueleto (§6.5: 60/150/400 objetos) vive **por debajo** de estos caps → no hay que subirlos; el desalojo determinista corta antes.

---

## §2 — Pieza 1: Consolidación de etiquetas (§6.2)

### 2.1 Factibilidad del modelo de objetos: ✅
Pine permite recolectar candidatos en `var array<...>` durante el cálculo y emitir en `barstate.islast`. El archivo YA lo hace por familia. La consolidación es un post-pass sobre el conjunto de labels pendientes: recolectar → ordenar por precio → clusterizar (ventana `labelClusterTol×ATR`) → emitir 1 label combinada por cluster. Con ≤500 labels, un clustering O(n log n) por render es trivial (milisegundos, una vez).

### 2.2 Costo real de perf: BAJO
Corre una vez por barra de render, no por barra histórica (§1). Sin riesgo contra el gate 20k.

### 2.3 Costo real = REFACTOR (este es el trabajo, no la perf)
Hoy **cada familia borra+redibuja su propio array de labels de forma independiente** (SMC_poolLabels, SMC_sweepLabels, SMC_dispLabels, SMC_idmLabels, …). Para consolidar ETIQUETAS ENTRE FAMILIAS (el arreglo del amontonamiento en 1.14, que mezcla OB·FVG·BPR) hay que:
1. Cambiar de "cada familia emite sus labels" a "cada familia PUSHEA a un buffer unificado de labels pendientes" (`SMC_pendingLabels` con {precio, texto, capa, strength, tf}).
2. Un único post-pass al final del bloque de dibujo clusteriza y emite.
- Es tocar los ~40 bloques de dibujo (los mismos que el paso 5 reordena a capas L0→L4). **Trabajo real, acotado y mecánico**, pero es la pieza de más líneas del esqueleto (el propio §6.2 lo marca).

### 2.4 Recomendación
Hacer **paso 5 (reorden a capas) y paso 6 (consolidación) como UN solo reestructurado** del bloque de dibujo — ambos reescriben los mismos 40 bloques; separarlos duplica el churn. (Ajuste al orden §11.2, ver §4.)

---

## §3 — Pieza 2: Ribbon de Kill Zones (§F9)

### 3.1 El problema confirmado
KZ hoy = `bgcolor(i_showKZ and curKZ != KZ_NONE ? color.new(..., 90) : na)` (línea 3375). `bgcolor()` pinta la **franja vertical completa** por cada barra de la sesión → es exactamente el "fondo de área" que colisiona con el grid Gradient (§0.2-4). Macros (2385) y RTH (2391) usan el mismo patrón.

### 3.2 Factibilidad del reemplazo: ✅ (fiddly, no bloqueante)
El "ribbon" (tira delgada en el borde, no full-height) necesita un ancla de precio superior. Opciones evaluadas contra el modelo Pine:
- **A — `box` delgado anclado a top-of-visible:** en `barstate.islast`, `ta.highest(high, lookback)` da un precio cercano al techo visible; el box abarca la ventana temporal de la sesión en X y una franja fina (≈0.5×ATR) en Y desde ese techo. Alineado al eje de tiempo. **Recomendado.** El "máximo visible" SÍ es obtenible en islast (desmiente la preocupación #6 de la revisión como bloqueante — es fiddly, no imposible).
- **B — `table` de celdas arriba:** posición de pantalla fija; se descarta como ribbon principal porque NO se alinea al eje de tiempo (la sesión es un tramo temporal). Sirve para el estado en panel, no para la tira.
- **Mantener `bgcolor` SOLO en modo Estudio** sobre la KZ activa (§F9 ya lo dice): en Operación → ribbon (A); en Estudio → + bgcolor ultra-tenue (≥92 transp) solo la KZ en curso.

### 3.3 Costo
Bajo. Reescribir 1 llamada `bgcolor` → 1 bloque de box en islast (reusa el patrón delete+rebuild ya presente). Perf trivial (1 box vs fill por barra — de hecho MÁS barato que bgcolor histórico).

---

## §4 — Impacto en el orden de implementación §11.2

Ajustes recomendados (no cambian el conjunto de pasos, solo su agrupación y 2 notas):

1. **Fusionar pasos 5 y 6** en un solo reestructurado del bloque de dibujo (reorden L0→L4 + buffer unificado de labels + consolidación + ribbon + grid sin fill). Razón: reescriben los mismos 40 bloques (§2.3, §3.2).
2. **Ribbon (§F9) entra en ese reestructurado**, no como afterthought: cambiar `bgcolor` KZ/macros/RTH a box-ribbon + gate por modo.
3. **Pasos 1–2 (CORE strength) siguen primero e intactos** — son ortogonales al refactor de dibujo y ya cubiertos por ADR-014.
4. **`f_strongestN` como variante nueva** (no mutar `f_nearestN`, validado S057) al cablear el orden del top-N (§2.5) — nota ya en ADR-014.
5. **Paso 9 verifica Ejes 0/1/3 además del Eje 2** (el overhaul de dibujo puede regresar presencia/variante/invalidación) — nota ya en ADR-014.

---

## §5 — Conclusión del Paso 0

| Pregunta del de-risking | Respuesta |
|---|---|
| ¿La consolidación es un riesgo de perf contra el gate 20k? | **No.** El dibujo corre en `barstate.islast`, no por barra histórica. Es costo de refactor, acotado por el cap de 500. |
| ¿El ribbon es factible en el modelo de objetos Pine? | **Sí** (opción A: box anclado a `ta.highest` en islast). Fiddly, no bloqueante. |
| ¿Hay que subir los caps `max_*_count`? | **No.** El presupuesto global (60/150/400) vive bajo los 500 actuales. |
| ¿Se puede tocar el CORE (pasos 1–2) con seguridad? | **Sí** — ADR-014 fija la frontera; ninguna sorpresa de dibujo lo condiciona. |
| ¿Cambia el plan? | Solo agrupación: fusionar pasos 5–6, ribbon dentro del refactor. Conjunto de pasos intacto. |

**Ambos spikes vuelven verdes. Vía libre a los pasos 1–2 (motor strength en el CORE).**

# BUGS-VISUAL — Revisión para Fable

> **Objetivo.** Recopilar los bugs detectados durante la **validación viva del F1-GATE** (Sesión 099, 2026-07-06) para que **Fable** los revise a fondo e indique **cómo arreglarlos** (root cause + parche propuesto), respetando las reglas duras del proyecto. Documento vivo: se le añaden bugs a medida que se validan las familias una por una en modo Operación.
>
> **Fuente de verdad SMC:** [`docs/reglas-smc-ict.md`](../reglas-smc-ict.md) (§1–§7). **Arquitectura:** 1 CORE byte-idéntico + Visual + Strategy. **NO tocar** la lógica de detección salvo que el bug esté ahí; la mayoría son de la **capa de dibujo** (`SMC-Visual.pine`).

---

## Contexto de la validación

- **Escenario:** OANDA:EURUSD, indicador `SMC Engine — Visual` (`SMC-Visual.pine`, commit `8618cc3`, Fase A A-7). Modo **Operación** (`i_densidad="Operación"`, input `in_123`).
- **CORE:** 1700 líneas, SHA `5510361166844bd5`, compila 0/0, core-sync OK. **Los bugs están en Visual, no en el CORE.**
- **Método:** familia por familia (apagar el resto → encender), leyendo panel T14 + `data_get_pine_boxes/lines/labels` + screenshots.
- **Densidad `in_123`:** {`Operación`, `Estudio`, `Todo`}. En **Estudio/Todo** las zonas SÍ dibujan; el bug se manifiesta en **Operación**.

---

## BUG #1 — Las zonas NATIVAS del TF no dibujan en Operación (solo dibujan las MTF-heredadas) 🔴 BLOQUEA F1-GATE

**Severidad:** alta. Es sistémico: afecta OB, FVG (y presumiblemente Breaker y toda caja nativa). Deja Operación **casi vacía de zonas** — que NO es el objetivo ("limpio" sí, "vacío" no).

### Síntoma
En modo **Operación**, en **cualquier TF**, las cajas de zonas **nativas del propio TF NO se dibujan**. Solo se dibujan las **heredadas MTF** (`H1:`/`D1:`):
- **H1:** solo aparecen cajas `D1:` (heredadas). Ninguna nativa H1. `data_get_pine_boxes` = 2 boxes, ambas MTF D1 (~1.16).
- **M5:** aparecen `H1:` y `D1:` (heredadas). **Ninguna nativa M5.**
- El panel T14 sí reporta "OB cercano / FVG cercano" nativos, pero **no hay caja correspondiente en el chart**.

### Evidencia de que las zonas son ACTIVAS (no mitigadas — el estado está bien)
- El OB cercano H1 **[1.14483, 1.14622]** = rango exacto de la vela **04-jul ~21:00** (`1783058400`: O1.14488 H1.14622 L1.14483 C1.14542).
- Datos OHLCV: tras crearse, **ningún máximo posterior volvió a 1.14622** (máx ≈1.14584) → por §2.1 debería estar **ACTIVO**.
- **Prueba concluyente:** el transporte MTF `f_nearestN` (línea ~1584) **solo toma zonas con `state < ZS_MITIGATED`** (activas/parciales). Ese mismo OB **se dibuja como "H1: OB" en M5** ⟹ es activo/parcial. La máquina `f_updateZoneMitigation` coincide con la regla §2.1 (mitigar = mecha alcanza borde lejano; 50%=parcial; cierre fuera=inválido). **El bug NO es de estado.**

### Localización (capa de dibujo)
- **Ruta NATIVA (falla):** `f_drawOB` (línea ~3742) y `f_drawFVG` (línea ~3969). Gate:
  `z.kind == KIND_OB and z.state != ZS_INVALID and (f_densOK(z.strength, isAnchor) or f_isBandPick(i, 0, z.top, z.bottom))`.
  En Operación `f_densOK` es estricto (`densMin` alto) → el dibujo depende de **`f_isBandPick`**.
- **Ruta MTF (funciona):** `f_drawMTFZones` (línea ~4054) — NO pasa por band-pick → por eso las heredadas sí dibujan.
- **Sospechoso:** la **población band-pick** `bandPickIdx`/`bandPickScore` (líneas ~2886–2942, en `barstate.islast`) no está poblando las celdas de las zonas nativas activas, **o** los índices `i` guardados no coinciden con los del loop de dibujo, **o** `f_isBandPick` (línea ~2870) recomputa una celda distinta.

### Descartado por análisis (para acotar a Fable)
- `f_isBandPick` (2870) y la población (2896) usan la **misma celda**: para zona "arriba" `lvl = z.bottom`, misma banda `f_depthBand(lvl, close)`. Lectura estática = consistentes.
- La zona cae en **banda 1** (dealing range vigente [1.13618, 1.14730], `r ≈ 0.17`).
- Aun con `strength = 0`, `v2 = f_renderScoreV2(...)` ≥ 0 ≥ `bandPickScore` inicial (−1.0) → **ganaría** la celda (línea ~2921, `>=`). Así que no es cuestión de fuerza.

### Preguntas para Fable
1. ¿Por qué la población band-pick (2886) no marca las celdas de las zonas nativas activas en Operación? ¿Se está ejecutando el bloque `if barstate.islast and array.size(SMC_zones) > 0` con `aAtr>0`?
2. ¿Coinciden los índices `i` de `SMC_zones` entre la población (2896) y los loops de dibujo (3740/3967)? ¿Se muta `SMC_zones` entre ambos puntos (push de breakers/IFVG en 2094) desalineando índices?
3. ¿Debería el gate nativo tener también una vía de promoción (como MB/BPR con `confDegree≥2`) para que las zonas importantes activas cercanas siempre entren, aunque no ganen band-pick?

### Restricciones del fix (reglas duras)
- Anti-repaint (`barstate.isconfirmed` para eventos; `islast` para dibujo).
- **CORE byte-idéntico** intacto — el fix vive en `SMC-Visual.pine`.
- **RE10045-safe:** sin `array.push` nuevos en `islast` sobre estructuras grandes; band-pick usa 40 escalares SET/GET.
- Parámetros CONGELADOS ADR-002 (wPos/kConf/tolConf/tolPos/bandas/i_profundidad) no se tocan sin ADR.

---

## BUG #2 — Premium / Discount 🟡 PENDIENTE (revisar con el usuario)

> Placeholder. El usuario pidió sumar la observación de **Premium/Discount** una vez revisadas todas las familias una por una. **A rellenar** tras la validación (comportamiento del grid P/D en Operación, "Discount camina hacia el precio", etc.). Ver [`docs/decisiones-pd-rango.md`](../decisiones-pd-rango.md).

---

## Observación menor — Panel ↔ chart inconsistente (no bloqueante)

El panel T14 titula **"OB/FVG cercano [a, b]"** usando `f_pNearZone` (línea ~4243), que devuelve la zona más cercana **sin filtrar por estado ni por si se dibuja**. Resultado: el panel anuncia una zona que el chart no dibuja en Operación. Depende del arreglo del BUG #1 (si las nativas vuelven a dibujar, la inconsistencia se reduce). Nota: los glifos **●●○** del panel son de **FUERZA** (`f_strGlyph`, línea ~4209), **no** confDegree.

---

## Qué DEBE verse en Operación por familia (checklist de validación, en curso)

> Se rellena a medida que se revisa cada familia. Objetivo: Operación = **limpio pero NO vacío** — las zonas **limpias y más importantes por TF + por herencia**.

| Familia (§7.2) | Debe verse en Operación | Estado validación |
|---|---|---|
| A1 Estructura (BOS/CHoCH/MSS/FLIP/swings) | Giro vigente + flips en giro | ✅ dibuja (labels) |
| A2 Order Blocks | OB nativos activos cercanos (top-N por banda) + heredados MTF | 🔴 **BUG #1** — nativos no dibujan |
| A3 FVG | FVG nativos activos cercanos + heredados | 🔴 **BUG #1** — nativos no dibujan |
| A4 Liquidez (EQH/EQL/pools/sweep) | EQ + pools + sweeps cercanos | ✅ dibuja |
| A5 P/D + Gradient | Grid Premium/UQ/EQ/LQ/Discount + eighths | ⚠️ dibuja — revisar (BUG #2) |
| A6 Gaps apertura (NWOG/NDOG/NYMO) | Gaps del día/semana | ✅ dibuja |
| A7 Contexto / MTF | Herencia D1/H1 (bias+P/D+zonas) | ✅ dibuja |

---

## Notas de herramientas (para reproducir)
- Densidad se conmuta por MCP con la clave real del input: `indicator_set_inputs {"in_123":"Operación"|"Estudio"|"Todo"}`.
- Toggles de familia: no hay uno único por familia; son per-concepto (mapa `in_*` en la Sesión 099).
- Lectores `data_get_pine_labels/boxes` a veces devuelven `study_count 0` durante el recompute (reintentar); el `data_get_pine_tables` es el más fiable.

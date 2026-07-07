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

### 🎯 ROOT CAUSE CONFIRMADO (análisis estático S100, alta confianza)

**`chartState.atr14` NUNCA se asigna en `SMC-Visual.pine` → se queda en su default de UDT (`na`) → colapsa TODO el path de selección nativa (anclas + band-pick) de una sola vez.**

Cadena de evidencia (verificada por grep sobre el archivo completo):
1. Las **únicas** asignaciones a campos de `chartState` en todo el Visual son `pdHigh` y `pdLow` (líneas **1962–1963**, dentro de `if barstate.isconfirmed`). **No existe ninguna `chartState.atr14 :=` en el archivo.**
2. La única función que muta `chartState` por referencia es `f_updateTFState(chartState, …)` (línea **1980**); su cuerpo (**489–500**) solo toca `bias / lastBOS* / lastCHoCH*` — **no toca `atr14`**. `chartState` no se construye vía `f_buildTFState` (esa función setea `st.atr14` en la 1798, pero opera sobre los `st` MTF, no sobre `chartState`).
3. El ATR sí se calcula como local (`float atr14 = ta.atr(14)`, línea **2006**), pero **nunca se copia** a `chartState.atr14`. Simple wiring faltante.

**Mecanismo del fallo:** el bloque de población de anclas + band-pick (línea **2886**) hace `float aAtr = chartState.atr14` (2888) y todo su cuerpo cuelga de `if not na(aAtr) and aAtr > 0` (**2893**). Con `chartState.atr14 = na` ese guard es **siempre FALSE** → `anchorHiIdx/anchorLoIdx` quedan en −1 y `bandPickIdx` queda todo en −1. En Operación (`densMin=2`) las nativas dibujan solo por `f_densOK(z.strength, isAnchor) OR f_isBandPick(...)`; sin anclas y sin band-picks, y con strength típico < nivel 2, **ninguna nativa pasa el gate**. La ruta MTF (`f_drawMTFZones`) NO lee `chartState.atr14` → sigue dibujando. → **síntoma exacto.**

Esto explica por qué el análisis estático previo no lo fijó: el fallo está **aguas arriba** del cómputo de banda/celda — el loop de población ni se ejecuta, así que volcar `state/dir/band` no habría revelado nada. También explica la asimetría Operación vs Estudio/Todo (en Estudio/Todo `densMin≤1` → las nativas dibujan por `f_densOK` sin depender del path roto).

**Efectos colaterales del mismo `na` (a validar tras el fix):** `f_posRole` (2788: `float atr = chartState.atr14`) devuelve siempre `INTERNO` (0) → `wPos` siempre 0.35; bandas 4/5 (`f_depthBand` gate 2739) quedan muertas; ribbon KZ usa `nz(chartState.atr14)→0` (2/3 líneas colapsadas). Todos se sanan con la misma asignación.

**Fix candidato (para que Fable confirme/apruebe):** copiar el ATR local a `chartState.atr14` una vez por barra, junto a las otras asignaciones de `chartState`. Ubicación natural: tras calcular `atr14` (2006) o junto al bloque `pdHigh/pdLow` (1962). Sin repaint (ATR de cierre; el dibujo sigue en `islast`), sin tocar CORE, sin arrays nuevos → cumple las 4 restricciones. **Cuidado:** el snapshot P/D se congela en `isconfirmed`, pero `atr14` se necesita en la barra viva para el path de dibujo `islast` → conviene asignar `chartState.atr14 := atr14` **sin gatear en `isconfirmed`** (o con `nz`), a diferencia de `pdHigh/pdLow`. Confirmar con Fable si esta asimetría es correcta o si el path de dibujo debería usar el ATR local directamente en vez de `chartState.atr14`.

### Localización (capa de dibujo)
- **Raíz (falla):** población anclas+band-pick `if not na(aAtr) and aAtr > 0` (línea **2893**), con `aAtr = chartState.atr14` (2888) = `na`.
- **Ruta NATIVA (síntoma):** `f_drawOB` (~3742) y `f_drawFVG` (~3969). Gate `… (f_densOK(z.strength, isAnchor) or f_isBandPick(i, 0, z.top, z.bottom))`; ambos insumos (anclas y band-pick) llegan vacíos por la raíz de arriba.
- **Ruta MTF (funciona):** `f_drawMTFZones` (~4054) — NO lee `chartState.atr14` ni band-pick → por eso las heredadas sí dibujan.

### Descartado por análisis (para acotar a Fable)
- **Desalineación de índices `i` — DESCARTADO formalmente.** `SMC_zones` NO se muta en `SMC-Visual.pine` (0 `array.push(SMC_zones` en el archivo; se puebla en el CORE). Población (2896) y loops de dibujo (3740/3800) recorren el mismo array final en `islast` → índices idénticos por construcción. (Antigua pregunta 2, cerrada.)
- `f_isBandPick` (2870) y la población (2896) usan la **misma celda** — consistentes en lectura. (Irrelevante: la población nunca corre.)
- No es cuestión de `strength` ni de banda: con el guard `aAtr>0` en FALSE, ni siquiera se llega a evaluar `v2`/`f_depthBand`.

### Preguntas para Fable
1. ¿Confirmas el root cause (`chartState.atr14` sin asignar) y el fix candidato (asignar `chartState.atr14 := atr14`)? ¿Gatear o no en `isconfirmed`, dada la asimetría con `pdHigh/pdLow` (snapshot P/D congelado vs ATR necesario en barra viva para el dibujo `islast`)?
2. ¿O prefieres que el path de dibujo (`f_posRole`, band-pick, ribbon KZ) lea el ATR local `atr14` directamente en vez de `chartState.atr14`, para no acoplar el dibujo al snapshot del scoring?
3. Tras el fix, ¿debería el gate nativo tener además una vía de promoción (como MB/BPR con `confDegree≥2`) para que zonas importantes activas cercanas siempre entren aunque no ganen band-pick? (mejora aparte, no bloquea).

### Restricciones del fix (reglas duras)
- Anti-repaint (`barstate.isconfirmed` para eventos; `islast` para dibujo).
- **CORE byte-idéntico** intacto — el fix vive en `SMC-Visual.pine`.
- **RE10045-safe:** sin `array.push` nuevos en `islast` sobre estructuras grandes; band-pick usa 40 escalares SET/GET.
- Parámetros CONGELADOS ADR-002 (wPos/kConf/tolConf/tolPos/bandas/i_profundidad) no se tocan sin ADR.

---

## BUG #2 — Premium / Discount 🟢 REVISADO EN VIVO (S100) — NO es bug

Barrido en vivo S100 (OANDA:EURUSD, Operación, H1 y M5). El grid P/D dibuja y es **numéricamente correcto**:
- **H1** (rango [Discount 1.13618, Premium 1.14730], precio 1.14401): EQ 1.14174 (50%), LQ 1.13896 (25%), UQ 1.14452 (75%), pct = (1.14401−1.13618)/0.01112 = **70.4% → "Premium 71%"** ✓. Todos exactos.
- **M5** (rango [1.14085, 1.14481], precio 1.14414): EQ 1.14283, LQ 1.14184, UQ 1.14382, pct **83% → "Premium 82%"** ✓.
- **D1** (rango [1.13246, 1.20831], precio 1.14401): pct 15.2% → **"Discount 15%"** ✓.

El "**Discount camina hacia el precio en tendencia**" es la **Opción A operando como se diseñó** (trailing extremes de LuxAlgo), decidido y **re-confirmado 2× por el usuario** (S057, S091) y diferido a **Fase 3** con datos OOS. **NO es un bug** — ver [`docs/decisiones-pd-rango.md`](../decisiones-pd-rango.md). Cierra el placeholder de BUG #2.

---

## BUG #3 — El contador "Ocultos" del panel sub-reporta Estructura/EQ nativas en TFs bajos (M5) 🟠 honestidad del panel

**Severidad:** media. No afecta el dibujo de zonas, pero **rompe la garantía §10-#8 / §1-7 "nada desaparece en silencio"** (motivo por el que se creó la fila "Ocultos" en S087/S088): el panel afirma que oculta 0 cuando oculta decenas. Independiente de BUG #1.

### Síntoma (reproducible desde los datos del panel, S100)
En **M5 Operación** la fila **Ocultos** reporta `Est 0 · EQ 0`, pero:
- Panel `EQ H/L` (columna M5) = **81** EQ detectados en el buffer nativo; en el chart solo se dibujan **2 EQH** (0 EQL) → ~79 EQ efectivamente no mostrados, contados como **0** ocultos.
- Estructura: solo 3 labels nativas dibujadas (CHoCH / BOS / CHoCH MSS) de una historia M5 con cientos de BOS/CHoCH → `Est 0`.
- **Contraste:** en **H1 Operación** la misma fila reporta `Est 498 · EQ 105` (el contador SÍ está activo y con valores grandes). Mismo código, resultado incoherente entre TFs.

### Root cause (hipótesis, verificada en código estático)
- `EQ H/L` (columna M5) = `array.size(SMC_eqhl)` (línea **4342**) = EQ **detectados** en el buffer nativo (81).
- `hidEq` (Ocultos EQ, línea **3336**) = lo que **recorta** `f_keepBestPerBand` del array de labels **DIBUJADAS** `SMC_eqLabels`, no el hueco detectado-menos-dibujado. Igual `hidStruct` (línea **3195/3336** análoga) para estructura.
- En M5 el array de labels dibujadas es pequeño (Pine `max_labels_count` auto-borra las viejas + pocas se pushean al islast), así que el recorte cuenta ~0 aunque la mayoría de los 81 EQ detectados nunca lleguen al chart. **La semántica de "Ocultos" mide el recorte top-N, no el verdadero "detectado − dibujado".**

### Preguntas para Fable
1. ¿La fila "Ocultos" debe contar **detectado − dibujado** (honesto respecto a §10-#8) en vez de solo el recorte `f_keepBestPerBand`? Si es así, para EQ sería `array.size(SMC_eqhl) − (EQ realmente dibujados)` y análogo para estructura.
2. ¿Por qué H1 da 105/498 y M5 da 0/0 con el mismo código? (probable: tamaño del array de labels dibujadas + `max_labels_count`). ¿Conviene contar sobre los buffers nativos (`SMC_eqhl`, estructura) que sí reflejan lo detectado?

### Restricciones del fix
- Solo panel/presentación (fuera del LIBRARY CORE byte-idéntico). RE10045-safe (contadores int, sin arrays nuevos en `islast`). No toca detección ni el dibujo de zonas.

---

## Observación menor — Panel ↔ chart inconsistente (no bloqueante)

El panel T14 titula **"OB/FVG cercano [a, b]"** usando `f_pNearZone` (línea ~4243), que devuelve la zona más cercana **sin filtrar por estado ni por si se dibuja**. Resultado: el panel anuncia una zona que el chart no dibuja en Operación. Depende del arreglo del BUG #1 (si las nativas vuelven a dibujar, la inconsistencia se reduce). Nota: los glifos **●●○** del panel son de **FUERZA** (`f_strGlyph`, línea ~4209), **no** confDegree.

---

## Qué DEBE verse en Operación por familia (checklist de validación, en curso)

> Se rellena a medida que se revisa cada familia. Objetivo: Operación = **limpio pero NO vacío** — las zonas **limpias y más importantes por TF + por herencia**.

| Familia (§7.2) | Debe verse en Operación | Estado validación |
|---|---|---|
| A1 Estructura (BOS/CHoCH/MSS/FLIP/swings) | Giro vigente + flips en giro | ✅ dibuja (labels) · ⚠️ contador Ocultos M5 (**BUG #3**) |
| A2 Order Blocks | OB nativos activos cercanos (top-N por banda) + heredados MTF | 🔴 **BUG #1** — nativos no dibujan |
| A3 FVG | FVG nativos activos cercanos + heredados | 🔴 **BUG #1** — nativos no dibujan |
| A4 Liquidez (EQH/EQL/pools/sweep) | EQ + pools + sweeps cercanos | ✅ dibuja · ⚠️ contador Ocultos M5 (**BUG #3**) |
| A5 P/D + Gradient | Grid Premium/UQ/EQ/LQ/Discount + eighths | ✅ correcto (BUG #2 cerrado — no era bug) |
| A6 Gaps apertura (NWOG/NDOG/NYMO) | Gaps del día/semana | ✅ dibuja (NDOG/NYMO en vivo) |
| A7 Contexto / MTF | Herencia D1/H1 (bias+P/D+zonas) | ✅ dibuja (cajas MTF extienden a barra actual) |

---

## Notas de herramientas (para reproducir)
- Densidad se conmuta por MCP con la clave real del input: `indicator_set_inputs {"in_123":"Operación"|"Estudio"|"Todo"}`.
- Toggles de familia: no hay uno único por familia; son per-concepto (mapa `in_*` en la Sesión 099).
- Lectores `data_get_pine_labels/boxes` a veces devuelven `study_count 0` durante el recompute (reintentar); el `data_get_pine_tables` es el más fiable.

# HANDOFF — Capa de discriminación + verificación visual graduada (rellenable por cualquier IA)

> **Origen:** Sesion-054 (2026-06-23). Diseño aprobado por Freddy: módulo de **calidad/jerarquización** sobre el Pine que hoy detecta 40+ conceptos sin graduarlos.
> **Quién ejecuta:** **cualquier IA** (Opus Ultracode o una sesión Claude Code). Este brief es **autocontenido** — con él + PLAN-049 + reglas-smc-ict.md se puede rellenar y verificar sin la conversación original.
> **Estado al entregar:** Fase 1. CORE 1517 líneas SHA `80fad14dd8d03758`, compila 0/0 los 3, core-sync OK. **Ningún `.pine` tocado en S054** (es diseño). Los 3 entregables del esqueleto ya existen (§2).

---

## 0. Tu misión (y la corrección de roles que la habilita)

> **Corrección respecto al plan original.** El plan decía "esta sesión = borrador → *Opus Ultracode* hace el esqueleto → Claude rellena". En S054 **Opus ya entregó diseño + esqueleto + plantilla refinada** (este handoff + los 2 docs de §2). Por lo tanto el paso intermedio "Opus genera el esqueleto" **ya está hecho**: vas directo a **(a) refinar si algo falta → (b) rellenar → (c) verificar**. Se elimina un salto de relevo.

1. **(opcional) Refinar la plantilla** del sub-bloque (`reglas-smc-ict.md §6.0`) y el inventario de primitivos (`§6.1`) **solo si** al rellenar detectas un eje/métrica que falta para **medir bien** un concepto. Si está completa, no la toques.
2. **Rellenar los 40+ conceptos** en `reglas-smc-ict.md` con el sub-bloque §6.0 (variante · fuerza · invalidación · visual · MTF), citando **solo** primitivos de `§6.1`. Empieza completando los **4 ejemplos-slot** (§6.2.2–6.2.5) — el OB (§6.2.1) ya está como calibración.
3. **Especificar (esqueleto, no producción)** el tag de fuerza en Pine (§5 de este doc) y la jerarquía visual + arreglo de errores de dibujo (§6).
4. **Ejecutar la verificación graduada + MTF** concepto a concepto según [`METODOLOGIA-VERIFICACION-VISUAL.md`](../METODOLOGIA-VERIFICACION-VISUAL.md) §7, y cerrar el **F1-GATE ampliado** (§8 de la metodología).

**NO** escribir Pine de producción sin pasar por el ciclo del proyecto (regla → compila 0/0 → validador ≥90 → core-sync → commit). **NO** recalcular las §4.8 (42 confluencias): el enjambre **lee**, no mide. Español. Output = reglas-smc-ict §6 relleno + tabla de verificación + (si toca Pine) commits por concepto.

---

## 1. Contexto a leer primero

- `CLAUDE.md` (reglas duras), `memory/ESTADO-ACTUAL.md` (fase/estado), `WORKPLAN-MAESTRO-V2.md`.
- **Los 3 entregables del esqueleto (S054):**
  - [`docs/METODOLOGIA-VERIFICACION-VISUAL.md`](../METODOLOGIA-VERIFICACION-VISUAL.md) — los 4 ejes + MTF + jerarquía visual + arreglo de errores (estado real) + runbook + gate.
  - [`docs/reglas-smc-ict.md`](../reglas-smc-ict.md) **§6** — plantilla §6.0 + inventario §6.1 + ejemplos §6.2.
  - este HANDOFF.
- **Fuentes de verdad:** `docs/reglas-smc-ict.md` §0–§5 (definiciones congeladas), [`docs/sprint-runs/PLAN-VALIDACION-Sesion-049.md`](../sprint-runs/PLAN-VALIDACION-Sesion-049.md) (lista ordenada 40+ con § + toggle + TF + casos).
- **ADRs relevantes:** `ADR-010` (transporte MTF + dibujo geométrico anclado, ya implementado T13c/S042), `ADR-012` (protocolo de razonamiento Q1–Q7 — capa de Contextualizar/invalidación), `ADR-002` (umbrales congelados hasta Fase 3).
- **Reutilización (NO reinventar):** `f_nearestN` ([SMC-Library.pine](../../pine/SMC-Library.pine) ~1385) = base del top-N; `SMC_Zone` (Library ~223) + flags `mitigado`/`state`/`trueFvg`/`propulsion` = base del campo de fuerza; `f_detectDisplacement` (§4.1) = primitivo de fuerza; panel T14 (`data_get_pine_tables`) = destino de lo que NO se dibuja; ~43 toggles `i_show*` por familia = perfiles de densidad; cadena ADR-012 Q1–Q7 = invalidación externa.

---

## 2. Estado de partida (qué ya existe, qué falta)

| Pieza | Estado |
|---|---|
| Detección de 40+ conceptos (§1–§5) | ✅ codificada, compila 0/0, core-sync OK |
| Dibujo geométrico MTF anclado (cajas/líneas/marcas por `bar_time`) | ✅ T13c/S042 — **los 5 síntomas de revision-T13b están CERRADOS** |
| Metodología graduada (4 ejes + MTF + visual) | ✅ esqueleto S054 |
| Plantilla §6.0 + inventario §6.1 + ejemplo OB | ✅ S054 |
| 4 ejemplos-slot (FVG/EMA/Rejection/MSS) | ⬜ **rellenar** |
| Sub-bloque §6 para los ~35 conceptos restantes | ⬜ **rellenar** |
| Tag de fuerza `strength` en Pine | ⬜ **especificar (§5) → implementar** |
| Jerarquía visual (3 niveles, `i_densidad`, top-N→panel) | ⬜ **especificar (§6) → implementar** |
| 3 pendientes diferidos de dibujo MTF (S042) | ⬜ **resolver** (metodología §6.b) |
| Verificación graduada + MTF de los 40+ | ⬜ **ejecutar** → F1-GATE ampliado |

---

## 3. Qué rellenar exactamente

### 3.1 Protocolo por concepto (mecánico)
Para cada concepto del checklist §8, **anexar al final de su ficha en `reglas-smc-ict.md`** (junto a sus casos ✓/✗) un sub-bloque con la plantilla `§6.0`, o registrarlo en `§6.2` si se prefiere centralizar. Reglas:
1. Cada uno de los 4 campos (variante/fuerza/invalidación/visual) **cubre su fallo** (#1/#2/#3) — ver §6.0.
2. La fórmula de **fuerza cita SOLO** primitivos de `§6.1`. Si falta uno, **propónlo como indicación** (cálculo sugerido), no lo inventes como hecho.
3. Marca los `strength`/pesos como **candidatos congelados hasta Fase 3** (ADR-002).
4. Si el concepto **no aplica** a EURUSD (RTH/ETH §5.15) o requiere otro símbolo (SMT §5.13), decláralo (igual que en §5).

### 3.2 Orden recomendado de relleno
1. Completar los 4 slots §6.2.2–6.2.5 (validan la plantilla en los 3 fallos).
2. Tier 1 (§1.1–§1.6) → Tier 2 (§2.1–§2.8) → Liquidez (§3.1–§3.7) → Contexto (§4.1–§4.4) → Gap ICT (§5.1–§5.15).
3. Anti-doble-conteo `[FIX P-05]`: una variante que *refina* otro concepto (True FVG, Propulsion) **no** suma confluencia ni sub-bloque nuevo independiente — eleva el `strength` del concepto base.

---

## 4. Restricciones duras (innegociables)

1. **Core byte-idéntico (regla #2):** la sección LIBRARY CORE de Visual y Strategy es idéntica. Si tocas el CORE (p.ej. campo `strength`) → `scripts/check-core-sync.ps1` y documentar SHA nuevo.
2. **Anti-repaint (regla #1):** eventos en `barstate.isconfirmed`; `request.security(..., lookahead = barmerge.lookahead_off)`. El tag de fuerza se calcula con velas cerradas.
3. **Símbolo-agnóstico + ATR-relativo (reglas #3–#4):** toda fuerza en múltiplos de ATR, nunca pips fijos; nada hardcodeado a EURUSD.
4. **No recalcular §4.8:** el enjambre lee las confluencias, no las mide. La capa de fuerza alimenta el peso; no redefine el catálogo.
5. **Híbrido:** Pine = tag barato (reusa primitivos); grading completo = scoring + ADR-012. No mover el grading pesado a Pine.
6. **Gate (regla #8):** ningún gate se salta; si un eje <90 → retroceso con diagnóstico, no se ajusta el criterio.

---

## 5. Esqueleto del tag de fuerza en Pine (ESPECIFICADO S056 — listo para implementar)

> Objetivo: `strength` por marca, **barato**, en el CORE, sin romper core-sync ni anti-repaint. Spec anclada en los UDTs/funciones reales (`pine/SMC-Library.pine`, CORE 1517 líneas). Pesos = **candidatos CONGELADOS hasta Fase 3** (ADR-002).

### 5.1 Campos nuevos en el CORE (byte-idéntico — exige `check-core-sync.ps1` + SHA nuevo)
- **`SMC_Zone`** (`SMC-Library.pine` L98–L109): añadir `float strength = 0.0` tras `propulsion` (L109). Cubre OB/FVG/Breaker/IFVG/BPR/Vacuum/VI/IPR/Flip-zona/Mitigation (todo lo que es zona).
- **`SMC_Event`** (L112–L118): añadir `float strength = 0.0` tras `kind`. Cubre BOS/CHoCH/MSS/Sweep/Judas/Displacement/IDM/CISD/EMA-cross/EMA-bounce (eventos puntuales).
- **`SMC_Swing`** (L121–L126) y **`SMC_Pool`** (L129–L138): añadir `float strength = 0.0`. Swing → escala+frescura+rol; Pool → `touches`+frescura+cercanía.
- *No tocar `SMC_TFState`* (L141–L158): el strength viaja en los buffers de evento/zona que ADR-010 ya aplana para MTF, no en el snapshot plano.

### 5.2 Funciones puras de fuerza (en el `=== LIBRARY CORE ===`, byte-idénticas)
Dos funciones nuevas, ambas **puras** y calculadas **solo al cierre** (anti-repaint, reusan ATR ya calculado — nunca recalcular intra-vela):

```
f_zoneStrength(SMC_Zone z, float curPrice, float atr14, int biasDir) =>
    // normaliza a 0–1 combinando primitivos §6.1 ya disponibles
f_eventStrength(SMC_Event e, float rangeAtr, float bodyPct, bool hadSweep, int biasDir) =>
```

**Pesos candidatos por primitivo (congelados hasta Fase 3 — ADR-002).** Suma ponderada normalizada a [0,1]; cada término en [0,1]:
| Primitivo (§6.1) | Fuente | Peso cand. | Mapa a [0,1] |
|---|---|---|---|
| `rango ×ATR` / `displacement` | `f_detectDisplacement` (L310) | **0.30** | `min(rangeAtr / 3.0, 1)`; +0.0 si no hay displacement, término pleno si lo hay |
| `cuerpo%` | misma vela | **0.15** | `(bodyPct − 0.5) / 0.5` clamp [0,1] |
| `frescura / state` | `SMC_Zone.state` (0/1/2/3) | **0.20** | activa=1 · parcial=0.5 · mitigada/inval=0 |
| `sweep previo` | `f_detectSweep`/`f_detectGrab` | **0.15** | binario (1 si barrió liquidez antes) |
| `distancia al nivel ×ATR` | `curPrice` vs zona | **0.10** | `1 − min(distAtr / 2.0, 1)` (cercano = más fuerte) |
| `alineación con bias` | `biasDir` vs `z.dir`/`e.dir` | **0.10** | 1 si coincide · 0.5 neutro · 0 en contra |
| `flags refinamiento` | `trueFvg` / `propulsion` | **bonus +0.10** | eleva el strength del base `[FIX P-05]` (no suma confluencia) |

- **Eventos** (`f_eventStrength`): solo aplican `rango×ATR`(0.40) + `cuerpo%`(0.20) + `sweep previo`(0.20) + `alineación`(0.20) — no tienen `state` ni distancia de zona.
- **Swing/Pool** (inline, no función propia): swing = `escala`(0.5: dominante 1 / swing 0.5 / interno 0.2) + `frescura no-roto`(0.3) + `alineación`(0.2); pool = `min(touches/3,1)`(0.5) + `¬swept`(0.3) + `cercanía`(0.2).

### 5.3 Quantización a 3 niveles (para el tag visual barato)
`f_strengthLevel(float s) => s >= 0.66 ? 2 : s >= 0.33 ? 1 : 0` → **alta/media/baja**. El 0–1 fino lo consume el scoring (Fase 3); el entero 0/1/2 alimenta la jerarquía visual (§6). **No confundir** con el `cap` 0–10 MTF (ADR-010) ni con el nivel visual {Primario/Secundario/Terciario} (gotcha S054).

### 5.4 Exposición MTF + lectura
- El `strength` viaja en los buffers de evento/zona que ADR-010 ya aplana para MTF (mismo patrón que `dir`/`kind`). La ranura de 6 campos → **se quantiza al nivel 0/1/2** y se empaqueta junto al `dir` (no requiere 7º campo: `dir·3 + level` cabe en un int, o campo float extra si el aplanado lo permite — decisión del `[impl]` al cablear).
- Lectura para el **Eje 2** (verificación de fuerza): `data_get_pine_labels` (el tag de la etiqueta lleva el nivel) o `data_get_pine_tables` (panel T14).

### 5.5 Gotchas duros
- **No recalcular ATR intra-vela**; `strength` solo cambia al cierre (`barstate.isconfirmed`).
- **Cálculo en CORE** (byte-idéntico → tras tocarlo: `scripts/check-core-sync.ps1` + documentar SHA nuevo, regla #2); el **dibujo** del tag vive en Visual (fuera del CORE, L3131+).
- Reusar el `atr14` ya disponible en el consumidor — las funciones lo reciben como parámetro, no lo calculan.

---

## 6. Jerarquía visual + arreglo de errores de dibujo (ESPECIFICADO S056 — listo para implementar)

Ver `METODOLOGIA-VERIFICACION-VISUAL.md` §5 (jerarquía) y §6 (errores). Todo el dibujo vive **fuera** del `=== LIBRARY CORE ===` (Visual L3131+) → **no rompe `check-core-sync`**.

### 6.1 Nivel visual = `f_visualLevel(strengthLevel, withinCap)`
Mapa determinista a {Primario=2 / Secundario=1 / Terciario=0}:
```
f_visualLevel(int sLevel, bool withinCap) =>
    not withinCap ? 0 : sLevel   // fuera del presupuesto top-N → Terciario sí o sí
```
- **Primario** (render completo: caja/línea sólida + etiqueta) = `strength` alta **y** dentro del cap top-N.
- **Secundario** (atenuado: color con transparencia ~60%, etiqueta corta) = `strength` media o lejana.
- **Terciario** (oculto del chart, **contado** en panel T14) = `strength` baja **o** fuera del cap.

### 6.2 Master input `i_densidad` (nuevo, `GRP_PANEL` o grupo propio `GRP_DENS`)
`input.string("Operación", "Densidad visual", options=["Operación","Estudio","Todo"])`:
| Modo | Qué dibuja | Para |
|---|---|---|
| **Operación** (default) | solo Primario | trading en vivo, chart limpio |
| **Estudio** | Primario + Secundario | análisis/validación |
| **Todo** | + Terciario | depuración/verificación graduada (Eje 2) |
- Filtro: cada bloque de dibujo añade `and f_visualLevel(...) >= i_densThreshold` junto a su `i_show*` existente (los `i_show*` por familia **se mantienen** — `i_densidad` es un filtro transversal adicional, no los reemplaza).
- **Z-order por familia** (dibujar de menor a mayor relevancia): contexto/PD (fondo) → zonas → liquidez → estructura/eventos (frente). Anti-solape de etiquetas: `style_label_left` / `style_label_right` alternado por lado del nivel (ya usado en el MTF).
- **Presupuesto de tinta:** top-N por familia con `f_nearestN`/`f_nearestNPools` (ADR-010) ya existentes → `withinCap`; el resto incrementa el contador de la familia en el **panel T14** (no se dibuja).

### 6.3 Arreglo de los 3 pendientes diferidos MTF (síntoma → causa → arreglo → criterio)
> Los 5 síntomas de `revision-T13b-mtf-dibujo-nativo.md §2` están **cerrados** (T13c/S042, commit 88500fd). Quedan estos 3 (metodología §6.b):

**(a) Tag `(D1)`/`(H1)` en BOS/CHoCH fusionados.**
- *Síntoma:* un evento BOS/CHoCH heredado de HTF y dibujado en M5 no indica de qué TF viene; si coincide con el nativo se fusionan sin distinguir origen.
- *Causa:* la etiqueta del evento MTF no concatena `e.tf` (el campo ya existe en `SMC_Event.tf`); el anti-duplicado S042 los une pero pierde el rótulo de procedencia.
- *Arreglo:* en el bloque de dibujo de eventos MTF (Visual, fuera del CORE), añadir sufijo `" (" + e.tf + ")"` al texto de la etiqueta cuando `e.tf != timeframe.period`; si fusionado con el nativo, rótulo combinado `"BOS (H1·M5)"`.
- *Criterio:* en M5 con D1+H1 activos, cada marca heredada muestra su TF; 0 marcas ambiguas en una pasada de 300 velas.

**(b) Cuadre fino EQH/EQL HTF↔LTF.**
- *Síntoma:* el nivel de un EQH/EQL heredado de HTF cae unos ticks desviado del cluster nativo en LTF.
- *Causa:* el `pool.level` HTF (promedio de extremos clusterizados, §3.1) se ancla por `bar_time` pero el redondeo de precio del TF menor no cuadra exacto.
- *Arreglo:* anclar la línea heredada al `pool.level` HTF **literal** (no recalcular en LTF) y dibujar con `xloc.bar_time`; tolerancia de fusión con el nativo = `poolTol×ATR` del LTF (ya parametrizado).
- *Criterio:* desviación HTF↔LTF ≤ `poolTol×ATR` en los EQH/EQL de los casos §2.4 (05-27/05-28 BSL, 06-03 SSL).

**(c) Exactitud vela-a-vela de OB/FVG heredados.**
- *Síntoma:* la caja de un OB/FVG HTF heredado a M5 se ancla a una vela M5 adyacente, no a la exacta del origen HTF.
- *Causa:* el mapeo `bar_time` HTF→LTF cae entre dos velas M5 cuando el `bar_time` HTF no coincide con un open M5 (FVG ancla la **vela media**, `time[1]`).
- *Arreglo:* anclar con `xloc.bar_time` al `barTime` exacto del UDT (`SMC_Zone.barTime`, ya guardado) y dejar que TV resuelva la vela contenedora; para FVG usar el `barTime` de la vela media real (ya corregido en T13c — verificar que el heredado use el mismo campo).
- *Criterio:* caja heredada cubre la misma vela origen que el OB/FVG nativo del HTF en los casos §2.1/§2.2 (OB 06-01/06-05/06-08; FVG 06-01/06-05).

### 6.4 Orden de implementación sugerido (paso 4 del plan §7)
1. CORE: campos `strength` (§5.1) → compila 3 + `check-core-sync` + SHA. **1 commit** `feat(pine-core): S1.x strength en UDTs`.
2. CORE: `f_zoneStrength`/`f_eventStrength`/`f_strengthLevel` (§5.2–5.3) + cálculo en sitios de creación → compila 3 + core-sync. **1 commit**.
3. Visual: `i_densidad` + `f_visualLevel` + filtro transversal (§6.1–6.2) → compila Visual. **1 commit**.
4. Visual: 3 arreglos MTF (§6.3), uno por commit con su criterio verificado.
5. → entra el **paso 5** (revisión visual graduada concepto a concepto = lo que el usuario revisa 1-a-1).

---

## 7. Plan de ejecución (orden + gates) — para que la IA lo ejecute

| Paso | Acción | Gate de salida |
|---|---|---|
| 1 | Completar slots §6.2.2–6.2.5 | plantilla probada en los 3 fallos |
| 2 | Rellenar sub-bloque §6 para los ~35 restantes (orden §3.2) | cada uno cita solo §6.1; doc coherente (metodología §9) |
| 3 | Especificar `strength` en Pine (§5) | diseño revisado; no rompe core-sync ni anti-repaint |
| 4 | Implementar `strength` + jerarquía visual + 3 pendientes (§6) en Pine | compila 0/0 los 3 + core-sync OK + commit por concepto |
| 5 | Ejecutar verificación graduada + MTF (metodología §7) por concepto | cada concepto ≥90 en los 4 ejes |
| 6 | Cierre del set | **F1-GATE ampliado**: ≥90 + anti-repaint (2 días) + perf (20k) + firma usuario → desbloquea Fase 2 |

> Pasos 1–2 son **solo docs** (sin tocar Pine). Pasos 3–4 tocan Pine → ciclo completo del proyecto. Paso 5 es la pasada de TV-MCP que **fusiona** el camino A (discriminación) y el camino B (F1-GATE).

---

## 8. Apéndice — Checklist de los 40+ conceptos (orden MTF D1→H1→M5)

> De PLAN-049 §"Lista ordenada". Marcar ☑ al rellenar el sub-bloque §6 + ☑ al verificar (4 ejes). TF de PLAN-049; revisión MTF en orden D1→H1→M5.
> **Estado S056:** los **sub-bloques §6 de TODOS los conceptos están RELLENOS** (5 en §6.2 + ~35 en §6.3). El segundo ☑ (verificación de 4 ejes) sigue **pendiente** para todos (paso 5 del plan §7). Notación: `☑relleno ⬜verif`.

**Tier 1 — Estructura (H1):** ☑⬜ Swings §1.1 *(6.3.1)* · ☑⬜ BOS/CHoCH swing §1.3/1.4 *(6.3.2)* · ☑⬜ BOS/CHoCH interno §1.4 *(6.3.3)* · ☑⬜ Estructura dominante §1.4 *(6.3.4)* · ☑⬜ MSS §1.5 *(slot 6.2.5)*

**Tier 2 — Zonas (H1):** ☑⬜ Order Block §2.1 *(ejemplo 6.2.1 ✅)* · ☑⬜ FVG+CE §2.2 *(slot 6.2.2)* · ☑ True FVG §5.1 *([FIX P-05] → strength FVG)* · ☑⬜ Premium/Discount/Eq §2.3 *(6.3.5)* · ☑⬜ EQH/EQL §2.4 *(6.3.6)* · ☑⬜ OTE/GP §2.5 *(6.3.7)* · ☑⬜ Breaker §2.6 *(6.3.8)* · ☑⬜ Rejection §2.7 *(slot 6.2.4)* · ☑⬜ Flip §2.8 *(6.3.9)* · ☑⬜ Mitigation Block §2.8#24 *(6.3.10)*

**Liquidez (M5; sweeps/pools también H1):** ☑⬜ Pools BSL/SSL §3.1 *(6.3.11)* · ☑⬜ Sweep §3.2 *(6.3.12, +Grab §3.3)* · ☑⬜ IDM §3.6 *(6.3.13)* · ☑⬜ Judas §3.5 *(6.3.14)* · ☑⬜ False Breakout §3.7 *(6.3.15)* · ☑⬜ Kill Zones §3.4 *(6.3.16)*

**Contexto/ICT/EMAs (H1; macros M5):** ☑⬜ Displacement §4.1 *(6.3.17)* · ☑⬜ EMAs estado §4.3 *(6.3.18)* · ☑⬜ EMA rebote #41 §4.3 *(6.3.19)* · ☑⬜ EMA cruce #40 §4.3 *(slot 6.2.3)* · ☑⬜ EMA Stack Flip §4.3 *(6.3.20)* · ☑⬜ Session Opens §4.2 *(6.3.21)* · ☑⬜ Impulsive/Corrective §4.4 *(6.3.22)*

**Gap ICT (H1 salvo nota):** ☑⬜ IFVG §5.2 *(6.3.23)* · ☑⬜ BPR §5.3 *(6.3.24)* · ☑⬜ Immediate Rebalance §5.4 *(6.3.25)* · ☑⬜ Volume Imbalance §5.5 *(6.3.26)* · ☑⬜ CISD §5.6 *(6.3.27)* · ☑ Propulsion Block §5.8 *([FIX P-05] → strength OB)* · ☑⬜ Vacuum Block §5.7 *(6.3.28, frontera/finde)* · ☑⬜ IPR §5.9 *(6.3.29)* · ☑⬜ Inside Day §5.12 *(6.3.30)* · ☑ Std Dev §5.11 *(6.3.31, herramienta, no confluencia)* · ☑⬜ Gaps apertura NWOG/NDOG/NYMO+BAG §5.10 *(6.3.32)* · ☑ Macros §5.14 *([FIX P-05] → refina #34 en 6.3.16)* · ☑⬜ SMT §5.13 *(6.3.33, requiere GBPUSD)* · ☑ RTH/ETH §5.15 *(6.3.34, N/A FX, Fase 5)*

**MTF:** ☑⬜ Herencia D1/H1 (bias+P/D+zonas) en M5 *(6.3.35)* — visibilidad cruzada por `bar_time`.

---

## 9. Definition of Done (qué cuenta como terminado)

1. ☑ `reglas-smc-ict.md §6` relleno para los 40+ conceptos (4 campos cada uno, citando §6.1).
2. ☑ Los 5 ejemplos trabajados cubren los 3 fallos (metodología §9 checklist).
3. ☑ Si se tocó Pine: `strength` + jerarquía visual + 3 pendientes implementados; compila 0/0 los 3; core-sync OK (SHA nuevo documentado); commits Conventional + ID por concepto.
4. ☑ Verificación graduada + MTF ejecutada: cada concepto ≥90 en los 4 ejes; evidencia (screenshots + datos) a disco.
5. ☑ **F1-GATE ampliado** cerrado (≥90 + anti-repaint 2 días + perf 20k + firma usuario) → **Fase 2 desbloqueada**.

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

## 5. Esqueleto del tag de fuerza en Pine (especificar → implementar)

> Objetivo: `strength` por marca, **barato**, en el CORE, sin romper core-sync ni anti-repaint.

- **Campo nuevo en `SMC_Zone`** (`SMC-Library.pine` ~223): `float strength` (0–1). Para conceptos de evento (BOS/CHoCH/MSS/sweep) que no son `SMC_Zone`, exponer `strength` en sus buffers de evento paralelos (los que ADR-010 ya usa para MTF).
- **Cálculo en CORE** (función pura, p.ej. `f_zoneStrength` / `f_eventStrength`) reusando: `f_detectDisplacement` (cuerpo% + ×ATR), `state` (frescura/mitigado), `f_detectSweep` (¿barrió liquidez?), distancia al precio ×ATR, alineación con bias. `[RELLENAR: pesos por primitivo — candidatos, congelar hasta Fase 3]`.
- **Quantización opcional** a 3 niveles (alta/media/baja) para el tag visual barato; el 0–1 fino lo consume el scoring.
- **Exposición:** el `strength` viaja en la ranura MTF (ADR-010, ranura de 6 campos → evaluar si cabe un 7º o se quantiza al `dir`) y se lee vía `data_get_pine_labels` para el Eje 2.
- **Gotchas:** no recalcular ATR intra-vela; `strength` solo cambia al cierre; mantener el cálculo en CORE (byte-idéntico), el *dibujo* del tag en Visual.

---

## 6. Esqueleto de jerarquía visual + arreglo de errores de dibujo (especificar → implementar)

Ver `METODOLOGIA-VERIFICACION-VISUAL.md` §5 (jerarquía) y §6 (errores). Resumen de lo implementable:

- **3 niveles visuales** derivados de `strength × cercanía`: Primario (completo) / Secundario (atenuado) / Terciario (oculto o → panel T14).
- **Master input `i_densidad`** (Operación / Estudio / Todo) que filtra por nivel; z-order por familia; anti-solape `style_label_left`.
- **Presupuesto de tinta:** top-N por familia vía `f_nearestN`; el resto se **cuenta** en el panel T14 (no se dibuja).
- **Arreglo de errores de dibujo MTF — ESTADO REAL:** los 5 síntomas de revision-T13b **ya cerrados** (T13c/S042); resolver los **3 pendientes diferidos** (metodología §6.b): (a) tag `(D1/H1)` en BOS/CHoCH fusionados, (b) cuadre fino EQH/EQL, (c) exactitud vela-a-vela OB/FVG. `[RELLENAR: síntoma→causa→arreglo→criterio de verificación de cada uno]`.

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

**Tier 1 — Estructura (H1):** ⬜ Swings §1.1 · ⬜ BOS/CHoCH swing §1.3/1.4 · ⬜ BOS/CHoCH interno §1.4 · ⬜ Estructura dominante §1.4 · ⬜ MSS §1.5 *(slot 6.2.5)*

**Tier 2 — Zonas (H1):** ⬜ Order Block §2.1 *(ejemplo 6.2.1 ✅)* · ⬜ FVG+CE §2.2 *(slot 6.2.2)* · ⬜ True FVG §5.1 · ⬜ Premium/Discount/Eq §2.3 · ⬜ EQH/EQL §2.4 · ⬜ OTE/GP §2.5 · ⬜ Breaker §2.6 · ⬜ Rejection §2.7 *(slot 6.2.4)* · ⬜ Flip §2.8 · ⬜ Mitigation Block §2.8#24

**Liquidez (M5; sweeps/pools también H1):** ⬜ Pools BSL/SSL §3.1 · ⬜ Sweep §3.2 · ⬜ IDM §3.6 · ⬜ Judas §3.5 · ⬜ False Breakout §3.7 · ⬜ Kill Zones §3.4

**Contexto/ICT/EMAs (H1; macros M5):** ⬜ Displacement §4.1 · ⬜ EMAs estado §4.3 · ⬜ EMA rebote #41 §4.3 · ⬜ EMA cruce #40 §4.3 *(slot 6.2.3)* · ⬜ EMA Stack Flip §4.3 · ⬜ Impulsive/Corrective §4.4

**Gap ICT (H1 salvo nota):** ⬜ IFVG §5.2 · ⬜ BPR §5.3 · ⬜ Immediate Rebalance §5.4 · ⬜ Volume Imbalance §5.5 · ⬜ CISD §5.6 · ⬜ Propulsion Block §5.8 · ⬜ Vacuum Block §5.7 *(frontera/finde)* · ⬜ IPR §5.9 · ⬜ Inside Day §5.12 · ⬜ Std Dev §5.11 *(herramienta, no confluencia)* · ⬜ Gaps apertura NWOG/NDOG/NYMO+BAG §5.10 *(frontera)* · ⬜ Macros §5.14 *(M5)* · ⬜ SMT §5.13 *(requiere GBPUSD)* · ⬜ RTH/ETH §5.15 *(N/A FX, Fase 5)*

**MTF:** ⬜ Herencia D1/H1 (bias+P/D+zonas) en M5 — visibilidad cruzada por `bar_time`.

---

## 9. Definition of Done (qué cuenta como terminado)

1. ☑ `reglas-smc-ict.md §6` relleno para los 40+ conceptos (4 campos cada uno, citando §6.1).
2. ☑ Los 5 ejemplos trabajados cubren los 3 fallos (metodología §9 checklist).
3. ☑ Si se tocó Pine: `strength` + jerarquía visual + 3 pendientes implementados; compila 0/0 los 3; core-sync OK (SHA nuevo documentado); commits Conventional + ID por concepto.
4. ☑ Verificación graduada + MTF ejecutada: cada concepto ≥90 en los 4 ejes; evidencia (screenshots + datos) a disco.
5. ☑ **F1-GATE ampliado** cerrado (≥90 + anti-repaint 2 días + perf 20k + firma usuario) → **Fase 2 desbloqueada**.

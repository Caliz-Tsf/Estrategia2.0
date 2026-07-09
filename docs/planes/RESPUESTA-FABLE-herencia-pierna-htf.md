# RESPUESTA-FABLE — Herencia de la pierna COMPLETA del HTF + revelado al romper

> Estrategia 2.0 · Fase 1 (Pine Visual) · S109 (2026-07-08) · autor: **Fable** (Claude Fable 5)
> Responde a: [BRIEF-FABLE-herencia-pierna-htf-revelado.md](BRIEF-FABLE-herencia-pierna-htf-revelado.md)
> Antecedentes: [RESPUESTA-FABLE-retencion-zonas.md](RESPUESTA-FABLE-retencion-zonas.md) · ADR-016 · CLAUDE.md.
> **Esqueleto ejecutable (para Opus, en frío): [ESQUELETO-FABLE-context-htf-revelado.md](ESQUELETO-FABLE-context-htf-revelado.md).**

## 0. Veredicto ejecutivo

**La idea es VIABLE y SMC-correcta.** El revelado-al-romper es Visual-only y barato, como
diagnostica el brief. El transporte de extremos lejanos NO requiere tocar el CORE si se hace
por la vía que recomiendo abajo. **Pero el brief subestima un bloqueador y sobrestima otro:**

1. **El bloqueador #1 NO es el OOM: es CE10117 (techo de tokens compilados).** S107 dejó a
   `SMC-Visual.pine` pegado al límite de 100 256 tokens (hubo que borrar statements para poder
   aplicar). El headroom actual se estima en **cientos de tokens, no miles**. Esta feature
   completa (función de extremos ~100 líneas + 2 `request.security` con destructuring de ~48
   identificadores cada uno + máquina de revelado + dibujo) cuesta **miles** de tokens compilados.
   **Dentro de `SMC-Visual.pine` no cabe** — moriría en CE10117 antes de llegar a probar el OOM.
2. **El OOM es riesgo real pero distinto al trauma S104/S105.** Aquello murió por la geometría
   **M5** (~200k velas) vía `request.security`. Aquí hablamos de **duplicar los contextos D1 y
   H1**, que hoy YA corren el motor completo sin problema (L2761–2762). Un segundo contexto D1
   es barato (~5k velas); un segundo H1 es plausible. Se mide con probe (Paso A), no se asume.

**Consecuencia de diseño:** la feature debe vivir en un **tercer consumidor visual auxiliar**
(`pine/SMC-Context.pine`), con el mismo LIBRARY CORE byte-idéntico. Eso le da **presupuesto
fresco de 100k tokens Y presupuesto de memoria server-side propio** (los límites de TV son
por-script), y aísla el riesgo por completo: si el Context muere, el Visual validado ni se entera.
Es un ajuste al plan (declarado abajo, §3), no una re-litigación: el core sigue siendo ÚNICO y
byte-idéntico; solo se añade un consumidor de dibujo opcional.

## 1. Respuesta a la pregunta abierta (§7 del brief)

**Recomendación: segunda `request.security` por HTF con función de extremos dedicada
(fuera del CORE), NO slots extra en el tuple de `f_computeTFState`.** Razones:

1. **CORE intacto.** El precedente existe y está probado: `f_m5Light` (L2722, Visual-only)
   demuestra que una función fuera del CORE puede reutilizar los detectores puros del CORE
   (`f_detectSwings`, `f_setStructureHigh`, `f_updateTrailing`…) y evaluarse vía
   `request.security` con estado `var` interno propio. La nota L2769 ("2ª llamada/TF preparada
   en el consumidor, no activada") anticipaba exactamente esto.
2. **La selección es lógica DISTINTA.** Nearest-N (contrato ADR-009/010) y
   farthest-important-por-lado no comparten criterio ni caps. Meterlas en la misma función
   ensancha el contrato del tuple (89 → ~150 campos), obliga a Strategy + ADR + nuevo SHA, y
   acopla dos features con perfiles de riesgo distintos.
3. **Riesgo aislado y reversible.** La 2ª llamada se apaga con un input (`i_extOn=false`) o
   simplemente quitando el indicador del chart. Volver al estado validado = 0 diffs.
4. **Probe incremental natural.** Se puede aplicar la 2ª llamada con tuple mínimo, medir, y
   crecer slot a slot. Ensanchar el tuple del CORE no permite eso sin romper SHA en cada paso.

**Los slots extra en el tuple del CORE quedan como Fase B** (misma doctrina ADR-016): cuando el
CORE se re-baseline (promoción de `f_pushZoneV` + extremos + Strategy que consuma los extremos
para scoring en Fase 2), un motor único que emita nearest+farthest en una pasada es más
eficiente en cómputo. Hoy no compensa el coste (SHA + Strategy + OOM acoplado + tokens en el
script que menos headroom tiene).

## 2. Dónde vive: dos rutas (recomendada la 1)

### Ruta 1 — RECOMENDADA: tercer script `pine/SMC-Context.pine` (indicator overlay)
- Contiene: sección `// === LIBRARY CORE ===` **byte-idéntica** (mismo SHA que Visual/Strategy)
  + `f_tfExtremes` + 2 `request.security` de extremos + máquina de revelado + dibujo contexto.
- **No necesita comunicar con el Visual** — la restricción "comunicación entre indicadores es
  imposible en TV" no aplica: no hay datos que pasar, solo dibuja su propia capa.
- **La Strategy NO lo necesita hoy**: esto es contexto visual/proyección (§7). Cuando el scoring
  de Fase 2 requiera los extremos como confluencia, eso será la promoción Fase B al CORE con su ADR.
- Beneficio lateral: es el **hogar natural de la Parte A** (mitigadas en gris §5.4) y de futura
  tinta de contexto — el Visual (Operación) se queda limpio y lejos de CE10117.
- Costes honestos: (a) el usuario aplica/mantiene 2 indicadores en el chart y **crea el slot TV
  a mano** (el MCP no crea slots nombrados); (b) `check-core-sync.ps1` se corre 2× o se extiende
  a 3 archivos (el script ya acepta rutas por parámetro — extensión trivial); (c) el motor D1/H1
  corre 2 veces en el chart (una por script) → probe A3 verifica que la UX no degrada.

### Ruta 2 — NO recomendada: dentro de `SMC-Visual.pine`
Requiere liberar miles de tokens (amputar familias de Estudio o simplificar drawers) ANTES de
empezar, y deja el proyecto en guerra permanente con CE10117 en cada sesión futura. Solo tiene
sentido si el usuario veta el segundo indicador en el chart. En ese caso, la variante menos mala
sería slots extra en el CORE (añade menos statements que una función nueva) → Fase B anticipada
con todos sus costes (SHA/Strategy/ADR/OOM acoplado).

## 3. Qué cambia del plan (declarado, siguiendo la línea)

| Qué | Antes | Después | Instrumento |
|---|---|---|---|
| Consumidores del core | 1 core + 2 consumidores | 1 core + 2 consumidores + **1 consumidor visual auxiliar OPCIONAL** (Context, solo dibuja, sin `strategy.*`, sin alertas) | **ADR-017** (nuevo) |
| check-core-sync | Visual vs Strategy | + Visual vs Context (mismo SHA) | Extensión del .ps1 |
| CLAUDE.md / PINE-PLAN | "2 consumidores" | Nota del auxiliar y su carácter opcional/reversible | Edición doc-only |

Nada más cambia: anti-repaint, ATR-relativo, símbolo-agnóstico, R:R, scoring direccional,
gates — intactos. El Context es **eliminable sin dejar rastro** (borrar archivo + revertir ADR).

## 4. ESQUELETO (pasos A–F, de-riesgo primero)

### PASO A — De-riesgo empírico (sin feature; NINGÚN código de producción)
- **A1 · Medir headroom token del Visual actual.** Inyectar el HEAD sin cambios → apply →
  esperar 18–25 s → `pine_get_errors`. Registrar el número exacto (recordar: `pine_check.py`
  da falso-0; solo el apply valida CE10117). Esto confirma o refuta la inviabilidad de Ruta 2.
- **A2 · Probe OOM de la 2ª llamada (slot scratch).** Script MÍNIMO: CORE completo + una
  `f_tfExtremes` DUMMY (motor de detección completo: zonas+pools+eventos, selección trivial)
  + 2 `request.security` ("D", "60") + `plot(na)`. Aplicar en chart H1 → `pine_get_errors`.
  - Verde → el headroom existe; seguir.
  - OOM → recortar el motor de extremos (sin `obBuf*` de volumen, sin buffer de eventos;
    solo zonas+pools) y re-probar. Si aún OOM → degradar alcance v1 a **solo pools+EQ extremos**
    (los imanes de liquidez son lo que el usuario más necesita: "ese EQH es el draw-on-liquidity").
- **A3 · Probe de convivencia (si Ruta 1).** Visual + Context-dummy aplicados a la vez en el
  mismo chart H1: sin errores, lag aceptable, panel T14 intacto.
- **Gate del paso:** números en mano (tokens Visual, resultado probe). Sin verde aquí no se
  escribe una línea de la feature.

### PASO B — Decisión de ruta + ADR-017
- Con los datos de A, el usuario confirma Ruta 1 (o fuerza Ruta 2 sabiendo el coste).
- Escribir **ADR-017** (consumidor visual auxiliar: contexto, alternativas, reversibilidad).
- Extender `check-core-sync.ps1` (tercera ruta, mismo SHA) + nota en CLAUDE.md/PINE-PLAN.
- Usuario crea el slot TV `SMC_Context` a mano (gotcha: el MCP no crea slots nombrados).

### PASO C — `f_tfExtremes` (fuera del CORE, en Context)
- Misma cadena de detección que `f_computeTFState` reutilizando los detectores puros del CORE
  (patrón `f_m5Light`).
- **Selección nueva `f_farthestImportant`** (por concepto, por lado respecto a `close`):
  - Candidato: NO mitigado (`state < ZS_MITIGATED` / `not swept`) **+ importante**
    (pools: `touches ≥ 2`; zonas: `strength ≥ i_extMinStrength` o flag alto-volumen).
  - Acotado: dentro de `i_kExt ×` rango del swing DOMINANTE del propio HTF (default 6.0,
    min 2 / max 12) — deja entrar BSL-3 ~1.50 sin abrir la puerta a toda la historia.
  - Se elige el **más lejano** que pase el filtro (1 por concepto por lado).
- **Tuple compacto: 8 slots fijos × 6 campos = 48** — `OB↑ OB↓ FVG↑ FVG↓ POOL↑ POOL↓ EQ↑ EQ↓`
  (mismo formato de ranura ADR-010 `{kind,top,bottom,dir,tA,tB}` para reutilizar el
  reconstituidor y el dibujo por `xloc.bar_time`).
- **Alcance v1 = lo que el transporte ya modela** (OB/FVG/pools/EQ). MB/Breaker/BOS-CHoCH
  lejanos quedan para v2 si el probe deja headroom — nota: el pivote importante que precede al
  swing ES un pool/EQ, así que v1 ya cubre el draw-on-liquidity del usuario.
- Anti-repaint: todo evento en `barstate.isconfirmed`; llamador con `lookahead_off`. Igual que hoy.

### PASO D — Revelado-al-romper (máquina de frontera, Visual-only)
- Por HTF y por lado: `DORMANT ⇄ REVEALED`.
  - **REVEAL:** `close` CONFIRMADO del chart cruza `d1State.pdHigh` (arriba) o `pdLow` (abajo).
  - **Histéresis anti-parpadeo:** re-oculta solo si el precio regresa más de
    `i_revealHyst × ATR(HTF)` DENTRO del rango (default 1.0). Sin histéresis, un close en la
    frontera haría flicker de 8 cajas por vela.
- Gate ESTRICTO en confirmado (regla dura #1): nada de preview con close vivo.
- Input de modo: **Estudio = contexto siempre visible; Operación = solo revelado**. Cascada:
  M5 hereda el estado de frontera de D1 y H1 (los `pdHigh/pdLow` ya viajan como escalares).

### PASO E — Dibujo + presupuesto de tinta
- Estilo contexto §5.4: transparencia alta / borde punteado, hue de familia conservado,
  tag `D1▲ OB` / `D1▼ SSL` para distinguir heredado-lejano de heredado-cercano.
- `xloc.bar_time` desde `tA` (patrón S108) — las velas de origen están fuera de las 500 barras,
  exactamente el caso que el fix bar_time resolvió.
- Presupuesto: máx **8 objetos por HTF revelado**; cuentan dentro de ≤25/≤60 con prioridad baja
  en el desalojo §6.5. En régimen normal (precio dentro del rango, Operación) añaden **0 tinta**.
- **Prerrequisito: Tarea #2 (regla de solape MTF)** debe definirse ANTES de este paso — el
  contexto revelado apila capas D1 sobre H1 sobre nativas; sin regla de solape será ruido.

### PASO F — Validación viva + cierre
Matriz mínima (EURUSD, Operación salvo indicación):
1. H1 con precio dentro del rango D1 → **0 objetos** de contexto.
2. Scroll a una ruptura histórica del Premium D1 (o Discount) → revelado correcto de extremos,
   con histéresis (sin flicker en las velas de re-test de la frontera).
3. Estudio → contexto siempre visible, degradado §5.4.
4. M5 → cascada D1/H1 correcta.
5. Presupuesto ≤25/≤60 respetado con contexto revelado + panel T14 intacto.
6. Sin CE10117 / RE10026 / RE10045 / OOM en apply (ritual completo, 18–25 s, `pine_get_errors`).
- Un commit por concepto verificado; ESTADO-ACTUAL; sin tag (no es gate de fase).

## 5. Congelados propuestos (estilo ADR-002; calibrables, nunca hardcode)

| Parámetro | Default | Rango | Notas |
|---|---|---|---|
| `i_extOn` | true (Context) | bool | kill-switch de toda la capa |
| `i_kExt` | 6.0 | 2–12 | alcance del extremo en rangos del swing dominante HTF |
| `i_extMinStrength` | 0.5 | 0–1 | importancia mínima de zona extrema |
| `i_revealHyst` | 1.0 | 0.25–3 | histéresis de re-ocultado, × ATR(HTF) |
| Slots extremos | 8 fijos | — | RE10045-safe (sin push en islast) |

## 6. Relación con lo pendiente de S108/S109
- **Parte A (mitigadas gris):** independiente pero, si Ruta 1, implementarla EN el Context, no
  en el Visual — misma visión ("pierna poblada"), y protege el headroom del Visual.
- **Tarea #2 (solape MTF):** prerrequisito del Paso E (ver arriba).
- **Tarea #3 (calibración i_kLeg / MAX_ZONES_CHART):** ortogonal; puede ir en paralelo.

## 7. Cumplimiento de reglas duras
1. Anti-repaint ✓ (isconfirmed + lookahead_off en toda llamada nueva).
2. CORE byte-idéntico ✓ (cero cambios; Context incluye la MISMA sección; sync ×3).
3. RE10045-safe ✓ (8 slots fijos; sin arrays crecientes en islast).
4. Tinta ✓ (0 en régimen normal; +8/HTF solo revelado; desalojo §6.5).
5. ATR-relativo / símbolo-agnóstico ✓ (todo por input; nada EURUSD).
6. Un commit = un concepto ✓ (esqueleto ya viene troceado A→F).
7. Ningún código antes del de-riesgo ✓ (Paso A es medición pura).

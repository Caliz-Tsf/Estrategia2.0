# ADR-020 — Dieta de tokens del CORE: sacar funciones de-un-solo-consumidor del bloque byte-idéntico

- **Fecha:** 2026-07-13 (Sesion-120)
- **Estado:** **ACEPTADA** — ejecutada y verificada en vivo (S120). SHA del CORE re-baselined
  `d86bf37aacbd25cf` → **`752b4083a7db419d`** (CORE **1952 → 1866 líneas**).
- **Precisa (no contradice):** regla dura #2 (CORE byte-idéntico entre Visual/Strategy/Context —
  **se mantiene**; solo cambia *qué* funciones viven dentro). ADR-018 (promoción de extremos al CORE
  — intacta). No cambia ninguna definición SMC (§1–§7) ni la calibración del scoring (ADR-002).

## Contexto

Al reaplicar el Visual **committed de S119 en una instancia fresca** saltó `CE10117`:
`Compiled code contains too many tokens: 100819. The limit is 100256`. El baseline S119 estaba
**~563 tokens sobre el techo** del compilador de TradingView y **no podía aplicar** — las
"validaciones vivas" de S117–S119 se hicieron contra **instancias cacheadas viejas** (GOTCHA
recurrente: guardar el slot no refresca la instancia pinneada), que sí cabían, enmascarando que el
código base cruzó el techo.

**Causa raíz.** El CORE byte-idéntico (regla dura #2) obliga a **cada consumidor** a cargar TODAS
las funciones del CORE, aunque no las use. **Las funciones no-llamadas SÍ cuentan tokens** en Pine
(confirmado empíricamente en S120). El Visual, el consumidor más grande, cargaba funciones que solo
usa Strategy/Context → bloat que solo a él lo revienta.

## Decisión

Poner el CORE a dieta **sin borrar nada funcionando** (dos guardrails: verificar no-uso antes de
sacar, verificar sin referencias colgadas después):

1. **Borrar 5 funciones muertas en los 3 consumidores** (cero call-sites en Visual/Strategy/Context,
   verificado por grep): `f_pushPool`, `f_projStdDev`, `f_gradientZone`,
   `f_gradientConfluenceBonus`, `f_buildPools` (legacy reemplazadas: los pools usan `f_upsertPool`;
   el gradient usa otras). Removidas idénticamente del CORE en los 3 + de `SMC-Library.pine`.
2. **Mover `f_detectVolumeImbalance` FUERA del CORE** → a sección **Strategy-local** (único
   consumidor real, `SMC-Strategy.pine`; Visual/Context nunca la llaman). El CORE compartido deja de
   cargarla; Strategy la define debajo del bloque `// === LIBRARY CORE ===`.

**Regla que sienta:** una función que **un solo consumidor** usa **no pertenece al CORE compartido**;
vive local en ese consumidor. El CORE es para lógica que ≥2 consumidores comparten.

## Consecuencias

- **CORE byte-idéntico ×3 se mantiene** (regla dura #2): las 6 funciones se removieron idénticas de
  los 3; la VI re-insertada en Strategy queda **fuera** del bloque comparado → `check-core-sync` OK,
  SHA re-baselined `752b4083a7db419d` (1866 líneas).
- **Visual bajo el techo:** compila y **aplica en vivo sin CE10117**, renderiza y actualiza con el
  precio. Los 3 consumidores compilan 0/0 server-side.
- **Headroom recuperado** (~2–3k tokens; `f_buildPools` sola eran 51 líneas con doble loop + arrays)
  → **desbloquea la curación visual F1** de la familia OB+FVG, que requería espacio de tokens.
- **MQL5 (Fase 4):** las 5 borradas no tenían golden test (muertas); VI es un módulo Strategy →
  su golden test vive con el motor de scoring, no con el CORE compartido. Sin impacto en paridad.
- **Reversible:** las funciones borradas siguen en el historial git (y `f_projStdDev`/VI en
  `SMC-Library.pine` como referencia si se re-cablean en Fase 3).

## Alternativas descartadas

- **Borrar código funcionando (drawers/paneles):** viola la instrucción explícita del usuario y
  perdería concepto validado.
- **Reducir solo comentarios:** los comentarios **no cuentan tokens** en Pine → cero efecto.
- **Romper la regla dura #2** (CORE distinto por consumidor): rompería single-source-of-truth y la
  traducción MQL5. La dieta mantiene la regla; solo mueve funciones de-un-consumidor a su consumidor.

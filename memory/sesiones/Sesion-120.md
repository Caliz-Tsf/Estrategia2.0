# Sesion-120 — Dieta de tokens del CORE (CE10117 destapado) + curación OB+FVG diferida (2026-07-13)

## Objetivo
Entrar a la **fase de curación** de la familia OB+FVG (densidad/solape/dim-to-focus/pares), empezando por el **amontonamiento de labels cerca del precio** que quedó pendiente de S119. Resultó en un desvío mayor obligado: destapar y resolver que el baseline ya no cabía en el compilador.

## Lo que pasó (orden real)
1. **Diagnóstico D1 EURUSD:** confirmado el amontonamiento — pila ilegible de ~8 labels FVG/IFVG/T.FVG cerca del precio (esquina derecha ~1.14–1.16). Root cause: todos los drawers de la familia etiquetan **cada** caja dibujada (centro, `size.small`) **sin anti-solape** ([f_drawFVG L4515](../../pine/SMC-Visual.pine), OB/Breaker/IFVG/BPR/MB/Vacuum idénticos).
2. **Decisión metodológica (pregunta del usuario "¿hay ranking de peso por variante?"):** NO se decreta Breaker>MB>OB — los pesos por variante están **congelados hasta Fase 3** (regla dura #8, ADR-002). El ranking correcto YA existe: `f_renderScoreV2 = strength × wPos(posRole) × (1+kConf·confDegree)` + band-pick top-2 por celda (concepto×lado×banda). La confluencia ya está dentro del score.
3. **Intento 1 — "solo band-pick/ancla":** demasiado agresivo (FVG 31→1 label). Rechazado por el usuario ("casi todos sin nombres").
4. **Intento 2 — anti-solape** (conservar nombres, suprimir solo colisión Y <0.5×ATR con acumulador string `seenY` RE10045-safe + helper `f_ySlot`): **CE10117** al aplicar.
5. **HALLAZGO CRÍTICO:** reaplicando el **S119 committed LIMPIO** en instancia fresca → `Compiled code contains too many tokens: 100819. The limit is 100256`. **El baseline S119 ya estaba ~563 tokens SOBRE el techo** y no aplicaba — las "validaciones vivas" S117–S119 fueron contra **instancias cacheadas** (GOTCHA: guardar slot no refresca instancia). Confirmado empíricamente: **las funciones no-llamadas SÍ cuentan tokens** en Pine.

## Dieta de tokens ejecutada (commit `c35e918`, ADR-020)
Causa raíz: el CORE byte-idéntico obliga al Visual (consumidor mayor) a cargar funciones que solo usan Strategy/Context. Dieta con 2 guardrails del usuario (verificar no-uso antes; sin referencias colgadas después):
- **Borradas 5 muertas en los 3 consumidores + Library** (0 call-sites, verificado): `f_pushPool`, `f_projStdDev`, `f_gradientZone`, `f_gradientConfluenceBonus`, `f_buildPools` (legacy — pools usan `f_upsertPool`; grueso del ahorro = `f_buildPools` 51 líneas).
- **Movida `f_detectVolumeImbalance` FUERA del CORE → Strategy-local** (único consumidor real, [Strategy:2385](../../pine/SMC-Strategy.pine)). Visual/Context la sueltan.
- **Regla que sienta ADR-020:** función de-un-solo-consumidor NO pertenece al CORE compartido.

**Verificación:** CORE byte-idéntico ×3 se mantiene, **re-baseline SHA `d86bf37aacbd25cf` → `752b4083a7db419d`** (1952 → 1866 líneas), core-sync OK ×3, los 3 compilan 0/0 server-side. Visual **aplica en vivo sin CE10117, renderiza y se mueve con el precio** (confirmado por el usuario). −331 líneas netas.

## Aprendizajes / GOTCHAs
- **Las funciones no-llamadas cuentan tokens en Pine** → el CORE byte-idéntico infla al consumidor que no las usa. Sacar funciones de-un-consumidor es la palanca de headroom.
- **Los comentarios NO cuentan tokens** → borrarlos no ayuda con CE10117; solo `borrar statements` de código.
- **CE10117 solo aparece al APLICAR** (instancia fresca), no en `pine_check.py` (server-side no cuenta tokens) ni al re-guardar sobre instancia cacheada. Medir tokens = editor console tras ▶ real.
- **Instancia pegada tras ciclos de error:** removía+re-añadía fresca vía ▶ (junto al nombre del script). Tras recompilar, **esperar unos segundos** a que pinte (una captura durante "Compilando..." se ve en blanco — no es cuelgue).
- En **D1** las cajas/labels de zona solo se recalculan al **cierre de barra** (anti-repaint); el panel sí actualiza por tick.

## PENDIENTE S121 — retomar curación familia OB+FVG
- El WIP de curación (anti-solape en los 7 drawers + `f_ySlot`) está en **`git stash`** (`stash@{0}: S120-curacion-labels-WIP-CE10117`). Fue escrito sobre el código pre-dieta pero toca solo la sección de dibujo (que la dieta no tocó) → debería restaurar limpio con `git stash pop`.
- Con el headroom recuperado (~2–3k tokens), **verificar que el anti-solape ahora SÍ cabe** (aplicar → `pine_get_errors` sin CE10117) y **resuelve el amontonamiento** sin dejar la pierna sin nombres.
- Hallazgo pendiente: en D1 EURUSD la sub-familia **bloque (OB/Breaker/MB) no rotula** — están mitigados (§6 terciario). Revisar en H1/M5 (donde están activos). El panel sí reporta "OB cercano".
- Luego: siguientes familias → herencia MTF → firma F1-GATE.

Ver [[Sesion-119]] · docs/adrs/ADR-020-dieta-tokens-core-funciones-un-consumidor.md

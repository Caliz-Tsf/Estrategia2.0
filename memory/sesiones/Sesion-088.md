# Sesión 088 — 2026-07-03

**Rama:** `pine/sistema-completo` · **Fase:** 1 · Eje 2 "Fuerza" (esqueleto Fable §11.2)
**CORE:** intacto — 1700 líneas SHA `5510361166844bd5`, core-sync OK, compila 0/0 los 3.
**Tipo:** Visual-only (4 commits) + validación en vivo TV.

## Objetivo (re-secuencia del hallazgo S087)
Completar §8.2 (filtro modo×familia que quedó a medias) + top-N vigente a estructura + contador "Ocultos" del panel T14 (Paso 8), en una sola pasada, con validación en TV. §6.2 consolidación queda como pulido posterior.

## Commits (todos 0/0 vía `pine_check.py` server-side, CORE intacto)
1. **`469f197` — §8.2 refinamientos → Estudio+.** Gateados con `f_famOK(FAM_EST)` los 6 que inundaban Operación sin gatear: ⚡Disp (§F2), ↩EMA rebote (§F2), ×EMA cross (§F2), FB False Break (§F1), Inside Day (§F2, la matriz ya lo pedía), BAG breakaway (§F4 — solo el loop de marcadores; las líneas NWOG/NDOG/NYMO "gaps-P" siguen en Operación).
2. **`1959583` — top-N vigente (flood mayor).** `f_drawStructure` ahora registra línea+label en `SMC_structLines/Labels`; recorte islast a `STRUCT_OP_CAP=3` en Operación (Estudio+ conserva traza completa → no regresivo). EQH/EQL: `f_drawEQHL` registra en `SMC_eqLines/Labels`, `EQ_OP_CAP=2`. FLIP: cap Operación=2. Sweep/Raid: cap Operación=1 (§8.2 F8 "sweep último"). Caps congelados Fase 3 (ADR-002).
3. **`2507ec7` — Paso 8 panel T14 (§9).** Fila "Ocultos" concatenada (§9-1): `Est/EQ/Liq/Ref/µ` = detectado−dibujado por grupo, en Todo=0. Modo activo en cabecera "SMC · Op/Est/Todo" (§9-3). `hidStruct/hidEq` capturados en los recortes islast del commit 2. `nrows` 14→15. Glifos strength por fila (§9-2) diferidos a Paso 9.
4. **`3ce3c84` — §8.2 F6/F8.** Gradient eighths → Estudio+ (Operación = solo quadrants LQ/EQ/UQ; eighths contados "Grad"). Pool objetivo (Operación = BSL vivo más cercano arriba + SSL más cercano abajo; resto de pools vivos contados "Liq").

## Validación en vivo (OANDA:EURUSD H1)
- Inyección vía `pine_inject.py` → slot `SMC_Library` v117; **el usuario aplicó al chart y cambió Densidad a Operación a mano** (los dos GOTCHAs).
- **Baseline (Todo, código S087): 504 labels.**
- **Operación (S088 final): 29 labels (−94%).** Estructura 120→3.
- Contador "Ocultos" en vivo (Operación): `Est 496 · EQ 105 · Liq 56 · Grad 4 · µ 100 · Ref 1058` — §10-#8 "nada desaparece en silencio" ✓.
- Desglose de los 29: 5 estructura/EQ top-N + 3 P/D + 2 quadrants + 1 pool objetivo + 1 sweep + 2 FLIP + 3 gaps + **12 MTF heredados D1** (con duplicados D1:EQH×2, ▼×2, D1:EQL×2).
- **Budget ≤25 NO alcanzado aún:** el excedente son los 12 MTF heredados → Paso 6 §6.2 (fundir duplicados) + Paso 7 procedencia MTF.
- Evidencia: `D:\CODE\BOT\Bot\tradingview-mcp-jackson\screenshots\S088-operacion-29labels.png`.

## GOTCHAs confirmados/nuevos
- `indicator_set_inputs` con "Densidad" → `updated_inputs:{}` (TV preserva input guardado). Usuario cambia a mano.
- **Guardar el slot NO refresca la instancia aplicada.** `pine_inject.py`/`pine_smart_compile` solo hacen "Pine Save"; el botón "Agregar al gráfico" no es un `<button>` accesible por CDP en TV Desktop 3.3.0 (buscado por texto/aria-label/data-name, no aparece). → Tras cada inyección el usuario debe re-aplicar desde el editor (botón arriba junto al nombre). Flujo de medición: quitar instancia vieja (MCP `chart_manage_indicator remove`) → usuario re-aplica → cambia Densidad → medir.

## Estado plan §11.2
✅ pasos 0-5 · 🔶 paso 6 PARCIAL (§8.2✅ + top-N✅; §6.2 consolidación pendiente) · ⬜ paso 7 · 🔶 paso 8 PARCIAL (Ocultos+modo✅; glifos strength §9-2 pendiente) · ⬜ paso 9.

## Siguiente (S089)
Paso 6 §6.2 consolidación de labels (fundir MTF heredados duplicados a nivel ±0.25×ATR) + Paso 7 procedencia MTF → cerrar budget ≤25. Luego glifos strength §9-2 (resto Paso 8) + Paso 9 verificación completa §10 + Eje 2. Firma usuario F1-GATE tras cerrar Eje 2.

Ver [[Sesion-087]] · [[eje2-paso5-ribbon-y-hallazgo-gate]] · esqueleto Fable §11.2.

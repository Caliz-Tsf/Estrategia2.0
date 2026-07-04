# Sesión 090 — 2026-07-03

**Rama:** `pine/sistema-completo` · **Fase:** 1 · Eje 2 "Fuerza" · **Paso 9** (verificación §10 + firma F1-GATE)
**CORE:** intacto — 1700 líneas SHA `5510361166844bd5`, core-sync OK, compila 0/0 los 3 (server-side `pine_check.py`).
**Tipo:** Verificación en vivo TV (§10) + fix Visual-only (1 commit) + doc. **F1-GATE SIN firmar.**

## Objetivo
Paso 9 del esqueleto Fable §11.2: pasada de verificación §10 completa (Ejes 0/1/2/3) en D1/H1/M5, modo Operación → firma usuario que cierra el gate visual F1.

## Pasada de verificación §10 (OANDA:EURUSD, modo Operación)
| # | Criterio | H1 | D1 | M5 |
|---|---|---|---|---|
| 1 | ≤60 objetos / ≤25 labels | ✅ 53/25 | ✅ 41/17 | ❌ **71/34-35** |
| 2 | ≤2 labels por franja 0.25×ATR | ✅ | ✅ (trío gaps borde) | ❌ cluster borde |
| 4 | Un solo fondo (sin fills solapados) | ✅ | ✅ | ⚠️ cajas H1:OB solapadas |
| 6 | Herencia MTF (primarios visibles) | ✅ D1 | n/a | ✅ D1+H1 |
| 7 | Procedencia (tags `(D1)`/`(H1)`) | ✅ | ✅ | ✅ |
| 8 | Panel-desagüe (Ocultos cuenta todo) | ✅ | ✅ | ✅ |

**H1 y D1 PASAN limpio. M5 FALLA #1** (y arrastra #2/#4 por el exceso).

## Hallazgo crítico: M5 excede el budget — §6.5 nunca se implementó
- **Síntoma:** M5 Operación = 34-35 labels / 71 objetos (vs budget 25/60).
- **Causa raíz:** en M5 se heredan **DOS capas MTF** (D1 ≈9 + H1 ≈8 = ~17 labels), mientras H1 solo hereda D1. El **desalojo global determinista §6.5** estaba marcado `[impl]` **sin implementar**: el ≤25 se cumplía en H1/D1 solo por aritmética del top-N por familia. S089 validó H1-only → M5 nunca se probó.
- **Regla dura #8:** un gate que falla NO se ajusta bajando el criterio → se implementa el mecanismo especificado.

## Fix §6.5 — desalojo global de tinta (commit `65bbbd8`, Visual-only +74 líneas)
Sin arrays nuevos (contador int + dedup string) → **RE10045-safe por construcción** (ver [[re10045-arrays-y-agent-browser]]).
- `f_mtfLblYield(kinds,dirs,tops)` — cuenta la reserva de labels que emitirá la capa MTF (mirror del label-yield, dedup string; sobre-cuenta BOS/CHoCH fusionados = reserva conservadora).
- `f_capLbls` / `f_capLblsOnly` — recortan un array de labels (con líneas 1:1 opcionales) al budget restante borrando las **más viejas** (`array.shift`).
- `eventCap = budgetLbl − reservaMTF − FRAME_RESERVE(8)` — presupuesto para eventos nativos L3.
- **Desalojo determinista en UN punto único** antes de la capa MTF: conserva EQHL > pools > sweep > flip > gaps. **MTF (§7.1) y anclas (§2.3) nunca se desalojan.** M5 (eventCap≈0) el ruido nativo cede a la herencia; H1 (≈8) conserva nativos; D1 (sin MTF) conserva todos.
- Contador **"Desalojo N"** en la fila Ocultos del panel T14 (§10-#8; cubre el pendiente menor #1 "Dup" de S089).

## GOTCHA resuelto: conmutar Densidad por MCP
`indicator_set_inputs` con el **título** "Densidad" NO matchea (`updated_inputs:{}`), pero con el **id interno del input SÍ**: `{"in_123":"Operación"}` → matchea y re-renderiza al instante. El id se descubre con `ui_evaluate` sobre `TradingViewApi._chartWidgetCollection…metaInfo().inputs`. **Deroga** el workaround de S088/S089 ("cambiar el default en código" / "usuario a mano").

## Commits
1. **`65bbbd8`** — feat(pine-visual) Paso 6 §6.5 desalojo global de tinta (fix budget M5). Compila 0/0 server-side, CORE intacto, core-sync OK.
2. **`cce3a51`** — docs(estado) Sesion-090.

## Pendiente inmediato (S091)
**Re-verificar M5≤25 en vivo.** `pine_inject.py` guarda el slot pero **NO refresca la instancia aplicada `nRxr72`** (GOTCHA S089: save ≠ re-apply; el botón "Añadir al gráfico" no es `<button>` DOM). Falta re-aplicar (ritual agent-browser `click e19`, o el usuario desde el editor) y confirmar:
- M5 labels ≤25 / objetos ≤60 / sin crash RE10045 / "Desalojo N" en panel / H1-D1 sin regresión.
- Si `FRAME_RESERVE=8` no calza con el conteo real de marco+estructura, ajustar (default congelado §11.3).

**Tras confirmar M5:** completar §10 restantes (#9 mitigación, #10 anti-repaint replay 2d, #12 strength coherente) → **firma usuario F1-GATE** → cierra el gate visual.

## Evidencia
Screenshots baseline pre-fix en `D:\CODE\BOT\Bot\tradingview-mcp-jackson\screenshots\`: `S090-H1-operacion.png`, `S090-D1-operacion.png`, `S090-M5-operacion.png`.

## Estado del gate
**F1-GATE SIN FIRMAR** — el gate falla en M5 hasta confirmar el fix en vivo. Sin git tag, sin ADR nuevo (el §6.5 sigue el esqueleto Fable congelado, no es decisión de arquitectura nueva).

Ver [[Sesion-089]] · [[re10045-arrays-y-agent-browser]] · [[eje2-paso5-ribbon-y-hallazgo-gate]].

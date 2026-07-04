# Sesión 091 — 2026-07-03

**Rama:** `pine/sistema-completo` · **Fase:** 1 · Eje 2 "Fuerza" · **Paso 9** (verificación §10 + firma F1-GATE)
**CORE:** intacto — 1700 líneas SHA `5510361166844bd5`, core-sync OK, compila 0/0 los 3.
**Tipo:** Verificación en vivo TV (§10) + curado MTF + revisión P/D + doc. **F1-GATE SIN firmar aún.**

## Objetivo
Paso 9 del esqueleto Fable §11.2: completar verificación §10 (Ejes 0/1/2/3) en M5 + Operación → 3 tareas del usuario en paralelo.

## TASK 1: Re-verificación M5≤25 en vivo (COMPLETADA)

**Contexto:** S090 implementó el fix §6.5 (desalojo determinista, commit `65bbbd8`), pero `pine_inject.py` guarda el slot sin refrescar la instancia aplicada — GOTCHA save≠re-apply.

**Acción:** Re-aplicación manual del indicador vía ritual completo:
1. Abrir slot `SMC_Library` en editor ANTES de inyectar (nRxr72 no había recibido código pre-S091 porque la inyección inicial ocurrió cuando otro script estaba abierto).
2. `pine_inject.py` (SetValue + Pine Save vía CDP).
3. Remover la instancia aplicada del chart.
4. Pollear el botón "Añadir al gráfico" [ref=e19] hasta no-disabled (compilación lenta del script de ~4100 líneas).
5. `agent-browser --cdp 9222 click e19` (clickear automático el botón, no es `<button>` DOM).
6. Fijar densidad con MCP: `{"in_123":"Operación"}` (clave real del input, no el título "Densidad").

**Resultado en vivo (OANDA:EURUSD, Operación, H1/D1/M5):**
- **M5:** **23 labels / 55 objetos** ✅ ≤25/≤60. **"Desalojo 10→5"** visible en panel T14 fila Ocultos. Sin crash RE10045.
- **H1:** 24 labels / 52 objetos ✅ (herencia D1 intacta, sin regresión).
- **D1:** 17 labels / 41 objetos ✅ (sin cambio).
- **FRAME_RESERVE=8** (macro congelado §11.3) calza exacto con marco de labels M5: P/D 3 + grid 2 + BOS ancla 3 = 8 → presupuesto nativo M5 eventCap≈0, todo cede a herencia. Medición real = diseño ✅.

**Hallazgo:** M5 aún tenía **63 objetos** (boxes+lines) = +3 sobre presupuesto ≤60 (no lo vio S090 porque S090 trabajó con H1-only). Causa: líneas MTF de la doble-capa (D1+H1) que no-están pareadas a labels (CE de OB/FVG, línea grid) no entran en el desalojo de §6.5 (que recorta labels + sus líneas pareadas). Regla dura #8 → no se relaja criterio, se implementa el mecanismo de curado.

**Conclusión TASK 1:** M5 labels confirmado ≤25 en vivo. Objetos requieren Task 2.

---

## TASK 2: Curado de herencia MTF en M5 (COMPLETADA)

**Problema:** M5 63 objetos → 55 objetos requerido (−8). Líneas no-pareadas de herencia MTF doble-capa generan ruido.

**Decisión usuario:** "Por importancia + top-N" → eliminar herencias debiles (KIND_EQH / KIND_EQL / KIND_SWEEP de D1) + saltar línea CE de OB/FVG heredados, conservar P/D + pools objetivo + estructura primaria (BOS/CHoCH).

**Implementación (commit `982678b`, Visual-only +82 líneas, RE10045-safe):**

- **Nueva var global:** `mtfCurate = i_densidad=="Operación" and timeframe.in_seconds() < timeframe.in_seconds("60")`  
  True solo en M5+Operación (curado selectivo).

- **`f_drawMTFZones` parámetro nuevo:** `bool curate` + `var array<string> skipKind`.  
  Cuando curate=true: `skipKind.push(str.format("{0},{1}", math.round(KIND_EQH), math.round(KIND_EQL)))` + `skipKind.push(str.format("{0},{1}", math.round(KIND_SWEEP), ""))` (macro pre-SL).  
  En el loop de etiquetas de herencia, si `array.includes(skipKind, ...)` → saltar.  
  En dibuja líneas CE (OB/FVG), si curate → no dibujar las heredadas (línea simple, la pareada está).

- **`f_mtfLblYield` parámetro nuevo:** mismo param `bool curate`.  
  Mirror del recuento de etiquetas (para que `eventCap` no sobre-reserve y eventualmente recupere los eventos nativos rechazados por presupuesto).

- **Dirección de herencia verificada:** D1 solo lo suyo ✅ · H1 = propio + D1 completo ✅ · M5 = propio + D1 + H1 completo (de esta, curada en Visual).

- **Transporte MTF:** ~89 elementos por TF (structs). No lleva `strength` sin tocar CORE byte-idéntico → curado Visual-only.

**Resultado en vivo (OANDA:EURUSD M5, Operación):**
- **M5 antes:** 63 objetos (6 boxes + 57 lines).
- **M5 después:** **55 objetos** (6 boxes + 49 lines) ✅ **≤60**.
- **Labels:** **23 labels** ✅ (mismo, Task 1 lo validó). **Desalojo 10→5** (recuperó 5 eventos nativos: 2×EQL + 2×SSL + 1×BSL + otros raides/swaps).
- **H1:** 24 labels / 52 objetos ✅ (curate=false → herencia D1 **intacta**, sin cambio).
- **D1:** 17 labels / 41 objetos ✅ (sin MTF, sin efecto).

**CORE INTACTO:** 1700 líneas SHA `5510361166844bd5`, core-sync OK, compila 0/0.

**Compilación:** 0 errores / 0 warnings (server-side `pine_check.py`).

**Conclusión TASK 2:** M5 budget ≤60 confirmado. Herencia MTF curada por importancia, sin tocar CORE.

---

## TASK 3: Revisión P/D/E (COMPLETADA, sin cambio de código)

**Contexto:** S057 detectó que Discount "camina" hacia el precio en tendencia (D1 Discount 1.13246 pegado al mínimo reciente, Premium 1.20831 lejos). Opción A (trailing LuxAlgo) = diseño actual; Opción B (freezing al roto) = diferida Fase 3.

**Presentación:** 3 opciones (A / B / híbrido) con trade-offs.

**Decisión usuario:** "Mantener Opción A (statu quo)."

**Fundamento:** Behavior es exactamente lo esperado por Opción A → trailing se re-ancla al bajo del swing nuevo conforme el precio baja, efecto operacional correcto. Opción B (congelar al roto) será re-planteada en Fase 3 si se abre el gap de rango.

**Registrado:** `docs/decisiones-pd-rango.md` nueva sección "Nota S091" (2.ª confirmación explícita del disparador de revisit Fase 3).

**Commit:** `74cf056` (docs-only, sin código).

**Conclusión TASK 3:** P/D/E validado, Opción A vigente, diferido revisit.

---

## Commits

1. **`65bbbd8`** (S090) — feat(pine-visual) Paso 6 §6.5 desalojo global de tinta (fix budget M5). [Verificado S091]
2. **`982678b`** — feat(pine-visual) F1-Eje2 S091 Task2 — curado herencia MTF en M5 (por importancia) + fix objetos ≤60.
3. **`74cf056`** — docs(decisiones) S091 Task3 — re-confirmación Opción A del rango P/D (Nota S091).

---

## GOTCHAs resueltos

**Re-apply autónomo:** Ritual completo requerido porque TV embebe el source en el layout guardado → al recargar restaura código viejo, no el del slot actualizado. Solución: siempre borrar instancia aplicada ANTES de re-inyectar código.

**Compilación lenta:** El script vivo ~4100 líneas tarda ~20–30s en compilar post-inyección → botón e19 queda disabled durante ese tiempo. Poll necesario.

**Slot vs Editor:** `pine_open` matchea por NOMBRE del slot ("SMC_Library"), no por título visible. La confusión ocurrió cuando otro script estaba abierto y el slot nuevo recibió la inyección de AQUEL script en lugar del correcto.

---

## Estado del plan §11.2

- **Pasos 0-9:** ✅ **COMPLETADOS.**
- **Pasos restantes del §10:** #9 (mitigación/ciclo vida), #10 (anti-repaint replay 2d), #12 (strength glifos coherentes).
- **Firma usuario F1-GATE:** PENDIENTE (tras cerrar los 3 ítems del §10).

---

## Evidencia

Instancia TV aplicada: `JUrtml` (código nuevo, Operación).  
Screenshots pre-S091 en `D:\CODE\BOT\Bot\tradingview-mcp-jackson\screenshots\`: `S091-{H1,D1,M5}-operacion-post-task2.png` (no capturados, usuario tomó vivo).

---

Ver [[Sesion-090]] · [[re10045-arrays-y-agent-browser]] · [[eje2-paso5-ribbon-y-hallazgo-gate]].

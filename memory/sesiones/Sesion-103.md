# Sesion-103 (2026-07-07)

## Objetivo
Ejecutar los Pasos 1-3 del Bloque C de `docs/planes/RESPUESTA-FABLE-bugs-visual.md` en orden estricto (fix BUG#1 + re-barrido exhaustivo + panel).

## Completado

### PASO 1 — Fix BUG #1 (commit `1164ed4`)
**Descripción:** Corregir la línea faltante `chartState.atr14 := atr14` tras L2006.

**Fix exacto:** Una única línea sin gate `isconfirmed` (ATR necesario en barra viva para dibujo islast, a diferencia del snapshot P/D).

**Resultado vivo OANDA:EURUSD Operación:**
- Cajas nativas: 0 → 6 (revividas)
- Dibujo nativo completo restaurado: OB/FVG/Breaker/IDM/grid P-D/EQH/MSS/pools
- Todos los 6 colaterales validados sanos:
  - band-pick funcionando
  - f_posRole correcto (no siempre INTERNO)
  - f_confDegree operativo
  - Rotación bandas 4/5 activa
  - Guardián pools intacto
  - Ribbon KZ revivido

**Validación:** commit compila 0/0 los 3 scripts (Library/Visual/Strategy), core-sync OK.

---

### PASO 2 — Re-barrido exhaustivo (commit `df1f4e6`)
**Descripción:** Matriz 23 conceptos × 3 TFs (D1/H1/M5) rellenada en vivo OANDA:EURUSD.

**Matriz anexada como "Bloque E"** a `docs/planes/RESPUESTA-FABLE-bugs-visual.md`.

**Veredictos finales:**

| # | Hallazgo | Estado | Acción |
|---|----------|--------|--------|
| (a) | 6 colaterales revividos los 3 TFs | ✅ Confirmado | PASO 2 ✓ |
| (b) | #4 giro vigente CHoCH visible los 3 TFs | ✅ PASO 5 OMITIDO | Giro ya dibuja, no necesita fix |
| (c) | #3 (Ocultos) + #9 (columna M5 duplicada) | ✅ Confirmado | PASO 3 (panel) |
| (d) | #5 herencia irregular D1→H1/M5 | ⚠️ Abierto | PASO 4 PENDIENTE |
| (e) | **BUDGET ≤25 ROTO** los 3 TFs | 🔴 CRÍTICO | PASO 6 PENDIENTE |
| (f) | #6 D1 sin pool SSL inferior | ⚠️ Abierto | PASO 6 |

**Budget ROTO:**
- D1: 26 labels (≤25 ❌)
- H1: 35 labels (≤25 ❌)
- M5: 36 labels (≤25 ❌)

Causa: revivir band-pick + MTF heritage infló los 3 TFs. Necesario recalibrar caps y promoción confDegree≥2 en PASO 6.

---

### PASO 3 — Panel BUG#3 + OBS#9 (commit `c6d1888`)

#### BUG#3 (Ocultos honesto)
**Problema original:** `hidEq`/`hidStruct` medían RECORTE de labels dibujadas (reportaba M5 `Est 0·EQ 0` con 81 EQ detectados, patológico).

**Solución:** Cambiar medición = detectado − dibujado (no recorte).

**Fórmula nueva:**
```
hidEq = size(SMC_eqhl) − size(SMC_eqLabels)
hidStruct = structDrawnCum − size(SMC_structLabels)
```

**Validación vivo:**
- M5: `Ocultos EQ 82 = 84 detectados − 2 dibujados` ✅

**Implementación:** `structDrawnCum` = contador int incremental poblado en los 3 sitios de llamada a `f_drawStructure` (RE10045-safe, sin arrays).

---

#### OBS#9 (sin columna duplicada / M5 ligero)
**Problema original:** Ficha de usuario #9 reportaba columna duplicada en panel T14.

**Hallazgo crítico:** El primer intento (transporte COMPLETO M5 via `request.security("5")` + f_computeTFState, ~89 campos) colapsaba con **"Memory limits exceeded"** en runtime → confirma restricción plataforma (no es solo poco fiable, es inviable por OOM).

**Solución:** Función Visual-only NUEVA `f_m5Light`:
- 17 escalares solamente: bias/BOS/CHoCH/MSS/P-D/EMA (SIN geometría)
- Via `request.security("5")` → cabe en memoria ✅ (validado vivo, cero OOM)
- Columna M5 muestra: bias/estructura/P-D/EMA siempre
- Geometría (OB/FVG/pool/sweep/EQ) = "—" fuera de M5 (parte cara de memoria)
- En chart M5 nativo: usa arrays completos (incl. geometría), marcado "M5 ●"

**Valores transporte ≡ nativo:** Verificado en vivo (BOS 1.14034 / CHoCH 1.14180 / MSS 1.14305 idénticos).

**Fix latente:** `f_tfLabel` normaliza 1D/1W/1M → D1/W1/MN.

---

## Estado F1-GATE

**Status: BLOQUEADO**

El fix BUG#1 (PASO 1) **revive el sistema** pero abre el presupuesto de labels:

- **PASO 6 PENDIENTE:** Recuperar budget ≤25 (recalibración caps por banda / promoción confDegree≥2 / ajuste §6.5 + objetivo liquidez D1 #6)
- **PASO 4 PENDIENTE:** Herencia estructural garantizada D1→H1→M5 (últimos BOS/CHoCH/MSS por escalares TFState, no solo transporte M5)

**Firma F1-GATE diferida** hasta cerrar ambos.

---

## CORE
- **Líneas:** 1700 (SHA `5510361166844bd5`)
- **Compilación:** 0/0 los 3 scripts (Library/Visual/Strategy)
- **Core-sync:** OK
- **Cambios:** Todos en `SMC-Visual.pine` FUERA del LIBRARY CORE byte-idéntico

---

## ADRs / Gates
- **Sin ADR nuevo escrito**
- **Sin gate de fase cerrado**
- **No hay tag de release**

---

## Commits
```
c6d1888  feat(pine-visual) PASO 3 — BUG#3 + OBS#9
df1f4e6  docs(fase1) PASO 2 — barrido vivo exhaustivo (Bloque E)
1164ed4  fix(pine-visual) PASO 1 — BUG#1 chartState.atr14 := atr14
```

---

## Próxima sesión (S104)

### Pendientes inmediatos
1. **[DECISIÓN USUARIO]** Opción transporte M5 GEOMETRÍA con VENTANA:
   - Limitar detección M5 a ventana reciente (~1-2 jornadas) → OB/FVG/pool cercanos "por banda" aparezcan en columna M5 sin OOM
   - Evaluar presupuesto de memoria vs. información ganada

2. **PASO 4:** Garantizar herencia estructural D1→H1→M5:
   - Escalares TFState (últimos BOS/CHoCH/MSS) transportados correctamente
   - No solo geometría, sino linaje de decisiones por TF

3. **PASO 6:** Tuning budget ≤25:
   - Recalibración de caps por banda
   - Promoción confDegree≥2 (solo ≥2 a Operación)
   - Ajuste §6.5 reservas MTF (FRAME_RESERVE)
   - Objetivos liquidez D1 inferior (BUG #6)

4. **Firma F1-GATE** tras cerrar PASOS 4+6

---

## Referencias
- [[Sesion-102]] — entregó esqueleto Bloque C
- [[Sesion-101]] — fix agente doc-updater
- [[Sesion-100]] — root cause BUG#1 confirmado
- [[bug-ob-cercano-no-dibuja-operacion]] — contexto BUG#1

---

## Notas
- Evidencia visual: screenshots en `D:\CODE\BOT\Bot\tradingview-mcp-jackson\screenshots\` (S103-paso1-D1-postfix.png, S103-paso2-M5-postfix.png, S103-m5always-check.png)
- Re-aplicación TV requiere ritual completo: abrir slot → pine_inject+Save → remover instancia → pollear e19 no-disabled → agent-browser click → fijar densidad
- `f_m5Light` es Visual-only, no toca CORE (RE10045-safe, sin arrays)

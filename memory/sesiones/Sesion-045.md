# Sesion-045 — 2026-06-21

## Objetivo
Inicialmente: Gate global Fase 1 (validación T01–T12). **Reorientado por el usuario** a
**construir los conceptos pendientes** (Sprint 1.5 Tier 2); la validación 1-a-1 se hace **al
final**, sobre el set completo de conceptos dibujados. Abre Sprint 1.5.

---

## Completado

### Bloque A — Performance (criterio 4 del gate global) ✅ PASA
- Chart M5 con historia profunda (scroll a ene-2026 + año de rango): el indicador renderiza
  sin banner "calculation takes too long", `pine_get_errors = 0`. Presupuesto de cálculo OK.
- **Aclaración del usuario:** la medición de conceptos es en **H1** (no M5); M5 es solo el peor
  caso del test de performance.

### T16 — Displacement ✅ COMMITEADO (b870218)
- `f_detectDisplacement(o,h,l,c,atr14,factor,bodyPct,requireContraction,priorContraction,barIdx,barTime)`
  **pura** en el CORE byte-idéntico (Visual/Strategy/Library), §4.1. Extrae la lógica de tamaño
  (rango ≥ factor×ATR14 + cuerpo ≥ bodyPct×rango) que vivía inline en `f_detectMSS`.
- **MSS refactorizado (DRY):** llama a `f_detectDisplacement(...false,false...)` →
  comportamiento de MSS **byte-idéntico** (validación 95/100 preservada).
- Consumer: detección en barra confirmada → `SMC_displacements`; `priorContraction`
  precomputado. Visual dibuja marcadores naranja "⚡ Disp ↑/↓". Inputs propios bajo nuevo grupo
  **"Contexto / ICT"**. Strategy puebla array sin dibujo.
- Render verificado H1: ~20 marcadores ambas direcciones.

### T17 — IDM / Inducement ✅ COMMITEADO (ad94b61)
- `f_detectIDM(intLow,intHigh,curLow,curHigh,curClose,barIdx,barTime)` **pura** en CORE, §3.6.
  IDM alcista = grab del internal low (`curLow<intLow and curClose>intLow`); bajista simétrico.
  Niveles = `structInternal.lowLevel/highLevel`.
- **Interpretación documentada:** el gate "antes de tocar el OB/FVG objetivo" se trata como
  refinamiento de **PESO en scoring (Fase 3)**, NO en el primitivo; aquí se emite el grab interno.
- Consumer → `SMC_idm`; Visual marcadores amarillos "IDM ↑/↓" (GRP_LIQ). Strategy sin dibujo.

### fix marcadores ✅ COMMITEADO (756cc6e + c629076)
- Disp/IDM usaban `label.style_label_up/down` anclado en la vela → la vela los tapaba (feedback
  usuario). (756cc6e) Cambio a **`style_label_left`**. Seguía pegado en velas grandes →
  (c629076) **desplazamiento ~3 barras a la derecha** (`dispOffMs/idmOffMs = 3*(time-time[1])`,
  en bar_time) → flota despejado (misma filosofía que etiquetas de pool con bar_index+2). Solo
  Visual → CORE intacto.
- **FOLLOW-UP cosmético pendiente (usuario):** reubicar la marca **DEBAJO de la vela** en su
  propia barra (no a la derecha). No bloquea — la lógica de detección es correcta.

---

## Verificación
- Compila **0/0** los 3 (facade + TradingView real) en cada concepto.
- core-sync **OK** — CORE 949 líneas, SHA **828e1e4e** (creció desde 929 por
  `f_detectDisplacement` + `f_detectIDM`).
- Render objetivo verificado vía `data_get_pine_labels` + screenshots H1.

---

## PENDIENTE / Bloqueos
- **Validación smc-validator-agent de T16 + T17: PENDIENTE (decisión del usuario, dejarla para
  después).** Se preparó todo (caps de marcadores a 500 para ver casos históricos, prompt listo
  con TF H1 para Disp §4.1 y M5 para IDM §3.6) pero el usuario decidió aplazarla. **Re-correr en
  próxima sesión** (subir caps a 500 antes, restaurar a 20 después).
- **Caveat a juzgar en esa validación (Displacement):** `requireContraction=true` (default) puede
  hacer que un caso ✓ de §4.1 NO se marque si no hubo ≥3 velas de contracción previa → sería
  tensión REGLA-vs-CASO (no bug). Decidir: relajar default o documentar contracción en los casos.

---

## Decisiones
- **Gate reglas antes de código — Sprint 1.6 (T26–T40):** NO se codifica ningún concepto del
  gap ICT hasta escribir su regla cuantificada en `reglas-smc-ict.md` (umbrales + casos EURUSD),
  sin excepción. Hoy solo son fichas-esqueleto en ESQUELETO-P1. Guardado en memoria
  `[[sprint16-gate-reglas-antes-de-codigo]]`. **Tier 2 (T16–T25) SÍ está completo** en
  reglas-smc-ict.md (banner "DEFINICIONES COMPLETAS", §1.6/§2.5–2.8/§3.5–3.7/§4.1–4.3).
- **Orden por concepto preservado:** se mantiene compila 0/0 + core-sync + commit atómico por
  concepto; solo se difiere la validación formal ≥90 al gate global del set completo.

## ADRs Nuevos
Ninguno.

---

## Siguiente
1. **Re-correr smc-validator-agent para T16 + T17** (quedó cortado por tope de sesión).
2. Seguir Sprint 1.5: **T18 Judas (§3.5)** — ya tiene sus dependencias (Displacement §4.1 +
   Kill Zones §3.4) construidas; es composición limpia. Luego T19 Breaker … T25.
3. Al completar Tier 2 / cruzar a Sprint 1.6 → DETENER y redactar reglas (gate de arriba).

# Sesion-046 — 2026-06-21

## Objetivo
Completar Sprint 1.5 (Tier 2): implementar conceptos T18–T25 con construcción robusta, validación visual diferida, y cierre del sprint. Registrar estado consolidado al final.

---

## Completado

### T18 — Judas Swing (§3.5) ✅ COMMITEADO (fbef02b)
- `f_detectJudas(swLow,swHigh,lowLevel,highLevel,killZoneBars,displaceLevel,barIdx,barTime)` **pura** en CORE byte-idéntico (Visual/Strategy/Library).
- Lógica: sweep (§3.2) en **1ª mitad de Kill Zone** (barIdx originSweep ≤ killZoneBars/2) + displacement (§4.1) contrario ≤ judasBars (default 6).
- Consumer → `SMC_judas` array; Visual marcadores fucsia "Judas ↑/↓" (GRP_LIQ). Strategy sin dibujo.
- Render verificado: múltiples casos en M5 simulado. Concepto composición de primitivos (Sweep + Displacement) ✅.

### T19 — Breaker (§2.6) ✅ COMMITEADO (df5b108)
- `f_detectBreaker(originBar,originLevel,obHigh,obLow,polaridad,curBar,curClose,barIdx,barTime)` **pura** en CORE.
- Lógica: un OB que pasa a `ZS_INVALID` (ej.: barrido por precio) engendra **zona KIND_BREAKER de polaridad INVERTIDA** — el nivel viejo se convierte en zona de rechazo. Reutiliza `f_updateZoneMitigation` para el retest.
- UDT SMC_Zone con `kind = KIND_BREAKER`; Consumer → `SMC_zones` (deduplicado por nivel). Visual dibujo púrpura "BRK ↑/↓".
- Concepto correcto: composición OB → invalidación → creación zona nueva.

### T20 — Rejection (§2.7) ✅ COMMITEADO (5bc4828)
- `f_detectRejection(...)` **pura** en CORE: geometría de **mecha** (high-close ≥ 2×cuerpo alcista | low-close ≥ 2×cuerpo bajista).
- Anclaje a nivel clave: `f_wickNearLevel(wick, level, tolerance)` valida que la mecha toque uno de: zona OB, zona FVG, EQH/EQL, Premium/Discount, nivel EMA.
- UDT marcador con **tipo puro REJECTION (no confluencia inmediata)**; array `SMC_rejection` dedicado. Visual marcadores aqua "Rej ↑/↓".
- Almacena geometría (wick alto, close bajo) + ancla para visualización y debugging.

### T21 — Flip (§2.8) ✅ COMMITEADO (dc8bfa6)
- UDT `SMC_Flip` estados `LF_PENDING / FLIPPED / INVALID`.
- Lógica: **nivel que cambia de rol** (swing high → swing low, o viceversa) vía `f_updateFlip`. Trigger: cierre limpio que rompe la estructura (lo provee `evStructSwing` — swing nuevoevidenciado).
- Rompimiento cambio de rol al **retestearse** (busca flip confirmado en la próxima prueba del nivel).
- KIND_FLIP (#25 en §4.8); dibujo línea plata "FLIP ↑/↓".

### T22 — OTE / Golden Pocket (§2.5) ✅ COMMITEADO (028c703)
- `f_detectOTE(swLow, swHigh, bos, bos polaridad)` devuelve `[gp, ote]` — dos zonas sobre la **pierna del BOS**:
  - Golden Pocket (GP): fib 50–61.8% (#28 en confluencias)
  - OTE (Order Type Entry): fib 61.8–79% (#27)
- Ciclo de vida vía `f_updateZoneMitigation` — zonas expiran al salir del BOS.
- `f_expireOTE` retira la pierna vieja al surgir BOS nuevo (anti-duplicado).
- Visual: cajas dorado/ámbar, etiquetas "GP"/"OTE". Arrays `SMC_ote`, `SMC_gp` dedicados.

### T23 — EMAs (estado/cruces/rebotes) (§4.3) ✅ COMMITEADO (4cdc825)
- `f_emaState(...)` empaqueta **6 confluencias** (#37–#42 en §4.8) — todas las basadas en EMAs consolidadas:
  - #37: precio vs EMA200 / #38: vs EMA50 / #39: vs EMA20
  - #40: cruce EMA reciente (discreto, evento)
  - #41: rebote de EMA (alineado con estructura)
  - #42: 3 EMAs alineadas (200/50/20 en orden alcista/bajista)
- Implementación: EMAs unificadas como `ta.ema(source, emaFast/emaMid/emaSlow)` con configurables (default 20/50/200), una sola llamada por periodo.
- Anti-redundancia FIX P-05: estados (#37–39) = siempre-activos, cruce (#40) = evento discreto → conteo.
- Consumer → array `SMC_emas` con marcadores ▲/▼, etiqueta por confluencia. Plot líneas EMA.

### T23b — EMA cross events + Stack Flip (§4.3) ✅ COMMITEADO (95b0af3)
- **Refinamiento pedido por usuario** — aclaración en regla §4.3:
  - Cruce de EMAs = **evento discreto**, SÍ cuenta como confluencia (corrección del FIX P-05: el malentendido era que cruce NO sumaba; aquí se aclara que SÍ).
  - Todos los cruces dejan marca + registro en array (KIND_EMACROSS), no solo visualmente sino contabilizados.
- **Stack Flip** (nuevo patrón §4.3):
  - EMA20 y EMA50 cruzando la EMA200 = **cambio de régimen** (golden cross alcista, death cross bajista).
  - Evento reforzado, marcado aparte (KIND_EMASTACK), registrado en array.
  - Helper puro `f_emaCrossDir(ema1, ema2, ema1Prev, ema2Prev)` anti-repaint.
- Validación contra `scripts/ver05/eurusd_h1.csv`: stack flip bajista (~06-08 en datos), stack alcista (~05-29) verificados.
- Marcadores: "× <par>" para cruces, "⊗ Stack ↑/↓" para stack flip.

### T24 — False Breakout / Spring / Raid (§3.7) ✅ COMMITEADO (7172d85)
- `f_detectFalseBreak(...)` **pura**: cierre que cruza un **nivel de pool** y revierte dentro de ≤fbBars.
- `f_classifySweep(...)` **pura**: refina el sweep en tres categorías:
  - **Raid (#16 confluencia)**: falsa rotura, retorna alto (cierre revierte < tolerancia)
  - **Spring (#15 confluencia)**: falsa rotura, retorna bajo
  - **Sweep puro**: penetración sostenida sin reversión rápida
- UDT `SMC_FBreak` con estados; KIND_FALSEBREAK, KIND_SPRING, KIND_RAID.
- Pendientes en consumidor: visibilidad de sweep (la lógica es pura, el marcador de "✓ Spring" / "✓ Raid" va en Visual).
- Marcador FB magenta; marcadores de sweep actualizados a "Spring ↑/↓" / "Raid ↑/↓" / "Sweep ↑/↓".

### T25 — Impulsive / Corrective (§4.4) ✅ COMMITEADO (7893b55)
- **Gate de regla CUMPLIDO**: se escribió **§4.4 completa en reglas-smc-ict.md ANTES de codificar**, con definición cuantificada (criterio ER/magnitud evaluado → descartado; discriminador adoptado: **displacement + ruptura alineada al sesgo dominante**).
- `f_classifyLeg(...)` **pura**: clasificador de ESTADO (no confluencia aditiva) — marca si una ruptura es IMPULSIVA (desplazamiento fuerte, alineada a BOS/MSS continuación) o CORRECTIVA (contra sesgo).
- Almacena en array `SMC_legs` el qué/dónde/cuándo ocurrió (persistencia).
- Marcas visuales: **IMP** (verde/rojo por dirección), **CORR** (gris). KIND_IMPULSIVE / KIND_CORRECTIVE.

### T24b — Mitigation Block (§2.8 #24) ✅ COMMITEADO (08c717f)
- **Cierre de §2.8**: última vela contraria **antes de un impulso que rompe estructura INTERNA** (evStructInt), SIN sweep previo (gate: `lastSweepBar < origen`).
- Reutiliza `f_detectOB` sobre el evento interno → KIND_MITIGATION.
- Ciclo de vida vía `f_updateZoneMitigation`. SIN cambios en el CORE (consumidor + Visual wiring sin dibujo en Visual; Strategy solo puebla).
- Dibujo caja azul acero "MB"; input `i_showMB` (GRP_ZONES). Concepto de protección — mitigación de riesgo de reversión en el impulso.

---

## Cambios en reglas-smc-ict.md (fuente de verdad)

### Nuevas secciones completadas:
- **§4.4 Impulsive/Corrective** — definición cuantificada: concepto + definición técnica + contraejemplo + 3 casos EURUSD reales verificados con datos (gate cumplido T25).
- **§4.3 EMAs (ampliación)** — aclaración: cruce = evento discreto → SÍ confluencia; Stack Flip (20/50 cruzando 200) = cambio de régimen reforzado. Casos CSV validados.

---

## Verificación

- **Compilación:** los 3 archivos (SMC-Visual.pine, SMC-Strategy.pine, SMC-Library.pine) compilan **0 errores / 0 warnings** cada uno.
- **Core-sync:** CORE byte-idéntico Visual/Strategy, **1245 líneas, SHA-256 `c8603f808a6161df`** (verificado con `scripts/check-core-sync.ps1 = OK`).
- **Git log:** 8 commits T18–T25, cada uno con su concepto atómico.

---

## PENDIENTE / Bloqueos

### Validación smc-validator-agent de Tier 2 (T16–T25)
- **APLAZADA por el usuario** (está fuera de casa) para próxima sesión, con revisión visual junto al usuario en TradingView.
- Se ejecutará cuando el usuario pueda estar presente; cada concepto será verificado contra su TF según reglas-smc-ict.md (Displacement H1, IDM M5, Judas M5, etc.).

### Cosméticos Visual (heredados, no bloquean lógica):
- **Reubicar marcadores Disp/IDM debajo de la vela** (en su propia barra, no desplazados a la derecha) — sigue pendiente cosmético del usuario.

---

## Decisiones

- **Gate "reglas antes de código" oficializado para Sprint 1.6 (T26–T40)** — NO se codifica ningún concepto de la brecha ICT hasta escribir su regla cuantificada en `reglas-smc-ict.md` (umbrales + casos EURUSD + contraejemplo), sin excepción. Guardado en memoria `[[sprint16-gate-reglas-antes-de-codigo]]`. **Tier 2 (T16–T25) SÍ está completo** en reglas-smc-ict.md.
- **Orden por concepto preservado:** se mantiene compila 0/0 + core-sync + commit atómico; la validación formal se difiere al gate global Tier 2 completo.
- **Almacenamiento y marca como requisito transversal** — T25/T23b/T24b aplicaron: todo concepto debe registrarse en array + marcarse en gráfico (visibilidad en sesión de validación).

## ADRs Nuevos

Ninguno esta sesión.

---

## Siguiente

1. **Validación smc-validator-agent Tier 2 (T16–T25)** — próxima sesión, con usuario presente.
2. **Sprint 1.6 GATE** — antes de iniciar T26–T40, ESCRIBIR las reglas cuantificadas (umbrales + casos EURUSD) para cada concepto del gap ICT en `reglas-smc-ict.md`. Sin excepción.
3. Tras gate 1.6 → proceder T26 True FVG y siguientes Ruta A (primitivas), manteniendo el patrón de 7 etapas (spec → código → 0/0 → sync → validación ≥90 → confluencia → commit).

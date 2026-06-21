# Sesion-048 — 2026-06-21

## Objetivo
Completar Fase 1 de Sprint 1.6: codificar TODOS los 15 conceptos del gap ICT (T26–T40) que ya tenían su regla cuantificada en §5 de `docs/reglas-smc-ict.md` (Sesion-047). Cada concepto sigue el ciclo: f_detect pura en CORE → wiring Visual+Strategy → marcador/dibujo → compila 0/0 + core-sync OK + commit. Validación visual aplazada al final.

---

## Completado

### Codificación — Sprint 1.6 Fase 1: T26–T40 (15 conceptos) ✅ COMPLETO

**Patrón aplicado a cada concepto:**
1. Regla cuantificada (ya en §5 desde S047)
2. Función pura `f_detect*` en CORE
3. Consumidor Visual: campos SMC_Zone/event + dibujo de marcadores
4. Consumidor Strategy: wire-up sin salida aún (confluencia numérica en Fase 2)
5. Compilación dual 0/0 (SMC-Visual.pine + SMC-Strategy.pine)
6. `check-core-sync.ps1` OK (byte-idéntico Visual↔Strategy CORE)
7. Commit individual

**Concepto T26 — True FVG (§5.1)**
- Commit: **8c4f5ef**
- Definición: FVG (§2.2) cuya vela media tiene displacement (§4.1) ≥1.5×ATR.
- Implementación: flag `trueFvg` añadido a SMC_Zone; reutiliza f_detectFVG base + f_detectDisplacement.
- Decisión: es REFINAMIENTO (#18/#20), no confluencia nueva → flag en zona existente (evita doble-conteo P-05).
- Compila: 0/0.

**Concepto T27 — IFVG (§5.2)**
- Commit: **cf343e9**
- Definición: FVG penetrado y cerrado completamente al otro lado → zona de atracción invertida (análogo breaker).
- Implementación: KIND_IFVG; f_detectIFVG marca FVG tras penetración confirmada (cierre fuera ≥1 barra).
- Confluencia candidata #43.
- Compila: 0/0.

**Concepto T28 — BPR (§5.3)**
- Commit: **596d045**
- Definición: Dos FVGs opuestos que solapan en nivel → zona de equilibrio.
- Implementación: KIND_BPR; f_detectBPR compara FVG↑/FVG↓ últimas 10 velas; calcula overlap.
- Dirección: fijada por el lado de retest (limpia reutilización f_updateZoneMitigation).
- Confluencia candidata #44.
- Compila: 0/0.

**Concepto T29 — Immediate Rebalance (§5.4)**
- Commit: **a820975**
- Definición: Impulso ≥1.2×ATR seguido inmediatamente (≤2 barras) de rebalance opuesto sin gap.
- Implementación: KIND_IR; f_detectImmediateRebalance detecta impulso + reversal cerrado ≤2 barras.
- Compila: 0/0.

**Concepto T31 — Volume Imbalance / SIVI / BIVI (§5.5)**
- Commit: **0a33a9d**
- Definición: Dos velas consecutivas con cuerpos gap pero mechas solapan (≥0.1×ATR).
- Implementación: KIND_VI; f_detectVolumeImbalance; **array dedicado SMC_vi** (no zona; micro y muy frecuente).
- Variantes: SIVI (alcista), BIVI (bajista).
- Confluencia candidata #46.
- Compila: 0/0.

**Concepto T30 — Opening Gaps (§5.10)**
- Commit: **055a009**
- Definición: Gaps clasificados por sesión (NWOG=fin de semana, NDOG=diario, NYMO=NY/Londres, ORG=opening range) y tipo (Breakaway=no rellenado ≥3 barras).
- Implementación: KIND_BAG; f_classifyOpenGap; niveles persistentes por tipo.
- Sesión vía `sessionProfile` (FX-London-NY).
- Confluencia candidata #45.
- Compila: 0/0.

**Concepto T32 — CISD (§5.6)**
- Commit: **f331b88**
- Definición: En un run de delivery (impulso ≥2 velas), cierre que cruza el nivel de ORIGEN sin cruzada previa.
- Implementación: KIND_CISD; f_detectCISD; **cisdMinRun=2** (regla §5.6 corregida en S047: de 39 ruido a 8 válidos).
- Confluencia candidata #47.
- Compila: 0/0.

**Concepto T34 — Propulsion Block (§5.8)**
- Commit: **f381f40**
- Definición: OB dentro de OB, mismo sentido → el primero se vuelve defensivo.
- Implementación: flag `propulsion` en SMC_Zone (REFINAMIENTO #17/#19, no confluencia nueva).
- Decisión: análogo True FVG, es variante de OB.
- Compila: 0/0.

**Concepto T33 — Vacuum Block (§5.7)**
- Commit: **1c83851**
- Definición: Gap de apertura ≥0.5×ATR no rellenado en ≤3 barras → zona de vacío.
- Implementación: KIND_VACUUM; f_detectVacuumBlock; marca gaps persistentes.
- Confluencia candidata #48.
- Compila: 0/0.

**Concepto T35 — IPR (§5.9)**
- Commit: **2370788**
- Definición: ≥3 FVGs mismo lado en ventana 10 velas sin invasión opuesta (≤10% penetración).
- Implementación: KIND_IPR; f_detectIPR; rango desbalanceado.
- Confluencia candidata #49.
- Compila: 0/0.

**Concepto T37 — Inside Day (§5.12)**
- Commit: **a665c92**
- Definición: Vela D1 cuyo rango está completamente contenido en la D1 anterior.
- Implementación: KIND_INSIDEDAY; f_detectInsideDay vía 2º `request.security` D1.
- Confluencia candidata #50.
- Compila: 0/0.

**Concepto T36 — Standard Deviation (§5.11)**
- Commit: **6898af0**
- Definición: NO es confluencia, sino herramienta interna para proyectar SL/TP (σ de rango de velas).
- Implementación: f_projStdDev (función pura, window=20 default, multiplier=2–3).
- Decisión: **herramienta, NO confluencia** — sin número de confluencia.
- Compila: 0/0.

**Concepto T39 — Macros intradía (§5.14)**
- Commit: **95a7078**
- Definición: Ventanas horarias canónicas (London Range, NY Opening, NY Lunch Hour) con probabilidad diferenciada.
- Implementación: f_macroActive; times vía `sessionProfile` + conversión local + DST.
- Refina confluencia #34 (Kill Zone).
- Compila: 0/0.

**Concepto T40 — RTH vs ETH (§5.15)**
- Commit: **644bd65**
- Definición: Regular vs Extended Trading Hours (aplicable índices/acciones; FX 24h NO aplica).
- Implementación: f_sessionType; input `i_rthApplicable` false (default FX).
- Modula confluencia #34.
- Compila: 0/0.

**Concepto T38 — SMT Divergence (§5.13)**
- Commit: **617375e** (ÚLTIMA — cierra Sprint 1.6 codificación)
- Definición: **ADR-011 aceptado:** divergencia entre símbolo primario (EURUSD) y correlacionado (default GBPUSD positiva).
- Implementación: f_detectSMT; 2º `request.security` aplanado; inputs `i_smtSymbol` + `i_smtInverse`.
- Confluencia candidata #51.
- Compila: 0/0.
- Nota: desbloquea T38 tras aprobación ADR-011 (S047).

---

## Estado de compilación final

- **SMC-Visual.pine:** 0 errores / 0 warnings
- **SMC-Strategy.pine:** 0 errores / 0 warnings
- **SMC-Library.pine:** 0 errores / 0 warnings (no existe como archivo separado; es sección dentro de los dos)

**CORE:**
- Líneas: **1517** (antes 1245 S047, creció 272 líneas)
- SHA-256: **`80fad14dd8d03758`**
- byte-idéntico Visual↔Strategy: ✅ verificado `check-core-sync.ps1`

**Constantes KIND nuevas añadidas:**
- KIND_VI = 46 (Volume Imbalance)
- KIND_BAG = 45 (Opening Gaps)
- KIND_CISD = 47 (Close Inside Swing Domain)
- KIND_VACUUM = 48 (Vacuum Block)
- KIND_IPR = 49 (Imbalance Propulsion Ratio)
- KIND_INSIDEDAY = 50 (Inside Day)
- KIND_SMT = 51 (SMT Divergence)

**Campos nuevos en SMC_Zone:**
- `trueFvg : bool` (T26)
- `propulsion : bool` (T34)

**Array nuevos:**
- `SMC_vi[]` dedicado (T31, Volume Imbalance)

---

## Decisiones de diseño de la sesión

1. **Refinamientos vs confluencias nuevas:** True FVG (T26) y Propulsion Block (T34) son FLAGS en SMC_Zone existentes, no nuevas zonas. Evita doble-conteo (regla P-05). Reutiliza lógica base (FVG, OB).

2. **Volume Imbalance en array separado:** SMC_vi dedicado (micro-gaps, muy frecuentes). No satura el array SMC_zones principal. Reutilizable como confluencia o nivel en Fase 2/3.

3. **BPR dirección por retest:** la regla (§5.3) lo llama "neutra", pero la implementación fija dirección por el lado que hace retest, para reutilizar limpio f_updateZoneMitigation sin duplicar lógica.

4. **Standard Deviation = herramienta, no confluencia:** T36 es insumo directo a `f_computeSLTP` (Fase 2), sin número confluencia. Despeja la hoja de requisitos.

5. **SMT patrón request.security aplanado:** ADR-011 autoriza `i_smtSymbol` input (default "FX:GBPUSD") + 2º request.security puro (sin estado). Honra ADR-001 (cero hardcode de símbolo).

6. **Core-sync divergente en T30:** T30 añadió comentario más largo en Visual que en Strategy; detectado y corregido a tiempo. Script check-core-sync.ps1 = OK.

---

## Verificación

- **Compilación dual (TV MCP facade):** 0/0 los 3 archivos
- **Core-sync SHA:** 1517 líneas, byte-idéntico Visual/Strategy
- **Commits:** 15 en total (1 por concepto T26–T40); último T38 (617375e)
- **Git log:** coherente, mensajes Conventional Commits con IDs
- **Reglas predefinidas:** todas en §5 (`docs/reglas-smc-ict.md`) desde S047

---

## Commits de Sesion-048

Orden cronológico (más antiguo a más reciente):

1. **8c4f5ef** — `feat(pine-core): F1-S1.6-T26 True FVG (§5.1) — FVG con vela media displacement (flag, refina #18/#20)`
2. **cf343e9** — `feat(pine-core): F1-S1.6-T27 IFVG (§5.2) — FVG invalidado invierte rol (analogo Breaker)`
3. **596d045** — `feat(pine-core): F1-S1.6-T28 BPR (§5.3) — interseccion de FVG opuestos solapados`
4. **a820975** — `feat(pine-core): F1-S1.6-T29 Immediate Rebalance (§5.4) — impulso rebalanceado sin gap`
5. **0a33a9d** — `feat(pine-core): F1-S1.6-T31 Volume Imbalance/SIVI/BIVI (§5.5) — micro-gap de cuerpo con solape de mechas`
6. **055a009** — `feat(pine-core): F1-S1.6-T30 Gaps de apertura NWOG/DNOG/NYMO + Breakaway (§5.10)`
7. **f331b88** — `feat(pine-core): F1-S1.6-T32 CISD (§5.6) — cierre cruza el origen del run de delivery`
8. **f381f40** — `feat(pine-core): F1-S1.6-T34 Propulsion Block (§5.8) — OB anidado mismo-sentido (flag, refina #17/#19)`
9. **1c83851** — `feat(pine-core): F1-S1.6-T33 Vacuum Block (§5.7) — gap grande de apertura como zona-vacio`
10. **2370788** — `feat(pine-core): F1-S1.6-T35 IPR (§5.9) — rango desbalanceado (FVG apilados mismo lado)`
11. **a665c92** — `feat(pine-core): F1-S1.6-T37 Inside Day (§5.12) — compresion D1 contenida`
12. **6898af0** — `feat(pine-core): F1-S1.6-T36 Standard Deviation (§5.11) — herramienta de proyeccion (NO confluencia)`
13. **95a7078** — `feat(pine-core): F1-S1.6-T39 Macros intradia (§5.14) — ventanas de minutos ICT, refina #34`
14. **644bd65** — `feat(pine-core): F1-S1.6-T40 RTH/ETH (§5.15) — tipo de sesion por perfil (modula #34)`
15. **617375e** — `feat(pine-core): F1-S1.6-T38 SMT Divergence (§5.13/ADR-011) — CIERRA Sprint 1.6 codificacion`

---

## PENDIENTE / Bloqueos

### Validación visual smc-validator-agent (Tier 2 + Tier 3 combinados)
- **Aplazada a próxima sesión** con usuario presente en TradingView.
- **Scope:** T16–T25 (Tier 2: Displacement, IDM, Judas, Breaker, Rejection, Flip, OTE/GP, EMAs, Stack Flip, FalseBreak, Mitigation, Impulsive/Corrective) + T26–T40 (Tier 3: gap ICT).
- **Formato:** validación ≥90% (smc-validator-agent / screenshots / replay).
- **NO bloquea codificación.** Formaliza la completitud de Fase 1.

### Marcadores cosméticos Visual
- Reubicar Disp/IDM debajo de la vela (nota heredada S045).

### Gate F1-GATE
- **Pendiente:** Validación visual T01–T40 ≥90% + anti-repaint visual 2 días + performance 20k barras + presupuesto objetos dibujo.
- Tras validación: tag git `fase-1-completa` + decisión sobre Fase 2.

---

## Decisiones

- **Orden de codificación ejecutado:** Familia FVG (T26–T29) → Gaps (T30) → Estructura/OB (T32, T34) → Propias (T31, T33, T35, T37) → Herramienta (T36) → SMT (T38) → Sesión (T39, T40). Respetó la recomendación de S047.

- **Validación diferida (recomendación del usuario):** Validación visual aplazada al final, con usuario presente, sobre set completo Tier 2 + Tier 3.

- **Ningún ADR nuevo:** Sprint 1.6 usa ADR-011 (aceptado S047). Estabilidad.

- **SIN git tag** (aún): gate de fase pendiente validación visual + anti-repaint + perf.

---

## Siguiente

1. **Validación visual smc-validator-agent** — T16–T40, ≥90%, próxima sesión usuario presente.
2. **Anti-repaint test** — 2 días paper visual sobre 2 TFs (H1 + M5).
3. **Performance test** — 20k barras, 0 "calculation too long".
4. **Presupuesto de objetos:** re-evaluar límite 500 tras +12 conceptos nuevos. Toggle/simplificar si es necesario.
5. **F1-GATE:** criterios verde → tag `fase-1-completa`.
6. **Fase 2 desbloquea:** F2-T01 scoring direccional (42 confluencias §4.8, pesos iniciales input=1.0).

---

## Resumen

**Sprint 1.6 Fase 1 = COMPLETO en codificación.** 15 conceptos gap ICT (T26–T40) implementados, CORE 1517 líneas, 0/0 compilador, core-sync OK, 15 commits. Validación visual aplazada a sesión próxima con usuario. Gate de fase (validación + anti-repaint + perf) después de validación. Transición a Fase 2 (scoring) sin bloqueos, si validación es OK.

---

*Sesion-048 cierra Fase 1 de Sprint 1.6. Siguiente: validación visual Tier 2+3, luego Fase 2.*

# Sesion-034 — 2026-06-19

**Rama:** pine/sistema-completo · **Estado Pine:** INTACTO (core-sync OK SHA 8967d31bdbb7ed13, 592 líneas, idéntico Sesion-033)

## Objetivo
**Sesión de PLANIFICACIÓN/ORDEN (NO sprint Pine).** Oficializar en el plan canónico lo que vivía parcialmente en los esqueletos Sesion-032/033: el **Sprint 1.6** (gap de conceptos ICT T26–T40), integración en el WORKPLAN y el PINE-PLAN, y aclaración de la secuencia de trabajo hasta EA. Incluye verificación de duplicados entre los nuevos conceptos y las reglas-smc-ict.md §1–§4 existentes (guardrails de delineación obligatorios). Sin cambios de código Pine.

**Encargo del usuario (textual):** clarificar qué es T26 (es NUEVO, no un "traslado"), ordenar antes de empezar Pine, registrar en el plan maestro.

## Completado

### 1. Entregables

#### 1.1 Oficialización Sprint 1.6 en `PINE-PLAN.md` y `WORKPLAN-MAESTRO-V2.md`
- **PINE-PLAN §7 [NEW]:** nuevo bloque "Sprint 1.6 — Gap Conceptos ICT (Primitivas)" insertado tras Tier 2 (T01–T25 Tier 1/2). Orden por palanca/riesgo: T26→T27→T28→T29 (FVG descendants) → T30 (gaps apertura) → T32/T34 (estructura/propulsión) → T31/T33/T35/T37 (detección propia) → T36 (SL/TP tool) → T38 (SMT). Tabla de dependencias. Sprint count: Tier 1 = S1.1, Tier 2 = S1.2–S1.3, **Sprint 1.6 = S1.6 (nuevo)**.
- **WORKPLAN-MAESTRO-V2.md §FASE 1 (línea F1-GATE):** expandido de "25 conceptos" a "**T01–T40 (Tier 1/2 + Sprint 1.6 primitivas + Rutas B/D/E/F 0-peso)**". Nota de expansión bajo §4.8 con candidatas #43–#51 nuevas confluencias (provisionales, se cierran al cablear F2-T01). Referencia a ESQUELETO-P1 para detalle.

#### 1.2 Cruce anti-duplicados en `ESQUELETO-P1` (nueva sección §2.1)
**5 guards de delineación obligatorios** registrados en la documentación (ESQUELETO-P1 §2.1):

1. **T32 CISD vs §1.4 CHoCH / §1.5 MSS (CRÍTICO):** CISD se entrega por "cierre de acción" (close dentro de swing range establecido). CHoCH = cambio de mínimo/máximo del swing. MSS = CHoCH + displacement ≥1.5×ATR + cuerpo ≥70%. Diferencia: CISD puede ocurrir sin movimiento posterior (resolución de rangos); CHoCH/MSS implican directionalidad. **Delivery:** implementar ficha T32 con contraejemplos vs CHoCH simple y vs MSS para validación.

2. **T30 Gaps de Apertura (ORG/ARG/NRG) vs §4.2 Session Opens:** T30 describe NIVELES de apertura de sesión (high/low de vela 1 de sesión). §4.2 describe SESSION OPENS como "gaps de apertura" de patrón (diferencia previo close vs nuevo open), contexto gapping. Diferencia: T30 = detección de nivel; §4.2 = entrada en zona gapped. **Delivery:** T30 usa `f_sessionOpens` existente, §4.2 alimenta scoring.

3. **Familia Gap entre sí (Vacuum, Breakaway, NWOG/NDOG) — NO duplicate triggers:** Vacuum = brecha de precio sin toque. Breakaway = brecha con dirección fuerte post-resistencia. NWOG/NDOG = Nueva Apertura Alta/Baja. Patrón: se activan en DIFERENTES contextos (Vacuum en rango plano; Breakaway post-estructura; NWOG/NDOG en tendencia abierta). **Delivery:** fichas separadas pero con matriz de exclusión mutua en scoring (si Breakaway activa, Vacuum ≤ peso reducido).

4. **Familia FVG (True FVG, IFVG, Volume Imbalance) vs §2.2 sin doble conteo (P-05):** True FVG = imbalance de 3 velas [high0, low2]. IFVG = inside day FVG (rango confinado). Volume Imbalance = gap sin cierre de volumen. Todas son "FVG" genéricos pero **diferente desencadenante + mitigación.** Regla P-05: cada mitigación se cuenta UNA vez por nivel; si 3 velas generan True FVG y el mismo close cierra IFVG, cuenta 1 FVG no 2. **Delivery:** contadores separados (fvgTrue, fvgInside, fvgVolume) + matriz agregación para confluencia.

5. **Colisión de nombre "Opening Range" (T30 ORG nivel vs T39 OR-Macro ventana):** T30 Opening Range = rango de 1ª vela de sesión (nivel de soporte/resistencia). T39 Opening Range (macro) = ventana temporal de 9:30-10:30 NY (sesgo de volumen/rango). Diferencia de escala (tick-level vs minuto-level). **Delivery:** T30 usa `high[1]`/`low[1]` EURUSD sesión abierta; T39 usa sesión macro (input `i_sessionProfile`). Nombres claros en outputs (ORG-Sesión vs ORG-Macro).

**Veredicto:** CERO duplicados exactos. Las 5 delineaciones aseguran que cada concepto entra/sale independiente y se pueden combinar sin colisión en scoring.

#### 1.3 Aclaración de orden de trabajo hasta EA (recordatorio)
**Secuencia confirmada en sesión:**
1. **Fase 1** (Tier 1 → Tier 2 → Sprint 1.6): T01–T40 detección/dibujo en Pine.
2. **Fase 2** (Sprint 2.1): scoring, strategy backtesting, confluencias §4.8, validación ≥90.
3. **Fase 3** (Sprint 3.1–3.4): calibración IS/OOS, ajuste umbrales/pesos, paralelismo enjambre Hermes.
4. **Gate DURO Fable:** revisión integral Pine + ADRs + VALIDACION completa pre-Fase 4 (líneas WORKPLAN §FASE 4).
5. **Fase 4** (MQL5 EA nativo, 100% autónomo, NO webhook). Implementación EA, módulos `SMC_*.mqh`, golden tests vs Pine.
6. **Fase 5** (Símbolos nuevos, optimización runtime, producción).

**Anotación:** NO hay cambio en el EA hasta Pine ✅ + enjambre ✅ + gate Fable ✅. El enjambre es paralelo (laboratorio Hermes Fase 3), no bloqueante para Fase 1-2-3 Pine.

### 2. Commits asociados

**Commit único:** `200d182` `docs(workplan): oficializa Sprint 1.6 (T26-T40) + cruce anti-duplicados` (2026-06-19)
- Archivos modificados: `PINE-PLAN.md`, `WORKPLAN-MAESTRO-V2.md`, `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` (nueva sección §2.1).
- Core Pine: **INTACTO** (0 cambios).

### 3. check-core-sync
SHA `8967d31bdbb7ed13` (592 líneas), **IDÉNTICO a Sesion-033** → ✅ Pine sin tocar, ningún cambio de código.

### 4. Bloqueos
Ninguno. ADRs: ninguno nuevo (el del SMT quedó anotado como candidato en Sesion-032; se decide al abordar T38).

### 5. Puertas completadas
Ninguna (sesión de planificación/orden).

## Archivos tocados
| Archivo | Acción | Propósito |
|---|---|---|
| `PINE-PLAN.md` | UPD §7 | Nuevo bloque Sprint 1.6, orden por palanca |
| `WORKPLAN-MAESTRO-V2.md` | UPD F1-GATE | Expandido a T01–T40, nota §4.8 #43–#51 |
| `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` | UPD §2.1 | Nueva sección cruce anti-duplicados (5 guards) |
| `memory/ESTADO-ACTUAL.md` | UPD | Entrada Sesion-034 |
| `memory/sesiones/Sesion-034.md` | NUEVO | Este cierre |

## Próximos pasos acordados

- **(a) Validación formal T09b/T10:** lanzar TradingView (tv_launch MCP), ejecutar `scripts/check-core-sync.ps1`, confirmar 0/0 compilación en Visual/Strategy, iniciar validación ≥90 con smc-validator-agent sobre pools+sweep EURUSD H1.

- **(b) Pine continúa T11:** tras cerrar T09b/T10 formal, iniciar **T11 Kill Zones** (Sprint 1.4, Visual, ubicación sesión London/NY). Pendiente desde Sesion-021 (anterior a S027 pools).

- **(c) Hermes/Enjambre en paralelo (S035+):** Sesion-033 entregó ESQUELETO-P2; próxima sesión Opus Max/Claude Code ejecuta piloto mínimo (1 vigía + kanban + 2 mentores NSL+Boxxocode + orquestador EURUSD). Sin bloqueo a Pine.

- **(d) ADR candidato (diferido T38):** SMT Divergence requiere decisión de "símbolo correlacionado" (second request.security) antes de implementar. Abierto.

## Notas operativas
- **Sesión de orden/planificación:** solo documentación. No código Pine. No commits de código, solo docs.
- **Cruce anti-duplicados:** registrado como metodología (§2.1 ESQUELETO-P1) para futuras referencias y validación de integridad.
- **Sprint 1.6 es oficial:** entra en PINE-PLAN y WORKPLAN canónicos. No es "esqueleto" ni "provisional".
- **Secuencia confirmada con usuario:** Fase 1→2→3→gate Fable→Fase 4 (EA). Nada de MQL5 antes de gate.

---
**Commit:** docs(workplan): oficializa Sprint 1.6 (T26-T40) + cruce anti-duplicados (200d182). **Core Pine:** SHA 8967d31bdbb7ed13 (592 líneas, INTACTO). **check-core-sync:** OK ✅

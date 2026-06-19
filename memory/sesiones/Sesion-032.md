# Sesion-032 — 2026-06-19

**Rama:** pine/sistema-completo · **Estado Pine:** INTACTO (core-sync OK SHA 8967d31bdbb7ed13, 592 líneas, idéntico Sesion-031)

## Objetivo
**Sesión de PLANIFICACIÓN/ESQUELETO** (NO sprint Pine). Dejar la arquitectura lista para integrar el **gap de conceptos** detectado al bajar cursos de mentores: `docs/reglas-smc-ict.md` cubre ~16 conceptos, pero los mentores ICT enseñan +50 (`docs/planes/MATRIZ-conceptos-cobertura.md`: ~16 ✅ / ~12 🔶 variantes / **~24 ❌ faltan**). El usuario pidió integrarlos por el **MISMO proceso que T01–T10** (sin atajos) y dejar todo estructurado para que cualquier IA rellene el esqueleto. Incluye motor de razonamiento del EA y orden de integración de los repos del plano EA/Pine.

**Encargo del usuario (textual):** solo el esqueleto + ordenar la integración; el relleno (cuantificación, casos reales EURUSD vía TV MCP, código) lo hace otra IA.

**Partición acordada (respuesta del usuario):** **PARTE 1 (EA + Pine + repos) = esta sesión.** **PARTE 2 (Hermes + enjambre) = sesión siguiente** (diferida).

## Completado (documentación/estructura — NO código Pine)

### 1. Entregable único: `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md`
Espeja el estilo de `ESQUELETO-MITIGACION-conceptos.md`. **9 secciones:**
- **§0** — 10 reglas duras para el implementador (proceso completo sin atajos, anti-repaint D-PINE-03, core byte-idéntico, funciones CORE puras, ATR-relativo, 0/0, símbolo-agnóstico + pesos congelados Fase 3 ADR-002, no duplicar lo ya hecho, no inflar las 42 confluencias, EA no consulta LLM en runtime ADR-005/007).
- **§1** — Las **7 etapas canónicas** que pasó T01–T10, con checkbox por etapa: (1) spec cuantificada en reglas-smc-ict.md con casos EURUSD ⏳PENDIENTE-TVMCP → (2) `f_detect*` pura + UDT/kind + patrón ciclo de vida P1–P4 → (3) 0/0 + core-sync → (4) validación ≥90 → (5) confluencia §4.8 → (6) golden test MQL5 (≥5 casos, 0 dif eventos/±1 tick) → (7) commit individual. Incluye la plantilla de ficha en formato reglas-smc-ict.md.
- **§2** — **Tabla maestra de ruteo:** todos los ❌/🔶 de la matriz a **6 rutas**:
  - **A** primitiva nueva de Pine (pipeline estándar): Vacuum, Propulsion, Volume Imbalance(+SIVI/BIVI), Immediate Rebalance, BPR, CISD, Breakaway Gap, IPR, Standard Deviation, IFVG, True FVG, Inside Day, serie de gaps de apertura, SMT.
  - **B** sesgo/contexto (alimenta bias/scoring): DOL, IRL/ERL, HRLR/LRLR, IPDA, PDArray Matrix.
  - **C** modelo de entrada/composición (→ motor EA, NO primitiva): IOFED, ICT Entry Model 2022, Low Hanging Fruit, Unicorn, MMXM, Silver Bullet, Power of 3.
  - **D** tiempo/macro (extiende `f_killZone`): NY Lunch/Midnight/ORG macros, RTH/ETH.
  - **E** noticias → gate determinista ADR-005 (NO confluencia): NFP.
  - **F** teoría a escrutar (experimental post-Fase 3, gate de lift OOS): Gray Pool, Event Horizon, Price Delivery Continuum, Early Buyer/Seller, Advanced Price Balancing, Fair Valuation.
  - Cobertura verificada 1:1 contra la matriz, sin huérfanos; los ✅ no se re-esqueletizan.
- **§3** — Esqueleto del **motor de razonamiento del EA** (handoff §3.A, Fase 4, spec sin código): modelo de combinación que GENERALIZA (suma ponderada por familia + mínimos por familia + gating por contexto, no exact-match); los modelos de entrada (Ruta C) expresados como patrones de confluencias+timing (Unicorn = Breaker#22+FVG#26; Silver Bullet = displacement+FVG+ventana; PO3 = Judas+sweep+displacement; etc.); contexto de zona en vivo sin repaint/sin LLM; trazabilidad Pine→MQL5 y **refactors de Pine señalados** (exponer scores parciales por familia, normalización ATR, umbrales por familia configurables → impacto core-sync, entran en Sprint 2.1/Fase 4, no ahora).
- **§4** — **Fichas esqueleto T26–T40** (plantilla §1 en esqueleto, valores `⏳ a cuantificar [impl]`, cuerpos `// TODO [impl]`), agrupadas en familias para no duplicar máquina: FVG/imbalance (T26 True FVG, T27 IFVG, T28 BPR, T29 IR, T31 Volume Imbalance), gaps de apertura (T30), estructura (T32 CISD), propias (T33 Vacuum, T34 Propulsion, T35 IPR, T36 Standard Deviation, T37 Inside Day, T38 SMT). Rutas B/D/E/F resumidas.
- **§5** — Expansión de las 42 confluencias: por concepto, **nueva # vs refina existente** (criterio anti-inflación). True FVG y Propulsion **refinan** (#18/#20 FVG, #17/#19 OB); candidatas **nuevas tentativas**: #43 IFVG, #44 BPR, #45 Breakaway Gap, #46 Volume Imbalance, #47 CISD, #48 Vacuum, #49 IPR, #50 Inside Day, #51 SMT. Standard Deviation = **NO confluencia** (insumo de SL/TP). Ruta B = modula pesos/bias, no añade #. Números se cierran al cablear F2-T01; pesos = Fase 3.
- **§6** — **Nuevo Sprint 1.6 "Gap conceptos ICT (primitivas)"** (continúa tras T25), ordenado de mayor palanca/menor riesgo a menor: primero lo que reusa máquinas validadas (T26→T27→T28→T29 sobre FVG), luego T30 sobre `f_sessionOpens`, luego estructura/OB (T32, T34), luego detección propia (T31, T33, T35, T37), T36 (herramienta SL/TP), T38 SMT (bloqueada por ADR). Ruta D = T39/T40. Tabla de dependencias. Nota: re-evaluar presupuesto de objetos de dibujo (P4 Present mode/cuota).
- **§7** — Repos del plano EA/Pine **ordenados con veredicto**: OpenMobius-skill = **Probar AHORA** (acelera cuantificación Ruta A, verificar catálogo vs matriz + licencia, no copiar sin verificar contra TV); multi-agent-investment/ContestTrade = **referencia de diseño** (precedente ADR-007), no software; MT5 MCPs = **diferir Fase 4**; Ponytail = **diferir/opcional Fase 4**; CallMeBot = **diferir Fase 4-5** (notificador, nada sensible); TV alterno = **rechazar** (ya hay fork). Los de enjambre → Parte 2.
- **§8** — Lo de **Hermes/enjambre DIFERIDO a Parte 2** (handoff §3.B runtime, §3.E piloto NSL, §3.C/§8 almacenamiento, §9.A tools), enganchado a esta parte (el enjambre descubre/valida el set ampliado y alimenta el motor EA vía IS/OOS, nunca en runtime).

### 2. Decisiones/notas señaladas (NO son ADRs aún)
- **SMT Divergence (T38):** requiere decidir el **símbolo correlacionado** (segundo `request.security`) → **candidato a ADR propio** antes de implementar.
- **Standard Deviation (T36):** ruteado como **herramienta de proyección para SL/TP, NO confluencia** de score.
- **OpenMobius-skill:** marcado "Probar AHORA" para acelerar la cuantificación de la Ruta A.
- Números de confluencia #43–#51 **tentativos**; se cierran al cablear F2-T01.

### 3. check-core-sync
SHA `8967d31bdbb7ed13` (592 líneas), **IDÉNTICO a Sesion-031** → ✅ Pine INTACTO, ningún cambio de código.

### 4. Bloqueos nuevos
Ninguno.

### 5. Gate completado
Ninguno (planificación pre-implementación).

## Archivos
| Archivo | Acción | Propósito |
|---|---|---|
| `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` | NUEVO | Esqueleto maestro Parte 1 (§0–§9) |
| `memory/ESTADO-ACTUAL.md` | editado | entrada S032 |
| `memory/sesiones/Sesion-032.md` | nuevo | este cierre |
| `WORKPLAN-MAESTRO-V2.md` | editado | línea F1-S1.6 (nota, sin checkboxes marcados) |

## Próximos pasos acordados
- **(a) Pine/EA — relleno del esqueleto:** una IA `[impl]` rellena las 7 etapas empezando por **Sprint 1.6, T26 True FVG** (reusa máquina FVG T06), orden por palanca, core-sync + validación ≥90 por concepto.
- **(b) Sesion-033+ (PARTE 2):** Hermes/enjambre (runtime del enjambre, agente piloto NSL como plantilla, almacenamiento, tools de orquestación). + pendiente: validación formal ≥90 de T09b/T10 (Opus Medio cierra el refactor del esqueleto S028).

## Notas operativas
- **Commits:** Conventional Commits + ID — p. ej. `feat(pine-core): F1-S1.6-T26 True FVG`.
- **Sin atajos:** cada T26–T40 recorre las 7 etapas (no hay "casi-validado").
- El esqueleto vive en `docs/planes/`; NO toca ningún `.pine` ni `reglas-smc-ict.md` (esos los actualiza el `[impl]` al implementar).

---
**Commit:** docs(cierre) Sesion-032 (este). **Core Pine:** SHA 8967d31bdbb7ed13 (592 líneas, INTACTO). **check-core-sync:** OK ✅

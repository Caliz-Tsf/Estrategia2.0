# HANDOFF OPUS MAX — Mapa MTF rico + Motor de Confluencias → Workplan unificado

> **Origen:** Sesion-037 (2026-06-20). Conversación de diseño entre Freddy y Claude Code al abrir el Sprint 1.4 (T13 MTF). El usuario amplió la visión más allá de un T13 técnico aislado y pidió **no implementar Pine todavía**: primero que Opus Max integre el diseño al workplan.
> **Quién ejecuta:** sesión Claude Code **Opus** aparte (no dentro de esta sesión).
> **Estado al entregar:** Fase 1, Sprint 1.3 cerrado (T12 MSS, commit `4b4f3cc`). Core 644 líneas SHA `2de06be3a3eb1321`. Ningún `.pine` tocado en S037.

---

## 0. Tu misión (Opus Max)

1. **Leer y analizar** este handoff + los esqueletos/ADRs existentes (§1).
2. **Producir un esqueleto integrado** "Mapa MTF rico + Motor de Confluencias" (estructura, contratos, tareas rellenables) que **Claude Code** pueda implementar en Pine — doc nuevo `docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md`.
3. **Integrarlo al workplan** → dejar un **WORKPLAN UNIFICADO** (orden, dependencias, gates) **siguiendo todas las reglas y políticas ya establecidas**, sin saltar fases (regla #8).
4. **Reconciliar ADR-005/007** con los matices nuevos (§2.5): enjambre en vivo (entradas demo), pared EA↔laboratorio, puente offline.

**NO** escribir Pine de producción. **NO** duplicar docs existentes (referencia, no copia). Español. Output = esqueleto rellenable + workplan integrado + ADR.

---

## 1. Contexto a leer primero

- `CLAUDE.md`, `WORKPLAN-MAESTRO-V2.md`, `docs/workplan/PINE-PLAN.md` (§4 MTF, §7 sprints), `docs/reglas-smc-ict.md` (§4.8 las 42 confluencias), `memory/ESTADO-ACTUAL.md`.
- Esqueletos previos:
  - `docs/planes/ESQUELETO-MITIGACION-conceptos.md` (S028) — 4 patrones de ciclo de vida.
  - `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` (S032) — gap T26–T40 + ruteo + motor de razonamiento EA.
  - `docs/planes/ESQUELETO-P2-hermes-enjambre.md` (S033) — runtime enjambre + roster + voto + notificaciones.
  - `docs/planes/HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md` (S030).
- ADRs: **ADR-005** (enjambre = laboratorio + copiloto), **ADR-006** (pools persistentes), **ADR-007** (EA determinista + enjambre continuo).

---

## 2. Visión del usuario (capturada en esta conversación)

### 2.1 Mapa MTF rico (no foto mínima)
- Cada TF (D1/H1/M5) mantiene su **mapa de conceptos cerca del precio**.
- Por concepto: los **últimos ~10 más cercanos al precio**, **separados por dirección** (alcistas / bajistas). El usuario elige **cuántos ver de cada lado**, por concepto y por TF (input 0–10).
- **Anidación top-down en cascada**: una zona/estructura de D1 debe verse en H1 **y** en M5; y las **nativas de H1** deben verse en M5. Cada TF hereda hacia todos los menores: **D1→{H1, M5}, H1→{M5}**. Dibujo MTF diferenciado: transp ~85, borde punteado, prefijo `"D1:"`/`"H1:"`.
- Objetivo: ver **macro y micro** sin saturar el gráfico → control de densidad fino. Caso de uso del usuario: "si se va a entrar en una estructura/OB/FVG de D1 en M5, debe verse esa zona en H1 y M5; si en H1 hay confluencias y se entra en mitigación de un FVG, en M5 se ve el FVG de H1".

### 2.2 Restricción física de Pine (innegociable)
- `request.security` **NO transporta objetos/arrays**, solo números → el mapa HTF se trae **aplanado**: N elementos × campos × dirección, **tope fijo** (p.ej. 10/lado). Presupuesto ~127 valores por llamada `security`; presupuestar las llamadas (D1, H1) y el tamaño de cada tuple.
- Anti-repaint: `lookahead = barmerge.lookahead_off` siempre, eventos en `barstate.isconfirmed` (regla #1).
- Core-sync byte-idéntico Visual/Strategy (regla #2): la encapsulación de la cadena (`f_computeTFState`) debería vivir en **LIBRARY CORE** → paridad MQL5 Fase 4 (`SMC_MTF.mqh`).

### 2.3 Reto técnico central (ya explorado por Claude Code en S037)
- La cadena de detección está **desplegada suelta** en la sección DETECCIÓN (`SMC-Visual.pine` ~697-960 / `SMC-Strategy.pine` ~678-904) con estado `var` global. Para correrla en D1/H1 dentro de `request.security` hay que **encapsularla** en una función con todo su estado interno (no globales, que se contaminarían entre contextos). Es un refactor del corazón, pero es justo lo que Fase 4 necesita.
- **Sutileza Pine v6 confirmada:** `request.security(sym, tf, expr)` evalúa `expr` en un contexto separado del TF; si `expr` es una función con estado `var` **interno**, ese estado persiste por-contexto (independiente del chart) — esto habilita correr la detección en D1 sin contaminar el chart. Si referencia globales `var`, contamina.
- Helpers existentes reutilizables: `f_pNearZone` (`SMC-Visual.pine:1232`, filtra `state != ZS_INVALID`; para "no mitigado" endurecer a `state < ZS_MITIGATED`), `f_pNearPool` (`:1245`, filtra `not swept`), `f_pLastEvent` (`:1229`), `f_updateZoneMitigation` (`SMC-Library.pine:327`), constantes `ZS_*` (`SMC-Library.pine:46-49`), UDT `SMC_TFState` (`SMC-Library.pine:113`, hay que **ampliarla** con MSS + OB/FVG/pool/sweep por dirección). La sección `=== MTF ===` es stub vacío (`SMC-Visual.pine:962-963`, `SMC-Strategy.pine:906-907`). No hay `request.security` en el proyecto todavía.
- Evaluar **T13 escalonado**: **T13a** "mapa núcleo" (bias + BOS/CHoCH + MSS + P/D, escalares ya casi en `chartState` línea 739, refactor menor) vs **T13b** "mapa enriquecido" (N OB/FVG/pool/sweep por dirección, exige la encapsulación completa de la cadena). Recomendar troceo con justificación de riesgo (no romper T01–T12 validados).

### 2.4 Motor de confluencias → entrada
- Las **5 imágenes** de referencia (aportadas por el usuario) = secuencias de confluencias que disparan entrada R:R≥1:3:
  1. **Sell Setup Confirmation** — liquidity grab sobre zona de liquidez → BOS → entry → TP1/TP2/TP3 (R:R 1:3).
  2. **Simple BOS Entry** — BOS → FVG → OB (última vela contraria antes del BOS) → entry en retest → target en liquidez previa.
  3. **Smart Money Entry** — BOS + IND + OB + QM entry **with MSS** → 4 RR.
  4. **SMC Setup for Beginners** — BOS / MSS / CHoCH / OB / FVG / IDM / Sweep → entry area entre BOS y CHoCH, SL sobre OB, target en liquidez no usada.
  5. **Institutional Trader Study Notes** — BOS + Trendline Liquidity Grab + FVG + OB + bearish liquidity sweep → smart money entry.
- **Foco del EA + enjambre:** buscar esas confluencias, **testearlas**, y entregarlas validadas al EA. El EA, con conocimiento de una **lista larga** de confluencias, decide "aquí voy a entrar".
- El sistema **no hardcodea recetas**: scoring direccional `scoreLong`/`scoreShort` ponderado, pesos calibrados en Fase 3 IS/OOS (regla #6); R:R 1:3 sin excepción (regla #5). Las imágenes **alimentan/validan** el catálogo (42 base §4.8 + las que el enjambre descubra).

### 2.5 Correcciones a ADR-005/007 (incorporar)
- El enjambre **opera en vivo**: acceso al MCP, testea en **replay y en vivo**, los agentes **opinan y discuten en vivo** (investigación + copiloto humano).
- **Precisión sobre "operar":** el enjambre **no ejecuta operaciones reales**. "Operar" = registrar **entradas demo en TradingView** (vía MCP) para **testear** confluencias/entradas y medir su resultado. Esas señales testeadas pueden **notificarse** al humano (WhatsApp / CallMeBot — ya contemplado en `ESQUELETO-P2`, push elevado a Fase 2 en S033).
- **Pared dura:** EA y Laboratorio-en-Vivo **no se comunican en runtime**. El EA es autónomo/determinista (ADR-007 se mantiene: nunca consulta LLM en runtime).
- **Puente EA←enjambre = offline:** el enjambre entrega confluencias **testeadas/validadas** que se cristalizan en pesos/reglas del EA vía calibración Fase 3 — no señales en vivo.

---

## 3. Qué debe producir Opus Max

### 3.1 Esqueleto integrado (`docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md`)
- **Modelo de datos del mapa**: estructura para N elementos por concepto/dirección/TF; cómo se **aplana** para `security` y cómo se **reconstituye** en el consumidor para dibujar/scorear; presupuesto de tuples por llamada.
- **Contrato `f_computeTFState` / `f_tfSnapshot`**: firma, retorno, dónde vive (CORE), impacto en `check-core-sync`, viabilidad del estado `var` por-contexto en `request.security`.
- **Inputs de densidad** (`GRP_MTF`): por concepto × dirección × TF (0–10).
- **Dibujo diferenciado MTF** + **panel multi-columna** (propio / D1 / H1).
- **Contrato del motor de confluencias**: cómo el mapa MTF se lee como entradas del scoring (interfaz con §4.8), y el **formato de entrega** de confluencias testeadas del enjambre al EA + su gate de validación.
- **Troceo en tareas rellenables por Claude Code** (T13a/T13b/T14/T15…) con *done* medible, respetando "un commit = un concepto verificado". **Etiquetar cada tarea por carril** (Pine/EA vs Hermes/Enjambre, ver §3.2).

### 3.2 Workplan unificado
- Insertar tareas en `PINE-PLAN.md §7` / `WORKPLAN-MAESTRO-V2.md` **sin romper la numeración** existente (T13–T15 + mapa rico; relación con Fase 2 confluencias y Fase 4 EA/enjambre).
- **La integración debe seguir TODAS las reglas y políticas ya establecidas del workplan** (las 8 reglas duras de `CLAUDE.md`, ciclo por concepto, gates de fase, anti-overfitting, convenciones de commits/IDs). No inventa proceso nuevo: **encaja en el existente**.
- Dependencias, orden, gates. Conexión con esqueletos previos (P1, P2, mitigación) por **referencia, no duplicación**.
- **Separación obligatoria de carriles de tareas** (para que nada se pierda en las integraciones):
  - **Carril Pine/EA** — todo lo que se implementa en `pine/*.pine` (Fases 1-3) y luego se traduce a MQL5 (Fase 4): detección del mapa MTF, dibujo, panel, alertas, scoring/confluencias en Strategy, motor de decisión del EA.
  - **Carril Hermes/Enjambre** — todo lo que vive en el Workspace Hermes / laboratorio: agentes, runtime del enjambre, descubrimiento y testeo de confluencias, entradas demo en TV, notificaciones (WhatsApp/CallMeBot), entrega offline de confluencias testeadas.
  - Marcar **explícitamente los puntos de integración** entre ambos carriles (el puente offline confluencias→calibración→EA) sin que se solapen ni se pierdan dependencias cruzadas.

### 3.3 ADRs
- ADR nuevo (o enmienda a ADR-005/007) con la **pared EA↔laboratorio-en-vivo**, **enjambre en vivo (entradas demo + notificación)** y **puente offline de confluencias testeadas**.

---

## 4. Restricciones para Opus Max
- NO Pine de producción. NO duplicar docs. Español. Respetar reglas duras (#1 anti-repaint, #2 core-sync, #3 ATR, #5 R:R 1:3, #6 scoring direccional, #8 no saltar gates).
- Output = esqueleto rellenable + workplan unificado + ADR, listo para que Claude Code implemente sin re-litigar.
- No correr workflows que invoquen Claude dentro de una sesión Claude Code (cuelgue, issue #1067).

---

## 5. Cómo lanzarlo
- Sesión Claude Code **Opus** aparte, leyendo este handoff + invocando `smc-architect` / `planner` / `plan-eng-review` / `autoplan` según convenga.

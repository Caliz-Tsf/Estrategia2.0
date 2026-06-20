# ADR-008 — Mapa MTF rico + motor confluencia→entrada; enjambre en vivo con entradas demo y pared dura EA↔laboratorio

- **Fecha:** 2026-06-20 (Sesion-038)
- **Estado:** Aceptado
- **Precisa (no contradice):** ADR-005 (enjambre = laboratorio + copiloto) y ADR-007 (EA razona determinista + enjambre continuo). Los **complementa** con los matices que el usuario fijó en S037 y registra la arquitectura del mapa MTF.
- **Tarea:** diseño Sprint 1.4 (MTF) + capa de decisión confluencia→entrada. Origen: `HANDOFF-OPUS-MAX-mapa-mtf-confluencias.md`; detalle en `docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md`.

## Contexto

Al abrir el Sprint 1.4 (T13 MTF), el usuario amplió la visión y aparecieron tres precisiones que ADR-005/007 no fijaban con suficiente filo, y que conviene blindar antes de implementar:

1. **El enjambre "opera en vivo".** ADR-005 hablaba de modo Copiloto en vivo, pero el usuario quiere algo más concreto: que el enjambre **tome confluencias en vivo y en replay, las discuta, y registre entradas para testearlas** — no solo que "opine". Surge la duda de si eso reintroduce un LLM en el lazo de ejecución.
2. **Qué significa "operar".** Aclarado: **NO** ejecutar operaciones reales. "Operar" = registrar **entradas DEMO en TradingView** (vía MCP) para **medir** el resultado de una confluencia/setup, y **notificar** al humano (CallMeBot). Es medición + aviso, no ejecución.
3. **El mapa MTF rico + el motor confluencia→entrada** (el "fondo de todo" que el usuario describió con 5 imágenes de setups SMC) necesitan una decisión de arquitectura: encapsular la cadena de detección en `f_computeTFState` para `request.security`, lo que **adelanta** trabajo de Fase 4 (`SMC_MTF.mqh`).

## Decisión

### 1. Pared dura EA ↔ laboratorio-en-vivo (refuerza ADR-005/007)
El **EA** y el **laboratorio-en-vivo del enjambre** **no se comunican en runtime**. El EA es autónomo, nativo MQL5, determinista (ADR-007 intacto: nunca consulta LLM en vivo). El único acoplamiento EA↔exterior en vivo sigue siendo el **gate funcional determinista** (noticias/macro, veto binario con fail-safe). El enjambre **opera en vivo para el HUMANO y para el laboratorio**, jamás para el EA.

### 2. "Operar" del enjambre = entradas DEMO + notificación (precisa ADR-007)
El enjambre **opera en vivo y en replay**, pero **operar = registrar entradas DEMO en TradingView (vía MCP) para testear confluencias/setups**, con **TradingView como árbitro del resultado** (`ESQUELETO-P2 §2.6`). No ejecuta trades reales, no toca MT5, no dispara el EA. Las señales testeadas se **notifican** al humano (CallMeBot, `ESQUELETO-P2 §2.8`). El producto del enjambre es **conocimiento + señal copiloto**, nunca una orden.

### 3. Puente EA ← enjambre = OFFLINE (cristalización por calibración)
El enjambre entrega **confluencias y setups testeados** que cristalizan en **pesos/reglas del EA solo vía validación Strategy Tester IS/OOS 70/30** (ADR-002). No hay flujo de señales en vivo del enjambre al EA. Formato de entrega: `ESQUELETO-P3 §3.6`.

### 4. Mapa MTF rico + motor confluencia→entrada = arquitectura adelantada de Fase 4
- **Mapa MTF rico:** cada concepto, sus últimos `N` por dirección, en cascada D1→{H1,M5}, H1→{M5}. El HTF viaja **aplanado y capado** por `request.security` (no UDTs/arrays); el TF propio se computa local y más rico. Encapsulación en `f_computeTFState` (CORE byte-idéntico) con **estado interno por-contexto** que no contamina el chart. Esto es exactamente lo que `SMC_MTF.mqh` (Fase 4) necesita → el refactor del Sprint 1.4 **adelanta** Fase 4 (consistente con ADR-007 "posible refactor de Pine").
- **Motor confluencia→entrada:** capa determinista (scoreLong/scoreShort + selector de POI con R:R≥1:3) que lee el mapa y decide la zona de entrada. Las 5 imágenes del usuario **validan/calibran** un catálogo de setups (`ESQUELETO-P3 §3.5`), **no** se hardcodean como recetas (regla #6; pesos = Fase 3, ADR-002).

## Alternativas descartadas

- **Enjambre con entradas reales / en el lazo del EA:** descartada (rompe validez del backtest, latencia, no-determinismo; ya descartada en ADR-005/007). Las entradas demo + árbitro TV dan el "testeo en vivo" sin el riesgo.
- **Mapa HTF transportando objetos/arrays por `security`:** imposible en Pine (`PINE-PLAN §4`). Se aplana a tuple capado (`ESQUELETO-P3 §2.2`).
- **Mapa rico completo (N=10/lado) por `security` en todos los conceptos:** excede el presupuesto del tuple (~127). Se capa `N_htf` (≈3) para HTF y se reserva la riqueza al TF propio (local).
- **Setups como `if exact-match` de las imágenes:** descartada (no generaliza, viola ADR-007). Se reconocen vía scoring + selector de POI.

## Consecuencias

- **Sprint 1.4 se desdobla:** T13a (mapa núcleo, escalares) → spike test de no-contaminación → T13b (mapa rico) → T14 panel → T15 alertas (`ESQUELETO-P3 §4.1/§5`). No se pone en riesgo lo validado (T01–T12).
- **Spike test obligatorio con protocolo de escalada** (`ESQUELETO-P3 §5.3/§6 R-1`): confirmar que el estado `var` interno a una función dentro de `request.security` no contamina el chart, antes de encapsular la cadena completa. **Si pasa → se continúa el plan. Si falla → DETENER, no improvisar workaround, avisar a Freddy con diagnóstico para que escale a Opus ultracode (Opus Max)** y se decida el rediseño del transporte MTF.
- **Gate pre-testeo de setups (decisión Freddy, S038):** el testeo de setups del enjambre (replay+demo → IS/OOS) **no arranca** hasta que **(A) el Pine esté completo** (todos los conceptos integrados + motor confluencia→entrada en Strategy) **y (B) el enjambre esté completo** (perfiles + archivos/knowledge + skills + MCP + workflow + loop, no el piloto mínimo). La construcción de ambos carriles puede ser paralela; el testeo no empieza antes de este gate (`ESQUELETO-P3 §5.3`).
- **Core-sync cambiará de SHA** al añadir `f_computeTFState`/`f_nearestN` al CORE — esperado y documentado en el commit.
- **`docs/laboratorio/`** registra entradas demo + árbitro TV + track record por setup/agente (ya previsto en ADR-007 y `ESQUELETO-P2`).
- **Anti-overfitting intacto:** nada del enjambre entra al scoring del EA sin IS/OOS (ADR-002). El voto del enjambre es cualitativo y no recalcula §4.8 (ADR-005).
- **Trazabilidad de carriles:** Pine/EA vs Hermes/Enjambre quedan separados con puntos de integración explícitos (`ESQUELETO-P3 §4.3`); el único puente vivo es el gate de noticias (I-4).

## Referencias

- Esqueleto: `docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md`.
- Encargo: `docs/planes/HANDOFF-OPUS-MAX-mapa-mtf-confluencias.md`.
- ADRs base: ADR-005 (enjambre laboratorio/copiloto), ADR-007 (EA razona + enjambre continuo), ADR-002 (congelación umbrales/IS-OOS), ADR-003 (gate Fase 4), ADR-001 (símbolo-agnóstico).
- Pine: `docs/workplan/PINE-PLAN.md` §4 (MTF) / §5 (dibujo) / §7 (sprints). MQL5: `docs/workplan/MQL5-PLAN.md` (SMC_MTF.mqh, golden tests).
- Reglas duras: `CLAUDE.md` (#1 anti-repaint, #2 core-sync, #5 R:R≥1:3, #6 scoring direccional, #8 gates).

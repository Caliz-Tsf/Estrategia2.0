# ADR-007 — El EA razona confluencias (scoring generalizador) + enjambre continuo con scoring de agentes

- **Fecha:** 2026-06-18 (sesión módulo mentores)
- **Estado:** Aceptado
- **Amplía:** ADR-005 (enjambre = laboratorio + copiloto, NO runtime del EA). NO lo contradice.
- **Tarea:** módulo mentores / arquitectura EA (Fase 4, diseño)

## Contexto

ADR-005 fijó que el enjambre de mentores es laboratorio + copiloto y que el EA ejecuta reglas
cristalizadas sin consultar al LLM en runtime. El usuario observó una ambigüedad: "el EA solo
ejecuta reglas congeladas" se leía como un EA rígido de *exact-match*, cuando el mercado **no da
siempre las mismas confluencias exactas** — y un EA debe poder **combinar confluencias similares-no-
exactas** y decidir según el contexto en tiempo real. Además, lo que el usuario quiere del enjambre
es que trabaje **en tiempo real y de forma continua**: tomando confluencias en vivo (vía TV MCP),
discutiéndolas, guardando las que cierran positivas con su **autoría**, y con el tiempo **puntuando a
los agentes** (track record) y combinando sus votos.

## Decisión

Se adopta el **modelo reconciliado**, que precisa (no cambia) ADR-005:

1. **El EA SÍ razona, de forma DETERMINISTA y GENERALIZABLE.** Su "razonamiento" es el **motor de
   scoring direccional** (scoreLong/scoreShort sobre las 42 confluencias, §4.8 WORKPLAN): dispara
   cuando hay **confluencia suficiente** (umbral + pesos + contexto de zona en tiempo real), **aunque
   no sea la combinación exacta**. NO es un *lookup* rígido ni un LLM por vela. Es backtesteable
   (Strategy Tester IS/OOS + golden tests Pine→MQL5).
2. **El enjambre es continuo y en tiempo real.** Loop persistente (cron+kanban): descubre confluencias
   nuevas, las toma en vivo vía TV MCP (solo un agente toca TV), discute si una entrada se abre o no,
   y **registra en `docs/laboratorio/` las que cierran positivas con autoría**. Incorpora **scoring/
   atribución de agentes** (track record por mentor; combinación de votos ponderada por desempeño).
3. **El enjambre alimenta al EA SOLO vía validación.** Las confluencias/ideas del laboratorio se
   validan en replay/Strategy Tester IS/OOS y solo lo que sobrevive cristaliza como peso/regla del
   scoring → se porta a MQL5. **El EA no se entera del enjambre en runtime.**
4. **Línea dura conservada (ADR-005):** el EA nunca consulta al LLM en vivo. Único puente EA↔exterior
   en tiempo real = gate funcional determinista (noticias/macro, veto binario, fail-safe).

## Alternativas descartadas

- **LLM en el lazo del EA** (el EA consulta al enjambre en vivo para ejecutar): descartada por el
  usuario. Rompe la validez del backtest (ejecutarías algo distinto a lo validado), añade latencia
  (la vela cierra antes de la respuesta) y no-determinismo; obligaría a rediseñar toda la columna de
  validación. Contradice ADR-005 y las reglas duras.
- **EA de exact-match rígido:** descartada. No generaliza a confluencias similares y no refleja cómo
  opera realmente un sistema SMC discrecional cristalizado.

## Consecuencias

- **Diseño pendiente (handoff a Opus Max):** `docs/planes/HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md`
  especifica (a) el motor de razonamiento del EA (modelo de generalización medible + mapeo Pine→MQL5),
  (b) el runtime del enjambre (cron/kanban, contrato de voto, regla de registro, scoring de agentes),
  (c) la traza end-to-end con los refactors necesarios **en cualquier capa, Pine incluido**.
- **Posible refactor de Pine (Fase 3+):** exponer scores parciales por familia / normalización ATR /
  umbrales configurables para soportar la generalización. Sujeto a core-sync, anti-repaint y a la
  **congelación de umbrales hasta Fase 3 (ADR-002)** — se define la *mecánica*, no se *ajustan* valores.
- **Gap de conceptos ICT (integración estándar):** los ~25-30 conceptos que los mentores enseñan y que
  hoy no están en `reglas-smc-ict.md` (inventario en `docs/planes/MATRIZ-conceptos-cobertura.md`) se
  integran al plan maestro de Pine **por el mismo proceso que todos** (spec cuantificada → detección
  Pine → validación ≥90 → confluencia §4.8 + golden test MQL5), para que **Pine y el EA los vean,
  identifiquen y calculen** como confluencias. El diseño de la integración es parte del handoff a Opus
  Max (§3.D). Respeta ADR-002 (mecánica ahora, pesos en Fase 3).
- **`docs/laboratorio/`** se crea como registro central: diario de confluencias (con autoría/resultado)
  + track-record por agente.
- **Anti-overfitting:** ninguna idea del enjambre entra al scoring sin pasar IS/OOS (ADR-002).

## Referencias

- ADR-005 (enjambre = laboratorio/copiloto, no runtime), ADR-002 (congelación umbrales), ADR-003 (gate Fase 4), ADR-001 (símbolo-agnóstico).
- Handoff: `docs/planes/HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md`.
- Spec SMC/scoring: `docs/reglas-smc-ict.md` §4.8 · `WORKPLAN-MAESTRO-V2.md` §4.8 / Fase 4 · `docs/workplan/MQL5-PLAN.md`.
- Superficies Hermes: `docs/planes/ESQUEMA-HERMES-mentor-module.md`.

# ADR-005 — El enjambre es laboratorio + copiloto, NO runtime del EA

- **Fecha:** 2026-06-16 (Sesion-025)
- **Estado:** Aceptado
- **Tarea:** Módulo Mentores / diseño del Swarm (Fase 5, diseño)
- **Contexto:** revisión del plan del swarm por Opus. Resuelve la tensión entre "quiero que el
  enjambre ayude a decidir entradas en tiempo real" y la regla dura **EA 100% nativo MQL5, sin webhook**.

## Contexto

El diseño previo del swarm (Sesion-024) terminaba el flujo en `Orchestrator → MT5/alerta` y su propósito
decía que los agentes *"votarán confluencia antes de decidir una entrada"*. Eso colocaba un enjambre de LLMs
en el **lazo de ejecución** del trade, lo que choca de frente con la arquitectura del proyecto (EA autónomo,
nativo, sin puente). El usuario aclaró su intención real: **el enjambre sirve para pulir y testear la
estrategia en TradingView ANTES de construir el EA**; el EA solo se crea cuando la estrategia ya es rentable
y validada en TV.

Por qué un LLM **no puede** estar en el runtime del EA:
1. **Mata la validez del backtest.** La estrategia se valida en el Strategy Tester **sin** enjambre (no se
   puede correr un LLM sobre años de histórico: caro, lento, no reproducible). Si el EA en vivo **sí**
   consultara al enjambre, ejecutaría algo distinto a lo validado → el backtest deja de predecir el
   rendimiento real. Se pierde la única prueba de rentabilidad.
2. **Fragilidad y latencia.** Una sola instancia de TV (CDP 9222), MCP secuencial, Puter en la nube → un
   broadcast puede tardar 30–90 s (la vela ya cerró). Si Puter cae, el EA queda ciego.
3. **TV ≠ MT5.** El enjambre lee TradingView; el EA opera en MetaTrader (otro broker, otro feed, otro cierre
   de vela). Validar en uno lo que ejecuta el otro introduce desalineación de datos.

## Decisión

**El enjambre opera en DOS modos, ambos FUERA del lazo de ejecución del EA. El EA hereda solo reglas
cristalizadas y validadas; el único acoplamiento EA↔exterior en vivo es un gate funcional determinista.**

- **Modo Laboratorio (offline / descubrimiento):** el enjambre opina sobre histórico y replay para
  **proponer y juzgar** confluencias. Produce hipótesis, rankings y análisis — **nunca órdenes**.
- **Modo Copiloto (en vivo, fase TV):** el enjambre opina en tiempo real vía MCP TV para **asistir la
  decisión del HUMANO** en paper/manual. Es herramienta del usuario, **no del EA**. Aquí viven "los expertos
  opinando en tiempo real sobre el gráfico".
- **EA MQL5 (Fase 4+):** 100% nativo y determinista. Ejecuta las **reglas ya cristalizadas** (Pine → MQL5,
  con golden tests de paridad). **Ningún LLM, ningún webhook, ninguna consulta al enjambre en runtime.**
- **Gate funcional determinista:** único puente EA↔exterior en vivo. Filtra solo **datos que el EA no
  calcula** (noticias/macro), implementado como **bandera/veto binario con fail-safe** (si el dato no llega,
  el EA usa su default seguro). Arranca mínimo (noticias, fuente TBD) y crece solo si el descubrimiento lo
  justifica. **No es un LLM decidiendo; es un dato externo vetando.**

> **Regla de una línea:** el enjambre y el EA **nunca se hablan en runtime**. El enjambre produce
> *conocimiento* (qué confluencias y cómo gestionarlas); ese conocimiento se cristaliza en Pine determinista,
> se valida con backtesting IS/OOS, y se porta a MQL5. El EA **hereda** el resultado — no lo consulta.

## Alternativas descartadas

- **(A) Enjambre dentro del EA** (el LLM decide/valida la entrada en vivo, vía webhook o consulta directa):
  descartada. Rompe la validez del backtest, es frágil (Puter/latencia), no es portable a MQL5 nativo y viola
  las reglas duras de arquitectura (EA autónomo sin webhook) y de scoring determinista (§4.8). Es lo que el
  usuario pidió literalmente al inicio; se reencauza con el modo Copiloto, que le da el "tiempo real" sin el
  riesgo.
- **(B) Enjambre 100% offline, sin copiloto:** válida y segura, pero pierde la asistencia en vivo que el
  usuario quiere mientras opera manual en TV. El modo Copiloto la recupera sin tocar el EA.

## Consecuencias

- El "tiempo real" **existe**, pero su consumidor es el **humano** (Copiloto en fase TV), no el EA autónomo.
- El **gate funcional** es el único acoplamiento del EA con datos externos en vivo; mínimo al inicio.
- Se adopta una **metodología de laboratorio** (escalera de validación + diario de experimentos) — detallada
  en `docs/MODULO-MENTORES-WORKFLOW.md`. El histórico profundo de **MT5 entra en Fase 4** (paridad +
  validación con datos del broker), no antes: el sistema actual es Pine y no corre sobre datos de MT5.
- El **voto del enjambre es cualitativo** (revisión/veto/descubrimiento) y **no recalcula** el score
  cuantitativo de las 42 confluencias del §4.8 (eso lo hace el Pine, determinista, y se calibra con IS/OOS).
  Separar ambas capas es obligatorio para no meter sesgo no-validado (guardián anti-overfitting).
- La **construcción** del swarm sigue siendo **Fase 5** (requiere mentores reales primero); este ADR fija su
  arquitectura para que se construya bien.

## Referencias

- Workflow canónico: `docs/MODULO-MENTORES-WORKFLOW.md`
- Plan: `docs/planes/PLAN-modulo-mentores-swarm.md`
- Reglas duras: `CLAUDE.md` (EA nativo sin webhook · scoring §4.8 · R:R≥1:3 · anti-repaint)
- Scoring direccional: `WORKPLAN-MAESTRO-V2.md` §4.8 (42 confluencias)
- Anti-overfitting / IS-OOS: ADR-002 · agente `smc-backtesting-analyst`

# ESTADO ACTUAL — Estrategia 2.0
> Actualizar al cierre de CADA sesión (lo hace smc-doc-updater vía /smc-session-close cuando existan).

## Estado
- **Fase actual:** FASE 0 — pendiente de iniciar
- **Última tarea completada:** Generación del WORKPLAN-MAESTRO-V2.md + 5 anexos (docs/workplan/) — commit cff7fb9 (2026-06-10)
- **Siguiente tarea:** SEC-01 (rotar API keys firecrawl/tavily — manual, usuario) → luego Fase 0 Bloque A: SEC-02 (.gitignore), GIT-01 (mover LuxAlgo a pine/reference/) → Bloque B: DOC-01 (reglas-smc-ict.md, la tarea más importante)

## Bloqueos
- SEC-01 pendiente: las keys expuestas en PLAN-MAESTRO-FASE0.md (histórico) siguen activas hasta que el usuario las rote.

## Decisiones vigentes (no re-litigar)
- Arquitectura Pine: 1 core compartido + SMC-Visual.pine (indicator) + SMC-Strategy.pine (strategy → Strategy Tester).
- EA MT5 100% nativo, SIN webhook.
- 42 confluencias direccionales; pesos en Fase 3 con split IS/OOS 70/30.
- Solo EURUSD hasta gate de Fase 3. R:R mínimo 1:3. Anti-repaint obligatorio.
- Fuente de verdad del plan: WORKPLAN-MAESTRO-V2.md + docs/workplan/*.

## Cómo arrancar la próxima sesión
1. Leer este archivo + WORKPLAN-MAESTRO-V2.md Sección 3 (Fase 0).
2. Confirmar SEC-01 hecho por el usuario.
3. Ejecutar Fase 0 en orden: Bloque A → B → C → D → E → F → VER-01..08.

*Última actualización: 2026-06-10 — sesión de generación del workplan (Fable)*

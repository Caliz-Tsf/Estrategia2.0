# ESTADO ACTUAL — Estrategia 2.0
> Actualizar al cierre de CADA sesión (lo hace smc-doc-updater vía /smc-session-close cuando existan).

## Estado
- **Fase actual:** FASE 0 — EN CURSO
- **Última tarea completada:** DOC-01 Tier 1 (Estructura) — reglas-smc-ict.md con convenciones globales + swings/clasificación/BOS/CHoCH/MSS/impulso, aprobado sección a sección — commit 414fa1b (2026-06-10)
- **Bloque A COMPLETO:** SEC-01 (keys rotadas por usuario + viejas redactadas), SEC-02 (.gitignore), GIT-01 (LuxAlgo → pine/reference/LuxAlgo-SMC-base.pine) — commit 5970a10
- **Siguiente tarea:** DOC-01 Tier 2 (Zonas: OB, FVG, Premium/Discount, EQH/EQL) → luego Liquidez → ICT/EMAs. PENDIENTE transversal: poblar casos de prueba EURUSD (marcados ⏳PENDIENTE-TVMCP) con una pasada de TradingView MCP cuando estén todas las definiciones.

## Bloqueos
- Ninguno. (SEC-01 resuelto: usuario confirmó keys viejas revocadas; nuevas en .env/.mcp.json gitignored.)

## Decisiones de esta sesión (DOC-01)
- Umbrales SIEMPRE relativos a ATR(14), nunca pips fijos.
- swingLen=5 / internalLen=3 (ajustable en pruebas Fase 3).
- BOS/CHoCH por CIERRE, no mecha. Modelo bias = structure high/low (extensor vs protector).
- MSS = CHoCH de nivel swing + displacement (≥1.5×ATR, cuerpo ≥70%) — lo distingue del CHoCH simple en el scoring.
- Storage keys: .mcp.json + .env (ambos gitignored), sin migrar a env vars de Windows.

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

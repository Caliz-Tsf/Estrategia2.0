# ESTADO ACTUAL — Estrategia 2.0
> Actualizar al cierre de CADA sesión (lo hace smc-doc-updater vía /smc-session-close cuando existan).

## Estado
- **Fase actual:** FASE 0 — EN CURSO
- **Última tarea completada:** DOC-01 §4 Contexto/ICT/EMAs. **TODAS las definiciones de reglas-smc-ict.md escritas** (§1 Estructura, §2 Zonas, §3 Liquidez, §4 ICT/EMAs — 42 confluencias cubiertas).
- **Commits:** Bloque A 5970a10 · Tier 1 414fa1b · Tier 2 3a17b79 · §3+ADR-001 429de10 · §4 (este).
- **Siguiente tarea — cerrar DOC-01 (gate VER-05):** (1) pasada TradingView MCP para poblar casos ⏳PENDIENTE-TVMCP con velas reales EURUSD (requiere TV abierto); (2) aprobación final del usuario. Luego DOC-02 (reglas-dev.md) y resto Bloque B.
- **PENDIENTE workplan:** aplicar cambios de ADR-001 a §4.8/F2-T02/PINE-PLAN/MQL5-PLAN cuando se toque cada sección.

## Bloqueos
- Ninguno. (SEC-01 resuelto: usuario confirmó keys viejas revocadas; nuevas en .env/.mcp.json gitignored.)

## Decisiones de esta sesión (DOC-01)
- Umbrales SIEMPRE relativos a ATR(14), nunca pips fijos.
- swingLen=5 / internalLen=3 (ajustable en pruebas Fase 3).
- BOS/CHoCH por CIERRE, no mecha. Modelo bias = structure high/low (extensor vs protector).
- MSS = CHoCH de nivel swing + displacement (≥1.5×ATR, cuerpo ≥70%) — lo distingue del CHoCH simple en el scoring.
- Storage keys: .mcp.json + .env (ambos gitignored), sin migrar a env vars de Windows.
- **ADR-001 — Bot MULTI-SÍMBOLO, sin filtro horario duro.** Kill Zone = confluencia ponderada + sessionProfile configurable (FX-London-NY/FX-Asia/None), no bloqueo. Guardián universal = filtro de spread. Pesos del scoring por símbolo. Valida EURUSD primero, cada símbolo nuevo = Fase 5 abreviada. Umbrales ATR-relativo = base de portabilidad.

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

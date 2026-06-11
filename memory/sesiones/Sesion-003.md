# Sesión 003 — Revisión Fable de lo informativo + correcciones pre-Bloque C
> Fecha: 2026-06-11 · Fase 0 · Fable (Claude Code) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.

## Objetivo de la sesión
Cumplir el paso acordado en Sesion-002: **validar con Fable todo lo informativo** (Bloques A+B) antes de arrancar Bloque C (MCPs).

## Veredicto de la revisión
✅ **APTO para continuar con Bloque C → D → E → F.** Revisado: ESTADO-ACTUAL, Sesion-002, WORKPLAN-MAESTRO-V2 completo, DOC-01/02/03/04/07, ADR-001, anexos (PINE-PLAN, MQL5-PLAN, SKILLS, AGENTES, WORKFLOWS) y barrido de residuos BotBase en todo el repo.

**Verificado OK:**
- Las 42 confluencias suman exactamente 42 (8+8+10+5+5+6) y DOC-01 las cubre todas con definición numérica + contraejemplo.
- Eliminar DOC-06 no rompe nada: golden tests Fase 4 = set propio desde TradingView, sin dependencia del BotBase.
- DOC-02/03/04/07 coherentes entre sí (nomenclatura, protocolo de sesión, regla workflows/agentes/skills).
- Anexos limpios de residuos BotBase; residuos solo en archivos históricos (correcto).

## Correcciones aplicadas (4)
1. **ADR-001 aplicado al workplan** (estaba pendiente y contradecía texto vigente):
   - WORKPLAN §4.8 regla de señal: quitada la precondición `KZ activa ∧`; añadido `spread ≤ maxSpread`.
   - WORKPLAN F2-T02: "KZ obligatoria" → "spread ≤ maxSpread"; KZ = confluencia #34 ponderada.
   - WORKPLAN descripción DOC-07: "solo EURUSD" → "símbolo-agnóstico [ADR-001]".
   - PINE-PLAN §3.4: `f_killZone(time, sessionProfile)` con ventanas en hora local+DST y perfiles; §6: lógica de entrada y filtros duros sin KZ, con inputs `sessionProfile`/`maxSpread`.
   - MQL5-PLAN: inputs del EA (sessionProfile, maxSpread, perfil por símbolo), guard de OnTick (spread en vez de KZ), flujo por tick, tabla de mapeo.
   - ADR-001 marcado como "items aplicados".
2. **Excepción TV-MCP en CLAUDE.md:** la prohibición de `D:\CODE\BOT\Bot\` ahora exceptúa explícitamente el fork del TV MCP (`tradingview-mcp-jackson`) — es herramienta, no referencia de código. Resuelve el conflicto con MCP-02.
3. **Aclaración KZ ≠ open en DOC-01 §0:** las ventanas Kill Zone arrancan antes del open A PROPÓSITO (convención ICT: London KZ 07:00–10:00 Londres = 02:00–05:00 ET). No es contradicción con "London open = 08:00".
4. **Banners en históricos:** PROMPT-FABLE-WORKPLAN.md ahora tiene banner HISTÓRICO; los banners de PLAN-BOT-SMC-ICT.md y PLAN-MAESTRO-FASE0.md reforzados con "menciones a BotBase/DOC-06 OBSOLETAS".

## Decisiones (confirmadas con Freddy)
- La excepción TV-MCP se resuelve con nota en CLAUDE.md (no se mueve el fork).
- KZ London 07:00–10:00 hora de Londres queda como convención ICT intencional, documentada.

## Pendientes abiertos (sin cambios)
- Poblar casos ⏳PENDIENTE-TVMCP de reglas-smc-ict.md + aprobación final (gate VER-05) — necesita gráfico.
- **Siguiente paso (próxima sesión): Bloque C (MCP-01..06) → D (skills) → E (agentes) → F (workflows/scripts) → VER-01..08 → gate VER-09.**

## Addendum (misma sesión) — 2 precisiones tras preguntas de Freddy
1. **Filtro de spread = SOLO EA (hueco técnico real detectado).** Pine no puede leer el spread real (TV no expone bid/ask en una strategy) → el "guardián universal" del ADR-001 solo es implementable en Fase 4 (`SMC_RiskManager`). Corregido en: PINE-PLAN §6 (filtro retirado de la lógica Pine, nota explícita), WORKPLAN §4.8 + F2-T02 (spread = solo EA), ADR-001 (nota de implementación), reglas-smc-ict §3.4. **Mitigación añadida:** F3-T02 ahora exige segmentación por sesión para detectar señales rentables solo por costes modelados constantes.
2. **Vault Obsidian precisado en CLAUDE.md:** lo prohibido es LEER `Mente/Estrategia-Nueva/` como fuente; el vault NO está prohibido como destino — `Mente/Estrategia2.0/` es el respaldo del proyecto (SCR-02). La limpieza del vault viejo es manual de Freddy con backup previo [P-21/OBS-01]; ninguna sesión de Claude la ejecuta.

**Veredicto multi-símbolo (opinión Fable):** decisión correcta como está diseñada — es arquitectura símbolo-agnóstica con validación de UN símbolo a la vez (EURUSD primero, Fase 5 par a par, pesos por símbolo). El único hueco real era el spread-en-Pine, ya corregido.

## Cierre
Revisión Fable de lo informativo ✅ PASADA con 4 correcciones aplicadas y commiteadas + addendum (spread solo-EA, vault precisado). El camino al Bloque C está despejado.

# Sesión 001 — Arranque Fase 0: seguridad + DOC-01 definiciones
> Fecha: 2026-06-10 · Fase 0 · Claude Code (Opus 4.8) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.

## Objetivo de la sesión
Iniciar Fase 0 del WORKPLAN-MAESTRO-V2: Bloque A (seguridad/git) y arrancar Bloque B (DOC-01, la fuente de verdad SMC/ICT).

## Qué se hizo, por qué y con qué finalidad

### Bloque A — Seguridad y git (commit 5970a10)
| Arreglo | Por qué | Finalidad |
|---|---|---|
| **SEC-01** keys viejas redactadas de PLAN-MAESTRO-FASE0.md | estaban commiteadas en texto plano (P-07) | que el repo no exponga credenciales. Freddy ya rotó las keys; las viejas quedaron como texto muerto y se redactaron por higiene (sin reescribir historial, innecesario) |
| **SEC-02** `.gitignore` completado | faltaban artefactos de herramientas y `*.local.json` | evitar commitear secretos/artefactos a futuro |
| **GIT-01** `Indicador Trading View SMC.txt` → `pine/reference/LuxAlgo-SMC-base.pine` | estaba suelto en la raíz | estructura limpia + atribución LuxAlgo (CC BY-NC-SA) intacta para Fase 1 |

### Bloque B — DOC-01 `docs/reglas-smc-ict.md` (commits 414fa1b, 3a17b79, 429de10, 7a8afa1)
**Por qué es la tarea #1:** es la fuente de verdad que valida TANTO el Pine (Fases 1-2) COMO el MQL5 (Fase 4). Sin definiciones cuantificadas (números, no prosa), `smc-validator-agent` no puede validar nada y cada implementación sería una interpretación distinta (P-14).
**Finalidad:** que cada concepto SMC/ICT tenga umbral numérico + parámetros default + contraejemplo, para codificar y validar sin ambigüedad.
**Estado:** TODAS las definiciones escritas — §1 Estructura, §2 Zonas, §3 Liquidez, §4 ICT/EMAs (42 confluencias). Falta poblar casos de prueba reales (TV MCP) + aprobación final.

## Decisiones tomadas (no re-litigar)
1. **Umbrales SIEMPRE relativos a ATR**, nunca pips fijos → base de portabilidad multi-símbolo.
2. **swingLen=5 / internalLen=3** (ajustable en pruebas Fase 3).
3. **BOS/CHoCH por CIERRE, no mecha**; modelo bias = structure high/low (extensor vs protector).
4. **MSS = CHoCH de nivel swing + displacement** (≥1.5×ATR, cuerpo ≥70%) — lo distingue del CHoCH simple en el scoring.
5. **OB = vela completa high/low** (SL detrás de la mecha); **FVG = umbral fijo 0.25×ATR14** (optimizable, respeta IS/OOS).
6. **EQH/EQL = tolerancia 0.1×ATR**; aclarado vs empate de detección.
7. **EMAs colapsadas a 6 confluencias direccionales** (FIX P-05: sin doble conteo precio-vs-EMA).
8. **ADR-001 — Bot MULTI-SÍMBOLO sin filtro horario duro.** Kill Zone = confluencia ponderada + `sessionProfile` configurable (FX-London-NY/FX-Asia/None). Guardián de calidad = filtro de spread, no el reloj. Pesos del scoring por símbolo. Valida EURUSD primero; cada símbolo nuevo = Fase 5 abreviada. Ver `docs/adrs/ADR-001`.
9. **Storage de keys:** .mcp.json + .env (gitignored), sin migrar a env vars de Windows.

## DECISIÓN para la próxima sesión (acordada con Freddy)
**Adelantar TODO lo informativo primero** — escribir, investigar, corregir, desglosar conceptos y estructuras — ANTES de tocar el gráfico. Razón: Freddy quiere **validar todos los conceptos/reglas/estructuras con Fable** antes de la fase visual.
- **Próxima sesión = documentos SIN gráfico:** DOC-02 `reglas-dev.md`, DOC-03 `WORKFLOW-ARQUITECTURA.md`, DOC-04 `TV-SMC-WORKFLOW.md`, DOC-06 `lecciones-estrategia-nueva.md` + `referencia-botbase.md`, DOC-07 `CLAUDE.md`.
- **Diferido (necesita gráfico):** pasada TradingView MCP para poblar los casos ⏳PENDIENTE-TVMCP de reglas-smc-ict.md + aprobación final (gate VER-05). Se hace cuando TODO lo informativo esté escrito y validado con Fable.

## Pendientes abiertos
- Aplicar cambios de ADR-001 al WORKPLAN (§4.8 regla de señal, F2-T02 filtros duros, PINE-PLAN §3.4/§6, MQL5-PLAN) cuando se toque cada sección.
- Poblar casos ⏳PENDIENTE-TVMCP (todos los conceptos) vía TV MCP.
- Aprobación final de reglas-smc-ict.md por el usuario.

## Cierre
7 commits, árbol git limpio. ESTADO-ACTUAL.md y memoria persistente actualizados.

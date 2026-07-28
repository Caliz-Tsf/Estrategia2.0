# ESTADO ACTUAL — Estrategia 2.0

> **Reglas de este archivo — leerlas antes de escribirlo.**
> 1. Es **estado vivo, no histórico**. El histórico de cada sesión vive en `memory/sesiones/Sesion-NNN.md` y ahí se queda.
> 2. **Ventana rodante:** la sesión en curso en detalle + las 3 anteriores como **una línea** con enlace. Al cerrar la sesión N, la N-4 se borra de aquí (su fichero ya la conserva).
> 3. **Techo duro 40 KB.** Por encima de **256 KB** el tool `Read` del agente no puede abrir el archivo y el arranque se hace **a ciegas**: eso pasó de hecho entre el 2026-07-20 (S~140) y S146, con el archivo en 291 KB.
> 4. La sección **«Cómo arrancar la próxima sesión» se REEMPLAZA, nunca se apila.** Estuvo congelada en S090 durante 56 sesiones.
> 5. Lo actualiza `smc-doc-updater` en `/smc-session-close`. **Rotar, no acumular.**

## Estado
- **Rama de trabajo:** **`pine/sistema-completo`** (creada Sesion-010, publicada en origin). Todo el código Pine (Fases 1-3) vive aquí; `main` queda estable hasta el gate de Fable pre-Fase 4. Ver **ADR-003**.
- **Fase actual:** **FASE 1 · S146 — HILO PRIORITARIO S145 RESUELTO (no era ausencia de creación, era el gate `touches>=2`) + §3.3 GRAB IMPLEMENTADO (F1-S1.3-T10b, confluencia #11).** Objetivo heredado de S145: verificar si el indicador regenera SSL/BSL al avanzar la tendencia. Probe nuevo `scripts/gen_probe_ciclo_pools.py` sobre D1 EURUSD, 6.292 velas confirmadas, cross-checks a 0: **704 altas de pool** (362 BSL/342 SSL), **666 barridos** con vida media **148 velas**, solo **9 de 666 (1,4%)** barridos ocurren en <=swingLen(5) velas, censo final **80 pools** (=MAX_POOLS_CHART) con **38 vivos/42 barridos**, de los vivos **37 con 1 solo toque** y apenas **1 con >=2 toques** (BSL 1.51421 x3), **12 SSL vivos bajo el precio** (mas cercano 1.13246, 24 velas de edad). Las dos sospechas de S145 quedan REFUTADAS con medición: ni "no crea pools" (crea 704) ni "nacen y mueren barridos en la misma pierna" (1,4%); la causa del "1 solo pool visible" era el gate de dibujo `p.touches >= i_minTouches`. Predicciones escritas antes de medir: **4 vivas de 5** (muerta P3: predije >50% de barras sin SSL dibujable, medido 11% abajo y 25% arriba). El usuario corrigió la propuesta de quitar el gate: por §3.1 `touches = nº de extremos que confirman (>=2)`, un swing suelto NO es un pool sino otro concepto, §3.3 Grab, con menos peso. **F1-S1.3-T10b implementado:** `f_detectGrab` (`KIND_GRAB=24`, declarado y sin usar desde el inicio del proyecto) en el LIBRARY CORE, pura, partición excluyente con `f_detectSweep` por `touches`, NO alimenta `lastSweepBar`/`sweptRecently`; dibujo `"· Grab"` transp 85 vs `"✗ Sweep"` transp 70, comparte toggle `i_showSweeps`. Es la confluencia **#11** de las 42 canónicas (WORKPLAN §4.8); entró en la doctrina el 2026-06-10 (commit `429de10`, DOC-01 §3 Liquidez) ANTES del gate VER-09 (tag `ver-09-aprobado`, 2026-06-11), verificado con `git merge-base --is-ancestor` — le faltaba la Fase 1, no la Fase 0. S057 la había visto y la dejó como follow-up no bloqueante ("implícito en IDM/sweep"); S146 midió que ese implícito no se sostiene (`f_detectSweep` exige `touches>=minTouches`; IDM usa `structInternal`, liquidez interna, no swings aislados del chart). **ADR-027 PROPUESTO y ACORDADO, NO IMPLEMENTADO:** tramo punteado vela→vela con etiqueta al medio para Grab/Sweep-Raid-Spring/pool BSL-SSL barrido; Judas y False Breakout se quedan con etiqueta en la vela (no tienen fin único); etiqueta hacia afuera del precio (BSL encima, SSL debajo). **CORE 1783→1809 líneas, SHA `7ad95b3e612d041a`→`5e21ca38b43cf0e4`, check-core-sync OK ×3 en cada commit.** TV `SMC_Library` v419 (Visual) / `SMC_Context` v22. Compila 0/0 los tres. La curación de Liquidez (objetivo original de S144) SIGUE SIN RETOMARSE. **GOTCHAS:** `pine_inject.py` reconfirmado escribiendo en `getEditors()[0]` oculto (antídoto escrito `scripts/pine_inject_v2.py`, elige por `offsetParent`, `executeEdits`); cero dibujos del grab no era build rancio sino el toggle `in_84` (`i_showSweeps`) apagado desde el aislamiento de S145 — discriminador: si el hermano tampoco dibuja, es el toggle; el Pine Editor está en el botón lateral derecho `pine-dialog-button`, no en la barra inferior; el histórico M5 de OANDA solo alcanza ~2 semanas, los 3 casos canónicos de §3.3 (2026-06-10/11) no son reproducibles. **SIGUIENTE (S147):** medir el coste en objetos del tramo ADR-027 sobre UN concepto antes de extenderlo (tope duro 500 labels/500 lines, el Visual ya roza el de labels); implementar ADR-027 por subconjuntos verificados uno a uno; verificar §3.3 Grab en H1/M5 con casos nativos fechados; retomar curación de Liquidez; el set de pools está al tope (80/80, 42 barridos ocupan slot sin dibujar, `f_prunePoolsV` desaloja barridos primero así que no tira imanes vivos, anotado sin medir el daño). Estado del chart al cerrar: M5, ventana últimas 7h, `in_84` ENCENDIDO — si se retoma el DOL hay que volver al aislamiento de S145 (apagarlo) y a D1. F1-GATE sigue sin firmar. Ver [Sesion-146](sesiones/Sesion-146.md).

## Sesiones recientes (detalle completo en `memory/sesiones/`)
- **[[Sesion-145]]** (2026-07-25/27) — DOL: escalera de liquidez del máximo histórico al mínimo. ADR-026 aceptado (D1-D14). CORE intacto `7ad95b3e612d041a`.
- **[[Sesion-144]]** (2026-07-25) — arranque de la curación de la familia **Liquidez** (objetivo original, aún abierto): EQH/EQL sano, far/old pivots se conservan, pools barridos no se dibujan.
- **[[Sesion-143]]** (2026-07-23) — cierre de pendientes S142 (BRK, IPR, weekend-safe FVG) + escalonado X de labels por `kind`. Familia de zonas CERRADA.

## Bloqueos
- Ninguno. (SEC-01 resuelto: usuario confirmó keys viejas revocadas; nuevas en .env/.mcp.json gitignored.)

## Cómo arrancar la próxima sesión — **S147** (acordado con el usuario al cierre de S146)

**Objetivo:** implementar **ADR-027** (tramo vela→vela de la familia Liquidez) por subconjuntos, y con ello retomar la curación de la familia Liquidez que quedó abierta desde S144.

1. **Medir primero el coste en objetos** del tramo sobre **un solo concepto**. Cada evento pasa de *1 etiqueta* a *1 etiqueta + 1 línea*, y hay **topes duros de 500 de cada uno**. Sin esta medición no se implementa el resto.
2. **Implementar ADR-027 por subconjuntos, verificando cada uno** en este orden: **grab** → **sweep/raid/spring** → **pool barrido**.
3. **Verificar el grab en H1 y M5** con casos **nativos de cada TF**, fechados.
4. **Retomar la curación de la familia Liquidez** — sigue siendo el objetivo original de S144.

**⚠️ Estado en que quedó el entorno al cerrar S146:**
- **TV está apagado** — lanzar con `mcp__tradingview__tv_launch` (nunca a mano).
- El chart quedó en **M5 con la ventana de las últimas 7 h**.
- **`in_84` (`i_showSweeps`) quedó ENCENDIDO.** Si se retoma el **DOL**, hay que volver a **D1 y apagarlo** para recuperar el aislamiento.
- Antes de escribir inputs: **mapear `in_N` en vivo** — los índices se corren (en S145 se corrompieron 6 inputs numéricos por adivinar).

## Decisiones vigentes (no re-litigar)
- Arquitectura Pine: 1 core compartido + SMC-Visual.pine (indicator) + SMC-Strategy.pine (strategy → Strategy Tester).
- EA MT5 100% nativo, SIN webhook.
- 42 confluencias direccionales; pesos en Fase 3 con split IS/OOS 70/30.
- Solo EURUSD hasta gate de Fase 3. R:R mínimo 1:3. Anti-repaint obligatorio.
- Fuente de verdad del plan: WORKPLAN-MAESTRO-V2.md + docs/workplan/*.
- **ADR-002 — VER-09 APROBADO (2026-06-11, Sesion-009).** MSS swing / Judas / Breaker aceptados como composiciones de primitivos evidenciados; criterios de done convertidos en T12/T18/T19 (Fase 1). Umbrales CONGELADOS hasta calibración Fase 3 (anti-overfitting). MCP-06 saltado. Paridad Python↔Pine anotada en Fase 1. Ningún código antes del gate (completado). Límite ~300 velas documentado; validación visual sin límite (chart_scroll_to_date/replay/screenshots).
- **ADR-003 — ESTRATEGIA DE RAMAS (2026-06-11, Sesion-010, decisión Freddy).** Dos ramas largas, una por gran etapa de desarrollo:
  - **`pine/sistema-completo`** = TODO el Pine (Fases 1-3, los 25+ conceptos + Strategy + calibración). Los commits de cierre de sesión (ESTADO-ACTUAL, Sesion-NNN, ADRs) fluyen **en esta rama**; `main` permanece estable. Se fusiona a `main` **SOLO** tras pasar el GATE DURO de entrada a Fase 4 (WORKPLAN §FASE 4, líneas 171-176): Fable revisa y aprueba explícitamente el sistema Pine completo.
  - **`mql5/ea-nativo`** (nombre propuesto) = Fase 4, el Expert Advisor MT5. Se crea **al cerrar la última sesión de Pine**, después de la aprobación de Fable, partiendo de `main` ya fusionado.
  - Regla: ningún MQL5 hasta cerrar la rama Pine + gate Fable. Cada rama = una gran etapa; main = hitos aprobados.

### Fundacionales (DOC-01)
- Umbrales SIEMPRE relativos a ATR(14), nunca pips fijos.
- swingLen=5 / internalLen=3 (ajustable en pruebas Fase 3).
- BOS/CHoCH por CIERRE, no mecha. Modelo bias = structure high/low (extensor vs protector).
- MSS = CHoCH de nivel swing + displacement (≥1.5×ATR, cuerpo ≥70%) — lo distingue del CHoCH simple en el scoring.
- Storage keys: .mcp.json + .env (ambos gitignored), sin migrar a env vars de Windows.
- **ADR-001 — Bot MULTI-SÍMBOLO, sin filtro horario duro.** Kill Zone = confluencia ponderada + sessionProfile configurable (FX-London-NY/FX-Asia/None), no bloqueo. Guardián universal = filtro de spread. Pesos del scoring por símbolo. Valida EURUSD primero, cada símbolo nuevo = Fase 5 abreviada. Umbrales ATR-relativo = base de portabilidad.

### ADRs
Índice completo en `docs/adrs/` (**ADR-001 … ADR-027**). Vigentes de referencia frecuente: **ADR-003** (ramas), **ADR-006** (ciclo de vida de pools), **ADR-014** (`strength` es propiedad de detección, vive en el CORE), **ADR-017** (consumidor Context), **ADR-021** (dealing range, 2.º extremo), **ADR-023** (el panel se lee desde el TF más bajo), **ADR-024** (reparto del dibujo Visual/Context), **ADR-026** (DOL: escalera + marcador de borde). **ADR-027 está 🟡 PROPUESTO — se implementa en S147.**

## Notas de herramientas
- **TV MCP:** lanzar SIEMPRE por `mcp__tradingview__tv_launch` (CDP 9222), nunca manual. Fork en `D:\CODE\BOT\Bot\tradingview-mcp-jackson` +4 ahead de origin (merge upstream sin pushear).
- **rules.json** (morning_brief) vive en la raíz del repo-herramienta TV MCP. Config EURUSD/H1/SMC. Si merges de upstream lo tocan, re-aplicar.
- **code-review-graph** v2.3.2: binario OK, repo registrado como `estrategia2`, `serve` arranca. Grafo vacío *por naturaleza* (P-12: no parsea Pine; el resto es .md). Útil de verdad desde Fase 1 SOLO si se le da código en lenguaje soportado — Pine NO lo es, así que su valor real es limitado. Los tools del MCP deberían registrar al reiniciar la sesión.
- **Archon (MCP-03) ✅ INSTALADO — OJO: cambió de arquitectura.** El Archon real (v0.4.1) NO es el RAG/Docker que asumía el workplan: es una **"Remote Agentic Coding Platform"** (Bun+SQLite, controla Claude Code/Codex vía Slack/Telegram/GitHub) con **motor de workflows DAG** (lo que sí usamos para `smc-sprint`). App clonada en `D:\CODE\Archon` (NO dentro del repo). `bun run cli doctor` = All checks passed; 20 workflows default visibles (archon-architect, archon-validate-pr, etc. — coinciden con refs del workplan). Sin Docker, sin Slack/Telegram (no se necesitan). Invocar con `scripts/archon.ps1 <args>` desde el proyecto. ⚠️ NO correr workflows que invoquen Claude dentro de una sesión Claude Code (CLAUDECODE=1 → cuelgue, issue #1067) — usar terminal normal. Ver [[estrategia2-archon-remote-agent-platform]].
- **task-master (MCP-06):** **OPCIONAL — se puede saltar sin perder nada** (decisión usuario Sesion-005). No es pieza del sistema (el WORKPLAN ya es el backlog; teoría→indicador corre sobre reglas-smc-ict.md + smc-sprint/Archon + smc-validator-agent). Si se hiciera, es en VER-09 y **a criterio de Fable** decidir si vale la pena (probablemente no). CLI disponible (0.43.1).
- **SCR-02 sync-obsidian.ps1** ✅: copia incremental (por hash) de `memory/sesiones/`, `docs/adrs/`, `memory/ESTADO-ACTUAL.md` → `D:\obsidian\boveda MENTE\Mente\Estrategia2.0\`. `-DryRun` para simular. Idempotente. Adelantado del Bloque F.

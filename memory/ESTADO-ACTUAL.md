# ESTADO ACTUAL — Estrategia 2.0

> **Reglas de este archivo — leerlas antes de escribirlo.**
> 1. Es **estado vivo, no histórico**. El histórico de cada sesión vive en `memory/sesiones/Sesion-NNN.md` y ahí se queda.
> 2. **Ventana rodante:** la sesión en curso en detalle + las 3 anteriores como **una línea** con enlace. Al cerrar la sesión N, la N-4 se borra de aquí (su fichero ya la conserva).
> 3. **Techo duro 40 KB.** Por encima de **256 KB** el tool `Read` del agente no puede abrir el archivo y el arranque se hace **a ciegas**: eso pasó de hecho entre el 2026-07-20 (S~140) y S146, con el archivo en 291 KB.
> 4. La sección **«Cómo arrancar la próxima sesión» se REEMPLAZA, nunca se apila.** Estuvo congelada en S090 durante 56 sesiones.
> 5. Lo actualiza `smc-doc-updater` en `/smc-session-close`. **Rotar, no acumular.**

## Estado
- **Rama de trabajo:** **`pine/sistema-completo`** (creada Sesion-010, publicada en origin). Todo el código Pine (Fases 1-3) vive aquí; `main` queda estable hasta el gate de Fable pre-Fase 4. Ver **ADR-003**.
- **Fase actual:** **FASE 1 · S148 — ADR-027 (tramo vela→vela de la familia Liquidez) ACEPTADO E IMPLEMENTADO EN D1, POR SUBCONJUNTOS VERIFICADOS.** Se ejecutaron las tareas 1-3 del plan de S147; la tarea 4 (curación de Liquidez, objetivo original de S144) queda para S149. **Tarea 1 — medición:** `data_get_pine_lines`/`data_get_pine_labels` devuelven `total_lines`/`total_labels` (censo crudo; `horizontal_levels` deduplica y engañaba desde S144). Coste real del ADR con rango visible fijo (la banda del DOL depende del rango, ADR-026, así que rangos distintos NO son comparables — las dos primeras medidas, contaminadas, dieron falsos +21/+20): **+42 líneas** sobre las 125 de la familia Liquidez (grab+sweep +40 exactas, pool barrido +2). **HALLAZGO 1 (el importante): el tope de 500 objetos YA ESTABA DESBORDADO antes de este ADR, y la culpable es ESTRUCTURA, no Liquidez.** Con todos los toggles encendidos: *Todo* 501 líneas/503 etiquetas, *Estudio* 504/500 (topes son 500/500) ⇒ Pine lleva tiempo desalojando en silencio los objetos creados primero (los de más señal). Aislado: `in_10` («Mostrar BOS/CHoCH (swing)») él solo genera **302 líneas + 302 etiquetas** (60% del presupuesto) y es el ÚNICO concepto de estructura SIN cuota `i_maxShow*`. La frecuencia del evento no predice el gasto; lo predice si el dibujo tiene cuota o no. **HALLAZGO 2:** el subconjunto pool-barrido nace casi inerte (solo 2 tramos en toda la historia D1) porque `f_prunePools` (ADR-006) borra los pools barridos ANTES de que sobrevivan para dibujarse — palanca real: la poda, no el dibujo. **Tarea 2 — implementación (3 commits, cada uno aplicado y medido en TV antes del siguiente):** grab (`e57c68a`, nuevo `SMC_Event.origBarTime`), sweep/raid/spring (`4f59c83`, bug encontrado: `SMC_Pool.barTime` guardaba el ÚLTIMO toque no el PRIMERO, se añade `SMC_Pool.firstBarTime` fijado en el alta), pool barrido (`4988819`, dotted, filtro anti-duplicado contra sweep ya emitido). ADR-027 → **ACEPTADO (`390164e`)**, D2 (Judas/False breakout sin tramo) sigue vigente y sin código. CORE **1813 líneas, SHA `b2be604143c08a83`** (verificado byte-idéntico ×3), TV `SMC_Library` v419→**v422**. **Tarea 3 — verificación nativa del grab en H1/M5** (cierra ADR-027 §6): el censo de dibujos no fecha (índices + precios redondeados), se reimplementó §3.3 independiente sobre velas nativas (`scripts/gen_probe_grab_nativo.js`). H1 (401 velas, 46 pools, 18 grabs): caso ancla Grab BSL 2026-07-22 13:00 UTC nivel 1.14184 coincide con lo dibujado. M5 (300 velas, 23 pools, 6 grabs, todos 2026-07-28): dos casos (BSL 12:50, SSL 12:30 UTC) coinciden. La sonda ve menos grabs que el indicador (18/6 vs 20/14) porque solo alcanza las velas cargadas por TV — no es discrepancia, los casos concretos coinciden uno a uno. Commits `31ba71b` (§3.3 en reglas-smc-ict.md) y `8ede405` (ADR-027 §6 RESUELTO). **Obstáculo de herramienta:** modal promocional de TV bloqueó `chart_set_timeframe`/`chart_set_visible_range`; se resolvió cerrándolo por DOM (`button[aria-label="Cierre"]`, en español) y forzando resolución vía `TradingViewApi._activeChartWidgetWV`. **F1-GATE sigue sin firmar.** Ver [Sesion-148](sesiones/Sesion-148.md).

## Sesiones recientes (detalle completo en `memory/sesiones/`)
- **[[Sesion-147]]** (2026-07-28) — reparado el arranque de sesión (ESTADO-ACTUAL rota, no acumula) + CLAUDE.md pasa a MAPA de ≤40 líneas + ADR-003 escrito + índice de ADRs. Plan de S147 (ADR-027) pasó íntegro a S148.
- **[[Sesion-146]]** (2026-07-28) — hilo de pools RESUELTO por medición (la causa era el gate `touches>=2`, no la creación: 704 altas) + **§3.3 Grab implementado** (`f_detectGrab`, F1-S1.3-T10b, confluencia #11, 96/100) + **ADR-027 propuesto**. CORE → `5e21ca38b43cf0e4` (1809 líneas).
- **[[Sesion-145]]** (2026-07-25/27) — DOL: escalera de liquidez del máximo histórico al mínimo. ADR-026 aceptado (D1-D14). CORE intacto `7ad95b3e612d041a`.

## Bloqueos
- Ninguno. (SEC-01 resuelto: usuario confirmó keys viejas revocadas; nuevas en .env/.mcp.json gitignored.)

## Cómo arrancar la próxima sesión — **S149**

**Objetivo:** retomar la **tarea 4 de S148, no ejecutada**: la curación visual de la familia
Liquidez (hue violeta sobrecargado, anti-solape EQL↔Sweep) — objetivo original heredado de
**S144**, sigue abierto.

1. **Volver a D1** (el chart quedó en M5 tras la tarea 3 de S148).
2. **Reencender los toggles de Liquidez** que quedaron apagados por el aislamiento de la
   tarea 3 (`in_78`, `in_81`, `in_87`, `in_90`, `in_92`) — mapear `in_N` en vivo antes de
   escribir, no adivinar.
3. Ejecutar la curación: revisar colisión de paleta/hue en la familia Liquidez y el
   anti-solape EQL↔Sweep, ahora con los tramos vela→vela de ADR-027 ya dibujados.
4. **Fuera de esta tarea pero anotado como pendiente** (no bloquea S149, decidir si se
   aborda): poner cuota a `in_10` (BOS/CHoCH swing), que hoy genera 302 líneas + 302
   etiquetas sin `i_maxShow*` — 60% del presupuesto de 500 objetos (hallazgo de S148). Y si
   se quiere ver el historial real de pools barridos, revisar la poda `f_prunePools`
   (ADR-006), no el dibujo.

**⚠️ Estado en que quedó el entorno (S148 dejó TV abierto):**
- **TV abierto**, `SMC_Library` **v422** guardado, editor de Pine abierto con el Visual.
- Chart en **M5**, ventana visible 2026-07-28 11:00→14:30 UTC. Volver a D1.
- Inputs: solo `in_84` (sweeps/grabs) encendido de la familia Liquidez; `in_78`, `in_81`,
  `in_87`, `in_90`, `in_92` apagados. `in_118` (Densidad) = Todo. `in_85` (max sweeps) = 20.
- Antes de escribir inputs: **mapear `in_N` en vivo** — los índices se corren (en S145 se
  corrompieron 6 inputs numéricos por adivinar).

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
Índice completo en `docs/adrs/` (**ADR-001 … ADR-027**). Vigentes de referencia frecuente: **ADR-003** (ramas), **ADR-006** (ciclo de vida de pools), **ADR-014** (`strength` es propiedad de detección, vive en el CORE), **ADR-017** (consumidor Context), **ADR-021** (dealing range, 2.º extremo), **ADR-023** (el panel se lee desde el TF más bajo), **ADR-024** (reparto del dibujo Visual/Context), **ADR-026** (DOL: escalera + marcador de borde). **ADR-027 🟢 ACEPTADO E IMPLEMENTADO en D1 (S148)** — tramo vela→vela de la familia Liquidez (grab/sweep/pool barrido); D2 (Judas/False breakout) sigue vigente y sin código.

## Notas de herramientas
- **TV MCP:** lanzar SIEMPRE por `mcp__tradingview__tv_launch` (CDP 9222), nunca manual. Fork en `D:\CODE\BOT\Bot\tradingview-mcp-jackson` +4 ahead de origin (merge upstream sin pushear).
- **rules.json** (morning_brief) vive en la raíz del repo-herramienta TV MCP. Config EURUSD/H1/SMC. Si merges de upstream lo tocan, re-aplicar.
- **code-review-graph** v2.3.2: binario OK, repo registrado como `estrategia2`, `serve` arranca. Grafo vacío *por naturaleza* (P-12: no parsea Pine; el resto es .md). Útil de verdad desde Fase 1 SOLO si se le da código en lenguaje soportado — Pine NO lo es, así que su valor real es limitado. Los tools del MCP deberían registrar al reiniciar la sesión.
- **Archon (MCP-03) ✅ INSTALADO — OJO: cambió de arquitectura.** El Archon real (v0.4.1) NO es el RAG/Docker que asumía el workplan: es una **"Remote Agentic Coding Platform"** (Bun+SQLite, controla Claude Code/Codex vía Slack/Telegram/GitHub) con **motor de workflows DAG** (lo que sí usamos para `smc-sprint`). App clonada en `D:\CODE\Archon` (NO dentro del repo). `bun run cli doctor` = All checks passed; 20 workflows default visibles (archon-architect, archon-validate-pr, etc. — coinciden con refs del workplan). Sin Docker, sin Slack/Telegram (no se necesitan). Invocar con `scripts/archon.ps1 <args>` desde el proyecto. ⚠️ NO correr workflows que invoquen Claude dentro de una sesión Claude Code (CLAUDECODE=1 → cuelgue, issue #1067) — usar terminal normal. Ver [[estrategia2-archon-remote-agent-platform]].
- **task-master (MCP-06):** **OPCIONAL — se puede saltar sin perder nada** (decisión usuario Sesion-005). No es pieza del sistema (el WORKPLAN ya es el backlog; teoría→indicador corre sobre reglas-smc-ict.md + smc-sprint/Archon + smc-validator-agent). Si se hiciera, es en VER-09 y **a criterio de Fable** decidir si vale la pena (probablemente no). CLI disponible (0.43.1).
- **SCR-02 sync-obsidian.ps1** ✅: copia incremental (por hash) de `memory/sesiones/`, `docs/adrs/`, `memory/ESTADO-ACTUAL.md` → `D:\obsidian\boveda MENTE\Mente\Estrategia2.0\`. `-DryRun` para simular. Idempotente. Adelantado del Bloque F.

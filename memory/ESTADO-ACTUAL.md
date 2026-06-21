# ESTADO ACTUAL — Estrategia 2.0
> Actualizar al cierre de CADA sesión (lo hace smc-doc-updater vía /smc-session-close cuando existan).

## Estado
- **Rama de trabajo:** **`pine/sistema-completo`** (creada Sesion-010, publicada en origin). Todo el código Pine (Fases 1-3) vive aquí; `main` queda estable hasta el gate de Fable pre-Fase 4. Ver **ADR-003**.
- **Fase actual:** **FASE 1 · Sprint 1.4 (MTF) EN CURSO** — gate P3+ADR-008 APROBADO (S040) → **T13a mapa MTF núcleo ✅ COMPLETO/VALIDADO 95/100/COMMITEADO (d6a5418, 2026-06-20)**; **T13b mapa MTF rico (buffer genérico etiquetado) ✅ COMPLETO/COMMITEADO (99ddeec, 2026-06-20)** entrega mapa de NIVELES sin geometría nativa; revisión S041 = diagnóstico: ADR-009 omitió barTime deliberadamente, T13c reconstruye forma nativa por xloc.bar_time; **T13c mapa MTF geométrico (dibujo nativo anclado) ✅ COMPLETO/IMPLEMENTADO/COMMITEADO (88500fd, 2026-06-20)** [implementación [[Sesion-042]] basada en ADR-010 + esqueleto revision-T13b-mtf-dibujo-nativo.md]. **Sprint 1.3 (Liquidez) ✅ COMPLETADO.** Sprint 1.1 COMPLETADO ✅ (T01 S011 45449f3 · T02 S012 aa4ed23 · T03 S013 abc5988 · T04 S014 3dff0a6). **T05 Order Blocks COMPLETO ✅ (S016 698b9dd).** **T06 Fair Value Gaps COMPLETO ✅ (S017 8c5f88f).** **T07 Premium/Discount/Equilibrium COMPLETO ✅ (S021 ddd8cc5).** **T07B Estructura BOS/CHoCH DOMINANTE (swing 50) COMPLETO ✅ (S022).** **T08 Equal Highs/Equal Lows (EQH/EQL) COMPLETO ✅ (S026 0b63eda).** **T09 Pools de Liquidez (f_buildPools) BUILD COMPLETO ✅ (S027 139e1c1).** **T09b/T10 Pools persistentes + Sweep ✅ COMPLETO, VALIDADO (93/100), COMMITEADO (45c4b40, 2026-06-17).** **T11 Kill Zones ✅ COMPLETO, VALIDADO (95/100), COMMITEADO (68f2946, 2026-06-19).** **T12 MSS ✅ COMPLETO, VALIDADO, COMMITEADO (4b4f3cc, 2026-06-20).** Compila 0/0 los 3, core-sync OK SHA **4dc885e1bd23ec8b** (926 líneas, antes 5e8887eb119bd340/853), commit 88500fd (2026-06-20).

- **Última tarea completada Pine (Sesion-042):** **F1-S1.4-T13c Mapa MTF geométrico (dibujo nativo anclado) ✅ COMPLETO, IMPLEMENTADO, COMMITEADO — implementación ADR-010.** Commit **88500fd** (2026-06-20). En CORE byte-idéntico (Visual/Strategy, export en Library): (1) **Ranura del buffer MTF extendida:** 4→6 campos `[kind,top,bottom,dir,tA,tB]` con anclaje temporal (tA=tiempo barra origen, tB=tiempo fin / na=extiende al borde). Constantes MTF_K reducida 16→12, MTF_SLOT aumentada 4→6 (tuple 17+12×6=89 < ~127, 1 request.security/TF). (2) **`f_nearestN`/`f_nearestNPools`:** anexan tA/tB a candidatos. (3) **NUEVAS `f_pushMTFEvent` + `f_nearestNEvents`:** buffer paralelo (kind/level/dir/tA/tB) para conceptos TRAMO/MARCA — BOS/CHoCH (origen→ruptura), EQH/EQL (toque→toque), Sweep (su barra). Antes BOS/CHoCH solo viajaban como escalar. (4) **`f_computeTFState`:** firma +4 caps (capSweep/capEQ/capBOS/capCHoCH), emite TODOS los conceptos con cap propio 0-10. FVG anclado en vela MEDIA real (`time[1]` barIdx-1 nativo). Visual (no en core byte-idéntico): (5) **`f_drawMTFZones` reescrita** con switch por kind + `xloc.bar_time`: OB/FVG=caja con línea 50% + nombre; EQH/EQL=línea punteada azul toque-a-toque + etiqueta centrada SIN nube; BOS/CHoCH=línea origen→ruptura + etiqueta (arriba alcista/abajo bajista); Sweep=marca ▲/▼; Pool=línea nivel. Cajas en `var array<box> SMC_mtfBoxes`. (6) **ANTI-DUPLICADO BOS/CHoCH:** si el BOS/CHoCH del HTF coincide con estructura grande nativa M5 (misma dir + nivel ±0.3·ATR + ruptura dentro tramo) capa MTF NO dibuja nada → queda nativo. HTFs no coincidentes muestran línea + etiqueta `BOS (H1)` / `CHoCH (H1)` / `CHoCH MSS (H1)`. (7) **Inputs GRP_MTF nuevos:** i_mtfCapSweep, i_mtfCapEQ, i_mtfCapBOS, i_mtfCapCHoCH (+ i_mtfSweepMark) en Visual; mismos caps en Strategy. **FIX importante:** RE10020 ("Objects positioned using xloc.bar_index cannot be drawn further than 500 bars into the future") — etiquetas EQ/BOS/CHoCH/Pool en f_drawMTFZones faltaban `xloc = xloc.bar_time`, caían como bar_index al futuro lejano. Resuelto. **Validación:** visual iterativa con usuario (3 rondas) en TradingView EURUSD M5; renderiza sin runtime errors; OB/FVG cubren zona, EQH/EQL/BOS/CHoCH/Sweep transferidos con forma nativa anclada. **Pendientes diferidos** (notas follow-up, NO bloquean): (a) Tag `(D1/H1)` en BOS/CHoCH FUSIONADOS con nativa (hoy quedan sin TF); (b) EQH/EQL cuadre fino líneas (revisar cálculo velas pivote-a-pivote); (c) FVG/OB exactitud vela-a-vela (usuario aceptó actual "cubre lo necesario"). Compila **0/0 los 3**, core-sync OK. **BLOQUEOS:** ninguno. **ADRs nuevos:** ninguno (ADR-010 ya existía S041; esta sesión lo IMPLEMENTÓ). **Siguiente:** T14 panel MTF o tarea siguiente Sprint 1.4. Ver [[Sesion-042]].

- **Última tarea completada ANTERIOR (Sesion-041):** **T13b REVISIÓN + T13c DISEÑO + ADR-010 — mapa MTF geométrico.** Tipo: revisión + diseño (NO implementación). Ver Sesion-041.

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
- **ADR-002 — VER-09 APROBADO (2026-06-11, Sesion-009).** MSS swing / Judas / Breaker aceptados como composiciones de primitivos evidenciados; criterios de done convertidos en T12/T18/T19 (Fase 1). Umbrales CONGELADOS hasta calibración Fase 3 (anti-overfitting). MCP-06 saltado. Paridad Python↔Pine anotada en Fase 1. Ningún código antes del gate (completado). Límite ~300 velas documentado; validación visual sin límite (chart_scroll_to_date/replay/screenshots).
- **ADR-003 — ESTRATEGIA DE RAMAS (2026-06-11, Sesion-010, decisión Freddy).** Dos ramas largas, una por gran etapa de desarrollo:
  - **`pine/sistema-completo`** = TODO el Pine (Fases 1-3, los 25+ conceptos + Strategy + calibración). Los commits de cierre de sesión (ESTADO-ACTUAL, Sesion-NNN, ADRs) fluyen **en esta rama**; `main` permanece estable. Se fusiona a `main` **SOLO** tras pasar el GATE DURO de entrada a Fase 4 (WORKPLAN §FASE 4, líneas 171-176): Fable revisa y aprueba explícitamente el sistema Pine completo.
  - **`mql5/ea-nativo`** (nombre propuesto) = Fase 4, el Expert Advisor MT5. Se crea **al cerrar la última sesión de Pine**, después de la aprobación de Fable, partiendo de `main` ya fusionado.
  - Regla: ningún MQL5 hasta cerrar la rama Pine + gate Fable. Cada rama = una gran etapa; main = hitos aprobados.

## Cómo arrancar la próxima sesión
1. Leer este archivo + WORKPLAN-MAESTRO-V2.md Sección 3 (Fase 0).
2. Confirmar SEC-01 hecho por el usuario.
3. Ejecutar Fase 0 en orden: Bloque A → B → C → D → E → F → VER-01..08.

## Notas de herramientas (Sesion-005)
- **TV MCP:** lanzar SIEMPRE por `mcp__tradingview__tv_launch` (CDP 9222), nunca manual. Fork en `D:\CODE\BOT\Bot\tradingview-mcp-jackson` +4 ahead de origin (merge upstream sin pushear).
- **rules.json** (morning_brief) vive en la raíz del repo-herramienta TV MCP. Config EURUSD/H1/SMC. Si merges de upstream lo tocan, re-aplicar.
- **code-review-graph** v2.3.2: binario OK, repo registrado como `estrategia2`, `serve` arranca. Grafo vacío *por naturaleza* (P-12: no parsea Pine; el resto es .md). Útil de verdad desde Fase 1 SOLO si se le da código en lenguaje soportado — Pine NO lo es, así que su valor real es limitado. Los tools del MCP deberían registrar al reiniciar la sesión.
- **Archon (MCP-03) ✅ INSTALADO — OJO: cambió de arquitectura.** El Archon real (v0.4.1) NO es el RAG/Docker que asumía el workplan: es una **"Remote Agentic Coding Platform"** (Bun+SQLite, controla Claude Code/Codex vía Slack/Telegram/GitHub) con **motor de workflows DAG** (lo que sí usamos para `smc-sprint`). App clonada en `D:\CODE\Archon` (NO dentro del repo). `bun run cli doctor` = All checks passed; 20 workflows default visibles (archon-architect, archon-validate-pr, etc. — coinciden con refs del workplan). Sin Docker, sin Slack/Telegram (no se necesitan). Invocar con `scripts/archon.ps1 <args>` desde el proyecto. ⚠️ NO correr workflows que invoquen Claude dentro de una sesión Claude Code (CLAUDECODE=1 → cuelgue, issue #1067) — usar terminal normal. Ver [[estrategia2-archon-remote-agent-platform]].
- **task-master (MCP-06):** **OPCIONAL — se puede saltar sin perder nada** (decisión usuario Sesion-005). No es pieza del sistema (el WORKPLAN ya es el backlog; teoría→indicador corre sobre reglas-smc-ict.md + smc-sprint/Archon + smc-validator-agent). Si se hiciera, es en VER-09 y **a criterio de Fable** decidir si vale la pena (probablemente no). CLI disponible (0.43.1).
- **SCR-02 sync-obsidian.ps1** ✅: copia incremental (por hash) de `memory/sesiones/`, `docs/adrs/`, `memory/ESTADO-ACTUAL.md` → `D:\obsidian\boveda MENTE\Mente\Estrategia2.0\`. `-DryRun` para simular. Idempotente. Adelantado del Bloque F.

*Sesion-042 (2026-06-20): **F1-S1.4-T13c Mapa MTF geométrico (dibujo nativo anclado) ✅ IMPLEMENTADO + COMMITEADO.** Commit **88500fd** (2026-06-20). CORE byte-idéntico MODIFICADO: NUEVO SHA `4dc885e1bd23ec8b` (926 líneas; antes `5e8887eb119bd340`/853). Ver "Última tarea completada" línea 7 (resumen completo). Implementación ADR-010 basada en esqueleto `docs/sprint-runs/revision-T13b-mtf-dibujo-nativo.md`. Validación: visual iterativa con usuario (3 rondas) EURUSD M5, inyectado + testeado en TradingView. Compila 0/0 los 3. Pendientes diferidos: tag TF en BOS/CHoCH fusionados, cuadre EQH/EQL, exactitud FVG/OB vela-a-vela (notas follow-up, NO bloquean). **BLOQUEOS:** ninguno. **ADRs:** ADR-010 IMPLEMENTADO (ya existía S041). **Gates:** ninguno completado. Siguiente: T14 panel MTF o siguiente tarea Sprint 1.4. ★ GATE PRE-TESTEO DE SETUPS sigue vigente (Pine completo Y enjambre completo). Ver [[Sesion-042]].*

*Última actualización: 2026-06-20 — Sesion-042: **T13c ✅ IMPLEMENTADO/COMMITEADO (88500fd).** ADR-010 ejecutado. Core-sync NEW SHA 4dc885e1bd23ec8b (926 líneas). Siguiente: T14 panel MTF o tarea Sprint 1.4. Ver [[Sesion-042]].*

*Sesion-041 (2026-06-20): **T13b REVISIÓN + T13c DISEÑO + ADR-010 — mapa MTF geometrico.** Tipo: revisión + diseño (NO implementación). (1) **T13b DIAGNOSTICADO:** buffer genérico etiquetado (ADR-009 4 campos [kind,top,bottom,dir]) entrega mapa de NIVELES (líneas punteadas), NO geometría nativa (cajas OB/FVG, marcas ▲▼ sweep, origen→ruptura BOS/CHoCH). Causa: ADR-009 omitió barTime deliberadamente. Hallazgo Freddy = preciso. Commit 99ddeec estaba pendiente revisión, APROBADO. (2) **T13c DISEÑO:** `docs/sprint-runs/revision-T13b-mtf-dibujo-nativo.md` [NUEVO] esqueleto implementación-ready (Paso 0–6 + gotchas §9). `ADR-010` [NUEVO] = supersede dibujo de ADR-009 solamente: ranura 4→6 campos `[kind,top,bottom,dir,tA,tB]` (anclaje temporal), consumidor reconstruye forma NATIVA por `xloc.bar_time` (OB/FVG=caja, sweep=marca ▲▼, EQH/EQL=línea, BOS/CHoCH=origen→ruptura), cap 0–10 por concepto, K=12 total recomendado, emitir BOS/CHoCH/EQH/EQL al buffer. Integrado PINE-PLAN §7 + ESQUELETO-P3 §4.1/§5.2/§5.4. Core-sync INTACTO SHA 5e8887eb119bd340 (853 líneas), 0 .pine editados. Decisión Freddy: implementación T13c = próxima sesión. **BLOQUEOS:** ninguno. **ADRs:** ADR-009 commiteado (99ddeec), ADR-010 aceptado (implementación S042). Commit **8eafd6f**. Ver [[Sesion-041]].*

*Sesion-040 (2026-06-20): **GATE P3+ADR-008 APROBADO por Freddy + F1-S1.4-T13a MAPA MTF NÚCLEO ✅ COMPLETO, VALIDADO 95/100, COMMITEADO — abre Sprint 1.4.** Commit **d6a5418**. CORE byte-idéntico MODIFICADO: NUEVO SHA `46b337d1952baa6c` (695 líneas; antes `2de06be3a3eb1321`/644). Ver [[Sesion-040]].*

*Sesion-039 (2026-06-20): **SPIKE TEST R-P3-1 ✅ PASA** — gate técnico de T13a→T13b superado. Ver [[Sesion-039]].*

*Sesion-038 (2026-06-20) — Última sesión:* **ENTREGA del encargo de Opus Max — ESQUELETO-P3 + ADR-008 + WORKPLAN UNIFICADO.** Ver [[Sesion-038]].*

*Sesion-037 (2026-06-20):* **DISEÑO + HANDOFF — Sprint 1.4 MTF + confluencias + enjambre.** Ver [[Sesion-037]].*

*Sesion-035 (2026-06-19): **F1-S1.3-T11 Kill Zones ✅ COMPLETO, VALIDADO, COMMITEADO.** Ver [[Sesion-035]].*

*Sesion-034 (2026-06-19): **PLANIFICACIÓN — Oficialización Sprint 1.6 + cruce anti-duplicados.** Ver [[Sesion-034]].*

*Sesion-033 (2026-06-19): **PLANIFICACIÓN — Esqueleto integración PARTE 2 (Hermes + enjambre).** Ver [[Sesion-033]].*

*Sesion-032 (2026-06-19): **PLANIFICACIÓN — Esqueleto integración gap conceptos.** Ver [[Sesion-032]].*

*Sesion-031 (2026-06-19): **Investigación + config Hermes.** Ver [[Sesion-031]].*

*Sesion-030 (2026-06-18): **F1-S1.3-T09b/T10 CIERRE FORMAL ✅ COMMITEADO + Módulo Mentores.** Ver [[Sesion-030]].*

*Sesion-029 (2026-06-17): **Módulo Mentores — fix timestamps + diagnóstico Hermes.** Ver [[Sesion-029]].*

*Sesion-028 (2026-06-17): **Esqueleto de implementación de la mitigación.** Ver [[Sesion-028]].*

*Sesion-027 (2026-06-17): **F1-S1.3-T09 Pools de Liquidez ✅ BUILD COMPLETO.** Ver [[Sesion-027]].*

*Sesion-026 (2026-06-16): **F1-S1.2-T08 Equal Highs/Equal Lows ✅ COMPLETO.** Ver [[Sesion-026]].*

*Sesion-025 (2026-06-16): **Revisión plan Mentores/Swarm por Opus — ADR-005.** Ver [[Sesion-025]].*

*Sesion-024 (2026-06-16): **Módulo Mentores CONSTRUIDO — pipeline E2E.** Ver [[Sesion-024]].*

*Sesion-023 (2026-06-15): **Sesión Hermes/mentores — GPU CUDA + workflow redesign.** Ver [[Sesion-023]].*

*Sesion-022 (2026-06-15): **F1-S1.2-T07B Estructura BOS/CHoCH DOMINANTE ✅ COMPLETO.** Ver [[Sesion-022]].*

*Sesion-021 (2026-06-14): **F1-S1.2-T07 Premium/Discount/Equilibrium ✅ COMPLETO.** Ver [[Sesion-021]].*

*Sesion-020 (2026-06-14): **Sesión de orden y cierre — GPU CUDA activada + módulo Mentores V1.** Ver [[Sesion-020]].*

*Sesion-019 (2026-06-14): **Pipeline transcripción Hermes — faster-whisper CPU int8.** Ver [[Sesion-019]].*

*Sesion-018 (2026-06-13): **Corrección de coherencia documental T06.** Ver [[Sesion-018]].*

*Sesion-017 (2026-06-13):* **F1-S1.2-T06 — Fair Value Gaps (FVG) + Competitive Edge (CE).** Ver [[Sesion-017]].*

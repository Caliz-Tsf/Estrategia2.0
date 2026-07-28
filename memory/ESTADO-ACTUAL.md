# ESTADO ACTUAL — Estrategia 2.0

> **Reglas de este archivo — leerlas antes de escribirlo.**
> 1. Es **estado vivo, no histórico**. El histórico de cada sesión vive en `memory/sesiones/Sesion-NNN.md` y ahí se queda.
> 2. **Ventana rodante:** la sesión en curso en detalle + las 3 anteriores como **una línea** con enlace. Al cerrar la sesión N, la N-4 se borra de aquí (su fichero ya la conserva).
> 3. **Techo duro 40 KB.** Por encima de **256 KB** el tool `Read` del agente no puede abrir el archivo y el arranque se hace **a ciegas**: eso pasó de hecho entre el 2026-07-20 (S~140) y S146, con el archivo en 291 KB.
> 4. La sección **«Cómo arrancar la próxima sesión» se REEMPLAZA, nunca se apila.** Estuvo congelada en S090 durante 56 sesiones.
> 5. Lo actualiza `smc-doc-updater` en `/smc-session-close`. **Rotar, no acumular.**

## Estado
- **Rama de trabajo:** **`pine/sistema-completo`** (creada Sesion-010, publicada en origin). Todo el código Pine (Fases 1-3) vive aquí; `main` queda estable hasta el gate de Fable pre-Fase 4. Ver **ADR-003**.
- **Fase actual:** **FASE 1 · S147 — EL ARRANQUE DE SESIÓN ESTABA ROTO: `ESTADO-ACTUAL` AHORA ROTA EN VEZ DE ACUMULAR (sesión de infraestructura documental, CERO Pine).** El plan de S147 (ADR-027) **no se ejecutó**: al leer este archivo, paso 1 BLOQUEANTE del arranque, el tool `Read` falló. Medidos **dos** defectos. **(a) Tamaño:** pesaba **291.219 B** contra el límite de `Read` de **262.144**; por `git log` cruzó el límite entre el **2026-07-18 (254.164 B)** y el **2026-07-20 (259.423 B)** ⇒ **desde ~S140 ningún arranque pudo leer el estado**, ~5 KB por sesión. Apilaba desde **Sesion-017** en **tres series superpuestas** (`Fase (SNNN)` ×18, `Última tarea (Sesion-NNN)` ~45, `*Sesion-NNN:*` ~30) con duplicados (S100, S095) y **4.685 chars** de historial embebido dentro de la línea de fase actual como `<!-- historial -->`. **(b) Frescura — el grave:** la sección «Cómo arrancar la próxima sesión» llevaba **congelada en S090 durante 56 sesiones** (mandaba al Paso 9 del Eje 2 y a las opciones A/B de S058). **Causa raíz:** regla ambigua de `smc-doc-updater` («Nunca borres historial; ESTADO-ACTUAL se sobreescribe») que mezclaba dos archivos con políticas opuestas; el histórico ya vivía completo en `memory/sesiones/` (133 ficheros) ⇒ la acumulación era duplicación pura. **Poda verificada:** 6 sesiones (S061/S067/S068/S070/S071/S115) solo existían aquí — rescatadas **verbatim** a su `Sesion-NNN.md` ANTES de borrar; re-cruzado contra el backup, solo quedan S010 y S049 y son menciones sin párrafo propio. **Nada perdido.** Archivo reescrito reutilizando las líneas vivas verbatim vía `sed`: **291.219 → 12.381 B (4,2 %)**. **Anti-recaída:** `smc-doc-updater` REGLA ABSOLUTA 3 «rota, no acumula» (reemplazo de fase actual sin `<!-- historial -->`, ventana de 3, reescritura del arranque con nº de sesión en el título, techo 40 KB por `wc -c`, y confirmar que existe el `Sesion-NNN.md` antes de podar); `smc-session-startup` mide el archivo **antes** de leerlo (40 KB ⚠️ / 256 KB ❌) y comprueba la frescura del título; reglas de mantenimiento escritas también en la cabecera de este archivo. **CORE INTACTO — 1809 líneas, SHA `5e21ca38b43cf0e4`, `check-core-sync` OK ×3 + EXTREMES CORE OK (ADR-022).** **SEGUNDA PARTE (petición del usuario):** **CLAUDE.md es ahora un MAPA de ≤40 líneas** (59→38, las 10 rutas verificadas), con la doctrina extraída **verbatim** a `docs/REGLAS-DURAS.md` (cero líneas perdidas, comprobado una a una) — declaraba «Fase 0» desde ~S010, rancio, ya no afirma fase. **ADR-003 escrito** (se citaba en 8 documentos y nunca tuvo fichero; transcrito del literal de ESTADO-ACTUAL, alternativas descartadas *no registradas*; validado: `main` congelado en `3e437f2` del 2026-06-11 y 429 commits en la rama). **ADR-015 NO se escribe y es correcto** — reservado desde S098, solo se redacta si el usuario ordena cambiar `minRR` (default 3.0 mandatorio); nuevo `docs/adrs/README.md` con índice de 26 ADRs y **huecos explicados**. **`reglas-smc-ict.md` NO se parte:** el usuario objetó que los conceptos ya están todos, y medido tenía razón — 42/42 confluencias cerradas (WORKPLAN §4.8:353), último contenido nuevo el 2026-07-04, y los 6 commits posteriores son **un solo hilo de enmienda** a §2.3.2; quedan **31.191 B** de margen. Mi «dos o tres conceptos más y lo cruza» era falso. `WORKPLAN-MAESTRO-V2.md` mide **58 KB**, no ~185 KB como estimé sin medir; intacto por orden del usuario. **`sync-obsidian.ps1` ahora respalda también la doctrina** (+5 destinos: CLAUDE.md, workplan, REGLAS-DURAS, reglas-smc-ict, reglas-dev) — antes el vault guardaba estado y decisiones pero no las reglas, que son lo irreemplazable. **F1-GATE sigue sin firmar.** Ver [Sesion-147](sesiones/Sesion-147.md).

## Sesiones recientes (detalle completo en `memory/sesiones/`)
- **[[Sesion-146]]** (2026-07-28) — hilo de pools RESUELTO por medición (la causa era el gate `touches>=2`, no la creación: 704 altas) + **§3.3 Grab implementado** (`f_detectGrab`, F1-S1.3-T10b, confluencia #11, 96/100) + **ADR-027 propuesto**. CORE → `5e21ca38b43cf0e4` (1809 líneas).
- **[[Sesion-145]]** (2026-07-25/27) — DOL: escalera de liquidez del máximo histórico al mínimo. ADR-026 aceptado (D1-D14). CORE intacto `7ad95b3e612d041a`.
- **[[Sesion-144]]** (2026-07-25) — arranque de la curación de la familia **Liquidez** (objetivo original, aún abierto): EQH/EQL sano, far/old pivots se conservan, pools barridos no se dibujan.

## Bloqueos
- Ninguno. (SEC-01 resuelto: usuario confirmó keys viejas revocadas; nuevas en .env/.mcp.json gitignored.)

## Cómo arrancar la próxima sesión — **S148**

**El plan sigue siendo el de S147, íntegro: S147 se fue entera en reparar el arranque y no ejecutó ni un punto.**

**Objetivo:** implementar **ADR-027** (tramo vela→vela de la familia Liquidez) por subconjuntos, y con ello retomar la curación de la familia Liquidez que quedó abierta desde S144.

1. **Medir primero el coste en objetos** del tramo sobre **un solo concepto**. Cada evento pasa de *1 etiqueta* a *1 etiqueta + 1 línea*, y hay **topes duros de 500 de cada uno**. Sin esta medición no se implementa el resto.
2. **Implementar ADR-027 por subconjuntos, verificando cada uno** en este orden: **grab** → **sweep/raid/spring** → **pool barrido**.
3. **Verificar el grab en H1 y M5** con casos **nativos de cada TF**, fechados.
4. **Retomar la curación de la familia Liquidez** — sigue siendo el objetivo original de S144.

**⚠️ Estado en que quedó el entorno (sin cambios: S147 no abrió TradingView):**
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

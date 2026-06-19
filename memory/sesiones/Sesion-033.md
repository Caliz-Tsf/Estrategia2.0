# Sesion-033 — 2026-06-19

**Rama:** pine/sistema-completo · **Estado Pine:** INTACTO (core-sync OK SHA 8967d31bdbb7ed13, 592 líneas, idéntico Sesion-032)

## Objetivo
**Sesión de PLANIFICACIÓN/ESQUELETO (PARTE 2: Hermes + Enjambre).** Complemento de Sesion-032 (Parte 1 = conceptos Pine/EA/repos). Documentar la arquitectura del runtime del enjambre de mentores: vigía/cron, kanban, rondas de deliberación, voto estructurado, registro de decisiones con autoría, scoring de agentes, modo replay, y la entrega final (push vía CallMeBot). Incluye el cerebro único (open-second-brain) y el agente piloto mínimo (NSL como plantilla de anatomía/comunicación). **Encargo:** esqueleto maestro de 2 archivos (documento + plantilla agente) que sirva de referencia para Opus Max construir el runtime.

**Partición acordada con usuario (sesión anterior):** **PARTE 1 (EA + Pine + repos) = Sesion-032 COMPLETADO.** **PARTE 2 (Hermes + enjambre) = esta sesión.**

## Completado (documentación/estructura — NO código/Hermes)

### 1. Entregables

#### 1.1 `docs/planes/ESQUELETO-P2-hermes-enjambre.md` [NEW]
Documento maestro Parte 2. **9 secciones:**
- **§0** — 10 reglas duras para el implementador (traza P1↔P2, vigía determinista, scoring trazable/replicable, sin LLM vivo en EA ADR-007, canal push CallMeBot, almacenamiento Obsidian/gh-brain, replayable, canónicas 42 confluencias, umbrales congelados Fase 3, no pivotar a timeout/webhooks).
- **§1** — Superficies Hermes: qué archivo pide cada sección (worker TCP `:37777`, config en `~/.hermes/config.yaml`, skillset, modelos por mentor). Listado de decisiones de arquitectura (síncrono vs async, delegate_task bloqueante, MCP TV secuencial, punto único de fallo = Router, no redundancia ahora).
- **§2** — Runtime del enjambre en tiempo real: vigía (script `smc-runtime-vigil.ps1` monitorea EURUSD 15m en TV, detecta señales de entrada, entra en modo "deliberación"; cron respeta descansos London/NY); kanban (4 estados: Pendiente / Deliberación / Votación / Ejecutado); rondas 1–2 (Ronda 1 = mentores SMC + 3 Expertos E1–E3 analizan confluencia bruta; Ronda 2 = Expertos E4–E6 + Funcionales validan contexto macro/noticias/tendencias; quórum = ≥2 "Sí", rechazados por timeout/rechazo unánime); voto estructurado (JSON per agente: `{agente, familia_ancestro, confluencia_#, score_parcial, voto:Sí/No, justificación}`, guardado en `docs/laboratorio/YYYY-MM-DD_HH-MM-SS_candle.json`); registro con autoría (firma del agente, timestamp barindex, sesión ID); scoring de agentes (track record por familia: % aciertos [IN correcta], % rechazo de falsas [OUT evitadas], sesgo familia, réplicas resueltas S025); modo replay (`scripts/smc-replay.ps1` acepta barindex/fecha → re-invoca enjambre sobre ese histórico, mismo SHA-256 de decisión).
- **§3** — Roster de 4 familias de agentes (26 agentes):
  - **Mentores SMC (7):** NSL/Boxxocode/Profittrading/TJ-Trading/Fedex (juzgan confluencia bruta vs patrones de curso) + 2 Expertos SMC genéricos (E0/E0bis, hedge contra ruido).
  - **Expertos-Concepto (6):** E1–E6 agrupan los 24 conceptos de `reglas-smc-ict.md` por familia (E1: Swings/Estructura; E2: Liquidez/OB/FVG; E3: Premium/Discount/EQH; E4: Mitigación/Pools/Sweep; E5: Scoring-contexto/Bias; E6: Herramientas/SL-TP). Cada Experto suma 4–5 conceptos, FICHA (§3.E).
  - **Funcionales (6):** Vigía (monitorea, elige candle), Router (orquesta), Confluencia (normaliza salida ronda 1→scoring unificado), Noticias (gate macro binario, TBD), Escéptico (simula contraria, protección, NO bloquea), Entrenador (logging/métricas).
  - **Control (7):** Orchestrator (máquina de estados kanban + dispatch rondas), Validador (aplica regla dura ADR-005: determinismo, no LLM), TimeShift (ajusta sesión según símbolo), SessionManager (reinicia cada símbolo), Guardrails (limites riesgo), Auditor (traza).
- **§4** — Cerebro único (open-second-brain, recomendado): dónde almacenar decisiones/logs/métricas/reportes (Obsidian vs Knowledge nativo ~/.hermes/knowledge/). Gate de verificación: **¿afecta al Workspace/Memoria de Hermes tener el cerebro en Obsidian en lugar de nativo?** Nota abierta.
- **§5** — Set de repos para el enjambre: OpenMobius-skill (grounding SMC/liquidez), tradememory-protocol (cerebro), TradingAgents (referencia swarms), MT5 MCPs (Fase 4), CallMeBot (notificador push), oh-my-hermes (framework vías mejorada, candidato). Adopción verificada (licencia, paridad, no copiar sin verificar).
- **§6** — Piloto mínimo → escala: 1 cron Vigía + kanban + 2 mentores (NSL + Boxxocode) + orquestador sobre EURUSD → 1 entrada de diario (CSV + JSON). Entregable: `docs/laboratorio/piloto-diario-2026-06-XX.csv` + `.json`. Gate: decisión user si escalar.
- **§7** — Traza P1↔P2 y paridad decisional: cómo TB `f_detectRoundXDecision(round, agentVotes[], context)` en EA se alimenta de B `docs/laboratorio/` decisiones + replayable (SHA-256 del set de confluencias en barindex → misma entrada del EA sea manual o enjambre, determinismo garantizado).
- **§8** — Riesgos catalogados: timeout network (fallback determinista), hallucination LLM (Validador ADR-007 rechaza), saturación MCP TV (secuencial, caché), desync barindex (timestamp+barindex dual, auditoría), ruptura contrato I/O (scoreboard de agentes por sesión = aprender).
- **§9** — Docs asociados: BRIEFING-mentor-module-v2.md (qué es el módulo), GUIA-transcripcion-expertos.md (cómo bajar cursos), COMANDOS-* (scripts por playlist), MATRIZ-conceptos-cobertura.md (qué cubre cada expert), handoff-opus-max (para implementar runtime).

**Diagramas mermaid embedidos:**
  1. **Flujo completo enjambre:** entrada Vigía → kanban Pendiente → Ronda 1 (mentores+E1–E3) → Ronda 2 (E4–E6+Funcionales) → Votación → escritura docs/laboratorio/ + push CallMeBot → salida TV.
  2. **Traza P1↔P2:** box CORE Pine (f_detect*, UDT, scoring), box Strategy (backtesting + alertas), box EA MQL5 (determin.), box Enjambre (deliberación), conexión TB: laboratorio/ → EA.

#### 1.2 `docs/planes/PLANTILLA-agente-mentor.md` [NEW]
Plantilla parametrizable de agente. **Caso trabajado: NSL (No soy liquidez)** — anatomía y comunicación end-to-end.
- **§1** — Anatomía de NSL: rol (juzgar confluencias brutas contra patrones enseñados), ancestro/familia (Mentores), modelo (gemini-2.5-flash/Puter), dominio (swings/liquidez/OB/FVG desde curso 65 eps), grounding (transcripción + reglas-smc-ict.md §1.1–§2.2), métricas (track record: precision/recall en confluencias vs oportunidades reales en EURUSD).
- **§2** — Ficha NSL (YAML parametrizable):
  ```yaml
  nombre: NSL
  familia: Mentores
  modelo: gemini-2.5-flash
  provider: google/puter
  dominio: Swings, Liquidez, OB, FVG
  grounding:
    - docs/reglas-smc-ict.md:§1.1-§2.2
    - hermes/skills/mentor-nsl/transcrip/*
  entrada: {confluencia_bruta: {...}, contexto: {...}}
  salida: {voto: Sí/No, justificación: str, score_parcial: 0.0-1.0}
  contrato_I_O: "voto Sí ⟹ ≥70% confluencia + ≥2 patrones identificados"
  restricciones:
    - no LLM en EA runtime (voto solo aquí)
    - timeout 5s → fallback Escéptico
    - voto rechazado sin justif → penalización track record
  norms:
    - respetar quórum ≥2 familias
    - no sobreconfiar en score_parcial (E1–E3 validan)
  métrica: precision_confluencias_NSL (baseline Boxxocode)
  ```
- **§3** — Comunicación de NSL en acción (diagrama + ejemplo JSON):
  - Vigía detecta candle con FVG #18 + OB #5 → entra a kanban.
  - Ronda 1: Router → NSL (y otras) reciben `{candle_idx, confluencias_brutas: [FVG#18, OB#5], barindex: 1234}`.
  - NSL emite `{familia: "Mentores", agente: "NSL", voto: "Sí", justif: "FVG coincide patrón sesión 12 (mitigación OB previo). OB toca nivel 1.15762 que vimos en 2025-06-15 04:00", score_parcial: 0.85}`.
  - Score_parcial = min(1.0, #patrones_identificados / 2).
  - Persistencia: JSON guardado inmediatamente en `docs/laboratorio/2026-06-19_14-32-15_barindex-1234.json` con firma NSL + timestamp.
- **§4** — Ciclo de vida NSL: (1) descarga curso "No soy liquidez" (65 episodios, ~100 hrs, Fase 1 S030 EN PROGRESO); (2) skill `mentor-nsl` construido vía `hermes-build-personality.ps1` + frontmatter modelo; (3) integración en Hermes runtime (registry de skills, llamadas via delegate_task); (4) sesión piloto (mock entrada EURUSD candle con 2–3 confluencias ciertas, verificar voto_correcto + tiempo <5s).
- **§5** — Checklist de verificación para cada mentor (NSL plantilla, repetir para Boxxocode/etc.):
  - [ ] Curso descargado + timestamps verificados
  - [ ] Transcripción consolidada (español, sincronizado con `reglas-smc-ict.md`)
  - [ ] Ficha YAML completada (contrato I/O claro)
  - [ ] Skill Hermes compilado (0/0 errores)
  - [ ] Mock sesión: 3 casos (correctos/falsos) → voto_esperado vs voto_real ✅ ≥2/3
  - [ ] Track record inicializado (baseline vs Boxxocode u otro benchmark)

#### 1.3 `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` [UPD]
Añadida nota en §8 (línea: "✅ ENTREGADO (S033)") — puntero hacia la Parte 2.

### 2. Cobertura del handoff Opus Max

Sesion-033 cubre los puntos del handoff S030 `HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md`:
- ✅ **§3.B** runtime enjambre (rondas, voto, kanban, logging) → §2 ESQUELETO-P2.
- ✅ **§3.C** traza end-to-end P1↔P2 (CORE Pine → laboratorio/ → EA) → §7 ESQUELETO-P2 + diagrama.
- ✅ **§3.E** agente piloto NSL como plantilla → PLANTILLA-agente-mentor.md (§1–§5).
- ✅ **§7 + §9** repos + almacenamiento Obsidian → §5 + §4 ESQUELETO-P2.
- ✅ **§8** handoff notas → §8 ESQUELETO-P2 (riesgos catalogados).

### 3. Decisiones del usuario (S033)

Recopiladas en sesión de planificación:

1. **Árbitro del resultado = TradingView:** los agentes deciden en tiempo real (entrar / esperar OB / esperar barrido / no actuar) y **el precio en TV resuelve quién acertó** (track record por agente, no score absoluto). Formalizado en §2 (Ronda 1→Ronda 2→quórum) y §8 (desync auditoría).

2. **Documento de confluencias = `reglas-smc-ict.md §4.8` + anotación:** §4.8 es canónico (grounding reglas duras); lo anotado en `docs/laboratorio/` asciende a §4.8 solo tras validación IS/OOS (Fase 3). Formalizado en §7 (traza paridad).

3. **Entrega señal al humano = push CallMeBot (elevado):** antes estaba "diferido Fase 4-5", ahora pasó a ahora (Fase 2/runtime). Formalizado en §2 (salida kanban) y §5 (repos: CallMeBot). Plantilla JSON: `{candle_time, confluencias_#, quórum_resultado, recomendación_entrada}`.

4. **Cerebro único = open-second-brain (recomendado):** sobre Obsidian o ~/.hermes/knowledge/, con gate de verificación: **¿afecta al Workspace/Memoria de Hermes tener el cerebro en Obsidian?** Anotado como nota abierta en §4, sin bloqueo para implementación (la arquitectura da igual si Obsidian o nativo).

5. **Entregable en 2 archivos + diagramas:** (a) ESQUELETO-P2 maestro de 9 secciones + 2 diagramas mermaid, (b) PLANTILLA-agente-mentor.md con NSL case-study + YAML + checklist.

### 4. Investigación: Catálogo LLMQuant/awesome-trading-agents (101 proyectos — COMPLETO)

**Revisión integral:** ~54 Agents + ~34 MCPs + ~13 Skills = 101 (reclasificados).

**Hallazgo clave:** **NO hay agente SMC/liquidez dedicado en el ecosistema.** El grounding queda cubierto por:
- **OpenMobius-skill** (referencia SMC/ICT ya adoptada en Ruta A Parte 1).
- **Mentores/Expertos (NSL, Boxxocode, etc.)** — grounding por curso + reglas-smc-ict.md (nuevo, lo que hace Estrategia 2.0 único).

**Nuevos añadidos a §5 (repos a evaluar):**
- **WyckoffTradingAgent** (#12, referencia estructura/movimiento ≈ Power of 3/MMXM) — candidato Ruta C (modelos entrada).
- **opennews-mcp** (#13, OpenNews →  noticias/macro) — candidato gate Ruta E (noticias determinista ADR-005). **Decisión:** probar Fase 3 (TBD en S030).
- **data-mcp** (#14, macro + datos económicos) — candidato Ruta D (tiempo/macro). **Decisión:** referencia, no adoptar ahora (data feeds complejos).

Resto confirmado sin cambios: MT5 MCPs (Fase 4), CallMeBot (push Fase 2, ahora), oh-my-hermes (framework candidato), TradingAgents (design reference).

### 5. check-core-sync
SHA `8967d31bdbb7ed13` (592 líneas), **IDÉNTICO a Sesion-032** → ✅ Pine INTACTO, ningún cambio de código.

### 6. Alertas de Pine (consulta del usuario — confirmada)

Usuario preguntó en S033 por el estado de las alertas en Pine. **Confirmado en la estructura:**
- Stubs `// === ALERTAS ===` presentes en `SMC-Visual.pine:1157` y `SMC-Strategy.pine:851`.
- Planificación oficial:
  - **T15 (Sprint 1.4, Visual):** `alertcondition()` determinista (confluencia_# + quórum).
  - **Sprint 2.1 (Strategy):** `alert_message` JSON (barindex + familia_voto + push CallMeBot).
- Detalle en `PINE-PLAN §5` + diferenciación en ESQUELETO-P2 §2.8: **alerta determinista del Pine** (trigger internal) vs **push cualitativo del enjambre** (recomendación humano).

### 7. Bloqueos nuevos
Ninguno.

### 8. Puertas pendientes
1. **ADR:** Candidatos anotados (se deciden tras gate de verificación [impl]):
   - Adopción de **open-second-brain** (cerebro en Obsidian vs Knowledge nativo) → impacto arquitectura Hermes/Memoria.
   - Adopción de **oh-my-hermes** vs construir el loop de enjambre a mano.
   - Gate de verificación: ¿Obsidian en cerebro afecta Workspace/Memoria? (nota abierta S033 §4.3).

2. **Gate:** Ninguno completado (planificación pre-implementación).

## Próximos pasos acordados

- **[impl] construye runtime enjambre:** piloto mínimo (§6 ESQUELETO-P2): 1 cron Vigía + kanban + 2 mentores (NSL + Boxxocode) + orquestador sobre EURUSD → 1 entrada de diario (`docs/laboratorio/piloto-diario-2026-06-XX.csv/json`).
  
- **[impl] gate open-second-brain:** decidir Obsidian vs ~/.hermes/knowledge/ antes de construir canal persistencia (impacto arquitectura: donde guardan/leen T-record, logs, métricas).

- **Pine sigue ruta oficial:** relleno esqueleto P1 empezando por **T26 True FVG** (Sprint 1.6, Parte 1). Paralelismo: enjambre pilot en Hermes (Parte 2) sin bloquear a Pine.

- **Bloqueos:** ninguno nuevo.

## Archivos tocados
| Archivo | Acción | Propósito |
|---|---|---|
| `docs/planes/ESQUELETO-P2-hermes-enjambre.md` | NUEVO | Esqueleto maestro Parte 2 (§0–§9 + 2 diagramas mermaid) |
| `docs/planes/PLANTILLA-agente-mentor.md` | NUEVO | Plantilla parametrizable agente + NSL case-study + YAML + checklist |
| `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` | UPD | Puntero ✅ ENTREGADO (S033) en §8 hacia Parte 2 |
| `memory/ESTADO-ACTUAL.md` | UPD | entrada S033 |
| `memory/sesiones/Sesion-033.md` | NUEVO | este cierre |

## Notas operativas
- **Sin código Pine:** toda la sesión es planificación documental.
- **Sin git:** documentación solamente. Commits coordinados por supervisor.
- **Catálogo revisado:** 101 proyectos LLMQuant (54+34+13), hallazgos integrados en §5 Parte 2.
- **Decisiones usuario S033:** 5 tópicos clave (árbitro TV, confluentcias §4.8+anotación, push CallMeBot, cerebro Obsidian con gate, 2 archivos).
- **Handoff Opus Max coverage:** Parte 2 cubre §3.B/C/E + §7/§9 del handoff S030.

---
**Commit:** docs(cierre) Sesion-033 — ESQUELETO-P2 (hermes-enjambre + plantilla-agente). **Core Pine:** SHA 8967d31bdbb7ed13 (592 líneas, INTACTO). **check-core-sync:** OK ✅

# Esquema — Superficies de Hermes Workspace × Módulo Mentores

> **Qué es:** mapa de CADA sección de Hermes Workspace (lo que vimos en la app, Sesion-030) y qué papel concreto cumple en el módulo mentores, más cómo se combinan. Consolida los esquemas/ideas (Sonnet) en uso concreto.
> **Anclas:** `BRIEFING-mentor-module-v2.md` (§0 enjambre=laboratorio, ADR-005) · `reglas-smc-ict.md` (grounding) · `MODULO-MENTORES-WORKFLOW.md` (roster).
> **No toca Pine/MQL5.** Módulo paralelo.

---

## 1. Las superficies de Hermes y su rol en el módulo

| Sección (sidebar) | Qué es en Hermes | Rol en el módulo mentores |
|---|---|---|
| **Panel** | Dashboard general | Vista de arranque; no operativo del pipeline. |
| **Chat** | Chat 1:1 con un modelo/perfil | Hablar con UN mentor puntual (modo copiloto manual). Probar una ficha. |
| **Archivos** | Explorador de archivos del workspace | Ver/editar fichas, transcripciones, knowledge docs. |
| **Terminal** | Terminal embebida | Correr `process-channel.ps1`, `hermes cron/kanban/profile` sin salir de la app. |
| **Trabajos / Jobs** | UI de **cron** ("No scheduled jobs" → New Job) | **El VIGÍA vive aquí.** Cron cada 15m que consulta TV vía MCP y abre tareas en el Kanban si hay algo accionable. Es el "cuándo pensar". |
| **Tasks** | **Kanban** (Triage/Ready/Running/Review/Blocked) | **El registro del pensamiento.** Cada evento del vigía = tarea; los comentarios de la tarea = protocolo de discusión entre mentores (ronda 1 / ronda 2 / síntesis). DB: `~/.hermes/kanban.db`. |
| **Conductor** | "Launch a mission and watch your agent team build it live" (mesa visual con agentes) | **Visualización** de una ronda de debate en vivo (mentores alrededor de la mesa). Útil para observar/depurar el enjambre, no es lógica nueva. |
| **Operations** | Equipo de agentes persistente · "Estado da Tropa" / Agent Bus · "Acciones seguras (sin restart, sin gasto pago automático)" | **El equipo persistente de mentores** y su salud. El Agent Bus registra misiones/pendencias. "Acciones seguras" = barandilla (greenlight) que encaja con ADR-005. |
| **Swarm** | Main Agent despacha misión (auto / one agent / broadcast) a workers | **El despacho de la discusión.** `broadcast` = mandar el evento a todos los mentores a la vez (ronda 1). El Orchestrator reparte y junta. |
| **Memoria** | `~/.hermes/memories/MEMORY.md` + `USER.md` | Hechos durables del sistema y del usuario (no la metodología del mentor). |
| **Knowledge** | `~/.hermes/knowledge/*.md` (patrón wiki-LLM de Karpathy) — hoy vacío | **AQUÍ va el conocimiento especializado de cada mentor** (un .md por tema/playlist). Es lo que responde tu pregunta — ver §3. |
| **Habilidades / Skills** | Skills instalables. Ya instaladas: `consult-mentor`, `mentor-extract-profile`, `mentor-transcribe` | La **capa de comportamiento** del mentor: `consult-mentor` carga su PERFIL desde el vault; `mentor-transcribe`/`mentor-extract-profile` son el pipeline V1. El skill-creator scaffolda nuevas. |
| **MCP** | Gestor de servidores MCP | Donde se enchufa el **TV MCP** (lectura de gráfico) y, en Fase 4, el MCP de MT5 (solo-lectura para laboratorio). |
| **Perfiles** | Instancias Hermes aisladas | Cada mentor puede ser un perfil aislado (memoria/skills propios). El `orquestador` es un perfil con solo Kanban. |
| **External providers** | `external_memory_providers.json` (vacío) | No se usa por ahora. |

---

## 2. Cómo se combinan (el flujo, end-to-end)

```
[Trabajos/Cron: Vigía 15m]  --consulta-->  [MCP: TradingView]
        |  (si accionable)
        v
[Tasks/Kanban: tarea "evento" en Triage]  --decompose-->  tareas hijas por mentor
        |
        v
[Swarm: broadcast a mentores]  ----  cada mentor lee su [Knowledge/<mentor>/*.md] + [reglas-smc-ict.md]
        |   ronda 1 (lectura) -> comentarios en la tarea
        |   ronda 2 (rebate)  -> comentarios en la tarea
        v
[Operations/Orchestrator]  --síntesis-->  voto estructurado (sesgo, nivel, invalidación, confianza)
        |
        +--> (a) diario laboratorio  docs/laboratorio/  (hipótesis falsable)
        +--> (b) sugerencia COPILOTO al humano (Conductor / Chat)
        |
        v
[Validación determinista: Strategy Tester IS/OOS - Fase 3]  --cristaliza-->  regla/peso
        v
[EA MQL5 - Fase 4]  (ejecuta; NO consulta al enjambre en vivo — ADR-005)
```

Resumen de responsabilidades: **Cron = cuándo · Kanban = dónde queda · Swarm/Operations = quién y cómo discute · Knowledge+Memoria = con qué fundamento · Conductor = cómo lo veo · MCP = de dónde sale el dato.**

> **ADR-007 (continuo + scoring de agentes):** este loop NO es solo on-demand — corre **en tiempo real de forma continua** (unos agentes evalúan confluencias actuales, otros descubren nuevas), registra en `docs/laboratorio/` las que cierran positivas con **autoría**, y mantiene **track record/score por agente** para ponderar votos. El EA al final de la cadena **razona** por scoring que generaliza (determinista), no consulta al enjambre en vivo. Diseño: `HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md`.

---

## 3. UN mentor con MÚLTIPLES conocimientos (respuesta a tu pregunta)

**Sí, exactamente como lo planteas.** "No soy liquidez" no es varios agentes: es **UN agente** (perfil/skill `mentor-no-soy-liquidez`) con **varias carpetas de conocimiento especializado**, una por cada playlist/tema suyo. Estructura:

```
~/.hermes/knowledge/no-soy-liquidez/
    ficha-mentor.md            # CÓMO decide (9 campos, incl. "Conflictos con el sistema") -> su personalidad/voto
    mentoria-curso.md          # síntesis del curso principal (65 eps ya bajados)
    price-action.md            # síntesis de su playlist de price action
    live-execution.md          # cómo ejecuta en vivo (gestión, parciales, timing)
    high-precision-entries.md  # entradas de alta precisión
    smart-money-flow.md        # smart money flow
```

- **El skill `consult-mentor`** carga la `ficha-mentor.md` (la personalidad/criterio de decisión) y puede **buscar** en los demás `.md` cuando la confluencia toca ese tema. Así el mismo mentor opina sobre price action, ejecución, entradas de precisión, etc., **con su voz**, aterrizado en lo que él mismo enseñó (cero invención).
- **Diferencia clave:** `ficha-mentor.md` (Memoria/personalidad) = CÓMO decide; los demás (Knowledge) = QUÉ sabe. La ficha es chica y siempre cargada; el knowledge es grande y se consulta por búsqueda.
- **Pipeline para llenarlo:** cada playlist extra → `process-channel.ps1` a una subcarpeta → un paso de síntesis LLM (Gemini) que condensa las transcripciones en el `.md` de knowledge correspondiente. (La transcripción cruda NO es el knowledge; el knowledge es la síntesis estructurada.)
- **Creación del agente:** sí, vía **skill** (el `skill-creator` ayuda a scaffoldar `mentor-<slug>`); el `build-personality.ps1` (V1) ya crea el skill `mentor-<slug>` desde la ficha. Lo nuevo es poblar la carpeta `knowledge/<slug>/` con los temas.

> **Requisito tuyo (pendiente):** para bajar esas playlists extra necesito sus **URLs** (price action, live execution, high precision entries, smart money flow). Con eso genero los comandos por-video como en el curso principal. Ver `GUIA-transcripcion-expertos.md`.

---

## 4. El cron como "skill" y las barandillas

- **Cron** es a la vez una **UI** (Trabajos/Jobs) y una **herramienta** (`cronjob`) que varios workers del `swarm.yaml` ya tienen (Orchestrator, Ops-Watch, KM). Es decir, un agente puede crear/gestionar sus propios crons. El Vigía es el caso de uso central.
- **Greenlight / "Acciones seguras":** el `swarm.yaml` define `greenlightRequiredFor` por worker (merge, publish, external-send, etc.). En el módulo mentores esto se reusa para que **ningún paso sensible** (p.ej. "enviar señal", "tocar MT5") ocurra sin visto bueno humano → es la implementación concreta del "human greenlight control" de ADR-005.

---

## 5. Qué NO hacer (para no sobre-ingenierizar)

- No conectar el enjambre directo a MT5 para ejecutar (ADR-005). MT5 = Fase 4, solo-lectura para laboratorio.
- No crear los 24 conceptos + E1–E6 + funcionales de golpe. Piloto con 2 mentores reales.
- No usar External providers ni knowledge graph todavía (vacíos, innecesarios ahora).
- No bajar el intervalo del cron a 5m antes de medir la cuota free tier de Gemini.

---

## 6. Próximos pasos (encajan con el plan)
1. Llenar `knowledge/no-soy-liquidez/` (curso ya bajado → síntesis; faltan URLs de las playlists extra).
2. Design doc del roster (pendiente Sesion-025) usando el schema de `swarm.yaml`.
3. Piloto: 1 cron Vigía + Kanban + 2 mentores + orquestador sobre EURUSD → 1 entrada de diario.
4. Medir cuota/ruido; recién ahí escalar.

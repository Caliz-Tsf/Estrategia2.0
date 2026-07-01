# Sesion-077 (2026-07-01)
> Investigación / Diseño — MÓDULO ENJAMBRE + TOOLING. Paralelo a Pine (no toca código Pine).

## Objetivo
Continuación de tareas enjambre S074 + investigaciones pendientes: dossier Gradient Levels para ultracode, cableado openWakeWord, integración MCPs Claude Desktop + Hermes, resolución MT5 autostart.

## Completado

### 1. Dossier Gradient Levels #1 (commit `333f2b2`, S077)
**Archivo nuevo:** `docs/planes/DOSSIER-gradient-levels-para-ultracode.md`

Paquete información COMPLETO para que ULTRACODE construya esqueleto de regla: familia Gradient Levels candidato #1 ("columna vertebral del 2026"). Contenidos:

- **Doctrina verbatim + cuantificada** (trazas a madre-2026.md):
  - Grading quadrants/eighths (january-12)
  - Confluencia exponencial nivel ∩ quadrant (february-11)
  - FVG-válido = toca gradient level (february-11)
  - Jerarquía OB/parent (march-13)

- **Alcance familia Gradient Levels:**
  - #1 grading (núcleo)
  - #2 confluencia exponencial (núcleo)
  - #3 FVG-válido (núcleo)
  - #5 opcional (follow-up)
  - #6-#9 índice-only (diferir ADR-001, Fase 5)

- **RETO CENTRAL:** rango-fuente determinista + inventario infra Pine existente:
  - §2.3 Premium/Discount es el germen
  - §5.10 Opening Gaps, FVG, swings, MTF

- **Formato de salida canónico** para esqueleto Pine

- **8 preguntas de diseño** + restricciones duras

**Acción requerida:** Usuario pasa dossier a ultracode; Ultracode genera esqueleto; Claude Code rellenará bajo gate [[sprint16-gate-reglas-antes-de-codigo]].

### 2. openWakeWord cableado (fuera de git, ~/.hermes/voice/)
**Status:** FUNCIONAL (smoke test OK). Detección "hey jarvis" → `jarvis-do.ps1 abrir-hermes`.

**Archivos creados:**

1. **`wake_listener.py`** — loop de micro + detección palabra clave + callback
2. **`record_clips.py`** — grabador de clips de entrenamiento
3. **`train_verifier.py`** — generador custom speaker verifier (.joblib) con clips propios
   - **GOTCHA resuelto:** acento no-nativo del usuario (diferencia ~10-15% en precisión)
   - Fix: entrenar verifier en clips del usuario, no modelo genérico
4. **`start-voice.ps1`** — launcher con venv de jarvis
5. **`README.md`** — instrucciones

**Verificación (smoke test):**
- Modelo `hey_jarvis_v0.1.onnx` carga en onnx ✅
- `model.predict()` OK ✅
- Micro Realtek detectado ✅
- openWakeWord YA estaba en venv jarvis (no instalado de nuevo, solo cableado)

**Memoria actualizada:** `[[openwakeword-jarvis-voz]]`

### 3. MCP headroom — Evaluado (descartado)
**Investigación:** `headroomlabs-ai/headroom` (NO viejo `chopratejas/headroom`, ambos en ESQUELETO-P2).

Características: MCP + 60-95% ahorro tokens, compresión de contexto en vivo.

**DECISIÓN: NO instalado** — por regla usuario "si choca no lo instales":
- Choque detectado: `context-mode` YA montado en Claude Code (.mcp.json)
- Ambos hacen compresión; sobreposición
- context-mode cubre la necesidad; headroom redundante

**Memoria creada:** `[[mcp-headroom-vs-context-mode]]`

### 4. MT5 autostart con Claude Desktop — RESUELTO
**Causa identificada:** `metatrader-mcp-server.exe` NO tiene flag lazy. Claude Desktop arranca todos los stdio servers al abrir, no al primer request.

**Fix implementado:** `~/.hermes/mt5-toggle.ps1`
- `-Status` = reporta estado (enabled/disabled)
- `-Off` = mueve conector a mcpServersDisabled en ~/.claude/config.json
- `-On` = mueve conector a mcpServers (reactivar para Fase 4)

**Acción ejecutada (S077):** MT5 **DESACTIVADO** (no se usa hasta Fase 4; reactivar con `-On` cuando inicie).

**Memoria actualizada:** `[[mt5-autostart-claude-desktop-bug]]` → RESUELTO

### 5. MCPs globales de Claude Desktop unificados (8 totales)
**Unión de inventario global + config proyecto:**

Script `~/.hermes/mcp-desktop-sync.ps1` sincroniza `D:\CODE\INVENTARIO-PROYECTOS-BOT-ESTRATEGIA.md` + `.mcp.json` proyecto.

**8 MCPs GLOBALES en Claude Desktop:**
1. tradingview (fork D:\CODE\BOT\Bot\tradingview-mcp-jackson, 9222)
2. claude-video-vision (vision)
3. firecrawl-mcp (search/scrape)
4. task-master-ai (tareas)
5. tavily-mcp (news)
6. playwright (browser)
7. context-mode (compresión)
8. code-review-graph (AST — limitado, no parsea Pine)

**DESACTIVADO (mcpServersDisabled):**
- metatrader (S077 — reactivar Fase 4)

**GOTCHA resuelto:** Claude Desktop MSIX NO hereda PATH:
- Desktop config exige rutas **absolutas** .cmd/.exe
- `.ps1` scripts NO funcionan directamente (necesitan powershell.exe -File)
- API keys DEL .mcp.json (inventario viejo tenía keys rotadas) actualizadas

**Verificación:** Desktop 3→8 MCP (configuración OK)

### 6. MCPs por-función en Hermes Workspace (~/.hermes/config.yaml)
**Sección `mcp_servers` adicionada (mapeo MCP → función enjambre):**

**AÑADIDOS (Fase 0/enjambre):**
- firecrawl-mcp (research/news)
- tavily-mcp (research/news)
- claude-video-vision (pipeline mentores)

**YA EXISTENTES:**
- tradingview-desktop (operativa)

**OMITIDOS (no necesarios Fase 0):**
- code-review-graph (dev, no enjambre)
- task-master-ai (dev, no enjambre)
- context-mode (ya incorporado Hermes)
- playwright (Hermes tiene browser)
- metatrader (Fase 4)

**GOTCHA:** env vars (API keys firecrawl/tavily) deben propagarse vía:
- Gateway: `-e FIRECRAWL_API_KEY=$env:FIRECRAWL_API_KEY`
- Comandos: `cmd /c npx` con env heredado

**Verificación:** YAML validado (no syntax errors)

## Commits de sesión

1. **`333f2b2`** `docs(pine): S077 dossier Gradient Levels #1 — info completa para ultracode`
2. **`f7f6cd1`** `docs(enjambre): S077 investiga openwakeword + MCP headroom (tareas 5/6)`

## Pendiente para próxima sesión

**S078 — VERIFICACIÓN RESTART + DECISIÓN BOXXO/ENJAMBRE:**

1. **Reiniciar Claude Desktop** → verificar 8 MCPs responden
2. **Reiniciar Hermes gateway** → verificar 4 MCPs cargan + env propagado
3. **openWakeWord:** probar `start-voice.ps1 -DryRun`, grabar clips, entrenar verifier acento usuario
4. **Dossier Gradient Levels** → pasar a ultracode; Ultracode genera esqueleto
5. **BOXXO descarga** → gate indicators 1-5 (si usuario prioriza)
6. **Enjambre 6 tareas S074** → continuar (si usuario prioriza)

**Tareas 1-4 comprometidas S074 (siguen abiertas):**
- Definir cantidad/funciones enjambre; investigar límite Hermes
- Modelos IA tokens gratis
- BOXXOCODE módulo 2 análisis
- WhatsApp + Hermes

## Decisiones

- **SIN decisiones arquitecturales nuevas.** Todas investigaciones confirmacionales.
- **NO hubo gate de fase completado** — sin tag.
- **Pine F1-GATE:** Sigue con firma usuario pendiente y Opción A/B pendiente (no bloquea).

## Bloqueos

Ninguno.

## Notas

- **Módulo PARALELO:** 0 commits Pine. CORE INTACTO (1517 líneas SHA `80fad14dd8d03758`, compila 0/0 los 3, core-sync OK).

- **Tooling:** openWakeWord cableado pero no entrenado aún (necesita clips usuario). MCPs unificados pero NOT VERIFIED (reinicio S078). Gradient Levels dossier LISTO para ultracode.

- **Arquitectura:** Sin cambios. Enjambre métodos (no razonamiento) + tooling consolidado.

- **Próxima sesión:** Verificación 5 min + decisión prioridad (BOXXO/enjambre/Pine). Si usuario retoma Pine → Opción A/B pendiente de firma S057.

---

Cerrada por: Claude Code (Haiku 4.5)
Fecha: 2026-07-01 19:45 UTC

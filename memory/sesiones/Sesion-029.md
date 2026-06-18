# Sesion-029 — 2026-06-17

> Cierre de sesión: **Módulo Mentores — fix de timestamps en transcripción + diagnóstico Hermes local (Ollama/Puter).** Sesión NO-PINE (Fase 1 deferida, core-sync intacto). Commit único: **7770b7e**.

## Objetivo
Sesión dedicada a parallelize tracks: Módulo Mentores (pipeline transcripción → personalidad, Fase 1 de descubrimiento) y diagnosticar Hermes con Ollama local como fallback tras pérdida de créditos Puter.

## Completado

### 1. Módulo Mentores — fix de timestamps en fw_transcribe.py ✅
**Commit:** `7770b7e` `feat(mentores): timestamps [M:SS] en transcripciones de fw_transcribe.py`

**Problema:** `scripts/fw_transcribe.py` (faster-whisper wrapper) extraía timestamps de segmentos (`seg.start` del parsed JSON) pero solo los imprimía a stdout en la consola — no se guardaban en el `.md` de salida. Cada transcripción perdía la referencia temporal exacta (minuto:segundo) del video.

**Solución implementada:**
- Se modificó `fw_transcribe.py` para anteponer un timestamp `[M:SS]` (o `[H:MM:SS]` si el video supera 1 hora) a cada segmento de transcripción antes de guardarlo en el `.md`.
- Formato: `[0:00]`, `[1:30]`, `[12:45:30]` (hora:minuto:segundo cuando applicable).
- El timestamp viene de `seg.start` (float, en segundos) → conversión a formato legible + interpolación en el texto.
- **Smoke test end-to-end OK:** `process-channel.ps1` con `-MaxVideos 1 -MaxSeconds 120 -Model tiny` sobre playlist del mentor "No soy liquidez" (video `_Wz4gpZsTiQ`, "Mentoria Ep.1 - Order Blocks"):
  - yt-dlp → ffmpeg downscale → faster-whisper GPU (idioma es, prob 1.00) → `.md` con timestamps `[0:00]...[1:55]` verificados en disco.
  - Carpeta de prueba creada (`nombre-mentor` placeholder) → **PENDIENTE borrar próxima sesión.**

**Impacto en el sistema:**
- Mentor puede citar minuto/segundo exacto del video en sus análisis.
- Entrada a `hermes-analyze-mentor.ps1` (Fase 2) ahora tiene referencias temporales de fuente.
- NO cambió reglas-smc-ict.md ni Pine (core-sync OK, mismo SHA **2949a931757b9900** de S027/S028).

### 2. Hermes — Diagnosticar Ollama local (Qwen3.5:9b) + Puter HTTP 402 ⚠️ (NO commiteado, config fuera del repo)

**Situación inicial:** Puter (único proveedor cloud vivo) devolvió **HTTP 402 insufficient_funds** → Hermes quedó sin LLM operativo. NIM/OpenRouter siguen suspendidos (api_key vacía).

**Intento de pivot a Ollama local:**
1. **Modelos descargados por el usuario:** `qwen3.5:9b` (6.6GB), `qwen3.6:35b-a3b` disponibles localmente.
2. **Edición de `~/.hermes/config.yaml`:**
   - provider `ollama` ahora apunta a los modelos REALES instalados (`qwen3.5:9b`, `qwen3.6:35b-a3b` — antes listaba `gemma4-chat`/`qwen3-chat`/`gemma4:12b` que no existen).
   - `active_model: qwen3.5:9b` (seleccionado).
   - `model.default` cambió a `ollama`.
   - `ollama_num_ctx` bajado de 65536 a 16384 (caber en RTX 3070 8GB sin spill a CPU).
   - `context_length` sincronizado (16384).
3. **Prueba de endpoint:** Ollama respondió OK (v0.1.48, socket 11434).

**HALLAZGO CLAVE — limitación de modelo pensante:**
- `qwen3.5:9b` es un modelo **thinking** (razonamiento interno).
- Por endpoint nativo Ollama con `think:false` → responde en 2.7s normalmente.
- Por endpoint **OpenAI-compatible `/v1`** (que usa Hermes) → **el thinking queda FORZADO encendido** y **NO se puede apagar** (se probaron 4 vías sin éxito):
  - `/v1` con header `{"think":false}` en el mensaje.
  - Query param `/v1?think=false`.
  - `chat_template_kwargs:{enable_thinking:false}` en config.
  - Modelo derivado personalizado con `SYSTEM "/no_think"`.
- **Resultado:** ~2 minutos por turno → inusable como cerebro de agente.
- **Recomendación:** bajar un modelo **instruct no-thinking** si se quiere Hermes operativo local (`qwen2.5:7b-instruct` o `llama3.1:8b`).
- **Alternativa:** esperar reset de créditos Puter o usar proveedor diferente (no resuelto en esta sesión).

**Impacto en pipeline:**
- La **descarga de cursos** (Fase 1 mentores) **NO necesita LLM** (es yt-dlp + ffmpeg + whisper).
- El **análisis de transcripción** (Fase 2, `hermes-analyze-mentor.ps1`) **sí necesita LLM operativo** → bloqueado hasta resolver Ollama o recuperar Puter.
- Próxima sesión: usuario puede solicitar bajar modelo instruct o esperar a que Puter se recupere.

**Nota de seguridad (ANOTADA, sin resolver):**
- `~/.hermes/config.yaml` contiene keys en texto plano (token Puter, nvapi vision).
- `hermes-proxy.mjs` contiene OpenRouter key en texto plano.
- **PENDIENTE Fase 5 (Operación):** rotar/mover a variables de entorno cuando se retome Hermes operativo en producción.

### 3. Decisión de diseño: NO construir capa visual en transcripción ✅

**Propuesta rechazada:** enriquecer transcripción con "descripción de fotogramas" usando un modelo de visión (extraer keyframes del video, una llamada de visión por frame).

**Decisión: YAGNI (You Aren't Gonna Need It)**
- **Coste:** alto (descargar video completo, extraer keyframes, múltiples llamadas de visión).
- **Beneficio:** bajo en el contexto del proyecto (en un curso de trading el profesor **narra lo que muestra** → gran parte ya está en el audio).
- **Revisión futura:** solo si al usar los mentores se detecta que falta "referente visual" ("aquí/esto" sin nombrar). Entonces se revisitará.
- **Valor real** del módulo vendrá de:
  - Ficha/Norms de mentor (8 campos).
  - Grounding en `docs/reglas-smc-ict.md` (definiciones cuantificadas).
  - Validador determinista del enjambre (ADR-005, laboratorio no runtime).

## Estado Pine (SIN CAMBIOS)

- **Working tree sucio a propósito:** `pine/SMC-Library.pine`, `pine/SMC-Strategy.pine`, `pine/SMC-Visual.pine`, `docs/sprint-runs/validaciones.md` (T09b pools persistentes + T10 sweep, validado 93/100).
- **check-core-sync OK:** 503 líneas, SHA **2949a931757b9900** (idéntico S027/S028).
- **PENDIENTE sin cambios:**
  - ADR "Pools persistentes con ciclo de vida" → commit Pine (T09b/T10) → cierre.
  - Sprint 1.3 continúa en Fase 1 deferida (T11 en adelante).
  - Decisión del usuario: esta sesión commitear SOLO el módulo Mentores, dejar Pine para próxima sesión Pine.

## Para la próxima sesión de Mentores (Sesion-030)

El usuario pidió: **sesión guiada comando-por-comando para bajar el curso completo del primer mentor "No soy liquidez"** (alumno del creador de ICT).

**Mentor a procesar:**
- Nombre: "No soy liquidez"
- Playlist: https://www.youtube.com/playlist?list=PLOwrTT3cFiA5Qo_k27soDPvyPo3Wr7T8S
- Comando base: `process-channel.ps1 -ChannelUrl "<playlist>" -Mentor "No soy liquidez" -Model small` (usar `small` o `medium`, NO `tiny` — transcribe flojo en español).

**Tareas Sesion-030:**
1. Borrar carpeta de prueba `nombre-mentor/` (placeholder de esta sesión).
2. Lanzar descarga curso del mentor (Fase 1 ingesta, sin LLM).
3. Verificar `.md` con timestamps correctos en disco.
4. Repasar la ficha que generaría Fase 2 (una vez Hermes/LLM se resuelva).

## Verificaciones

- **Git status:** rama `pine/sistema-completo`, 1 archivo modificado (`scripts/fw_transcribe.py`), commit limpio.
- **check-core-sync.ps1:** OK — CORE INTACTO, SHA **2949a931757b9900** (idéntico a S027/S028, 503 líneas).
- **No hay inconsistencias git↔resumen:** commit 7770b7e ✅, ESTADO-ACTUAL reflejado aquí ✅.

## Notas

- **Hermes config fuera del repo** (`~/.hermes/`) → no refleja los cambios de config.yaml en el git del proyecto (esperado, por diseño).
- **MCP TV no necesario esta sesión** (no se tocó Pine).
- **Puter bloqueado (HTTP 402)** → no se puede correr análisis Fase 2 de mentores hasta resolver.
- **Seguridad Hermes** → anotada en Sesion-025 y aquí, pendiente Fase 5 (usar env vars).

---

*Sesion-029: Cierre 2026-06-17 · módulo Mentores timestamps commit 7770b7e + Hermes Ollama diagnostic (Qwen3.5 thinking bloqueante, recomendación modelo instruct) + decisión YAGNI visión · Pine INTACTO (core-sync OK SHA 2949a931757b9900) · próxima mentores: E2E con "No soy liquidez" comando-por-comando.*

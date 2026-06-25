# Sesion-058 — Módulo Mentores (Transcripción Audiovisual) + Tooling MCP
**Fecha:** 2026-06-24  
**Tipo:** Infraestructura (módulo mentores + conectores MCP), **NO Pine/MQL5**  
**Rama:** `pine/sistema-completo` (sin cambios, core intacto)

---

## Objetivo
Completar el pipeline de transcripción multicanal para el módulo mentores, documentar hallazgos audiovisuales de Boxxocode (canal mudo), y validar arquitectura de extracción de datos audiovisuales.

---

## Completado

### 1. Documentación: Lotes de videos por playlist
**Archivos modificados:**
- `docs/planes/COMANDOS-profittrading.md` — Reescrita: antes solo mostraba el comando para el primer lote de 5 videos; ahora lista TODOS los lotes con rangos exactos vía parámetro `-PlaylistItems` de `yt-dlp`, incluyendo URLs de cada playlist.
- `docs/planes/COMANDOS-boxxocode.md` — Análoga reescrita: todas las 3 playlists documentadas (Backtest, Custom Indicators, Money Management), 76–100 videos por playlist, comandos listos para ejecutar con `scripts/process-channel.ps1`.

**Commit:** `38e0de0` · 2026-06-24 19:12

### 2. Hallazgo crítico: Boxxocode es canal de screencasts mudos
**Descripción:** El canal "Boxxocode" (toolbox para EA/MT5: conceptos de backtesting, custom indicators, money management, indicadores avanzados) NO tiene narración de voz. Es un screencast puro con música de fondo. El presentador nunca habla.

**Implicación:** El pipeline de transcripción actual (`scripts/process-video.ps1` → descargar audio → `whisper` + transcripción → `.md`) **NO extrae nada útil** del contenido visual de Boxxocode. Whisper retorna archivos vacíos o solo marcas de tiempo.

**Decisión:** Boxxocode requiere un flujo paralelo **videovisión**, no audiovisión.

### 3. Evaluación de conectores: `claude-video-vision` vs `agent-browser`
**Conector agregado:**
- **`claude-video-vision`** (npm global, paquete `jordanrendric/claude-video-vision`)  
  - Rol: extraer frames de un archivo `.mp4` ya descargado (NO captura en vivo de pantalla).  
  - Integración: agregado a `claude_desktop_config.json` (MSIX, AppData\Local\Packages\...\LocalCache\Roaming\Claude\), documentado en `docs/CONECTORES-MCP.md`.  
  - **LIMITACIÓN DETECTADA:** consume tokens reales de Claude (~150–200 tokens/frame a 512px). Para Boxxocode (76–100 videos × N frames/video) = escala no viable sin tokens Anthropic (contrato cerrado en este proyecto).

**Conector evaluado y descartado:**
- **`agent-browser`** (v0.26.0, ya instalado global; vercel-labs/agent-browser)  
  - Rol: navegar webs vivas (DOM) + screenshots anotados. Excelente para acciones sobre páginas interactivas.  
  - **NO sirve para:** analizar archivos de video descargados. Diseñado para nav web live, no analítica de contenido multimedia local.

**Commit:** `65cc611` · 2026-06-24 19:22

### 4. Arquitectura alternativa: visión sin claudevisión (NVIDIA NIM gratis)
**Redescubrimiento documental:**
- Se confirma que la decisión de **descartador visión local** (Qwen2.5-VL 7B/3B ~20s/imagen) fue tomada en S044–S045.
- **Ya existe:** visión en nube GRATIS vía NVIDIA NIM (`meta/llama-3.2-90b-vision-instruct`, 0.65s/imagen, free tier 40 req/min), **YA cableada en Hermes** (ver `memory/zenmux-nvidia-hermes-providers.md`).

**Plan para próxima sesión:**
1. Construir script determinista **análogo a `process-video.ps1`** pero para video:
   - `ffmpeg -vf scdet` para detectar cambios de escena.
   - Extraer frames clave (1 por escena o N FPS).
   - Loop determinista: cada frame → NVIDIA NIM (gratis, no Claude tokens) → descripción.
   - Ensamblar `.md` final, limpiar archivos intermedios (video/frames descargados).

2. **Ventaja:** costo cero en tokens de Claude, determinista, automatizable sin supervisión (a diferencia de `claude-video-vision` que requiere input manual cada frame).

### 5. Confirmación: Pipeline audio actual es determinista
**Hallazgo:** `scripts/process-video.ps1` **NO conserva nada en disco** más allá del `.md` final en Obsidian.
- Descarga solo audio (ni video completo; optimiza espacio).
- Transcribe con whisper.
- Borra intermedios (mp3/wav/txt crudo).
- Deja `.md` final en `D:\obsidian\boveda MENTE\Mente\Mentores\<mentor>\`.

Esto es diferente a `claude-video-vision`, que requeriría conservar video completo + acceso a Anthropic.

---

## Pendiente (para Sesion-059)

1. **Probar flujo NVIDIA NIM con 1–2 videos cortos de Boxxocode:**
   - Descargar 1 video pequeño (min ~3 min, max ~10 min).
   - Extraer frames con ffmpeg scdet.
   - Describir cada frame con NVIDIA NIM.
   - Evaluar calidad del `.md` resultante (¿cubre lo visual?).
   - Si OK → patrón validado para script determinista.

2. **Construir script determinista video+NVIDIA:**
   - Análogo a `process-video.ps1` (versión audio).
   - ffmpeg scdet + frame extraction.
   - Loop NVIDIA NIM (determinista, sin Claude).
   - Ensamblador `.md`.
   - Integración en GUIA §2 (documentar línea de comando final).

3. **Activar `claude-video-vision` en Claude Desktop (opcional, respaldo puntual):**
   - Ya está en config; usuario ya reinició.
   - Pendiente: correr `video-configure` / `video-setup` primera vez (fija backend).
   - Usar SOLO para puntual/casos raros, no para lote completo Boxxocode.

4. **Investigación pendiente (documentada, no resuelta):**
   - Por qué MT5 se abre solo al abrir Claude Desktop (no lazy al invocar tool).
   - Hipótesis: `metatrader-mcp-server.exe` lanza terminal en su arranque.
   - Nota guardada en `docs/CONECTORES-MCP.md` §Pendientes.

---

## Commits de la sesión

```
38e0de0 docs(mentores): listado completo de lotes de 5 videos por playlist
65cc611 docs(mcp): agregar conector claude-video-vision + evaluar agent-browser
```

---

## Estado del código Pine/Core

**INTACTO.** No hubo cambios al sistema SMC/ICT.
- CORE: 1517 líneas, SHA `80fad14dd8d03758`, compila 0/0 los 3.
- core-sync: OK (no cambios a verificar).

---

## Decisiones

- **Boxxocode = canal audiovisual mudo** → requiere videovisión determinista, NO whisper.
- **Arquitectura audiovisual:** audio.ps1 (whisper local, determinista) + video.ps1 (NVIDIA NIM gratis, determinista). NO claudevisión directo.
- **`claude-video-vision` como respaldo,** no patrón principal.

---

## Sin ADR, sin gate, sin tag

- No fue decisión de arquitectura del sistema SMC/ICT.
- Fue decisión de **tooling/infraestructura** del módulo mentores paralelo.
- Documentación actualizada en `docs/CONECTORES-MCP.md` y `docs/planes/COMANDOS-*.md`.

---

## Notas

- El enjambre (Hermes/NSL/mentores) sigue en paralelo, no bloqueado por F1-GATE.
- Validación Pine (Sesion-057) ✅ COMPLETADA; F1-GATE aprobado pero pendiente firma usuario.
- Próxima sesión: Opción A (Paso 4 impl. motor strength) O Opción B (Fase 2 motor decisión). Enjambre continúa paralelo.

---

## Refs

- [[Sesion-057]] — F1-GATE validación completa.
- [[Sesion-056]] — Reglas §6 pobladas.
- [[memory/boxxocode-necesita-video-mcp]] — Diagnóstico canal mudo.
- [[memory/validacion-esperar-render-tv]] — Hallazgo render TF.
- `docs/CONECTORES-MCP.md` — Configuración MCP TV+MT5+claude-video-vision.
- `docs/planes/COMANDOS-boxxocode.md`, `docs/planes/COMANDOS-profittrading.md` — Lotes documentados.

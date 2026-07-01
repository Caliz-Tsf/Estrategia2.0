# Sesion-078 (2026-07-01)
> Infraestructura — DEBUG + FIX de 2 BUGS CRÍTICOS. Paralelo a Pine (no toca código Pine).

## Objetivo
Verificación post-S077 (reinicio Claude Desktop, Hermes, MCPs). Sesión interrumpida por bugs infraestructura no anticipados; sesión consumida íntegra en debugging y fixes.

## Completado

### 1. Bug 1 — Claude Desktop mcpServers reseteado a vacío (RESUELTO)

**Síntoma:** Al reiniciar Claude Desktop tras S077, la ventana de Settings mostró:
```
No se pudieron cargar los ajustes de la aplicación...
Unexpected token, is not valid JSON
```
Las primeras líneas de error fueron:
```
Unexpected token '', "{ "m...
```
Se perdieron todos los MCP integrados (8 → 0), la extensión Chrome, carpetas de confianza.

**Causa raíz identificada:**
- `mcp-desktop-sync.ps1` y `mt5-toggle.ps1` (en `C:\Users\Fredd\.hermes\`, fuera del repo) escribían `claude_desktop_config.json` con:
  ```powershell
  ConvertTo-Json | Set-Content -Encoding UTF8
  ```
- Windows PowerShell 5.1 **SIEMPRE antepone BOM (Byte Order Mark)** invisibles `EF BB BF` cuando se usa `-Encoding UTF8` (no existe `utf8NoBOM` en 5.1)
- Claude Desktop hace `JSON.parse()` sin despojar BOM → parseador falla en el primer carácter invisible → `Unexpected token ''` (el BOM es un token vacío para el parser)
- Desktop, al fallar, se "auto-reparaba" escribiendo un config **por defecto VACÍO**, perdiendo todo

**Diagnóstico:**
1. Verificado con Python: `open(path, 'rb').read(3) == b'\xef\xbb\xbf'` → TRUE (BOM presente)
2. Desktop config respaldado en `.bak-mcpsync-20260701-023345` (encontrado en `~/.claude/config.json` histórico)
3. Restaurado backup (que tenía BOM removido manualmente previamente)

**Fix permanente implementado:**
En ambos scripts (`mcp-desktop-sync.ps1`, `mt5-toggle.ps1`), cambio de:
```powershell
$json | Set-Content -Path $p -Encoding UTF8
```
A:
```powershell
[System.IO.File]::WriteAllText($p, $json, (New-Object System.Text.UTF8Encoding $false))
```
El constructor `System.Text.UTF8Encoding($false)` fuerza UTF-8 **SIN BOM**.

**Verificación final:**
- Config Desktop recargado correctamente
- Todos **8 MCP cargan sin errores** (Settings → Developed → Logs confirma):
  1. tradingview (9222)
  2. claude-video-vision
  3. firecrawl-mcp
  4. task-master-ai
  5. tavily-mcp
  6. playwright
  7. context-mode
  8. code-review-graph
- metatrader en `mcpServersDisabled` (propósito, reactivar Fase 4)
- Extensión Chrome re-apareció
- Carpetas confianza restauradas

**Documentación:** Nota de usuario en memoria `claude-desktop-config-bom-crash.md` (fuera del repo, en `C:\Users\Fredd\.claude\projects\...`).

### 1b. Bug secundario — code-review-graph "Server disconnected"

**Síntoma:** MCP `code-review-graph` mostraba "Server disconnected" en Settings.

**Causa:** El config incluía:
```json
"args": ["serve", "--repo", "D:\\CODE\\Estrategia2.0", "--tools", "query_graph_tool,analyze_graph_patterns"]
```
La flag `--tools` **NO existe en la versión actual del CLI** (`code-review-graph serve --help`). El proceso moría al arrancar.

**Fix:** Simplificado a:
```json
"args": ["serve", "--repo", "D:\\CODE\\Estrategia2.0"]
```
El servidor autoparsea el repo y carga todas las herramientas disponibles. Verificado manualmente que `code-review-graph serve --repo D:\CODE\Estrategia2.0` arranca sin errores.

**Status:** OK — MCP cargar sin "Server disconnected".

### 2. Bug 2 — 4/5 videos boxxocode-moneymgmt descarga fallaba (RESUELTO)

**Síntoma:** Al ejecutar tareas boxxocode de descarga (S077 objetivo pendiente):
```powershell
La cadena de entrada no tiene el formato correcto
   en línea: ...  [double]$durationSec = ...
```
4 de 5 videos del curso 2 (moneymgmt) fallaban en descarga.

**Causa identificada en `scripts/process-video-vision.ps1`:**

Original:
```powershell
yt-dlp ... --print "%(id)s|%(title)s|%(duration)s" ...
$parts = $output -split '\|', 3
$videoId = $parts[0]
$title = $parts[1]
$durationSec = $parts[2]
```

**Problema:** Si el título contenía un carácter `|` (muy común en YouTube, p. ej. "How to do robot trading in mt5 | The Simplest Price Action Strategy"), el split de 3 partes se desalineaba:
- `$parts[0]` = `videoId` (OK)
- `$parts[1]` = `"How to do robot trading in mt5 "`  (OK, pero incompleto)
- `$parts[2]` = `"The Simplest Price Action Strategy|<duration>"` (OK, pero lleva el resto del title + duration)

Después:
```powershell
[double]$durationSec = $parts[2]  # Falla: no es un número, es "The Simplest...Strategy|123"
```

**Fix:** Reordenar campos en el comando yt-dlp:
```powershell
yt-dlp ... --print "%(id)s|%(duration)s|%(title)s" ...
$parts = $output -split '\|', 3
$videoId = $parts[0]      # Nunca tiene pipes (ID único)
$durationSec = $parts[1]  # Nunca tiene pipes (número)
$title = $parts[2]        # Puede tener pipes, pero es el último campo → se atrapa completo
```

Ahora el `split '\|', 3` garantiza:
- Primeros 2 campos seguros de pipes
- Tercer campo atrapa TODO el resto (incluyendo cualquier pipe del título)

**Verificación:**
- Usuario confirmó: descarga del curso 2 funcionando post-fix
- Frames bajándose correctamente en la lista 1
- Latencia NVIDIA variable es normal (variación de 30-90s por video)

**Commit:** `fb85c2c fix(scripts): S078 corrige orden id|duration|title en process-video-vision.ps1`

## Commits de sesión

1. **`fb85c2c`** `fix(scripts): S078 corrige orden id|duration|title en process-video-vision.ps1`

## Pendiente para próxima sesión

**S079 — RETOMAR PENDIENTES S077 (NO AVANZADOS ESTA SESIÓN):**

1. **Reiniciar Claude Desktop + verificar 8 MCP** ✅ Ya hecho S078, pero chequear estado vivo
2. **Reiniciar Hermes gateway** → verificar 4 MCP cargan + env propagado a firecrawl/tavily
3. **openWakeWord:** probar `~/.hermes/start-voice.ps1 -DryRun`, grabar clips, entrenar verifier acento usuario
4. **Dossier Gradient Levels** → pasar a ultracode; Ultracode genera esqueleto
5. **BOXXO descarga** → gate indicators 1-5 (pipeline ya probado S078, listo para escalar)
6. **Enjambre 6 tareas S074** → continuar si usuario prioriza

## Decisiones

- **SIN decisiones arquitecturales nuevas.** Session = pure debugging.
- **NO hubo gate de fase completado** — sin tag.
- **Pine F1-GATE:** Sigue vigente (firma usuario pendiente, Opción A/B pendiente).

## Bloqueos

Ninguno. Infraestructura estable post-fixes.

## Notas

- **Módulo PARALELO:** 0 commits Pine. CORE INTACTO (1517 líneas SHA `80fad14dd8d03758`, compila 0/0 los 3, core-sync OK).

- **Tooling:** 2 bugs críticos resueltos:
  1. BOM en JSON (PS5.1 encoding fix) — **PERMANENTE** (ambos scripts corregidos)
  2. Pipe en título yt-dlp (reordenar campos) — **PERMANENTE** (boxxo descarga ya operativa)

- **Status infrastructure:** Stable. Todos 8 MCP Desktop OK. Boxxo pipeline listo. Hermes pending restart verify.

- **Próxima sesión:** Verify restart, retomar pendientes S077 (openWakeWord, Gradient Levels→ultracode, BOXXO/Enjambre/Pine user decision).

---

Cerrada por: Claude Code (Haiku 4.5)
Fecha: 2026-07-01 20:15 UTC

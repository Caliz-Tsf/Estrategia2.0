# Sesión 020 — Cierre documental S018 + activación GPU CUDA + módulo mentores V1

> Fecha: 2026-06-14 · Fase 1 Sprint 1.2 · Claude Code (Opus 4.8) + Freddy
> Sesión de orden y cierre (NO sprint Pine). Sin tocar código Pine.

## Objetivo
Revisar y ordenar los archivos sin commitear que se habían acumulado, commitearlos
en grupos coherentes y cerrar sesión para arrancar T07 (Premium/Discount) en la próxima.

## Qué se hizo y por qué

### 1. Cierre documental pendiente de S018 (sprint Pine)
Quedaban sin commitear las correcciones de coherencia de T06 hechas en S018:
- `M docs/reglas-smc-ict.md` (§2.2 contraejemplo sub-umbral real 06-04 11:00 0.209×ATR + 06-03 reubicado como invalidación)
- `M docs/sprint-runs/validaciones.md` (nota T06 reconciliada)
- `M memory/sesiones/Sesion-017.md` (aritmética + atribución −5 a MAX_ZONES)
- `?? memory/sesiones/Sesion-018.md` (acta S018)
- `?? scripts/ver05/_scan_sub.py` (verificador FVG sub-umbral, 33 gaps en ventana)

Revisados uno por uno: son la evidencia reproducible de la corrección. El código Pine
nunca se tocó; T06 sigue válido 95/100, core-sync OK (342 líneas SHA 16f5e945af5f27c7).

### 2. Activación GPU CUDA en el pipeline de transcripción (continuación S019)
`scripts/fw_transcribe.py` traía cambio post-S019 sin commitear: defaults `cpu`/`int8`
→ `cuda`/`float16`. Motivo: los videos de mentores son de 20+ min y la GPU acelera mucho.
**Verificado en esta sesión:** `nvidia-smi` detecta RTX 3070 (8 GB, driver 610.47) y
faster-whisper carga el modelo en GPU sin error. Resuelve la nota de S019 ("GPU no activa,
falta cublas64_12.dll"). El script conserva doble fallback automático a CPU int8 (al cargar
y durante la transcripción si falla cuBLAS/CUDA), así que es seguro.

### 3. Módulo mentores V1 (PARALELO — no toca Pine/MQL5)
`docs/MODULO-MENTORES-V1.md`: documentación del módulo que transcribe canales SMC/ICT
(reusa `process-video.ps1`), arma PERFILes de mentores, y permite invocar su "voz" desde
Hermes para revisar el bot, decidir confluencias, etc. Vive en Workspace de Hermes
(`~/.hermes/`) y vault Obsidian, NO en `.claude/` ni `.mcp.json` del proyecto.
**Regla del usuario:** nada del módulo de mentores toca el código del bot (Pine ni MQL5).
Se trabajará en sesiones paralelas dedicadas. Corregido en el doc: dependencia
`whisper` → `faster-whisper` + nota GPU.

## Decisiones registradas
1. Tres commits separados para no mezclar asuntos: (A) cierre documental S018,
   (B) activación GPU CUDA, (C) doc módulo mentores.
2. El módulo de mentores entra a git como documentación (paralelo), pero su implementación
   (skills/PERFILes/MCP video-vision) vive fuera del repo, en Workspace Hermes + Obsidian.
3. CUDA confirmado operativo — defaults GPU válidos con fallback CPU.

## Estado al cierre
- **Fase:** FASE 1 Sprint 1.2 — T05 OB ✅ · T06 FVG ✅ (validado + doc coherente).
- **Rama:** `pine/sistema-completo`. Core sync OK (342 líneas, Pine intacto).
- **Siguiente tarea:** **T07 Premium/Discount** (Sprint 1.2, PINE-PLAN §7).

## Links
- [[Sesion-018]] — corrección documental T06 (origen de lo commiteado aquí).
- [[Sesion-019]] — pipeline faster-whisper (origen del cambio GPU).
- `docs/MODULO-MENTORES-V1.md` — módulo mentores (paralelo).

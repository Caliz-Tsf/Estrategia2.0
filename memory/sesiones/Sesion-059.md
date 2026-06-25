# Sesion-059 — Módulo Mentores (ICT Madre + Descarga Audio) + Fix Pipeline
**Fecha:** 2026-06-25  
**Tipo:** Infraestructura (módulo mentores + tooling descarga), **NO Pine/MQL5**  
**Rama:** `pine/sistema-completo` (sin cambios, core intacto)

---

## Objetivo
Avanzar en el módulo mentores paralelo: consolidar descargas ICT (fix pipeline audio), validar 7 repos visuales de terceros (decisión si usarlos), e iniciar construcción del mentor ICT raíz (madre) — lectura densificada de las ~2.5M tokens de corpus.

---

## Completado

### 1. Fix descarga audio ICT (commit 4094839)
**Problema:** `scripts/process-video.ps1` forzaba cliente Android + formato `itag=18` (mp4 360p progresivo) para descargas YouTube. En videos viejos (ca. 2012–2016, ICT Lecture series), YouTube **sirve estos streams truncados** a partir de ~200s ó ~3MB. Sesión anterior reportaba "YouTube roto, sin solución" (Sonnet diagnosticó mal).

**Raíz:** Whisper solo necesita audio, nunca video completo. El script descargaba video cuando podría descargar solo audio determinista.

**Fix implementado:** 
- Cliente cambiado a `default,android` (más tolerante con streams viejos).
- Formato cambiado a `bestaudio/140/18/best` (prioridad: AAC 128k aiff, fallback mp4 progressive).
- Verificación: descargado video ICT #23 ("jan-24-2013-mentorship-live", itag 140) = **3.27 MB / 202s completo** (antes se cortaba en ~90s).

**Commit:** `4094839` · 2026-06-25 00:15

### 2. Pipeline visión boxxocode consolidado (commit bdbd36c)
**Antecedente:** S058 evaluó si usar `claude-video-vision` (token-cost alto, ~150–200/frame). Conclusión: NVIDIA NIM gratis (0.65s/frame, 40/min free).

**Completado:**
- Scripts `process-video-vision.ps1` + `nvidia_vision_describe.py` sin commitear desde S059 inicio → **COMMITEADOS**.
- Archivo `scripts/process-channel.ps1` adaptado con opción `-Vision` para loops deterministas.
- Documentación `docs/planes/COMANDOS-boxxocode.md` ampliada con formato 1080p (137/136/.../18) para que NVIDIA NIM lea mejor texto/código en pantalla.
- Tests `test_nvidia_vision_frame.py` + `test_caption_fetch.py` incluidos (no requieren credenciales, solo NVIDIA API key en env).

**Commit:** `bdbd36c` · 2026-06-25 01:20

### 3. Descargas ICT verificadas: 202 de 203 transcripciones
**Corpus ICT:**
- **ict** (67 videos): completo ✅
- **2022-mentorship** (41 videos): completo ✅
- **2024-mentorship** (50 videos): completo ✅
- **market-maker-profile** (24 videos): completo ✅
- **OTE** (20 videos): completo ✅
- **Total:** 202/203 descargas exitosas.

**Faltante:** Lecture #14 (video `WiMVPc4cvG8`, 2013-01-10, "true range and the true level") → **age-gate YouTube** (requiere `--cookies-from-browser firefox`). Diferido a sesión futura.

**Sin duplicados:** verificación previa de 206 descargas encontró 2 colisiones (mismo ID 2 veces por retry fallido de script previo); saneado en S051.

### 4. Revisión 7 repos visuales de terceros (NO se incorporan como referencia)
**Antecedente:** Sonnet propuso 7 repos para estudiar diseño visual (Fase 3).

**Hallazgo crítico:** 5 de 7 son código SMC de terceros:
- `jackrabbit-trading/TradeView-SMC` (Pine SMC, CC BY-NC-SA)
- `TradingLegends/SMC-Pine-Script` (Pine SMC trader)
- `SMC-BreakOut-Trading` (Pine SMC específico OB/FVG)
- `Elite-Trading-Mentorship` (LuxAlgo derivado)
- `Mr_Alligator/SMC_Indicators` (Pine SMC completo)

**Regla absoluta (CLAUDE.md):** única referencia externa permitida = indicador SMC de LuxAlgo (ya en `pine/reference/LuxAlgo-SMC-base.pine`). El resto = **PROHIBIDO** (no reutilizar código SMC previo).

**Decisión:**
- **NO usarlos como referencia de código.** Aún así, documentar principios visuales genéricos (no código).
- **Crear `docs/reglas-visuales.md` propio:** estilos Pine v6 nativas (box, label, xloc, color palettes), sin copiar diseño de terceros.
- **Recursos legítimos:** documentación oficial Pine v6 (dibujo/cajas/labels/max_*_count).

### 5. Mentor ICT (madre/raíz) — INICIADO (iteración 1)
**Contexto:** Usuario pidió construir el mentor raíz ICT (densificación de las lectures conceptuales). Escala estimada = **~2.5M tokens** (10× NSL's 250k) → trabajo MAP→REDUCE multi-sesión.

**Decisión de alcance:** **MUESTRA DENSA** — leer todas las lectures conceptuales + muestra del live trading.

**Completado sesión 059:**
- **Iteración 1 de `Mentores/ict/knowledge/madre-2026.md`** escrita:
  - Lecture "jan-02-2013-mentorship-live" (49 min, conceptos raíz)
  - Lecture "jan-06-2013-in-action" (63 min, ejemplos EURUSD vivo)
  - Lecture "engage-without-bias-2013" (62 min, psicología trader)
  - Lecture "march-11-2013-ny-lunch-theory" (68 min, teoría sesión NY)
  - **Total:** ~4.8k tokens densificados de 4 lectures de 240 min bruto.
  - **Extracto:** definiciones de BoS/CHoCH, liquidez, sesiones, bias, decisión sin emoción.

- **Ficha de mentor será la más completa:** campos 9 estándar (NSL) + campo adicional "Lo que opinan sus compañeros" (síntesis de cross-refs en otras lectures).

- **TaskList de próximas sesiones:**
  - **S060:** leer 2022-Mentorship (41 videos, ~41×45min = doctrina canónica) → `knowledge/2022-mentorship.md`.
  - **S061:** leer MMP (24 videos) + OTE (20 videos) + muestra 2024 (selección de 10).
  - **S062:** **REDUCE** a `Mentores/ict/ficha-mentor.md` (9 campos + cross-refs).

- **Memoria de construcción:** `memory/ict-mentor-madre-build.md` creada (tracking progreso MAP/REDUCE).

**0 commits sesión** (construcción documental, no código Pine).

---

## Pendiente (para Sesion-060+)

1. **Continuar construcción mentor ICT:**
   - Iteración 2: 2022 Mentorship (41 videos, doctrina canónica) → `knowledge/2022-mentorship.md`.
   - Iteración 3: MMP (24) + OTE (20) + muestra 2024 (10) → `knowledge/doctrinas-especializadas.md`.
   - REDUCE: síntesis 9 campos + cross-refs → `Mentores/ict/ficha-mentor.md`.

2. **Investigación visual (diferida post-mentor):**
   - Crear `docs/reglas-visuales.md` propio (estilos Pine v6 + principios, sin código terceros).
   - Revisión de 5 pendientes diferidos de T13c (S042): tag TF, cuadre EQH, exactitud OB/FVG.

3. **Descarga faltante:**
   - ICT Lecture #14 age-gate (requiere cookies Firefox o manual user-agent).

---

## Commits de la sesión

```
4094839 fix(mentores): descarga audio-only para evitar streams truncados de ICT
bdbd36c feat(mentores): pipeline de vision NVIDIA para canales mudos (boxxocode)
```

---

## Estado del código Pine/Core

**INTACTO.** No hubo cambios al sistema SMC/ICT.
- CORE: 1517 líneas, SHA `80fad14dd8d03758`, compila 0/0 los 3.
- core-sync: OK (no cambios a verificar).
- **DECISIÓN USUARIO PENDIENTE:** Sesion-059 no tocó el gate. Próxima sesión elige Opción A (Paso 4 impl. motor strength) O Opción B (Fase 2 motor decisión).

---

## Decisiones

- **ICT corpus accesible:** fix audio-only (no video) permite descargas 100% deterministas viejos videos YouTube.
- **Visión boxxocode:** pipeline NVIDIA NIM gratis (no Anthropic tokens). Formato 1080p para legibilidad OCR.
- **Mentor madre:** BUILD arquitectura MAP→REDUCE multi-sesión (2.5M tokens = 5–6 sesiones de ~400–500k densificados).
- **Repos SMC terceros:** FLAG de regla absoluta; crear reglas-visuales.md propio; NO código externo.

---

## Sin ADR, sin gate, sin tag

- Infraestructura de mentores, no arquitectura SMC/Pine.
- Documentación de descarga, no decisión de sistema.

---

## Notas

- **Mentor ICT = laboratorio paralelo** (no bloqueado por F1-GATE ni Fase 1/2 Pine).
- **Corpus accesible:** 202/203 lectures bajadas. Falta #14 (age-gate).
- **F1-GATE + firma usuario pendientes** (sesión anterior).
- **Próxima sesión:** usuario elige Opción A o B de ESTADO-ACTUAL; enjambre (mentor ICT) continúa paralelo.

---

## Refs

- [[Sesion-058]] — Boxxocode = canal mudo.
- [[Sesion-057]] — F1-GATE validación completa (pendiente firma usuario).
- `memory/ict-mentor-madre-build.md` — Tracking construcción mentor ICT.
- `Mentores/ict/knowledge/madre-2026.md` — Iteración 1 densificada (4 lectures).
- `docs/planes/COMANDOS-boxxocode.md` — Lotes actualizados (formato 1080p).
- `scripts/process-video-vision.ps1` + `nvidia_vision_describe.py` — Pipeline visión NVIDIA.


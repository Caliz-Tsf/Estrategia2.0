# Sesion-051 — 2026-06-23

> **Módulo PARALELO (Hermes / enjambre), NO Pine.** Core intacto, ningún `.pine` tocado, core-sync OK (verificado: 1517 líneas SHA `80fad14dd8d03758`). La validación visual del set completo (Sesion-049, F1-GATE) **sigue pendiente**. Continuación directa de `[[Sesion-050]]`.

## Objetivo
Dejar listos los comandos de descarga (lotes de 5) de todos los mentores, cerrar las descargas de NSL, levantar el Hermes Workspace para ver al agente, y aclarar dudas de arquitectura (modelo por agente, diseño visual del Pine).

---

## Completado

### 1. Higiene de memoria (Puter obsoleto)
- Borradas 2 memorias caducas: `hermes-puter-provider.md` y `hermes-modelos-locales-pendiente.md` (giraban en torno a Puter como solución; Puter quedó obsoleto por HTTP 402). La lección útil (VRAM 8GB → no usar modelos 12B+, `num_ctx` sobredimensionado saca el modelo a CPU) ya vive en `[[mimo-xiaomi-hermes]]`. Índice `MEMORY.md` limpiado. **(memoria del usuario, fuera de git.)**

### 2. NSL — lotes 5-en-5 completos + descargas cerradas
- **GUIA §2 expandida:** antes solo tenía el lote `1-5` de cada playlist; ahora **todos los lotes de 5** escritos para las 6 playlists (price-action 22→5 lotes, smart-money-flow 20→4, live-execution 32→7, entradas-precision 8→2, high-precision 7→2, feedback 23→5).
- **Verificación yt-dlp:** las 6 playlists resuelven y los conteos cuadran exactamente.
- **Descargas verificadas por carpeta (vs esperado):**
  - price-action 22/22 ✅, smart-money-flow 20/20 ✅, entradas-precision 8/8 ✅, high-precision 7/7 ✅, curso madre 66/65 ✅.
  - **live-execution 5/32 → DEJADO FUERA A PROPÓSITO:** son videos en vivo con **música encima, sin voz** → la transcripción no sirve. Trabajo de análisis de video aparte (futuro), no de whisper.
  - **feedback 21/23 → arreglado a 22/23 = COMPLETO en español.** Dos faltantes diagnosticados: (a) par #04/#05 con **título idéntico** colisionó en un solo `.md` (el nombre sale solo del título; re-bajados con sufijo de id); (b) #16/#17 eran la **misma sesión es/en** (yt-dlp android devuelve título español para ambos) → la inglesa es duplicado, se descartó y se restauró la española. **22 = número correcto** (23 − 1 duplicado inglés).
  - **Gotcha documentado:** `process-video.ps1` nombra el `.md` solo con el slug del título (sin id) → títulos idénticos colisionan/sobrescriben. Patrón de arreglo = re-bajar con sufijo de id.

### 3. ICT — `COMANDOS-ict.md` (nuevo) con 5 playlists esenciales
- Conteos verificados con yt-dlp. **5 esenciales elegidas** (de las 35 del canal @InnerCircleTrader), 43 comandos en lotes de 5, idioma `en`:
  1. 2026 Smart Money Concept Lecture (MADRE) — 67 → `ict`
  2. 2022 ICT Mentorship (canónica) — 41 → `ict-2022-mentorship`
  3. ICT 2024 Mentorship — 51 → `ict-2024-mentorship`
  4. ICT Market Maker Primer Course — 24 → `ict-market-maker-primer`
  5. ICT OTE Pattern Recognition — 20 → `ict-ote-pattern-recognition`
- Descartadas "Forex Precision" (3) y "High Prob Scalping" (3) por chicas. Las otras 30 playlists quedan listadas para integrar luego.
- **GUIA §4 corregida:** referencia a `COMANDOS-ict.md` + **nota de síntesis arreglada: la redacta CLAUDE leyendo las transcripciones, NO Gemini** (lección S050/NSL — el pipeline cloud era el cuello de botella). Whisper solo saca el verbatim crudo en inglés; el destilado a español y todos los documentos del agente los hace Claude.

### 4. Hermes Workspace levantado + agente visible
- Gateway (8642) + Workspace UI (3000) lanzados directamente (el `start-hermes.ps1` tiene menú interactivo + chat → no corre headless). Chrome abierto en `http://localhost:3000`.
- **NSL ya aparece** en `/operations` como agente `mentor-no-soy-liquidez`, con cartel **"NEEDS SETUP — CLICK TO CONFIGURE"** (su modelo todavía apunta al `puter` muerto). En `/conductor` aún no sale en la mesa hasta completar el setup.
- Extensión Claude-in-Chrome NO conectada al MCP (`list_connected_browsers` vacío) → no pude operar la UI desde aquí; el usuario compartió capturas.

### 5. Aclaraciones de arquitectura
- **Modelo por agente vs global:** el menú de `start-hermes` fija el `active_model` GLOBAL (default solo para el chat de terminal y agentes sin override). **Cada agente lleva su propio modelo clavado** (`model:` en `swarm.yaml` / `model.txt` junto a la skill) → no hay que re-elegir en el menú. Va con el criterio modelo-por-rol (ESQUELETO-P2 §2.9): mentor que habla = rápido; rol que razona (Escéptico/Supervisor) = razonador fuerte; visión = NVIDIA cloud.
- **Claude Design / UI-UX:** las skills empaquetadas (`design-review`, `ui-ux-pro-max`) son **solo web** (HTML/CSS). Mejorar lo visual del **indicador Pine** SÍ es posible, pero lo hace Claude con un loop **screenshot (MCP TV) → crítica → editar `.pine` → re-screenshot** + una guía de estilo propia (`PINE-VISUAL-STYLEGUIDE.md`, a futuro), NO un repo de diseño web. Timing: después de la validación visual 1-a-1, antes de `SMC-Strategy.pine`.

---

## Verificación
- **Commit:** `931f6c1` (1, coherente).
- **Core:** intacto, core-sync OK (1517 líneas SHA `80fad14dd8d03758`).
- **NSL feedback:** 22/23 = completo en español (inglés descartado a propósito).
- **Playlists ICT:** 5 ids resuelven, conteos cuadran (yt-dlp).
- **Workspace:** gateway 8642 + UI 3000 escuchando; NSL listado en /operations.

---

## Commits de Sesion-051
1. **931f6c1** — `docs(mentores): S051 — lotes 5-en-5 completos (NSL §2 + COMANDOS-ict.md)`

---

## PENDIENTE — próxima sesión arranca con UNA de estas dos
1. **Configurar NSL:** asignarle un modelo vivo (nvidia_nim `nemotron-3-super-120b` o google `gemini-2.5-flash`) → pasa de "NEEDS SETUP" a operativo y aparece en el Conductor.
2. **Protocolo de razonamiento (#1, lo de fondo):** definir QUÉ recibe el agente para mirar (esquema del **snapshot** que arma el Vigía vía MCP TV y deja en el Kanban: estructura actual, pools sin barrer, FVGs abiertos, premium/discount, sesión/hora, gate de noticias) + **cadena de auto-preguntas** (¿la zona importa? ¿rompió/no rompió? ¿ya liquidaron a los tempranos? ¿qué confluencia falta? ¿R:R≥1:3?) → decisión `ESPERAR / ENTRAR / DESCARTAR` + proyección (qué espera, qué lo invalida). Pieza COMPARTIDA del enjambre (no por mentor); candidato a ADR. Extiende el voto YAML existente.

### Heredado (sigue pendiente)
- Bajar ICT (5 esenciales) y las playlists/cursos → re-destilar fichas + knowledge (lo hace Claude).
- 2º mentor real → **piloto E2E** (Vigía+kanban+2 mentores+orquestador) sobre EURUSD.
- CallMeBot · open-second-brain (gate §4.3) · Expertos E1–E6 → Funcionales/Control · deuda V1.
- **Validación Pine Sesion-049 (F1-GATE)** sigue pendiente (camino crítico hacia Fase 2/EA).

---

## Resumen
Sesión paralela de enjambre. Comandos de descarga 5-en-5 completados para NSL (GUIA §2) y creados para ICT (`COMANDOS-ict.md`, 5 esenciales). NSL cerrado en español (feedback 22/23, live-execution fuera por música). Corregida regla del proyecto: **la síntesis la hace Claude, no Gemini.** Hermes Workspace levantado, NSL visible en /operations con "NEEDS SETUP". Aclarado: modelo por agente (no menú global) + diseño visual de Pine lo hace Claude por screenshots, no skills web. Core Pine intacto. Próxima: configurar NSL **o** escribir el protocolo de razonamiento.

---

*Sesion-051 = módulo paralelo enjambre. Descargas mentores listas + NSL cerrado + Workspace arriba. Siguiente: configurar NSL o protocolo de razonamiento. Validación Pine (049) sigue pendiente.*

# Sesion-050 — 2026-06-22

> **Módulo PARALELO (Hermes / enjambre), NO Pine.** Core intacto, ningún `.pine` tocado, core-sync N/A. La validación visual del set completo (planificada como Sesion-049) **sigue pendiente** — esta sesión avanzó la estructura del enjambre en paralelo, según la secuencia acordada (`[[proxima-sesion-enjambre-plan]]`).

## Objetivo
Generar el plan completo del enjambre (revisión de ESQUELETO-P2 + diagrama + flujos) y **dejar listo el PRIMER PERFIL del enjambre: `mentor-no-soy-liquidez` (NSL)**, partiendo del curso madre ya bajado.

---

## Completado

### 1. Plan + diagrama del enjambre
- Revisados: `ESQUELETO-P2-hermes-enjambre.md`, `PLANTILLA-agente-mentor.md`, `GUIA-transcripcion-expertos.md`, pipeline de scripts.
- Diagrama del conducto de 7 pasos del primer perfil (widget) + plan macro confirmado (§6: piloto E2E → notificador → cerebro único → escala).

### 2. PRIMER AGENTE DEL ENJAMBRE — `mentor-no-soy-liquidez` ✅ CONSTRUIDO Y VERIFICADO E2E
Conducto de 7 pasos completo:
1. **Curso 65 transcripciones** ✅ (ya en vault). ep 1–63 leídas íntegras; **ep 64 (Inside Day) vino sin transcripción** (solo audio/música) → marcado `[no cubierto en el material]`.
2. **`ficha-mentor.md` de 9 campos** — **destilada por Claude Opus 4.8 leyendo las 65 transcripciones directo** (NO el pipeline `hermes-analyze-mentor.ps1`). Parciales de trabajo en `%TEMP%/nsl-ficha/parcial-01..05.md`. En vault Obsidian.
3. **Revisión** — campo 9 (conflictos) cruzado contra `docs/reglas-smc-ict.md`.
4. **`SKILL.md`** — `build-personality.ps1` → `~/.hermes/skills/mentor-no-soy-liquidez/`.
5. **Perfil Hermes** — `hermes profile create mentor-no-soy-liquidez` (aislamiento).
6. **Registro** — entrada en `~/.hermes/swarm.yaml` (creado) + `docs/laboratorio/track-record-no-soy-liquidez.md`.
7. **Verificación E2E** ✅ — respondió en su voz (tesis "precio se mueve por liquidez e imbalances", método ERL/draw on liquidity, cuerpo vs mecha = run vs sweep, early buyer/seller, sus 4 reglas del OB válido, cierre "si tú no ves la liquidez, tú eres la liquidez").

### 3. Cuello de botella resuelto
NO se usaron las 65 llamadas MAP a Puter del pipeline viejo. **Lo hizo Opus directo** = cero cuota, mejor calidad. El cuello real eran las llamadas cloud secuenciales, no el material (decisión del usuario, confirmada).

### 4. Saneamiento de scripts y docs (commiteado)
- **Scripts** (`762ee07`): `hermes-chat-mentor.ps1` y `hermes-analyze-mentor.ps1` parametrizados con `-Provider` (default `nvidia_nim`, gratis 40/min) y `-Model`. Antes forzaban `--provider puter`, que **ya no existe** en `config.yaml`. Verificado: el mentor responde por NIM.
- **Docs** (`dc65222`): `ESQUELETO-P2 §2.9` reescrito = **mapeo ACTUAL de modelos** (solo lo mapeado HOY). Hermes (config.yaml): `nvidia_nim`, `ollama`, `zenmux`, `google`. Jarvis (start-jarvis.ps1): Tier1 local (hermes3/mimo), Tier2 NVIDIA gratis (llama-4-maverick), Tier3 Claude pendiente. Retirados: Puter, nemotron-ultra-550b, nano-omni, minimax-m3, mistral-large-3, gpt-oss-120b, cadenas OpenRouter (no configuradas).
- **GUIA-transcripcion §2** (`dc65222`): placeholders → **URLs reales de las 6 playlists NSL**, verificadas con yt-dlp (conteos cuadran: 22/20/32/8/7/23 + madre 65) + fix de slugs/labels.
- **track-record NSL** (`ae3142d`): plantilla del laboratorio.

---

## Hallazgo clave (campo 9 de la ficha)
El vocabulario de NSL mapea ~1:1 al sistema (ambos ICT). **Tensión principal: su R:R base es 1:2 — choca con el 1:3 duro del sistema.** Resolución (arquitectural, sin tocar a NSL): su 1:2 es *Expertise/sugerencia* (voz cualitativa); el R:R≥1:3 es *Norm DURA en código* (regla §0.10) — el validador determinista del Orchestrator descarta lo que no cumpla 1:3 ANTES de mostrarlo. El mentor es laboratorio/copiloto, NO recalcula el score §4.8. Sus refinamientos de ratios grandes ("1 a la liquidez", piramidación) llegarán con las playlists extra. **Aporta NUEVO a evaluar:** Early Buyer/Seller, regímenes HRLR/LRLR, MSS vs MSB, liquidity run vs sweep, Gray Pool, Event Horizon, Fair Valuation, Price Delivery Continuum, Silver Bullet v2 (07:00–09:00 NY). Horarios killzone de NSL = probable hora Colombia, verificar huso.

---

## Verificación
- **Mentor E2E:** responde en su voz por `nvidia_nim` / `nemotron-3-super-120b-a12b` ✅.
- **Playlists NSL:** 7/7 resuelven con yt-dlp, conteos exactos ✅.
- **Core:** intacto (ningún `.pine` editado), core-sync N/A.
- **Commits:** 3 coherentes (`762ee07`, `dc65222`, `ae3142d`).

---

## Commits de Sesion-050
1. **762ee07** — `chore(mentores): parametrizar --provider/-Model en scripts de mentores`
2. **dc65222** — `docs(enjambre): S050 mapeo actual de modelos (Hermes+Jarvis) + URLs reales NSL`
3. **ae3142d** — `feat(enjambre): track-record mentor-no-soy-liquidez (primer perfil del enjambre)`

---

## PENDIENTE / Tareas del enjambre

### Inmediato (lo está haciendo el usuario)
- **Bajar las 6 playlists extra de NSL** (comandos por-lotes listos en `GUIA-transcripcion-expertos.md §2`). Tras bajar → **re-destilar la ficha** (enriquece campo 3/7 con los refinamientos de ratios grandes) + sintetizar `knowledge/<tema>.md` por playlist.

### Construcción del enjambre (orden §6 de ESQUELETO-P2)
1. **Piloto mínimo E2E:** 1 cron **Vigía** (gemini-flash o NIM, 15m) + 1 **kanban** + **2 mentores reales** + **orquestador**, sobre EURUSD, generando 1 entrada de diario. Medir cuota (RPD) y ruido. *(NSL ya es 1 de los 2 mentores; falta un 2º — bajar otro curso, p.ej. ICT raíz o Boxxocode.)*
2. **Notificador:** cablear **CallMeBot** al push del copiloto (§2.8).
3. **Cerebro único:** pasar el gate de **open-second-brain** (§4.3) y migrar el recall.
4. **Escala:** cerrar **Expertos E1–E6** (no dependen de cursos) → Funcionales/Control (Router, Supervisor de Confluencia, Orchestrator, Entrenador, Escéptico) → más mentores al bajar sus cursos.
5. **Deuda V1/higiene:** retirar `hermes-proxy.mjs` (OpenRouter, obsoleto); archivar skills V1 (`consult-mentor`, `mentor-extract-profile`, `mentor-transcribe`).

### Preguntas abiertas / candidatos a ADR (§8)
- open-second-brain vs Knowledge nativo (memoria/cerebro en Obsidian).
- oh-my-hermes vs construir el loop cron+kanban+swarm a mano.
- Fuente del calendario de noticias para el gate determinista (candidato: `opennews-mcp`).
- Fórmula de ponderación de votos por track record (§2.6).

### Pendientes heredados de sesiones anteriores
- **Sesion-049 (VALIDACIÓN) sigue pendiente:** validación visual 1-a-1 aislada del set completo T16–T40 (≥90%, anti-repaint, perf 20k) — cierra el F1-GATE. Plan en `docs/sprint-runs/PLAN-VALIDACION-Sesion-049.md`.
- **Jarvis voz** (`[[proxima-sesion-enjambre-plan]]`): alargar ventana de follow-up; fix wake-word "Jarvis" (openWakeWord custom o Porcupine).
- **Live-test del MCP TV Desktop** (CDP 9222) + browser_navigate.
- **Lista completa de agentes** (tenemos + faltan): 8 internos + skills + roster de mentores/expertos/funcionales/control.

---

## Siguiente
- Usuario baja las playlists NSL → re-destilar ficha + knowledge.
- Bajar un 2º curso de mentor → instanciar 2º agente → **piloto E2E** (Vigía+kanban+2 mentores+orquestador).
- En paralelo (cuando se apruebe la visual del indicador): cerrar la **validación Sesion-049** (F1-GATE).

---

## Resumen
**Primer agente del enjambre LISTO Y VERIFICADO** (`mentor-no-soy-liquidez`): ficha de 9 campos destilada por Opus de las 65 transcripciones, skill, perfil Hermes, swarm.yaml, track-record, E2E ✅. Cuello de botella resuelto (Opus directo, no Puter). Scripts y docs saneados al mapeo de modelos actual (Hermes+Jarvis). URLs de las 6 playlists NSL corregidas y verificadas. Core Pine intacto. Validación visual (Sesion-049) y resto del enjambre quedan como tareas.

---

*Sesion-050 = módulo paralelo enjambre. Primer perfil NSL construido. Siguiente: playlists + 2º mentor + piloto E2E. La validación Pine (049) sigue pendiente.*

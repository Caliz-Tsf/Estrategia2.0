# Guía — Transcripción de los otros expertos (por lotes de 5) + playlists extra

> **Para qué:** dejar listas las carpetas y los comandos para transcribir los canales de los próximos mentores, y las playlists extra de "No soy liquidez". Prep de la próxima sesión del módulo mentores.
> **Estado:** "No soy liquidez" curso principal (65 eps) = ✅ bajado. Faltan: sus playlists extra + los demás expertos (URLs pendientes — ver §4).

---

## 1. Comando por LOTES de 5 (lo que pediste)

`process-channel.ps1` ahora acepta `-PlaylistItems "rango"` (estilo yt-dlp). Baja ese lote **uno por uno** (secuencial, no todos a la vez), sin reprocesar lo ya bajado. Patrón:

```powershell
# Lote 1 (videos 1-5)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "<URL_CANAL_O_PLAYLIST>" -Mentor "<nombre-mentor>" -Model small -PlaylistItems "1-5"
# Lote 2 (6-10)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "<URL_CANAL_O_PLAYLIST>" -Mentor "<nombre-mentor>" -Model small -PlaylistItems "6-10"
# Lote 3 (11-15) ... y así
```

- Cada lote baja sus 5 videos en orden, transcribe y actualiza `Index.md`. Lanzas el siguiente lote cuando termine el anterior.
- También sirve `-PlaylistItems "1,3,5"` para videos sueltos.
- Para reanudar: solo cambia el rango al siguiente bloque. (Si un video falla, se loguea y sigue; lo reintentas con `-PlaylistItems "<n>"`.)
- Carpeta destino: `D:\obsidian\boveda MENTE\Mente\Mentores\<slug-del-mentor>\`.

> Para un canal completo (no playlist) usa la pestaña de videos: `https://www.youtube.com/@Canal/videos`.

---

## 2. Playlists extra de "No soy liquidez" (un mentor, varios temas)

Cada playlist temática va a su **propia subcarpeta** (luego se sintetiza en un `knowledge/*.md`, ver `ESQUEMA-HERMES-mentor-module.md` §3). El `-Mentor` lleva el tema incluido para que el slug genere la carpeta correcta. **URLs reales verificadas (S050, 2026-06-22): las 7 playlists resuelven y los conteos cuadran. Lotes 5-en-5 completos generados (S051).** Corre los lotes de cada playlist **en orden, uno tras otro** (esperar a que termine el anterior); si un video falla se loguea y sigue.

```powershell
# === Lectura Price Action (22 vids)  ->  Mentores\no-soy-liquidez-price-action\  (5 lotes) ===
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4aLY0PxiFCY2VO1paxV9xf" -Mentor "no soy liquidez price-action" -Model small -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4aLY0PxiFCY2VO1paxV9xf" -Mentor "no soy liquidez price-action" -Model small -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4aLY0PxiFCY2VO1paxV9xf" -Mentor "no soy liquidez price-action" -Model small -PlaylistItems "11-15"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4aLY0PxiFCY2VO1paxV9xf" -Mentor "no soy liquidez price-action" -Model small -PlaylistItems "16-20"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4aLY0PxiFCY2VO1paxV9xf" -Mentor "no soy liquidez price-action" -Model small -PlaylistItems "21-22"

# === Smart Money Flow (20 vids)  ->  Mentores\no-soy-liquidez-smart-money-flow\  (4 lotes) ===
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4CdYD__c0Sqd1U81IX8nVb" -Mentor "no soy liquidez smart-money-flow" -Model small -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4CdYD__c0Sqd1U81IX8nVb" -Mentor "no soy liquidez smart-money-flow" -Model small -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4CdYD__c0Sqd1U81IX8nVb" -Mentor "no soy liquidez smart-money-flow" -Model small -PlaylistItems "11-15"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4CdYD__c0Sqd1U81IX8nVb" -Mentor "no soy liquidez smart-money-flow" -Model small -PlaylistItems "16-20"

# === Live Execution (32 vids)  ->  Mentores\no-soy-liquidez-live-execution\  (7 lotes) ===
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA5raD2oTFE5JTo48uw7o3fR" -Mentor "no soy liquidez live-execution" -Model small -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA5raD2oTFE5JTo48uw7o3fR" -Mentor "no soy liquidez live-execution" -Model small -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA5raD2oTFE5JTo48uw7o3fR" -Mentor "no soy liquidez live-execution" -Model small -PlaylistItems "11-15"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA5raD2oTFE5JTo48uw7o3fR" -Mentor "no soy liquidez live-execution" -Model small -PlaylistItems "16-20"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA5raD2oTFE5JTo48uw7o3fR" -Mentor "no soy liquidez live-execution" -Model small -PlaylistItems "21-25"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA5raD2oTFE5JTo48uw7o3fR" -Mentor "no soy liquidez live-execution" -Model small -PlaylistItems "26-30"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA5raD2oTFE5JTo48uw7o3fR" -Mentor "no soy liquidez live-execution" -Model small -PlaylistItems "31-32"

# === Entradas de Alta Precision SMC (8 vids)  ->  Mentores\no-soy-liquidez-entradas-precision\  (2 lotes) ===
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4Oq5tx5WsmTu5hZ9LIbroi" -Mentor "no soy liquidez entradas-precision" -Model small -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4Oq5tx5WsmTu5hZ9LIbroi" -Mentor "no soy liquidez entradas-precision" -Model small -PlaylistItems "6-8"

# === High Precision Trading Entries (7 vids)  ->  Mentores\no-soy-liquidez-high-precision\  (2 lotes) ===
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4J3gr2fBoqvcxhE746uUvY" -Mentor "no soy liquidez high-precision" -Model small -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA4J3gr2fBoqvcxhE746uUvY" -Mentor "no soy liquidez high-precision" -Model small -PlaylistItems "6-7"

# === Sesion de Feedback (23 vids)  ->  Mentores\no-soy-liquidez-feedback\  (5 lotes) ===
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA6ozzF8PHaiDY-0N03Os0N9" -Mentor "no soy liquidez feedback" -Model small -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA6ozzF8PHaiDY-0N03Os0N9" -Mentor "no soy liquidez feedback" -Model small -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA6ozzF8PHaiDY-0N03Os0N9" -Mentor "no soy liquidez feedback" -Model small -PlaylistItems "11-15"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA6ozzF8PHaiDY-0N03Os0N9" -Mentor "no soy liquidez feedback" -Model small -PlaylistItems "16-20"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLOwrTT3cFiA6ozzF8PHaiDY-0N03Os0N9" -Mentor "no soy liquidez feedback" -Model small -PlaylistItems "21-23"
```

> El curso MADRE (65 vids, ✅ ya bajado) es la playlist `PLOwrTT3cFiA5Qo_k27soDPvyPo3Wr7T8S` → `Mentores\no-soy-liquidez\`. Sus comandos por-video están en `COMANDOS-curso-no-soy-liquidez.md`.

Resultado = el MISMO mentor sabrá de todos esos temas (un agente, varios conocimientos), no 6 agentes distintos. Tras bajar cada tema → se sintetiza en un `knowledge/<tema>.md`.

---

## 3. Plantilla de carpetas (objetivo final por mentor)

```
~/.hermes/knowledge/<mentor-slug>/
    ficha-mentor.md            # CÓMO decide (personalidad/voto) — de la síntesis del curso principal
    <tema-1>.md                # síntesis de cada playlist temática
    <tema-2>.md
    ...
D:\obsidian\boveda MENTE\Mente\Mentores\<mentor-slug>[-<tema>]\   # transcripciones crudas (.md + Index.md)
```
Flujo por mentor: bajar curso principal → ficha (9 campos) → bajar playlists extra (por lotes) → sintetizar cada una en un knowledge `.md`.

---

## 4. Expertos y URLs (recibidas) — comandos los genero la PRÓXIMA sesión

> Los comandos 5-en-5 por playlist los genera **Claude** (no Opus Max) en la próxima sesión. Aquí quedan registradas las URLs.

### No soy liquidez — curso ✅ + 6 playlists extra (mismo agente, varios knowledge)
| Tema | Videos | Playlist | Slug carpeta |
|---|---:|---|---|
| Curso (madre) ✅ | 65 | `PLOwrTT3cFiA5Qo_k27soDPvyPo3Wr7T8S` | `no-soy-liquidez` |
| Lectura Price Action | 22 | `PLOwrTT3cFiA4aLY0PxiFCY2VO1paxV9xf` | `no-soy-liquidez-price-action` |
| Smart Money Flow | 20 | `PLOwrTT3cFiA4CdYD__c0Sqd1U81IX8nVb` | `no-soy-liquidez-smart-money-flow` |
| Live Execution | 32 | `PLOwrTT3cFiA5raD2oTFE5JTo48uw7o3fR` | `no-soy-liquidez-live-execution` |
| Entradas de Alta Precisión SMC | 8 | `PLOwrTT3cFiA4Oq5tx5WsmTu5hZ9LIbroi` | `no-soy-liquidez-entradas-precision` |
| High Precision Trading Entries | 7 | `PLOwrTT3cFiA4J3gr2fBoqvcxhE746uUvY` | `no-soy-liquidez-high-precision` |
| Sesión de Feedback | 23 | `PLOwrTT3cFiA6ozzF8PHaiDY-0N03Os0N9` | `no-soy-liquidez-feedback` |

### ICT — Inner Circle Trader (🇬🇧 creador de ICT, mentor-experto raíz)
Canal: `https://www.youtube.com/@InnerCircleTrader/playlists` — **el canal completo es la fuente**.
| Rol | Playlist | ID |
|---|---|---|
| **MADRE** (conceptos actualizados) | 2026 ICT Smart Money Concept Lecture | `PLVgHx4Z63paaja3GW0dYSr6y_V2Sttx4-` |
| Agregados clave | 2025 Lecture Series · ICT 2024 Mentorship · 2023 ICT Mentorship · 2022 ICT Mentorship · ICT Forex Precision Trading Concepts · ICT OTE Pattern Recognition · ICT Market Maker Series · Mastering High Probability Scalping | (ver canal) |

> Slug ICT: `ict` (madre) + `ict-<tema>`. Es el mentor-experto de los conceptos raíz → su knowledge alimenta el cierre del gap (matriz).

### Los demás expertos ya tienen su doc de comandos (con lotes de 5 completos)
`COMANDOS-ict.md` (5 playlists esenciales, S051) · `COMANDOS-boxxocode.md` · `COMANDOS-profittrading.md` · `COMANDOS-tj-trading.md` · `COMANDOS-fedex.md`.

### ⚠️ Inglés → español (ICT y Boxxocode): la síntesis la hace CLAUDE, no Gemini
faster-whisper **solo traduce hacia inglés** (no a español). Para fuentes en inglés:
- **Transcribir en su idioma nativo** (`-Language en`) — es lo más fiel; no traducir el verbatim crudo (solo añade error).
- **El español sale en la SÍNTESIS, que la redacta CLAUDE** leyendo las transcripciones íntegras (igual que se hizo con NSL en Sesion-050: la destiló Opus directo, NO el pipeline cloud). La `ficha-mentor.md` (9 campos) y cada `knowledge/<tema>.md` los escribe Claude en español. Cero invención: cita literal entre comillas, lo no cubierto se marca `[no cubierto en el material]`. **No es Gemini ni map-reduce cloud** — ese fue el cuello de botella que se descartó.

---

## 5. Para la próxima sesión (checklist)
1. Pegar las URLs de §4.
2. Yo genero, por cada canal, la lista de comandos por-video (como `COMANDOS-curso-no-soy-liquidez.md`) o los lotes de 5.
3. Tú bajas; yo reviso (conteo de `.md`, faltantes, transcripciones vacías).
4. Síntesis Fase 2 → `ficha-mentor.md` (con campo 9 "Conflictos con el sistema") + knowledge `.md` por tema.
5. Scaffold del skill `mentor-<slug>` (skill-creator / build-personality.ps1).

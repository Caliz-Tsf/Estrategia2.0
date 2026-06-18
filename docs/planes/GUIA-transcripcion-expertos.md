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

Cada playlist temática va a su **propia subcarpeta** (luego se sintetiza en un `knowledge/*.md`, ver `ESQUEMA-HERMES-mentor-module.md` §3). Usa el `-Mentor` con el tema incluido para que el slug genere la carpeta:

```powershell
# Price action  ->  Mentores\no-soy-liquidez-price-action\
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "<URL_PLAYLIST_PRICE_ACTION>" -Mentor "no soy liquidez price-action" -Model small -PlaylistItems "1-5"

# Live execution  ->  Mentores\no-soy-liquidez-live-execution\
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "<URL_PLAYLIST_LIVE_EXECUTION>" -Mentor "no soy liquidez live-execution" -Model small -PlaylistItems "1-5"

# High precision entries  ->  Mentores\no-soy-liquidez-entradas-precision\
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "<URL_PLAYLIST_ENTRADAS>" -Mentor "no soy liquidez entradas-precision" -Model small -PlaylistItems "1-5"

# Smart money flow  ->  Mentores\no-soy-liquidez-smart-money-flow\
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "<URL_PLAYLIST_SMF>" -Mentor "no soy liquidez smart-money-flow" -Model small -PlaylistItems "1-5"
```

Resultado = el MISMO mentor sabrá de todos esos temas (un agente, varios conocimientos), no 5 agentes distintos.

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

### Los otros 4 expertos ya tienen su doc de comandos
`COMANDOS-boxxocode.md` · `COMANDOS-profittrading.md` · `COMANDOS-tj-trading.md` · `COMANDOS-fedex.md`.

### ⚠️ Traducción inglés → español (ICT y Boxxocode)
faster-whisper **solo traduce hacia inglés** (no a español). Para fuentes en inglés:
- **Transcribir en su idioma nativo** (`-Language en`) — es lo más fiel.
- **El español sale en la SÍNTESIS (Fase 2):** la ficha y los knowledge `.md` se generan con **Gemini**, que produce el resumen **en español** aunque la transcripción esté en inglés. No hace falta traducir las transcripciones crudas (eso solo añade error); se traduce/sintetiza el conocimiento, no el verbatim.

---

## 5. Para la próxima sesión (checklist)
1. Pegar las URLs de §4.
2. Yo genero, por cada canal, la lista de comandos por-video (como `COMANDOS-curso-no-soy-liquidez.md`) o los lotes de 5.
3. Tú bajas; yo reviso (conteo de `.md`, faltantes, transcripciones vacías).
4. Síntesis Fase 2 → `ficha-mentor.md` (con campo 9 "Conflictos con el sistema") + knowledge `.md` por tema.
5. Scaffold del skill `mentor-<slug>` (skill-creator / build-personality.ps1).

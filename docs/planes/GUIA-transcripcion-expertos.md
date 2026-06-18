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

## 4. Expertos y URLs — PENDIENTE QUE LLENES

Lléname esta tabla con los canales/playlists (la próxima sesión genero los comandos por-video concretos como el del curso principal):

| Mentor | Tipo | URL canal/playlist | ¿Bajado? |
|---|---|---|---|
| No soy liquidez — curso | playlist | `https://www.youtube.com/playlist?list=PLOwrTT3cFiA5Qo_k27soDPvyPo3Wr7T8S` | ✅ |
| No soy liquidez — price action | playlist | `<URL>` | ⬜ |
| No soy liquidez — live execution | playlist | `<URL>` | ⬜ |
| No soy liquidez — high precision entries | playlist | `<URL>` | ⬜ |
| No soy liquidez — smart money flow | playlist | `<URL>` | ⬜ |
| Boxxocode | canal `/videos` | `<URL>` | ⬜ |
| Experto 3 | ? | `<URL>` | ⬜ |
| Experto 4 | ? | `<URL>` | ⬜ |

---

## 5. Para la próxima sesión (checklist)
1. Pegar las URLs de §4.
2. Yo genero, por cada canal, la lista de comandos por-video (como `COMANDOS-curso-no-soy-liquidez.md`) o los lotes de 5.
3. Tú bajas; yo reviso (conteo de `.md`, faltantes, transcripciones vacías).
4. Síntesis Fase 2 → `ficha-mentor.md` (con campo 9 "Conflictos con el sistema") + knowledge `.md` por tema.
5. Scaffold del skill `mentor-<slug>` (skill-creator / build-personality.ps1).

# Comandos — Transcripción del mentor "Fedex" (lotes de 5)

> Mentor SMC. Pipeline determinista (yt-dlp android-bypass → ffmpeg → faster-whisper GPU), sin LLM.
> Cada comando baja **5 videos, uno por uno**. Lanzas el siguiente lote cuando termina el anterior.
> Carpeta destino: `D:\obsidian\boveda MENTE\Mente\Mentores\<slug>\`.

## Clasificación del canal
| Playlist | Rol | Videos | Slug / carpeta |
|---|---|---:|---|
| **Esses Bootcamp – Curso de Trading desde Cero** | **MADRE** (su método completo) | 50 | `fedex` |
| Estrategia IFVG – ICT × SMC | agregado (estrategia específica: Inverse FVG) | 27 | `fedex-ifvg` |
| Live Trading | agregado (cómo ejecuta en vivo) | 23 | `fedex-live` |

> Orden sugerido: primero la **madre** (define su forma de ver SMC), luego IFVG y Live (extras que portan a su conocimiento).

---

## 1. MADRE — Esses Bootcamp (50 videos → 10 lotes)
Lote 1 (cambia solo el rango `-PlaylistItems` en cada corrida):
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PL4hId-DTkHg50047_yeFJOvPK1rOCrSoR" -Mentor "fedex" -Model small -PlaylistItems "1-5"
```
Lotes a correr en orden: `1-5` · `6-10` · `11-15` · `16-20` · `21-25` · `26-30` · `31-35` · `36-40` · `41-45` · `46-50`

## 2. AGREGADO — Estrategia IFVG (27 → 6 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PL4hId-DTkHg5crb2xiVOxuaHTcMLbVOx4" -Mentor "fedex ifvg" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-20` · `21-25` · `26-27`

## 3. AGREGADO — Live Trading (23 → 5 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PL4hId-DTkHg5mAiXs35yybIlNnB0H6aKM" -Mentor "fedex live" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-20` · `21-23`

---
## Cómo se usa
- Copia el comando de la playlist, corre el lote `1-5`, espera a que termine, cambia el rango al siguiente y vuelve a correr.
- Si un video falla, se loguea y sigue; lo reintentas con `-PlaylistItems "<n>"`.
- Auto-chequeo: `(Get-ChildItem "D:\obsidian\boveda MENTE\Mente\Mentores\fedex\*.md" | Where-Object Name -ne 'Index.md').Count`
- Cuando termines, dime *"revisa la descarga de fedex"* y verifico conteos/faltantes.

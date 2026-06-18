# Comandos — Transcripción del mentor "TJ Trading" (lotes de 5)

> Mentor SMC / institucional (español). Canal @tj-trading24. Pipeline determinista, sin LLM.
> Cada comando baja **5 videos, uno por uno**. Carpeta: `D:\obsidian\boveda MENTE\Mente\Mentores\<slug>\`.

## Clasificación del canal
| Playlist | Rol | Videos | Slug / carpeta |
|---|---|---:|---|
| **SMC BOOTCAMP ELITE** | **MADRE** (su curso SMC núcleo) | 17 | `tj-trading` |
| MASTERCLASS: Smart Money Concept | agregado (clase única) | 1 | `tj-trading masterclass` |
| BOOTCAMP 2025 | agregado (mentalidad/aplicación 2025) | 6 | `tj-trading bootcamp2025` |
| Análisis de TRADES | agregado (ejemplos en vivo) | 19 | `tj-trading analisis` |
| Herramientas daytrading | agregado (herramientas/metodología) | 36 | `tj-trading herramientas` |

> Canal con 14 playlists; se omiten básicos/arbitraje/shorts por ahora (se añaden luego si aportan).

---

## 1. MADRE — SMC Bootcamp Elite (17 → 4 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLw5tI70A_rjJoJDimTiy9mcoRNAHXaWDz" -Mentor "tj-trading" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-17`

## 2. AGREGADO — Masterclass SMC (1 video)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLw5tI70A_rjI-Ol03ptQ_EPvy2A_IdNhV" -Mentor "tj-trading masterclass" -Model small -PlaylistItems "1"
```

## 3. AGREGADO — Bootcamp 2025 (6 → 2 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLw5tI70A_rjJ1tQLXc9_xp0OOG_pirWpS" -Mentor "tj-trading bootcamp2025" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6`

## 4. AGREGADO — Análisis de Trades (19 → 4 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLw5tI70A_rjKZKaACSBEH6JPtLo820pog" -Mentor "tj-trading analisis" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-19`

## 5. AGREGADO — Herramientas daytrading (36 → 8 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLw5tI70A_rjJhZ9-QrLHNx9iReVoA6si3" -Mentor "tj-trading herramientas" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-20` · `21-25` · `26-30` · `31-35` · `36`

---
Auto-chequeo: `(Get-ChildItem "D:\obsidian\boveda MENTE\Mente\Mentores\tj-trading\*.md" | Where-Object Name -ne 'Index.md').Count`

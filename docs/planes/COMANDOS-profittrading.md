# Comandos — Transcripción del mentor "Profittrading specialist" (lotes de 5)

> Mentor SMC (español). Canal @profittrading9412. Pipeline determinista, sin LLM.
> Cada comando baja **5 videos, uno por uno**. Carpeta: `D:\obsidian\boveda MENTE\Mente\Mentores\<slug>\`.

## Clasificación del canal
| Playlist | Rol | Videos | Slug / carpeta |
|---|---|---:|---|
| **CURSO VIP 2023 AVANZADO** | **MADRE** (su curso avanzado núcleo) | 18 | `profittrading` |
| (SMC) Trading con Smart Money Concepts | agregado (SMC base) | 15 | `profittrading smc` |
| INTENSIVOS DE SMC | agregado (intensivo SMC) | 23 | `profittrading intensivos` |
| Domina el Trading con SMC2026 | agregado (SMC actualizado) | 14 | `profittrading smc2026` |
| Sesiones en vivo (Zoom) | agregado (ejecución/aplicación en vivo) | 27 | `profittrading live` |
| Scalping 1min | agregado (método extra) | 6 | `profittrading scalping` |

> Canal con 14 playlists; se omiten básicos/broker/shorts por ahora.

---

## 1. MADRE — Curso VIP 2023 Avanzado (18 → 4 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLk7TdJSck21MjiCwIWZOdKJyCXd2OxgwM" -Mentor "profittrading" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-18`

## 2. AGREGADO — (SMC) Smart Money Concepts (15 → 3 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLk7TdJSck21OC7OjlV4tyig4LlAexmho8" -Mentor "profittrading smc" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15`

## 3. AGREGADO — Intensivos de SMC (23 → 5 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLk7TdJSck21O4AF5Da89q4S3RtpAE72nc" -Mentor "profittrading intensivos" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-20` · `21-23`

## 4. AGREGADO — Domina SMC2026 (14 → 3 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLk7TdJSck21Op-XbQHnOaBZ3F8EQ27jhN" -Mentor "profittrading smc2026" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-14`

## 5. AGREGADO — Sesiones en vivo Zoom (27 → 6 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLk7TdJSck21OSfvM7Lpdmq12P6I3_h83c" -Mentor "profittrading live" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-20` · `21-25` · `26-27`

## 6. AGREGADO — Scalping 1min (6 → 2 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLk7TdJSck21OPnVD7LRr3Uh6VeBEAtpra" -Mentor "profittrading scalping" -Model small -PlaylistItems "1-5"
```
Lotes: `1-5` · `6`

---
Auto-chequeo: `(Get-ChildItem "D:\obsidian\boveda MENTE\Mente\Mentores\profittrading\*.md" | Where-Object Name -ne 'Index.md').Count`

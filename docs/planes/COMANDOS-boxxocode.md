# Comandos — Transcripción del experto "Boxxocode" (lotes de 5)

> **Archetipo distinto:** NO es mentor SMC. Es un **experto en estrategias / automatización-EA** (canal en inglés, @Boxxocode): construcción de EAs/bots en MT5, backtesting, money management, indicadores custom (herramientas fxDreema / EA Builder). Alimenta el lado del **EA (Fase 4)** y el diseño de estrategias, no la lectura de confluencias SMC.
> Pipeline determinista, sin LLM. Carpeta: `D:\obsidian\boveda MENTE\Mente\Mentores\<slug>\`.

## Clasificación del canal (no hay "curso madre" único — es un toolbox)
| Playlist | Rol | Videos | Slug / carpeta | Prioridad |
|---|---|---:|---|---|
| **Backtest Trading Strategy (EA Robot - MT5)** | núcleo: cómo backtestear estrategias/EA en MT5 | 40 | `boxxocode-backtest` | ⭐ alta |
| Custom Indicators (by EA Builder) | indicadores propios para EAs | 13 | `boxxocode-indicators` | ⭐ alta (corta) |
| Advance Money Management (by fxDreema) | gestión de riesgo/dinero en EA | 100 | `boxxocode-moneymgmt` | media |
| Advance Code (by fxDreema) | lógica/código avanzado de EAs | 87 | `boxxocode-code` | media |
| RobotTrade Courses (by fxDreema) | cursos de bots de trading | 100 | `boxxocode-robottrade` | media |
| AI trading bot | bots con IA | 76 | `boxxocode-aibot` | baja |

> ⚠️ **Playlists grandes** (100/87/76). Sugerencia: baja primero **Custom Indicators (13)** y **Backtest (40)** —las más densas en valor— y deja las de 100 para después o parciales. Idioma inglés: whisper `small` transcribe en inglés igual (no fuerces `-Language es` aquí; usa `-Language en`).

---

## 1. ⭐ Backtest Trading Strategy EA-MT5 (40 → 8 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQo0JAVfCNz-oda3htf_pG9" -Mentor "boxxocode backtest" -Model small -Language en -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-20` · `21-25` · `26-30` · `31-35` · `36-40`

## 2. ⭐ Custom Indicators EA Builder (13 → 3 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMSG26fgyaXMjJALMR3envDW" -Mentor "boxxocode indicators" -Model small -Language en -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-13`

## 3. Advance Money Management (100 → 20 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Model small -Language en -PlaylistItems "1-5"
```
Lotes: `1-5` · `6-10` · `11-15` · `16-20` · `21-25` · `26-30` · `31-35` · `36-40` · `41-45` · `46-50` · `51-55` · `56-60` · `61-65` · `66-70` · `71-75` · `76-80` · `81-85` · `86-90` · `91-95` · `96-100`

## 4. Advance Code fxDreema (87 → 18 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Model small -Language en -PlaylistItems "1-5"
```
Lotes: `1-5` … `81-85` · `86-87` (rangos de 5 hasta 87)

## 5. RobotTrade Courses fxDreema (100 → 20 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Model small -Language en -PlaylistItems "1-5"
```
Lotes: `1-5` … `96-100` (rangos de 5 hasta 100)

## 6. AI trading bot (76 → 16 lotes)
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Model small -Language en -PlaylistItems "1-5"
```
Lotes: `1-5` … `71-75` · `76`

---
## Nota de uso para este experto
- Por ser de **automatización-EA**, su conocimiento se sintetizará distinto a un mentor SMC: en vez de "ficha de personalidad de trading", su síntesis apunta a **patrones de construcción/backtest/gestión de EAs** → insumo del **HANDOFF-OPUS-MAX** (motor del EA) y de Fase 4.
- Auto-chequeo: `(Get-ChildItem "D:\obsidian\boveda MENTE\Mente\Mentores\boxxocode-backtest\*.md" | Where-Object Name -ne 'Index.md').Count`

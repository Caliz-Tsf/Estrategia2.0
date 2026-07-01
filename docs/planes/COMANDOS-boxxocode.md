# Comandos -- Boxxocode via VISION (lotes de 5)

> **Canal MUDO confirmado (S059):** whisper transcribe solo alucinaciones del ruido/musica
> de fondo ("I'll see you in the next video", "music", "the the the"). Las 19 notas
> de whisper generadas para este canal se borraron -- 0 contenido real. Pipeline correcto:
> **`process-channel.ps1 -Vision`** (NVIDIA NIM, describe frames, 0 tokens Claude).
>
> Mismo archetipo que antes: experto en estrategias/automatizacion-EA (construccion de
> EAs/bots en MT5, backtesting, money management, fxDreema/EA Builder). Alimenta Fase 4
> (EA) y diseno de estrategias, no confluencias SMC.
>
> Carpeta: `D:\obsidian\boveda MENTE\Mente\Mentores\<slug>\`. Cada video produce un
> `<slug-video>-vision.md` (frames descritos en espanol por NVIDIA NIM).
>
> **DESCARTADA (revision S059):** Backtest Trading Strategy EA-MT5 -- es el backtest de
> UNA estrategia/EA particular (resultados de cuenta, no metodo generalizable), no aporta
> patron reusable. Se deja documentada al final por si cambia el criterio, pero NO se corre.

## Pipeline mejorado (A/B S075) -- ya es el DEFAULT, los comandos de abajo no cambian
> El A/B del Modulo 2 (video `BEStJddJjhM`) mostro que la DETECCION DE ESCENA
> submuestreaba: en un tutorial de 61 min daba 2 frames en la fase de PREPARACION
> (0-35 min) y amontonaba 10 en la edicion final. Cambios adoptados:
>
> 1. **Muestreo UNIFORME** (`-UniformSample`, default en `process-channel.ps1 -Vision`):
>    extrae `-MaxFrames` (default **40**) frames equiespaciados en todo el video
>    (intervalo = duracion/MaxFrames). Cubre por igual preparacion y ejecucion.
> 2. **Prompt NVIDIA endurecido + fallback**: pide texto verbatim entre comillas y
>    "no se lee" en vez de adivinar (menos relleno/alucinacion); si el modelo rechaza
>    un frame (tipico en capturas de ChatGPT -> falso positivo de copyright), reintenta
>    con un prompt neutro. Verificado 0/5 rechazos en frames reales.
> 3. **`-Provider nvidia|gemini`**: NVIDIA es el motor de barrido (free, 40 req/min, escala).
>    Gemini 2.5 (`gemini_vision_describe.py`) queda como spot-check puntual -- su free tier
>    (~10 RPM / cupo diario) se agota con UN solo video de 40 frames, NO sirve para volumen.
>
> Overrides opcionales: `-MaxFrames N`, `-Provider gemini`, `-SceneDetect` (modo viejo).

## Clasificacion del canal (no hay "curso madre" unico -- es un toolbox)
| Playlist | Rol | Videos | Slug / carpeta | Prioridad |
|---|---|---:|---|---|
| **Custom Indicators EA Builder** | indicadores propios para EAs | 13 | `boxxocode-indicators` | alta (corta) |
| **Advance Money Management** | gestion de riesgo/dinero en EA | 100 | `boxxocode-moneymgmt` | media |
| **Advance Code fxDreema** | logica/codigo avanzado de EAs | 89 | `boxxocode-code` | media |
| **RobotTrade Courses fxDreema** | cursos de bots de trading | 100 | `boxxocode-robottrade` | media |
| **AI trading bot** | bots con IA | 79 | `boxxocode-aibot` | baja |
| ~~Backtest Trading Strategy EA-MT5~~ | descartada -- backtest de 1 estrategia, no patron | ~~40~~ | `boxxocode-backtest` | descartada |

> Primero **Custom Indicators (13, 3 lotes)** -- la mas chica, gate de calidad. Si las notas
> aportan parametros/codigo legibles, seguir con las 4 restantes (100/87/100/76).

---

## 1. Custom Indicators EA Builder (13 -> 3 lotes)
URL: <https://www.youtube.com/playlist?list=PLtefuVjyVOMSG26fgyaXMjJALMR3envDW>
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMSG26fgyaXMjJALMR3envDW" -Mentor "boxxocode indicators" -Vision -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMSG26fgyaXMjJALMR3envDW" -Mentor "boxxocode indicators" -Vision -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMSG26fgyaXMjJALMR3envDW" -Mentor "boxxocode indicators" -Vision -PlaylistItems "11-13"
```

## 2. Advance Money Management (100 -> 20 lotes)
URL: <https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx>
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "11-15"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "16-20"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "21-25"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "26-30"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "31-35"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "36-40"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "41-45"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "46-50"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "51-55"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "56-60"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "61-65"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "66-70"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "71-75"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "76-80"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "81-85"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "86-90"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "91-95"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMTltvle0shVPj2J5hueqQwx" -Mentor "boxxocode moneymgmt" -Vision -PlaylistItems "96-100"
```

## 3. Advance Code fxDreema (89 -> 18 lotes)
URL: <https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa>
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "11-15"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "16-20"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "21-25"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "26-30"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "31-35"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "36-40"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "41-45"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "46-50"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "51-55"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "56-60"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "61-65"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "66-70"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "71-75"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "76-80"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "81-85"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQSXqTMA9elkOCM2-nEvuFa" -Mentor "boxxocode code" -Vision -PlaylistItems "86-89"
```

## 4. RobotTrade Courses fxDreema (100 -> 20 lotes)
URL: <https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K>
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "11-15"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "16-20"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "21-25"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "26-30"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "31-35"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "36-40"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "41-45"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "46-50"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "51-55"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "56-60"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "61-65"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "66-70"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "71-75"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "76-80"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "81-85"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "86-90"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "91-95"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMS-P4uC4fiIYu8eoH58fj7K" -Mentor "boxxocode robottrade" -Vision -PlaylistItems "96-100"
```

## 5. AI trading bot (79 -> 16 lotes)
URL: <https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_>
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "1-5"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "6-10"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "11-15"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "16-20"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "21-25"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "26-30"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "31-35"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "36-40"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "41-45"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "46-50"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "51-55"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "56-60"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "61-65"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "66-70"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "71-75"
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-channel.ps1" -ChannelUrl "https://www.youtube.com/playlist?list=PLtefuVjyVOMQsYYjOuu996HcmY-dCg5P_" -Mentor "boxxocode aibot" -Vision -PlaylistItems "76-79"
```

---

## Descartada -- Backtest Trading Strategy EA-MT5 (NO correr)
> Revisado S059: es el backtest de UNA estrategia/EA puntual (resultados de cuenta
> especificos), no ensena un metodo/patron reutilizable como las otras 5. Queda aqui
> solo de referencia por si mas adelante se decide que algun video puntual sirve.

URL: <https://www.youtube.com/playlist?list=PLtefuVjyVOMQo0JAVfCNz-oda3htf_pG9> (40 videos, `boxxocode-backtest`)

---
## Nota de uso para este experto
- Sintesis distinta a un mentor SMC: en vez de "ficha de personalidad de trading", apunta a **patrones de construccion/backtest/gestion de EAs** -> insumo del HANDOFF-OPUS-MAX (motor del EA) y de Fase 4.
- Auto-chequeo: `(Get-ChildItem "D:\obsidian\boveda MENTE\Mente\Mentores\boxxocode-indicators\*.md" | Where-Object Name -ne 'Index.md').Count`
- Tras los primeros 1-2 lotes de una playlist nueva, revisar 1 nota generada antes de seguir -- confirmar que las descripciones visuales realmente aportan (parametros, codigo, valores legibles) y no son solo "se ve un grafico" generico. Si una playlist no aporta valor real, frenar ahi y no gastar el resto de los lotes.

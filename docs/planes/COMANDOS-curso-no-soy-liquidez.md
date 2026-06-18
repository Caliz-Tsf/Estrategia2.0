# Comandos — Descarga + transcripción del curso "No soy liquidez" (video por video)

> **Para qué:** bajar y transcribir el curso completo al vault, **un video a la vez**, marcando cuáles ya están.
> **Auto-contenido:** si te quedas sin tokens, sigue tú mismo comando por comando desde aquí.
> Generado Sesión-030 (2026-06-17). Pipeline determinista (yt-dlp → ffmpeg → faster-whisper GPU), **sin LLM**.

---

## Datos del curso

| Campo | Valor |
|-------|-------|
| Playlist | `https://www.youtube.com/playlist?list=PLOwrTT3cFiA5Qo_k27soDPvyPo3Wr7T8S` |
| Mentor | `No soy liquidez` |
| Slug (auto) | `no-soy-liquidez` |
| Carpeta destino | `D:\obsidian\boveda MENTE\Mente\Mentores\no-soy-liquidez\` |
| Videos | **65** (64 episodios numerados + 1 sin numerar en la posición 51) |
| Modelo whisper | `small` (recomendado; `medium` si quieres más calidad; **NO** `tiny`) |

Cada comando se ejecuta desde la raíz del repo:
```powershell
cd D:\CODE\Estrategia2.0
```

---

## PASO 0 — Una sola vez, antes de empezar

```powershell
# Borrar el placeholder del smoke-test de la S029
Remove-Item -Recurse -Force "D:\obsidian\boveda MENTE\Mente\Mentores\nombre-mentor" -ErrorAction SilentlyContinue

# Verificar herramientas (deben imprimir versión, no error)
yt-dlp --version ; ffmpeg -version | Select-Object -First 1 ; python -c "import faster_whisper; print('faster-whisper OK')"
```

---

## PASO 1 — Bajar los videos UNO A UNO

Plantilla (todos los comandos siguen este patrón, solo cambia el `?v=<ID>`):
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=<ID>" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
```

Copia y ejecuta la línea del video que toque. **Marca el `[ ]` → `[x]` en la tabla del PASO 2 cuando termine cada uno.**

```powershell
# Pos 01 · Ep. 1  - Order Blocks
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=_Wz4gpZsTiQ" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 02 · Ep. 2  - Mitigation Block
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=OC_LXzhrm0w" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 03 · Ep. 3  - Breaker Block
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=OWzaehWN20c" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 04 · Ep. 4  - Fractality & Market Structure
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=xQTQTQ4MSHg" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 05 · Ep. 5  - FVG / SIBI / BISI
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=3qZTOqMSVoM" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 06 · Ep. 6  - Market Structure Shift (MSS)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=Ezjbj9KIYlc" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 07 · Ep. 7  - Vacuum Block
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=KUQ9JouIEdM" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 08 · Ep. 8  - Liquidity Run (BSL/SSL)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=DMozgpnevqg" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 09 · Ep. 9  - Rejection Block
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=52UMKO4PgC4" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 10 · Ep. 10 - EQL / EQH
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=0N-gbIIiMus" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 11 · Ep. 11 - OTE / Fibonacci
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=Ojk9ip3TN_I" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 12 · Ep. 12 - Power of 3
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=tF_jGug64EE" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 13 · Ep. 13 - Propulsion Block
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=GITshky548A" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 14 · Ep. 14 - SMT Divergencias
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=3fo16lNiykI" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 15 · Ep. 15 - Premium vs Discount
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=Ou2bYq2wciE" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 16 · Ep. 16 - IPDA y PD Arrays
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=XCy6faJb3Ts" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 17 · Ep. 17 - Volume Imbalance
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=TexNsNvAKx0" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 18 · Ep. 18 - Como se crean las velas
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=LE2CJtau4eA" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 19 · Ep. 19 - NWOG (New Week Opening Gap)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=ghKeNEhP4S8" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 20 · Ep. 20 - MSS avanzado
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=9F2bUpKkK9g" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 21 · Ep. 21 - IOFED
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=q1-YXOcmmB0" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 22 · Ep. 22 - IRL vs ERL
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=ZE66MkzjHBQ" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 23 · Ep. 23 - SIVI / BIVI
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=BT4zzd2I5h4" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 24 · Ep. 24 - Advanced Price Balancing
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=FLB14YG5kNs" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 25 · Ep. 25 - Stop Raid
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=paPvf9BUwKU" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 26 · Ep. 26 - IFVG
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=5efQTQAkuWY" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 27 · Ep. 28 - Immediate Rebalance (IR)   [OJO: la playlist trae 28 antes que 27]
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=vUU1YfOCAXY" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 28 · Ep. 27 - New York Lunch Macro
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=dt1KZs5avc0" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 29 · Ep. 29 - NY Midnight Open (NYMO)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=2U_dA1tZJrg" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 30 · Ep. 30 - Opening Range Gap
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=PQhuafulEh0" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 31 · Ep. 31 - ICT Entry Model 2022
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=SndeKeJ9sSU" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 32 · Ep. 32 - Turtle Soup
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=S2vr0otvs5I" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 33 · Ep. 33 - Low Hanging Fruit
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=BNmGRM4AXcU" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 34 · Ep. 34 - The Order Block
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=uZNU-ot7mQI" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 35 · Ep. 35 - Reclaimed Order Block
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=DLj9ssEaE4Y" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 36 · Ep. 36 - Standard Deviation
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=Ov1E2IetbF8" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 37 · Ep. 37 - Opening Range Macro (índices)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=6p9l2GL5REE" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 38 · Ep. 38 - NY Lunch Hour Macro
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=tWZYXZIyqt4" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 39 · Ep. 39 - Unicorn Model
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=P2kGX9w3fh4" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 40 · Ep. 40 - PDArray Matrix
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=9GSYi231I38" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 41 · Ep. 41 - MMXM (Market Maker Model)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=uNRcYc6c7MM" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 42 · Ep. 42 - NDOG (New Day Opening Gap)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=YDcZMMLclc0" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 43 · Ep. 43 - CISD
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=9RYSwxQJgfU" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 44 · Ep. 44 - Killzones and Profiles
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=6RRRLzONrvs" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 45 · Ep. 45 - Breakaway Gap (BAG)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=EqASKlYfqvw" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 46 · Ep. 46 - Balanced Price Range (BPR)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=yKhRC5QmvXk" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 47 · Ep. 47 - Fair Valuation
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=sHUst5u9xBo" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 48 · Ep. 48 - Liquidity Swap vs Run
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=3L0c3s8DWQ4" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 49 · Ep. 49 - Draw on Liquidity
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=vxwjTOlwTQU" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 50 · Ep. 50 - MSS vs MSB
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=LmSX8QXfn9Y" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 51 · (sin nº) - Displacement Phase
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=Ow5QL8iNFSQ" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 52 · Ep. 51 - Early Buyer & Early Seller
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=D_ErnWzxjWo" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 53 · Ep. 52 - Gray Pool Theory
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=7R7TG9f8LiI" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 54 · Ep. 53 - High Resistance Liquidity Run (HRLR)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=U-679mnionY" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 55 · Ep. 54 - Low Resistance Liquidity Run (LRLR)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=jwPBvv-aceo" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 56 · Ep. 55 - Dealing Range
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=bO6TICIQcxs" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 57 · Ep. 56 - RTH vs ETH
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=KVrIj-0RX9g" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 58 · Ep. 57 - Event Horizon
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=5ZRtJZmkdTs" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 59 · Ep. 58 - HRLR vs LRLR
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=eARzn3ajSI4" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 60 · Ep. 59 - NFP Week Protocol
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=JXvOOonvRiI" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 61 · Ep. 60 - IPR (Imbalanced Price Range)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=pOkGOmFPKF0" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 62 · Ep. 61 - True Fair Value Gap (T.FVG)
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=tN6quBccj8Y" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 63 · Ep. 62 - Price Delivery Continuum Theory
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=UULw4hf3IgI" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 64 · Ep. 63 - Silver Bullet V2
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=6eCbirwyte0" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
# Pos 65 · Ep. 64 - Inside Day
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "https://www.youtube.com/watch?v=3XcY9JFurq0" -SubFolder "Mentores\no-soy-liquidez" -Model small -Language es
```

---

## PASO 2 — Checklist (marca `[x]` lo que ya bajaste)

| Pos | Ep. | ID | Tema | OK |
|----:|----:|----|------|:--:|
| 01 | 1  | `_Wz4gpZsTiQ` | Order Blocks | [ ] |
| 02 | 2  | `OC_LXzhrm0w` | Mitigation Block | [ ] |
| 03 | 3  | `OWzaehWN20c` | Breaker Block | [ ] |
| 04 | 4  | `xQTQTQ4MSHg` | Fractality & Market Structure | [ ] |
| 05 | 5  | `3qZTOqMSVoM` | FVG / SIBI / BISI | [ ] |
| 06 | 6  | `Ezjbj9KIYlc` | Market Structure Shift | [ ] |
| 07 | 7  | `KUQ9JouIEdM` | Vacuum Block | [ ] |
| 08 | 8  | `DMozgpnevqg` | Liquidity Run (BSL/SSL) | [ ] |
| 09 | 9  | `52UMKO4PgC4` | Rejection Block | [ ] |
| 10 | 10 | `0N-gbIIiMus` | EQL / EQH | [ ] |
| 11 | 11 | `Ojk9ip3TN_I` | OTE / Fibonacci | [ ] |
| 12 | 12 | `tF_jGug64EE` | Power of 3 | [ ] |
| 13 | 13 | `GITshky548A` | Propulsion Block | [ ] |
| 14 | 14 | `3fo16lNiykI` | SMT Divergencias | [ ] |
| 15 | 15 | `Ou2bYq2wciE` | Premium vs Discount | [ ] |
| 16 | 16 | `XCy6faJb3Ts` | IPDA y PD Arrays | [ ] |
| 17 | 17 | `TexNsNvAKx0` | Volume Imbalance | [ ] |
| 18 | 18 | `LE2CJtau4eA` | Cómo se crean las velas | [ ] |
| 19 | 19 | `ghKeNEhP4S8` | NWOG | [ ] |
| 20 | 20 | `9F2bUpKkK9g` | MSS avanzado | [ ] |
| 21 | 21 | `q1-YXOcmmB0` | IOFED | [ ] |
| 22 | 22 | `ZE66MkzjHBQ` | IRL vs ERL | [ ] |
| 23 | 23 | `BT4zzd2I5h4` | SIVI / BIVI | [ ] |
| 24 | 24 | `FLB14YG5kNs` | Advanced Price Balancing | [ ] |
| 25 | 25 | `paPvf9BUwKU` | Stop Raid | [ ] |
| 26 | 26 | `5efQTQAkuWY` | IFVG | [ ] |
| 27 | 28 | `vUU1YfOCAXY` | Immediate Rebalance (IR) ⚠ orden invertido | [ ] |
| 28 | 27 | `dt1KZs5avc0` | New York Lunch Macro | [ ] |
| 29 | 29 | `2U_dA1tZJrg` | NY Midnight Open (NYMO) | [ ] |
| 30 | 30 | `PQhuafulEh0` | Opening Range Gap | [ ] |
| 31 | 31 | `SndeKeJ9sSU` | ICT Entry Model 2022 | [ ] |
| 32 | 32 | `S2vr0otvs5I` | Turtle Soup | [ ] |
| 33 | 33 | `BNmGRM4AXcU` | Low Hanging Fruit | [ ] |
| 34 | 34 | `uZNU-ot7mQI` | The Order Block | [ ] |
| 35 | 35 | `DLj9ssEaE4Y` | Reclaimed Order Block | [ ] |
| 36 | 36 | `Ov1E2IetbF8` | Standard Deviation | [ ] |
| 37 | 37 | `6p9l2GL5REE` | Opening Range Macro (índices) | [ ] |
| 38 | 38 | `tWZYXZIyqt4` | NY Lunch Hour Macro | [ ] |
| 39 | 39 | `P2kGX9w3fh4` | Unicorn Model | [ ] |
| 40 | 40 | `9GSYi231I38` | PDArray Matrix | [ ] |
| 41 | 41 | `uNRcYc6c7MM` | MMXM | [ ] |
| 42 | 42 | `YDcZMMLclc0` | NDOG | [ ] |
| 43 | 43 | `9RYSwxQJgfU` | CISD | [ ] |
| 44 | 44 | `6RRRLzONrvs` | Killzones and Profiles | [ ] |
| 45 | 45 | `EqASKlYfqvw` | Breakaway Gap (BAG) | [ ] |
| 46 | 46 | `yKhRC5QmvXk` | Balanced Price Range (BPR) | [ ] |
| 47 | 47 | `sHUst5u9xBo` | Fair Valuation | [ ] |
| 48 | 48 | `3L0c3s8DWQ4` | Liquidity Swap vs Run | [ ] |
| 49 | 49 | `vxwjTOlwTQU` | Draw on Liquidity | [ ] |
| 50 | 50 | `LmSX8QXfn9Y` | MSS vs MSB | [ ] |
| 51 | —  | `Ow5QL8iNFSQ` | Displacement Phase (sin nº) | [ ] |
| 52 | 51 | `D_ErnWzxjWo` | Early Buyer & Early Seller | [ ] |
| 53 | 52 | `7R7TG9f8LiI` | Gray Pool Theory | [ ] |
| 54 | 53 | `U-679mnionY` | High Resistance Liquidity Run | [ ] |
| 55 | 54 | `jwPBvv-aceo` | Low Resistance Liquidity Run | [ ] |
| 56 | 55 | `bO6TICIQcxs` | Dealing Range | [ ] |
| 57 | 56 | `KVrIj-0RX9g` | RTH vs ETH | [ ] |
| 58 | 57 | `5ZRtJZmkdTs` | Event Horizon | [ ] |
| 59 | 58 | `eARzn3ajSI4` | HRLR vs LRLR | [ ] |
| 60 | 59 | `JXvOOonvRiI` | NFP Week Protocol | [ ] |
| 61 | 60 | `pOkGOmFPKF0` | IPR | [ ] |
| 62 | 61 | `tN6quBccj8Y` | True Fair Value Gap | [ ] |
| 63 | 62 | `UULw4hf3IgI` | Price Delivery Continuum | [ ] |
| 64 | 63 | `6eCbirwyte0` | Silver Bullet V2 | [ ] |
| 65 | 64 | `3XcY9JFurq0` | Inside Day | [ ] |

---

## PASO 3 — Revisión por Claude (cuando recargues tokens)

Cuando vuelvas con tokens, pídeme: **"revisa la descarga del curso No soy liquidez"**. Yo:
1. Cuento cuántos `.md` hay en `D:\obsidian\boveda MENTE\Mente\Mentores\no-soy-liquidez\` (debe haber **65** + `Index.md`).
2. Re-listo la playlist y comparo los 65 IDs esperados contra lo presente → te digo **cuáles faltan** (por ID y posición de esta tabla).
3. Reviso que las transcripciones no estén vacías ni truncadas y que tengan timestamps `[M:SS]`.
4. Marco esta checklist y te dejo la lista exacta de comandos a re-ejecutar para los faltantes.

Comandos de auto-chequeo rápido que puedes correr tú mismo:
```powershell
# ¿Cuántos .md llevo? (excluye Index.md)
(Get-ChildItem "D:\obsidian\boveda MENTE\Mente\Mentores\no-soy-liquidez\*.md" | Where-Object Name -ne 'Index.md').Count

# Listar transcripciones con su tamaño (las muy pequeñas = posible fallo)
Get-ChildItem "D:\obsidian\boveda MENTE\Mente\Mentores\no-soy-liquidez\*.md" | Sort-Object Length | Select-Object Name, @{n='KB';e={[math]::Round($_.Length/1KB,1)}}
```

---

## Notas

- ⚠️ Re-ejecutar un video que ya bajaste **lo reprocesa** (el script no salta existentes). Por eso la checklist: baja solo los `[ ]`.
- Cada video de ~30-60 min tarda ~10-20 min de transcripción en GPU. Es normal.
- Si un comando falla, anótalo y sigue con el siguiente; lo reintentas después.
- **Fase 2 (análisis con LLM)** va DESPUÉS de tener las transcripciones, y ahora puede usar **Gemini** (proveedor `google` en Hermes, `gemini-2.5-flash`, free tier):
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts\hermes-analyze-mentor.ps1 -Mentor "No soy liquidez" -Model gemini-2.5-flash
  ```

# Sesion-094 (2026-07-04)

## Objetivo
Continuar el punto 2 del gate del rediseño §7 (definido en S093): **pasada TV de casos EURUSD** para poblar los placeholders `[Extracción TV]` de las fichas §7.2, y **arrancar la Fase A** (pasos A-1…A-7 en `SMC-Visual.pine`, Visual-only, sin tocar CORE). Bajo gate [[sprint16-gate-reglas-antes-de-codigo]].

## Decisiones del usuario
1. **Ancla de la pasada = JULIO VIVO** (opción 1 recomendada). Nada por replay; se buscan casos usando el histórico disponible en TV.
2. **Modo lote:** extraer todas las familias con sus casos → integrar todo (A-1…A-7) → **luego** revisar familia por familia (apagando el resto, después todo encendido).

## Completado

### Tarea 1: Pasada TV (contexto julio vivo)
Chart OANDA:EURUSD H1, indicador `Hcihce` "SMC Engine — Visual". Contexto base capturado:
- Precio **1.14376** · **ATR14 H1 = 0.00085** → tolConf (0.25×ATR) = 0.000213 · tolPos (0.5×ATR) = 0.000425
- Dealing range vigente **[1.13618, 1.16221]**, EQ 1.14919, **Discount 29%**; bias H1 alcista / dom.(50) bajista; EMAs ⬆⬆⬆
- Grid: Premium 1.16221 / UQ 1.15570 / EQ 1.14919 / LQ 1.14269 / Discount 1.13618
- D1: Premium 1.20831 / Discount 1.13246 · **GIRO vigente = MSS 1.13827 · 01-07 12:00**
- Datos M5/H1/D1 vía panel T14 (nearest por familia por TF) + textos del grid

**Commit `38e56ce`** (docs(reglas), CORE intacto). Fichas actualizadas en `docs/reglas-smc-ict.md`:
- **§7.0.1 posRole:** GIRO+ORIGEN (→ORIGEN gana) MSS 1.13827·01-07 / ORIGEN puro OB D1 [1.15726,1.16221] / INTERNO BOS M5 1.14380·03-07. Verif. fina posLookfwd=20/tolPos pendiente en A-2.
- **§7.0.2 confDegree:** 2 clusters ≥2 — #1 OB M5 [1.14380,1.14406] + Pool 1.14408 BSL (dif 0.00002); #2 OB D1 [1.15726,1.16221] + FVG D1 [1.15283,1.15748] (premium). Contraejemplo =1: OB H1 [1.13740,1.13794] (ninguna otra familia contada en tol).
- **§7.0.3 depthBand:** mapa completo bandas 1/2/3 arriba (OB M5, FVG M5, FVG D1, OB D1 premium) y abajo (FVG H1, Pool H1, BOS H1, OB H1); bandas 4/5 proxy D1.
- **§7.2.2 (3 giros):** MSS 1.13827 (inferior) / premium ~1.16221 (superior) / CHoCH 1.14119·02-07 (intermedio).
- **§7.2.28/29/30 P/D:** grid refrescado a valores actuales (LQ 1.14269 / EQ 1.14919 / UQ 1.15570; eighth 1/8 ≈ 1.13943; junio archivado).

**Pendiente pasada:** casos precisos de **Flip (§7.2.7)** y **Mitigation Block (§7.2.11)** — placeholders "antes de A-5". Las herramientas TV no exponen sus niveles con precisión → se cierran al llegar a A-5.

**Límite de herramienta documentado:** `data_get_pine_labels` topa en 50 de 455 labels y redondea el precio a 2 decimales → inservible para enumerar múltiples zonas con precisión. Fuentes precisas: panel T14 (nearest por familia por TF) + textos del grid.

### Tarea 2: Fase A — paso A-1
**Commit `ca91777`** (feat(pine-visual), Visual-only aditivo). En `SMC-Visual.pine`:
- Input **`i_profundidad`** (`input.int(3, minval=3, maxval=5, GRP_DENS)`) — alcance de bandas de proyección (3 = rango vigente; 4/5 = rangos previos).
- Función pura **`f_depthBand(level, px)`** — banda {1..3} del retroceso de un nivel en el dealing range vigente (`chartState.pdHigh/pdLow`), cortes CONGELADOS 0.33/0.66/1.0 (ADR-002); devuelve 0 si el nivel cae fuera del rango vigente (territorio bandas 4/5, `[impl B-4]`). Sin arrays → RE10045-safe.
- **AÚN NO CABLEADA** (la consumen A-4/B-7) → sin cambio visual todavía; puramente aditiva (mismo patrón que el `strength` del Paso 1).

**Verificación:** `pine_check.py` server-side → **CLEAN_0_0**. `check-core-sync.ps1` → CORE idéntico, 1700 líneas, SHA `5510361166844bd5`.

## Pendiente (próxima sesión S095)
Continuar Fase A pasos **A-2…A-7** en `SMC-Visual.pine` (Visual, sin tocar CORE):
- **A-2** `f_posRole(top,bot,barIdx)` [GIRO/ORIGEN/INTERNO] + verificar posLookfwd=20/tolPos con MSS 1.13827
- **A-3** `f_confDegree(level)` [conteo de familias en ±0.25×ATR]
- **A-4** `f_renderScoreV2` + selección OB/FVG por banda (40 escalares int, sustituye `f_renderScore` en anclas §2.3)
- **A-5** Breaker + IDM + promoción `confDegree≥2` (+ cerrar casos Flip §7.2.7 y Mitigation Block §7.2.11)
- **A-6** guardián de draws (inmunidad al recorte top-N/desalojo/MTF) + reserva desalojo §6.5
- **A-7** estructura/EQ re-llaveados + bandas 4/5 → **tras A-7, cierra la parte visual → FIRMA F1-GATE**

Luego revisión usuario familia por familia (apagando el resto, luego todo encendido).

## Notas
- Sin gate de fase completado (F1-GATE sigue **SIN FIRMAR**, espera A-7).
- Sin ADR nuevo (A-1 bajo ADR-002 congelados / ADR-014 frontera CORE/Visual vigentes).
- GOTCHAs herramienta TV: `chart_manage_indicator` action=remove requiere `entity_id`; `indicator_set_inputs` usa `entity_id` + clave `in_123` para Densidad; densidad "Estudio" revela estudio pero dispara desalojo (121 recortadas).

Ver [[Sesion-093]] · [[fork-rediseno-proyeccion-s7]] · [[re10045-arrays-y-agent-browser]].

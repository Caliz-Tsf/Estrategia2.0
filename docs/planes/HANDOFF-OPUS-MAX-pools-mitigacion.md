# Plan / Handoff a Opus Max — Ciclo de vida (mitigación) de Pools + revisión de mitigación para los conceptos restantes

> Sesión S027 · Fase 1 · Sprint 1.3 · rama `pine/sistema-completo`. Documento de DISEÑO para que **Opus Max** desarrolle el esqueleto de implementación. NO ejecutar nada con esta sesión (decisión del usuario: dejar la nota para Opus Max).

## Context (por qué)
- **T09 (Pools BSL/SSL) ya está construido, compila 0/0 los 3 y core-sync OK** (503 líneas, SHA `2949a931757b9900`). `f_buildPools` clusteriza EQH/EQL + swings no barridos → `SMC_pools`. Pendiente de validación ≥90 + commit.
- **Problema detectado por el usuario (correcto):** el gráfico se satura de líneas BSL/SSL en todos los niveles. Causa raíz = **falta de ciclo de vida**: T09 solo *construye* (el campo `SMC_Pool.swept` siempre queda en `false`) y además **reconstruye el set desde cero cada vela** desde todo el histórico → aunque se marcara uno como tomado, reaparecería. Se dibujan TODOS, incluidos los que el precio ya cruzó hace semanas.
- **Aclaración de modelo SMC (confirmada con el usuario):** BSL = liquidez ENCIMA de los máximos; al barrerla (sweep + cierre de vuelta) → **VENDER** (reversión baja). SSL = liquidez DEBAJO de los mínimos; al barrerla → **COMPRAR**. La señal es el **barrido**, no "llegar".
- **"Colores mezclados arriba y abajo" NO es un bug aparte** — es el mismo síntoma. Un BSL solo es imán mientras esté por encima del precio; si el precio lo dejó abajo, ya fue tomado. **Con mitigación, los tomados desaparecen y los colores se segregan solos** (BSL vivos arriba del precio, SSL vivos abajo).
- Respaldo en reglas/referencia: `docs/reglas-smc-ict.md` §3.1 *"solo los niveles no barridos son imanes"* y §3.2 (sweep pone `pool.swept := true`). LuxAlgo (`pine/reference/LuxAlgo-SMC-base.pine`) trackea un flag `crossed` por nivel (campo `pivot.crossed`, :217-223) — mismo concepto.

## Decisión del usuario
- Implementar la **Opción A recomendada = Mitigación completa (pools persistentes con ciclo de vida)**.
- **Display = Propuesta B** ("marcar el barrido"): los imanes vivos quedan como línea; al tomarse un pool, dibujar un marcador (✗ + etiqueta `Sweep ↑/↓`) en la barra del barrido como historial, y terminar la línea del pool ahí. El usuario quiere "ver cuándo sucedió o está sucediendo", no que desaparezca en silencio.
- Esta nota la desarrolla **Opus Max** (esqueleto de implementación), e incluye la revisión de mitigación de TODOS los conceptos restantes (abajo) para sentar el patrón de una vez.

## Diseño objetivo (a esqueletizar por Opus Max)

### 1. Pools persistentes con ciclo de vida (refactor de T09)
- **Cambiar `SMC_pools` de "rebuild stateless cada vela" → estado PERSISTENTE.** El rebuild-desde-cero es incompatible con recordar `swept`; es el cambio de fondo.
- **Creación/merge:** al confirmarse un nuevo EQH/EQL (o swing relevante), crear un pool nuevo o hacer *merge* en un pool **vivo** cercano dentro de `poolTol×ATR` (sube `touches`, recalcula `level` promedio). Reutilizar la lógica de clustering de `f_buildPools` pero aplicada de forma incremental (un candidato contra el set vivo), en vez de reconstruir todo.
- **Marcar tomado (mitigación):** cada `barstate.isconfirmed`, para cada pool vivo: BSL tomado si `high >= level`; SSL tomado si `low <= level` → `swept := true` + guardar `sweptBarTime`/`sweptBarIdx`. Helper PURO `f_markPoolsSwept(pools, high, low)` para paridad MQL5 (ADR-002).
- **Dibujo (Propuesta B):** dibujar como línea solo los pools `swept == false` (imanes vivos), de `barTime` → barra actual. Al pasar a `swept == true`: dibujar marcador `✗` + etiqueta `Sweep ↓` (BSL, rojo) / `Sweep ↑` (SSL, verde) anclado en `sweptBarTime`, y terminar la línea del pool ahí (no extender a la derecha). Opcional: stub tenue (ghost) unas velas y luego quitarlo.
- **Relación con T10 (Sweeps):** el "tomado" (cruce simple del nivel) es la **mitigación del pool**. T10 añade encima la **clasificación del sweep-trampa** (mecha que perfora + cierre de vuelta = evento DIRECCIONAL con peso para el scoring, §3.2). El marcador visual de la Propuesta B **es** el evento de T10 → conviene que Opus Max diseñe pool-lifecycle (T09) y sweep-event (T10) juntos para no duplicar.
- **Nota de paridad/golden tests:** el merge persistente reemplaza la pureza del rebuild. Documentar el cambio para los golden tests MQL5 (el EA opera incremental/vivo, así que el modelo persistente es de hecho más fiel al EA — ventaja).
- **Ruido residual:** aun con mitigación, los defaults `poolTol=0.1`/`minTouches=2` generan muchos pools. Eso es **calibración Fase 3** (congelado, ADR-002). La mitigación es la palanca grande disponible ahora; no tocar umbrales.

### 2. Revisión: qué conceptos restantes necesitan mitigación / ciclo de vida
> Objetivo: que Opus Max esqueletice el patrón de "consumo/invalidación" una sola vez y lo reutilice.

| Concepto | Tarea | ¿Necesita ciclo de vida? | Tipo / mecanismo |
|---|---|---|---|
| **Pools BSL/SSL** | T09 | **SÍ — nuevo** | Nivel consumido al ser barrido (`swept`). Este plan. |
| Sweep / Grab | T10 | No (es el EVENTO que consume) | Evento puntual; marca `pool.swept`/`swing.swept`. |
| Kill Zones | T11 | No | Ventana temporal (fondo), no se consume. |
| MSS | T12 | No | Evento puntual (marca histórica). |
| Displacement | T16 | No | Evento puntual. |
| **IDM (inducement)** | T17 | **SÍ** | Nivel de liquidez interna que se barre ANTES del objetivo → consumido (`swept`), igual patrón que pools. |
| Judas | T18 | No | Evento puntual. |
| **Breaker** | T19 | **SÍ (ya existe máquina)** | Zona: reutiliza `f_updateZoneMitigation` (4 estados) del OB; nace de un OB invalidado. |
| Rejection | T20 | No | Evento puntual (marca en la vela). |
| **Flip** | T21 | **SÍ** | Nivel con cambio de rol; se invalida si se vuelve a romper limpio → lifecycle de nivel. |
| **OTE / Golden Pocket** | T22 | **SÍ** | Zona fib que caduca: al alcanzar el objetivo del impulso o invalidarse el swing origen. Reutilizar máquina de zona o expiración por evento. |
| EMAs | T23 | No | Dinámico (siempre vivo). |
| False Breakout | T24 | No | Evento puntual. |
| Impulsive/Corrective | T25 | No | Clasificación de estado. |
| **Mitigation block** | (tier2) | **SÍ (ya existe máquina)** | Zona: reutiliza `f_updateZoneMitigation`. |
| OB | T05 | Ya hecho | `f_updateZoneMitigation` (ACTIVE/PARTIAL/MITIGATED/INVALID). |
| FVG | T06 | Ya hecho | Misma máquina. |

**Patrones a esqueletizar (Opus Max):**
- **(P1) Nivel-consumido-por-barrido** (Pools, IDM): flag `swept` + `sweptBarTime`, helper puro `f_mark*Swept`, dibujo vivo + marcador al consumirse.
- **(P2) Zona con máquina de 4 estados** (Breaker, Mitigation block, OTE/GP): reutilizar `SMC_Zone` + `f_updateZoneMitigation`; OTE/GP además expira por alcance de objetivo.
- **(P3) Nivel-rol-invalidable** (Flip): nivel que se respeta hasta re-ruptura limpia.
- **(P4) Eventos puntuales** (Sweep, Grab, MSS, Judas, Displacement, Rejection, False Breakout): NO mitigan, pero necesitan **límite de presentación** ("mostrar solo últimas N velas / Present mode", PINE-PLAN §5) para no saturar — diseñar un patrón de cuota/Present común.

## Archivos a tocar (cuando se implemente)
- `pine/SMC-Visual.pine` y `pine/SMC-Strategy.pine` — sección `// === LIBRARY CORE ===` byte-idéntica (nuevos helpers puros `f_markPoolsSwept`, merge) + wiring de detección + dibujo (Propuesta B) solo en Visual. Tras tocar el CORE → `scripts/check-core-sync.ps1`.
- `pine/SMC-Library.pine` — versión `export` equivalente de los helpers nuevos.
- `docs/reglas-smc-ict.md` §3.1/§3.2 — referencia (ya cubre el concepto; no requiere cambio salvo precisar el ciclo de vida si se desea).
- Posible ADR nuevo: "Pools persistentes con ciclo de vida (reemplaza rebuild stateless de T09)".

## Estado de T09 (build) y decisión pendiente
- El **build de T09 funciona** (pools generan, niveles/touches correctos contra §3.1) y compila 0/0. 
- Bug ya corregido en esta sesión: el volcado con `f_pushPool` (FIFO a MAX_POOLS=50) descartaba los BSL (construidos antes que los SSL) → cambiado a volcado completo. (Esto queda **superado** por el refactor persistente, pero el build actual es coherente.)
- **Decisión abierta para el usuario/Opus Max:** ¿commitear el build de T09 primero (validación ≥90 de niveles) y luego Opus Max hace el refactor persistente como T09b/T10, o esperar y commitear todo junto? Recomendación: commitear el build (concepto verificado) y abordar el ciclo de vida como tarea siguiente unificada con T10.

## Verificación (cuando se implemente)
1. `scripts/check-core-sync.ps1` → CORE idéntico Visual/Strategy.
2. `pine_set_source` + `pine_smart_compile` + `pine_get_errors` los 3 → 0 errores / 0 warnings.
3. En EURUSD H1 vía TV MCP: confirmar que (a) tras el cruce de precio, el pool BSL/SSL **desaparece** como imán y queda su **marcador de barrido** (Propuesta B); (b) los imanes vivos quedan BSL arriba del precio / SSL abajo (colores segregados); (c) los 3 casos §3.1 (BSL ~1.16615, SSL ~1.15948, SSL ~1.15274) siguen apareciendo y luego se marcan barridos donde corresponde.
4. `smc-validator-agent` ≥90.

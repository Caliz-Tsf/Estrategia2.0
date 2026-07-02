# Sesion-085 (2026-07-02)
> Eje 2 "Fuerza" — completar **Paso 4 (resto)** del ESQUELETO-FABLE §11.2. Fase 1 · rama `pine/sistema-completo`. 4 commits Pine, todos compilan 0/0, CORE intacto, verificados en vivo OANDA:EURUSD H1.

## Contexto de entrada
S084 dejó el **Paso 4 base** (`i_densidad` + `f_visualLevel` + filtro por strength en 10 familias de ZONA, con `isAnchor=false`). Pendiente para completar Paso 4: anclas §2.3, `f_visualLevel` v2 (piso MTF §7.1), matriz §8.2, y extender el filtro a marcadores/líneas. CORE 1700 líneas SHA `5510361166844bd5` (Paso 2, intacto esta sesión — todo el trabajo es Visual, fuera del CORE).

## Completado en S085 (4 commits)

### 1. Anclas §2.3 (commit `9cc69d4`)
- `f_renderScore(strength, distAtr)` §2.5 (CONGELADO): `strength × (1 − min(distAtr/6, 0.8))` — llave de orden de anclas y del futuro top-N.
- Precomputo (guardado `barstate.islast`) de `anchorHiIdx`/`anchorLoIdx` = índices en `SMC_zones` de la zona activa más cercana por lado (mayor `score_render`), sobre OB/FVG/Breaker no mitigados/invalidados.
- Cableado `isAnchor = (i == anchorHiIdx or i == anchorLoIdx)` en los 3 loops OB/FVG/Breaker → salta `densMin`, fuerza Primario (§2.2 paso 2). Las anclas no consumen top-N.

### 2. f_visualLevel v2 (piso MTF) + matriz §8.2 (commit `c2410ca`)
- `f_visualLevel(sLevel, isAnchor, mtfFloor)`: `isAnchor ? 2 : max(sLevel, mtfFloor)`. Piso Secundario para heredadas MTF Primarias (§7.1-2; nunca caen a Terciaria). `f_densOK` nativo delega con `mtfFloor=0` → sin churn en los 12 callers. Pine v6 no soporta parámetros por defecto (por eso el wrapper).
- Matriz §8.2: `modeIdx` (0<1<2) + `f_famOK(famMinMode)` curan por familia ENCIMA del filtro strength. Zonas: BPR/Mitigation/Vacuum → Estudio+ (`FAM_EST`); VI/IPR → Todo (`FAM_TODO`); OB/Breaker/IFVG/FVG/OTE → Operación. Default "Todo" no-regresivo.

### 3. Extender filtro a marcadores/líneas (commit `655b323`)
- Swings HH/HL/LH/LL y estructura interna → Estudio+ (§F1). Pools barridos → Estudio+ (§F8). EMAs y BOS/CHoCH swing se dejan en Operación (§F2/§F1).

### 4. Matriz §8.2 en marcadores de contexto/liquidez (commit `a733a6b`)
- Gateados a Estudio+ (`f_famOK FAM_EST`): IDM/Judas (§F8), IR (§F4), CISD (§F1), Rejections/Stack-EMA/tramos-IMP-CORR (§F2). Es lo que hizo que Operación quedara realmente limpio.

## Verificación viva (OANDA:EURUSD H1, indicador `SMC Engine — Visual` id `JIXYBm`, input densidad = `in_123`)
- **Cajas: Todo = 9 → Operación = 2** (declutter real; las 2 restantes = heredadas D1:OB/D1:FVG del bloque MTF, que no pasa por `f_densOK`).
- **Operación limpio de marcadores**: desapareció el ruido de IR/CORR/Stack/Judas/Rejections/IDM; permanece estructura BOS/CHoCH/MSS + EMAs + marco grid+P/D + zonas de decisión (coherente §8.2).
- **Default "Todo" no-regresivo** (baseline 9 cajas intacto).
- Compila 0/0 los 3 (pine_check.py server-side), core-sync OK, CORE `5510361166844bd5` SIN cambios.

**GOTCHA reconfirmado:** cambiar el *default* de un `input.string` en el código NO altera el valor de la instancia ya en el chart (TV conserva el valor guardado). Para probar modos usar `indicator_set_inputs` sobre el input real (`in_123`), no reinyectar con otro default. `pine_inject.py` clickea "Pine Save" (recompila y actualiza el study; los valores de input persisten).

## Estado del plan §11.2 (esqueleto Fable)
- ✅ Pasos 0-3
- ✅ **Paso 4** — i_densidad + f_visualLevel v2 (anclas §2.3 + piso MTF §7.1) + matriz §8.2 + filtro a marcadores. **Funcionalmente completo y verificado.**
- ⬜ **Sub-ítem diferido a Paso 6:** `f_strongestN` (top-N por familia §2.5) — comparte maquinaria collect→sort→cap con el presupuesto global §6.5 y reestructura los mismos loops que el Paso 5 reordena; hacerlo suelto obliga a tocar cada loop dos veces. Decisión usuario S085: plegarlo al Paso 6.
- ⬜ Pasos 5-9 (Paso 5 = reorden a capas L0→L4 + KZ→ribbon + grid sin fill; el sombreado KZ full-height sigue visible en Operación = Paso 5, fuera de scope Paso 4).

## Arrastre pendiente (independiente del Eje 2)
- ⚠️ Re-validación FORMAL `smc-validator-agent` de T43 alcance completo (P1 stale→P2, FVG cerca de gap→P3). Arrastrado desde S082.

## Commits sesión
1. `9cc69d4` — anclas §2.3 (isAnchor en OB/FVG/Breaker)
2. `c2410ca` — f_visualLevel v2 (piso MTF) + matriz modo×familia §8.2
3. `655b323` — extender matriz §8.2 a marcadores/líneas
4. `a733a6b` — matriz §8.2 en marcadores de contexto/liquidez

## Decisiones sesión (DOC-01)
- Anclas eligibles solo OB/FVG/Breaker (§2.3); tie-break por `score_render`, a igualdad gana el primero (≈frescura por orden de inserción).
- Números CONGELADOS hasta Fase 3 (ADR-002): `score_render` f(cercanía) `1−min(distAtr/6,0.8)`; umbrales strength 0.33/0.66 (ya existentes).
- `f_strongestN` (top-N) se pliega al Paso 6, no se hace suelto (evita doble edición de loops).
- Ningún ADR nuevo; ADR-014 (S083) cubre la arquitectura de strength.

## Siguiente sesión (S086)
- **Paso 5:** reordenar bloques de dibujo a capas L0→L4 (§3) + KZ full-height → ribbon (§6.3, resuelve solape grid vs KZ) + grid sin fill de área.
- Luego **Paso 6:** consolidación de labels (§6.2) + alternancia + presupuesto global (§6.5) **+ `f_strongestN` top-N** (plegado aquí).
- Sin gate de fase completado en S085; sin ADRs pendientes.

Ver [[Sesion-084]] (Pasos 2-3-4base) · [[ESQUELETO-FABLE-sistema-visual.md]] (plan Eje 2).

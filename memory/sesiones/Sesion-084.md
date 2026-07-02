# Sesion-084 (2026-07-02)
> Eje 2 "Fuerza" (último eje del gate visual F1) — Pasos 2, 3 y 4-base del ESQUELETO-FABLE §11.2. Fase 1 · rama `pine/sistema-completo`. 3 commits Pine, todos compilan 0/0, verificados en vivo OANDA:EURUSD H1.

## Contexto de entrada
Sesion-083 completó Pasos 0 (ADR-014) + 1 (campo `strength` en UDTs). CORE creció 1647→1651 líneas SHA `0ae1f9de2ea3cd23` → `91b11f3759087c4a` (byte-idéntico en Visual/Strategy + export Library). Plan S083 pedía **Paso 2 (motor de fuerza en CORE)** como siguiente hito.

## Completado en S084

### 1. PASO 2 — Motor de fuerza en el CORE (commit `0f1a485`)
**Tema:** 5 funciones puras nuevas en el `=== LIBRARY CORE ===` (byte-idéntico Visual/Strategy, export Library).

**Funciones CORE nuevas:**
- `f_zoneStrength(z: SMC_Zone, curPrice, atr14, biasDir) → strength (float 0.0-10.0)`
  - Calcula fuerza zona según: tipo (`kind`), distancia a precio, validez mitigable.
  - Pesos fuente: HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md §5.2 (congelados Fase 3).
- `f_eventStrength(e: SMC_Event, rangeAtr, bodyPct, hadSweep, biasDir) → strength (0.0-10.0)`
  - Entrada/salida por: rango (ATR), cuerpo %, sweep previo, bias actual.
- `f_swingStrength(sw: SMC_Swing, biasDir) → strength (0.0-10.0)`
  - Estructura: cuerpo vs mecha, longitud, contexto direccional.
- `f_poolStrength(p: SMC_Pool, curPrice, atr14) → strength (0.0-10.0)`
  - Liquidez: distancia, densidad hits, edad.
- `f_strengthLevel(strength: float) → 0 | 1 | 2`
  - Quantiza 0.0-10.0 → Terciario(0) / Secundario(1) / Primario(2) (§5.3 esqueleto).

**Integración en sitios de creación (42 call sites principales):**
- `f_pushZone()`, `f_pushEvent()`, `f_pushSwing()` amplían firma: llaman a la función de fuerza y setean `obj.strength` al entrar en el array maestro.
- Pools dinámicos: fuerza recalculada al cierre vela en `f_upsertPool()` + `f_prunePools()` (no en único sitio).
- **Insumos por-vela** (`evRangeAtr`, `evBodyPct`, `sweptRecently`) + `chartState` reubicado **antes de los swings** para alimentar fuerza con bias vigente.
- Runtime verificado: panel T14 intacto, sin regresión visual.

**Compilación & core-sync:**
- ✅ **Compila 0/0** los 3 archivos (SMC-Library, SMC-Visual, SMC-Strategy).
- ✅ **core-sync OK** — byte-idéntico visual/strategy confirmado.
- ✅ CORE creció 1651→**1700 líneas** SHA `91b11f3759087c4a` → **`5510361166844bd5`** (new SHA con 5 funciones).

### 2. PASO 3 — Paleta centralizada COL_* + hue por familia (commit `042e1e2`)
**Tema:** 100% en Visual (fuera CORE). Colapsa 165 colores dispersos → paleta canónica §5.2 por familia.

**Estructura nueva:**
- Bloque único de constantes `COL_*` (colores base) + matriz de render (transp 82/92, grosores) antes de `=== DIBUJO ===`.
- **Hue por familia:**
  - **AZUL** (16 tonos) — OB, Breaker, MB, Vacuum
  - **NARANJA** (16 tonos) — FVG, IFVG, BPR, IR, VI, IPR, opening-gaps
  - **VIOLETA** (16 tonos) — IDM, Judas, EQH-EQL, rejection
  - **ÁMBAR** (8 tonos) — OTE, GP
  - **GRIS-AZUL** — grid, P/D-eq
  - **GRIS** — ghosts, mitigado, tools
  - **Verde/Rosa/Índigo por sesión** — KZ (Kill Zones)
- **Preserva VERDE/ROJO direccional** (explícita del usuario):
  - Estructura (BOS/CHoCH/MSS), swings, CISD/legs/flip/FB/stack/emaBounce
  - Pools BSL/SSL, sweeps, P/D Premium/Discount
  - Lenguaje nativo del trader intacto.

**Comentarios por-bloque** reconciliados con la paleta. 

**Pendiente (diferido, no bloquea):**
- Procedencia MTF (§7.2 = Paso 7)
- Panel T14 (§9 = Paso 8)

**Verificación:** Recolor coherente, direccional intacto, Ejes 0/1/3 sin regresión.

### 3. PASO 4 (BASE) — i_densidad + f_visualLevel + filtro por strength (commit `86e7092`)
**Tema:** Fundación del Paso 4. 100% en Visual (fuera CORE). Aquí por fin se **CONSUME** el strength del Paso 2.

**Input maestro nuevo:**
- `i_densidad` (grupo GRP_DENS): 
  - "Operación" = solo Primario (mayor fuerza)
  - "Estudio" = Primario + Secundario
  - "Todo" = sin ocultar nada (default, no-regresivo)

**Funciones de filtro (Visual):**
- `f_visualLevel(sLevel, isAnchor) → 0 | 1 | 2`
  - Terciario(0) / Secundario(1) / Primario(2)
  - Ancla estructural → fuerza Primario (§2.3)
- `f_densOK(strength, isAnchor) = f_visualLevel(f_strengthLevel(strength), isAnchor) >= densMin`
  - Devuelve true si pasa el filtro de densidad del modo actual.

**Cableado en 10 familias de ZONA (OB/Breaker/IFVG/BPR/MB/Vacuum/OTE/FVG/VI/IPR):**
- Cada caja se dibuja **solo si** `f_densOK(box.strength, box.isAnchor)` = true.
- Resultado real: con modo "Operación" cajas 9→2 (solo strength alta), confirma que:
  - Strength del Paso 2 está poblado ✅
  - Strength varía entre zonas ✅
  - Filtro declutteriza realmente ✅

**Umbrales:** CONGELADOS hasta Fase 3 (ADR-002).

**Verificado en vivo:** OANDA:EURUSD H1, modo "Operación" activa → declutter observable.

**Pendiente (completar Paso 4, siguiente sesión):**
- Anclas estructurales §2.3 (`isAnchor` hoy=false)
- Top-N por score `f_strongestN` §2.5
- Pisos MTF §7.1
- Matriz fina por-familia §8.2
- Extender filtro a marcadores/líneas (estructura, liquidez, EMAs)

## Estado del plan §11.2 (esqueleto Fable)
- ✅ Paso 0 (ADR-014 + spike)
- ✅ Paso 1 (campo strength UDTs)
- ✅ Paso 2 (motor de fuerza CORE + integración)
- ✅ Paso 3 (paleta COL_* + hue por familia)
- ✅ Paso 4 (base) — i_densidad + f_visualLevel + filtro
- ⬜ Paso 4 (resto) — anclas §2.3 + `f_strongestN` §2.5 + pisos MTF §7.1 + matriz §8.2 + extender filtro
- ⬜ Pasos 5-9

## Arrastre pendiente (independiente del Eje 2)
- ⚠️ **Re-validación FORMAL `smc-validator-agent` de T43 alcance completo** (P1 stale→P2, FVG cerca de gap→P3). Viene arrastrado desde S082. Registrar en `docs/sprint-runs/validaciones.md`.

## Commits sesión
1. `0f1a485` — `feat(pine-core): F1-Eje2 Paso 2 — motor de fuerza (strength) en el CORE`
2. `042e1e2` — `feat(pine-visual): F1-Eje2 Paso 3 — paleta centralizada COL_* + hue por familia`
3. `86e7092` — `feat(pine-visual): F1-Eje2 Paso 4 (base) — i_densidad + f_visualLevel + filtro por strength`

## Decisiones sesión (DOC-01)
- Paso 2 motor de fuerza: pesos CONGELADOS (HANDOFF §5.2) hasta Fase 3 (ADR-002 intacto).
- Paso 3 paleta: preserva lenguaje direccional nativo (verde/rojo estructura, swings, liquidez, P/D).
- Paso 4 input densidad: default "Todo" no-regresivo; modos activos verificados live (declutter real).
- ADRs: ningún ADR nuevo (ADR-014 S083 cubre arquitectura de strength; paleta/densidad = implementación esqueleto aprobado).

## Siguiente sesión (S085)
**Completar Paso 4 (resto) + Pasos 5-9:**
1. Anclas estructurales §2.3 — `isAnchor` mapeo en conceptos clave
2. Top-N por score `f_strongestN` §2.5 (función nueva Visual, no mutar `f_nearestN` validado S057)
3. Pisos MTF §7.1 — procedencia MTF en etiquetas
4. Matriz fina §8.2 — perfiles por-familia
5. Extender filtro a marcadores/líneas (BOS/CHoCH/EQH-EQL/FVG/OTE/Sweeps/liquidez/EMAs)
6. Pasos 5-9 como roadmap esqueleto (consolidación, ribbon, etc.)

No hay gate de fase completado en S084. No hay ADRs nuevos pendientes de escribir.

Ver [[Sesion-083]] (Pasos 0-1) · [[ESQUELETO-FABLE-sistema-visual.md]] (plan completo Eje 2).

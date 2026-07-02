# Sesion-083 (2026-07-02)
> Arranque del Eje 2 "Fuerza" / orden visual (esqueleto Fable). Paso 0 (de-risking) + Paso 1 (campo `strength` en UDTs del CORE). Fase 1 · rama `pine/sistema-completo`. 2 commits (1 docs + 1 Pine core).

## Contexto de entrada
Fable entregó `docs/planes/ESQUELETO-FABLE-sistema-visual.md` (S083, commit `95fd4d6`): el sistema visual definitivo que resuelve la problemática 502 líneas + 502 labels + solapes + 0 jerarquía. El usuario pidió (1) mapa de tareas hasta terminar Fase 4, y (2) lectura crítica del esqueleto antes de que Opus lo ejecute, y luego arrancar.

## Completado

### 1. Mapa de tareas hasta Fase 4 (respuesta al usuario)
Cierre Fase 1 (Eje 2 + firma gate) → Fase 2 (F2-T01..05, motor decisión) → Fase 3 (F3-T01..06, calibración IS/OOS + 30d paper) → gate duro Fable → Fase 4 (F4-T00..08, EA MQL5 + 60d demo + 30d live). ~29-47 sesiones + calendarios obligatorios (30+60+30 días).

### 2. Lectura crítica del esqueleto Fable
Verificado contra el Pine real: `GRP_*` (135 refs), `f_nearestN`/`f_nearestNPools`/`f_nearestNEvents` (15 refs) EXISTEN; motor strength es greenfield (`f_zoneStrength`/`f_visualLevel`/`i_densidad`/`COL_*` = 0 matches). El esqueleto conserva lo real, no inventa infraestructura. Veredicto: **sólido y ejecutable**, 6 observaciones (secuenciación/de-risking, no rediseño): (1) `strength` en CORE es decisión de arquitectura sin declarar → ADR; (2) perf de consolidación llega tarde (paso 9) → spike temprano; (3) no mutar `f_nearestN` validado S057 → variante nueva; (4) falta regresión Ejes 0/1/3 en paso 9; (5) colisión latente de hue violeta (5 conceptos); (6) ribbon KZ con fricción real en Pine. Decisión usuario (AskUserQuestion): **Paso 0 primero** (de-risking antes de tocar CORE).

### 3. PASO 0 — ADR-014 + spike (commit `0b1ffba`)
- **ADR-014** (`docs/adrs/ADR-014-strength-propiedad-de-deteccion-en-core.md`): `strength` es propiedad de DETECCIÓN → vive en el LIBRARY CORE byte-idéntico, NO en Visual. Razón: dos consumidores (jerarquía visual ahora + scoring F3, ya declarado en HANDOFF §5.3). Frontera exacta: `strength`/`f_zoneStrength`/`f_eventStrength`/`f_strengthLevel` = CORE; `f_visualLevel`/`COL_*`/`i_densidad`/consolidación/ribbon = Visual. Notas ancladas: usar `f_strongestN` nuevo (no mutar `f_nearestN`), verificar Ejes 0/1/3 en paso 9. No infla confluencias (P-05 intacto). Valores congelados Fase 3 (ADR-002).
- **Spike** (`docs/planes/SPIKE-S083-consolidacion-y-ribbon.md`): hallazgo base = todo el dibujo YA corre solo en `barstate.islast` (delete+rebuild, ~40 bloques) → NO se ejecuta x20k barras. **Consolidación de labels: NO es riesgo de perf**, es costo de refactor (unificar labels de ~40 bloques en un buffer pendiente + post-pass). **Ribbon KZ: factible** (hoy usa `bgcolor()` full-height = el colisionador con el grid; reemplazo = box delgado anclado a `ta.highest` en islast). Caps 500 actuales > presupuesto global 60/150/400 → no subir caps. **Ajuste al plan**: fusionar pasos 5+6 del §11.2 (reescriben los mismos 40 bloques). Ambos spikes VERDES → vía libre a tocar CORE.

### 4. PASO 1 — campo `strength` en 4 UDTs (commit `2fc7d9f`)
Añadido `float strength = 0.0` a `SMC_Zone`/`SMC_Event`/`SMC_Swing`/`SMC_Pool` en los 3 archivos (Visual+Strategy byte-idénticos, Library export). Puramente aditivo: default 0.0, nada lo computa aún (el motor es el Paso 2). Compila **0/0** los 3 (`pine_check.py` server-side). **core-sync OK**. CORE 1647→**1651 líneas**, SHA `0ae1f9de2ea3cd23` → **`91b11f3759087c4a`**.

## Estado del plan §11.2 (esqueleto Fable)
- ✅ Paso 0 (ADR-014 + spike) · ✅ Paso 1 (campo strength UDTs)
- ⬜ **Paso 2 (SIGUIENTE)**: `f_zoneStrength`/`f_eventStrength`/`f_strengthLevel` + cálculo en sitios de creación (CORE, byte-idéntico → core-sync + SHA). Pesos candidatos HANDOFF §5.2 (congelados). Es el cambio de CORE grande; con él el motor queda funcional.
- ⬜ Paso 3 (COL_* + matriz render) · Paso 4 (i_densidad + f_visualLevel + anclas + matriz §8.2) · Paso 5+6 fusionados (reorden L0→L4 + buffer labels + consolidación + ribbon) · Paso 7 (procedencia MTF + 3 pendientes diferidos) · Paso 8 (panel T14 Ocultos + glifos) · Paso 9 (verificación §10 + Ejes 0/1/2/3 → cierra gate visual F1).

## Commits
- `0b1ffba` — `docs(eje2): S083 Paso 0 — ADR-014 (strength al CORE) + spike consolidacion/ribbon`
- `2fc7d9f` — `feat(pine-core): F1-Eje2 Paso 1 — campo strength en UDTs (Zone/Event/Swing/Pool)`

## Siguiente sesión (S084)
Arrancar **Paso 2** (motor de fuerza en el CORE). Bajo ADR-014. Referencia: HANDOFF §5.2/§5.3 (funciones + pesos), ESQUELETO-FABLE §11.2. Recordar: `f_strongestN` variante nueva (no mutar `f_nearestN`) cuando se llegue al top-N (Paso 4), y regresión Ejes 0/1/3 en Paso 9.

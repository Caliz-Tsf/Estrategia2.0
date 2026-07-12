# Sesión 117 — 2026-07-11

**Rama:** `pine/sistema-completo` · **Fase:** 1 (F1-GATE BLOQUEADA) · **CORE:** SHA `d86bf37aacbd25cf` intacto (1952 líneas, core-sync OK ×3)
**Commit:** `fae1ced` feat(pine-visual) estructura de swings leg-based + dim-to-focus · **Sin tag** (F1-GATE sigue bloqueada).

## Objetivo
Continuar la auditoría visual D1 con "poblar la pierna hacia atrás". Derivó en un **rediseño completo de la estructura de swings** del Visual, iterando en vivo con el usuario hasta una versión robusta.

## Recorrido (enfoques probados y descartados)
1. **Retención por importancia + rol pegajoso** (`SMC_swingsV` FIFO + `SMC_swingRoleT`): fosilizaba el array con pivotes viejos → recientes se expulsaban. Descartado.
2. **Dos capas (macro len 50 + menor len 5):** producía **etiquetas dobles** (todo pivote mayor es también menor) + mezclaba escalas. Descartado.
3. **`ta.pivothigh/pivotlow`:** muy estrictos (extremo de 2·len+1 velas) y **sin alternancia** → huecos en caídas/subidas. **Causa raíz.**
4. **Filtro por amplitud ×ATR (ZigZag deviation) que ELIMINA swings:** borraba demasiado. El usuario prefiere **atenuar, no quitar**. Descartado como filtro; reusada la idea como jerarquía visual.

## Diseño final (commit `fae1ced`, todo Visual-only)
- **Detección leg-based** portada de LuxAlgo (`pine/reference/ L337-361`): máquina de estado que ALTERNA H-L-H-L, marca más reversiones, sin huecos ni dobles. Anti-repaint. Decoplada de `i_majorLen`/`structMajor`.
- **Capa única**, 4 tipos HH/HL/LH/LL, **color SMC por tendencia** (HH/HL verde, LH/LL rojo — el usuario confirmó que es correcto, no un bug).
- **Retención FIFO** `i_swingMaxKeep` (default 350) + dibujo al final (sobrevive buffer 500 labels).
- **Jerarquía dim-to-focus (rúbrica §3):** amplitud del tramo ÷ATR histórico → `sw.strength`; dominante `size.small`/transp25, menor `size.tiny`/transp65. No elimina, atenúa.
- **Inputs GRP_STRUCT** ajustables en vivo: `i_swingStructLen`, `i_swingMaxKeep`, `i_swingDomAtr`.
- ADR-019 reescrito al diseño final.

## Conceptos aclarados con el usuario
- **Color SMC por tendencia** (no por pico/valle): HH+HL alcista/verde, LH+LL bajista/rojo. Correcto, se mantiene.
- **Downtrend = LH+LL, uptrend = HH+HL** es la lectura correcta (no es que "todo abajo sea LL por error").
- **Clasificación relativa:** cada pivote vs el anterior del MISMO tipo; un HH local en una bajada = mini-CHoCH (correcto).
- **Impulso limpio = pocos swings** (una pierna); no se pueden inventar swings que no existen.

## GOTCHA crítico (perdió mucho tiempo)
TV **cachea el bytecode compilado**: tras inyectar código nuevo, "Añadir al gráfico" seguía aplicando el **compilado viejo** (datos idénticos byte a byte). **Solo se limpia reiniciando TV** (`tv_launch kill_existing`). Flujo fiable: inject → reiniciar TV si aplica viejo → eliminar Visual → click botón `title='Añadir al gráfico'` vía `ui_evaluate` (NO desde favoritos = versión guardada vieja). Límite free = 2 indicadores.

## Vista solo-pivots (inspección)
`indicator_set_inputs` apaga todos los `i_show*` menos `i_showSwings`; `indicator_toggle_visibility` oculta el Context. Recalcular `in_N` parseando el archivo cada vez que cambian inputs.

## Pendiente S118
1. **Verificar colisión de encoding** (rúbrica §2/§2bis): swings comparten familia teal/rojo con BOS/CHoCH, legs, flips, stack, CISD, SMT. Riesgo real = **swings vs BOS/CHoCH** (mismo hue, mismos pivotes). Encender estructura junto a swings; diferenciar por **nivel L1/L2/L3**, no por hue. (El usuario lo dejó explícitamente para S118.)
2. Calibrar defaults (`i_swingStructLen=20`, `i_swingMaxKeep=350`, `i_swingDomAtr=1.5`) viendo el chart.
3. Seguir la matriz de auditoría (otros conceptos D1 → H1/M5).

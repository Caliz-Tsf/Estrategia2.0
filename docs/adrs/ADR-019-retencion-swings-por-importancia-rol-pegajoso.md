# ADR-019 — Estructura visual de swings: capa única leg-based (LuxAlgo) + jerarquía dim-to-focus

> **Nota de título:** el nombre del archivo ("retención por importancia + rol pegajoso") refleja el
> **primer** enfoque de la sesión S117. El diseño **evolucionó** durante S117/S117-B hasta lo que se
> documenta abajo. Se mantiene el número/archivo por continuidad de referencias.

- **Fecha:** 2026-07-11 (Sesion-117, iteraciones A→B)
- **Estado:** Aceptada — capa Visual-only en `SMC-Visual.pine`, **fuera del CORE byte-idéntico** (SHA `d86bf37` intacto, core-sync ×3 OK).
- **Precisa:** ADR-014 (`strength` es propiedad del CORE; aquí se **reusa el campo** para almacenar la amplitud del tramo, uso Visual-only), ADR-002 (`i_swingStructLen`/`i_swingMaxKeep`/`i_swingDomAtr` son candidatos a calibrar), rúbrica de curación (`docs/planes/rubrica-curacion-visual.md` §1/§2/§3).
- **Tarea:** S117 "poblar la pierna hacia atrás" → derivó en rediseñar la **detección y presentación** de swings del Visual.

## Contexto y evolución (por qué el diseño final)

El objetivo era poblar la pierna de swings hacia atrás de forma legible. El camino descartó tres enfoques antes de llegar al definitivo:
1. **Retención por importancia + rol pegajoso** (primer intento): fosilizaba el array con pivotes viejos; abandonado.
2. **Dos capas (macro len 50 + menor len 5)**: producía **etiquetas dobles** (todo pivote mayor es también menor) y mezclaba escalas → confuso. Abandonado.
3. **Pivotes independientes `ta.pivothigh/pivotlow`**: muy estrictos (extremo de `2·len+1` velas) y **sin alternancia** → huecos en caídas/subidas.

**Causa raíz identificada:** el método de detección. Un pivote independiente no alterna y deja huecos.

## Decisión (diseño final)

**Una sola capa de estructura de swings, detectada por el algoritmo "leg" de LuxAlgo, con jerarquía visual dim-to-focus. Todo Visual-only; el CORE y `structMajor` no cambian.**

### 1. Detección: máquina de estado "leg" (portada de LuxAlgo `L337-361`)
`newLegHigh = high[len] > ta.highest(len)` / `newLegLow = low[len] < ta.lowest(len)`. Al confirmarse un HIGH el estado pasa a bajista; al confirmarse un LOW, a alcista. **Cada cambio de estado = un pivote** → **alterna siempre H-L-H-L** (nunca dos iguales seguidos) y marca más reversiones que `pivothigh/pivotlow`. Sensibilidad = `i_swingStructLen` (default 20). Anti-repaint: `ta.highest/lowest` cada barra; cambio de estado + push solo en `barstate.isconfirmed` (comparación `prevLeg` vs nuevo, sin `ta.change` intrabar).

### 2. Clasificación y color (convención SMC estándar)
`f_classifySwing` (CORE, solo se llama): un máximo es **HH** si supera al máximo anterior, **LH** si no; un mínimo es **LL** si rompe el mínimo anterior, **HL** si no. Color por **tendencia** (§2 rúbrica, familia teal/rojo): **HH+HL = verde** (alcista), **LH+LL = rojo** (bajista). Se dibujan **los 4 tipos** para que la secuencia lea correcta (subida HH+HL, bajada LH+LL).

### 3. Retención + orden de dibujo (presupuesto de 500 labels)
`SMC_majorSwingsV` (FIFO puro `f_pushSwingV`) a `MAX_MAJOR_CHART = i_swingMaxKeep` (default 350, input) → retiene el historial hacia atrás. Dibujo **al final** de la sección (tras la capa MTF): en modo "Todo" las familias crean >500 labels y Pine (`max_labels_count=500`) borra las creadas PRIMERO; al dibujar los swings al último, sobreviven.

### 4. Jerarquía dim-to-focus (§1/§3 rúbrica)
En vez de eliminar los pivotes menores (probado con filtro ×ATR y descartado por el usuario: borraba demasiado), se **atenúan**. La **amplitud del tramo** (`|pivote − pivote previo| ÷ ATR histórico`) se guarda en `sw.strength` al detectar. Al dibujar, `f_pushSwingLabel`:
- **Dominante** (`strength ≥ i_swingDomAtr`, default 1.5): `size.small`, `textcolor` transp 25.
- **Menor**: `size.tiny`, `textcolor` transp 65 → se hunde al fondo sin desaparecer.

### 5. Inputs (GRP_STRUCT, ajustables en vivo desde ⚙️ Settings)
`i_swingStructLen` (sensibilidad), `i_swingMaxKeep` (historial), `i_swingDomAtr` (corte dominante/menor).

### 6. Frontera exacta
| Pieza | Ubicación | Cambio |
|---|---|---|
| `SMC_Swing` / `MAX_SWINGS` / `f_pushSwing` / `structMajor` | CORE | **sin cambio** (SHA `d86bf37` intacto) |
| Detección leg-based, `SMC_majorSwingsV`, `f_pushSwingV`, `f_pushSwingLabel` | Visual | nuevos/decoplados de `i_majorLen` |
| Inputs `i_swingStructLen`/`i_swingMaxKeep`/`i_swingDomAtr` | Visual | nuevos |

## Consecuencias

- **Positivas:** estructura consecutiva legible (alterna, sin dobles, sin huecos groseros), llega al origen histórico, jerarquía que resalta lo dominante sin borrar el detalle; todo ajustable en vivo; CORE/SHA intactos.
- **Deuda / pendiente S118:** (a) **verificar colisión de encoding** con la familia teal/rojo — sobre todo **swings vs BOS/CHoCH** (mismo hue, mismos pivotes) — encendiendo estructura junto a swings (rúbrica §2/§2bis: diferenciar por nivel L1/L2/L3, no por hue); (b) calibrar defaults (`i_swingStructLen=20`, `i_swingDomAtr=1.5`) con el usuario; (c) `strength` como amplitud es uso Visual-only — si el scoring F3 llegara a leer swings, revisar.
- **Limitación aceptada:** un impulso limpio (sin pullbacks ≥ sensibilidad) tiene pocos swings — es correcto (pierna impulsiva = un tramo).

## GOTCHA de sesión (crítico para próximas)
TradingView **cachea el bytecode compilado**: tras inyectar código nuevo, "Añadir al gráfico" puede seguir aplicando el **compilado viejo**. La caché **solo se limpia reiniciando TV** (`tv_launch kill_existing`). Flujo fiable de apply: inject → `tv_launch kill_existing` (si hace falta) → eliminar Visual viejo → click "Añadir al gráfico" (botón `title='Añadir al gráfico'` vía `ui_evaluate`, NO desde favoritos = trae versión guardada vieja). Límite free = 2 indicadores → hay que eliminar antes de añadir.

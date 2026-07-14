# Sesion-123 — 2026-07-14 — Matriz Presupuesto Labels: Pérdida Silenciosa de la Estructura

## Objetivo sesión
Completar el pendiente S122: matriz medida D1 familia×concepto×variante. La matriz fue a revelar un hallazgo arquitectural que reordenó toda la sesión.

## Completado
- **HALLAZGO 1 (CRÍTICO) — Saturación silenciosa + desalojo de estructura:** Censo vivo D1 OANDA:EURUSD modo "Todo": `total_labels=500` (tope `max_labels_count` Pine ALCANZADO). Familias con CERO labels visuales: BOS / CHoCH / MSS (estructura madre), EQH/EQL (eventos equilibrio), pools BSL/SSL (liquidez), sweeps, OTE/GP (objetivos), y las etiquetas descriptivas Premium/EQ/Discount. Las líneas SÍ se dibujaban (límite separado) → lo que desaparecía eran los NOMBRES. **Impacto:** explicaba la queja "visual incompleto atrás" (S115) + "BOS/CHoCH sin nombre D1" (análisis vivo incompleto).

- **HALLAZGO 2 (ARQUITECTURA) — Prioridad invertida A PROPÓSITO + ineficacia del parche S118:** Consumo baseline: swings 178 labels (36%) + triángulos IR ▲▼ 65 (13%) = **243/500 (49%) para DOS familias sin nombre sustancial** (indicadores de entrada); zonas ~96 (19%). Notas históricas (L4700-4702 código) indican: *"AL FINAL de sección a propósito: en modo Todo >500 labels y Pine borra LOS PRIMEROS creados; swings al final quedan en slots finales, sobreviven."* Una sesión previa PROTEGIÓ swings colocándolos al final del dibujo. S118 intentó "recortar swings a dominantes ≥4.0·ATR para dejar sitio estructura" — **medición S123 confirmó: FALLÓ**, estructura seguía en 0. **Root cause:** no fue reducción de swings, fue que la estructura *nunca entró en islast*.

- **HALLAZGO 3 (CLAVE ARQUITECTURAL) — `f_drawStructure` NO corre en islast:** Leyendo código L3773-3792: `f_drawStructure` se llama **durante el recorrido histórico** (barstate.isnew, no islast) → los ~342 labels de estructura BOS/CHoCH/MSS son **los MÁS VIEJOS de todos** → Pine los desaloja por antigüedad sin importar orden de dibujo dentro islast. **Corolario crítico:** "invertir orden de dibujo" (estrategia S118) NO salva la estructura; el único lever es **CREAR MENOS en islast total** (respetar presupuesto 150 real vs. ~500 creados).

- **HALLAZGO 4 (FALLA DE DISEÑO) — `f_capLbls` post-hoc ineficaz:** Función `f_capLbls` (§6.5 código) solo APARECE 2 instancias: el cap en 5 familias (EQ, pools, sweep, flip, gaps) cuando EXISTEN. Pero "cap" borra DESPUÉS de crear (`label.delete`), DESPUÉS de que Pine YA desalojó los viejos en el MOMENTO de crear. **No funciona:** el desalojo ocurre al `label.new`, no al delete posterior. Todo cap debe ser **at-creation, no post-hoc**.

- **HALLAZGO 5 (BUG REAL) — `i_maxShowIR` HUÉRFANO:** Apariciones en código: definición L90, comentario L4012 ("acotado a i_maxShowIR"). **El bucle nunca lo usaba.** Dibujaba 65 IR en vez del cap 20 presupuestado. Sus hermanos (CISD/IDM/Sweeps) sí lo aplican (3-4 apariciones = def + comentario + USO ×2). **Fix (commit `bc0d7f2`):** iteración hacia atrás desde el más reciente + early break, contando **DIBUJADOS** (no recorridos) para respetar "poblar hacia atrás".

## Resultado medido D1 EURUSD (Operación)
- **Baseline → Final:**
  - Swings: 178 → 65 (reducción S118 SÍ ayudó, pero a factor ×2.7)
  - IR ▲▼: 65 → **20** (fix `i_maxShowIR`, cap = 10+10 por dirección)
  - **BOS+CHoCH (todas variantes): 0 → 104** (ESTRUCTURA RESURGIÓ al liberar ~200 labels)
  - EQH/EQL: 0 → 16
  - Sweep/Raid/Spring/Disp: 0 → 40
  - OTE/GP/pools/grid P/D: presentes

- **Modo Operación (205 labels total):** SIN desalojo, estructura SOBREVIVE pero **87% swings** (ruidosidad sin resolver).

## GOTCHAs S123
1. **CE10117 real y medido:** Primer intento fix IR (variable contador `drawnIR`, incrementos) = **100258 tokens** (pasa techo 100256 × 2). Segunda versión usa `array.size(SMC_irLabels) >= i_maxShowIR` (2 statements menos), **ENTRA**. Confirma regla S122: script vive pegado al techo.

2. **Default no se persiste en instancia sin override explícito:** `i_swingDomAtr=8.0` existía SOLO en Script nuevo; re-aplicar instancia vieja con default 1.5 → BOS/CHoCH/EQH/EQL **desaparecían sin error**. Commit `fd54448` persiste el default. TV **conserva overrides** (usuario lo ajustó) pero NEW scripts cargan defaults escritos. Solución pragmática: cambiar default = hay que fijar input en instancia viva O re-añadir fresca.

3. **Error método propio (anotar investigación):** Reporté "faltan pools/Discount/EQ" basado en `head -45` del censo truncado; eran PRESENTES, apenas fuera del rango leído. Diagnóstico de ausencias desde vistas parciales es justo lo que la matriz existe para evitar. De no verificar se habría lanzado un refactor innecesario de prioridades.

4. **`data_get_pine_labels` verbose supera tokens:** volcar FULL label list al contexto revienta límite. Solución: guardar JSON a fichero, procesar con script local (nunca volcar al contexto).

5. **Entity_id estudios cambia al re-aplicar:** `DLVOHq` → `vf6tZu` instancia nueva. Mapear por nombre (estable).

## DEUDA / PENDIENTE S124 (por orden de valor)
1. **Cap top-N POR TIPO en swings:** umbral global 8.0 filtra por amplitud; tipos no son igual de amplios → esqueleto DESBALANCEADO (HH 31 / LL 19 / HL 11 / **LH 4**) → rotura alternancia H-L-H-L (S117 leg-based) → "pierna se ve HH…HH…HH" sin retrocesos. Guardar top-N de CADA tipo. Costo ~2 tokens. Recalibrar 8.0 al hacerlo o desaparecer.

2. **Meter EQ (L3826) y estructura (L3760) en `f_evLbl` anti-solape:** ambos dibujan `label.new` CRUDO → fuera todo anti-solape → **EQL ↔ Sweep se pisan zoom cercano** (verificado capturas usuario). Anti-solape solo funciona entre labels del MISMO acumulador (evSeen eventos / f_ySlot zonas = SEPARADOS). Migrar = ~6 tokens. **GOTCHA:** `f_evLbl` fuerza `size.tiny` + `xloc.bar_time`; EQ hoy usa `size.small` + `bar_index` → migrar cambia aspecto O requiere parámetro (pagado ×19 call-sites).

3. **Zoom = límite plataforma, NO bug de código:** ranura anti-solape mide en DATOS (3 velas × 0.5×ATR); Pine sin acceso zoom/píxeles → dos labels pasando regla se tocan visuales al alejar. NO tiene arreglo fondo, solo calibración (elegir zoom prioridad). Pendiente histórico "calibración ranura X" de S122.

4. **Nudo confluencia S122 INTACTO:** cúmulo cerca precio = OB+FVG+IFVG al MISMO nivel = CONFLUENCIA que usuario QUIERE ver. NO es ruido. Deduplicar fuerte = EQUIVOCADO (oculta señal). Decidir opción: fusión etiqueta / marcador confluencia / nombre fuera banda.

5. **Estructura antigua (pre-~2016, x<679) sigue sin nombre:** se crea `f_drawStructure` durante recorrido histórico, es la VIEJA de todas, cae por edad. Seguirá saturado ~500 mientras islast rebase 150 presupuestado.

6. **Herencia H1/M5 → firma F1-GATE:** llevante desde S115; auditoría matriz concepto×variante×TF.

7. **Opción 2 arquitectural:** "presupuesto explícito por importancia" (mejor que parches). Sistema hoy pierde su capa principal porque un número volvió a default sin error. Parches S123 funcionan pero diseño frágil.

## Commits
- `bc0d7f2`: fix(pine-visual) F1-S123 i_maxShowIR huérfano + cap early-break
- `fd54448`: fix(pine-visual) F1-S123 i_swingDomAtr default 4.0→8.0 provisional

## CORE
- **SHA `752b4083a7db419d`** (1866 líneas)
- core-sync OK ×3
- pine_check 0/0
- Vivo sin CE10117

## Estado
- **F1-GATE BLOQUEADA** (confirmada causa: estructura creada fuera islast, overflow presupuesto)
- SIN ADR nuevo
- SIN tag
- Rama `pine/sistema-completo`
- Working tree limpio post-commits

## Siguientes pasos (S124)
1. Implementar cap top-N per tipo swings
2. Migrar EQ + estructura a `f_evLbl`
3. Calibración ranura X (zoom prioridad)
4. Resolver confluencia diseño
5. Remediación estructura vieja
6. Herencia H1/M5 auditoría
7. Arquitectura presupuesto explícito (opcional)

## Enlaces
- [[Sesion-122]]
- [[Sesion-121]]
- [[Sesion-120]]
- [[Sesion-118]]

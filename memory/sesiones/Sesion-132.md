# Sesión 132 — 2026-07-15

## Título
FASE 1 · F1-GATE BLOQUEADA — LA AMPLITUD REFUTADA, LA PREMISA ERA FABRICADA, Y LA CAUSA RAÍZ DEL P/D ENCONTRADA

## Objetivo
Con el que se ARRANCÓ (heredado de S131): medir si etiquetar pools por amplitud de swing (en ATR) hace
emerger los 5 niveles del usuario y no "los 6 intermedios que descarta".

⚠️ **Ese objetivo estaba viciado**: los "6 que descarta" son una premisa **fabricada** por el doc de
S131 §3bis.4 — el usuario nunca dijo tal cosa (ver Tarea 4). El objetivo REAL, en sus palabras, era:
*"dónde están marcándose en este minuto en el indicador los premium y discount de cada temporalidad
y no dan"*. La sesión terminó ahí, y ahí encontró la causa raíz (Tarea 9).

## Estado del repo
- Rama `pine/sistema-completo`.
- `pine/` NO SE TOCÓ en toda la sesión.
- CORE SHA `752b4083a7db419d` (1866 líneas) INTACTO.
- core-sync OK ×3.
- pine_check 0/0 en ambos probes.
- SIN ADR (nada se implementó). SIN tag. F1-GATE sigue BLOQUEADA.

## Completado

### Commits (2)
- `51e7985` chore(scripts): F1-S132 amplitud REFUTADA, premisa fabricada, y el fix de S130 rompía la doctrina. Archivos: `docs/planes/DISENO-amplitud-de-swing-S132.md` (nuevo), `docs/planes/DISENO-regla-de-pools-S131.md` (modificado: §3bis.4 marcada como corregida), `scripts/gen_probe_amplitud_swing.py` (nuevo), `scripts/gen_probe_amplitud_escala.py` (nuevo).
- `0032741` docs(fable): F1-S132 dossier P/D. Archivos: `docs/planes/DOSSIER-FABLE-premium-discount-S132.md` (nuevo), `docs/planes/evidencia-S132/S132-D1-pd-motor.png` (nuevo), `docs/planes/evidencia-S132/S132-H1-pd-motor.png` (nuevo).

### Tarea 1 — hallazgo que abarató la medición
La amplitud del swing YA se calcula en `pine/SMC-Visual.pine:2246` (`ampH = na(legPrev) or sAtr14 <= 0 ? 0.0 : math.abs(legPh - legPrev) / sAtr14`), dentro de la máquina leg-based de S117 (L2232-2251), que está FUERA del CORE (el CORE va de L154 a ~L2019). Lo que falta no es calcularla: es que `SMC_Pool` (L266) la RECUERDE — `f_upsertPool` (L1363) recibe solo `level`. Por eso la medición cupo entera fuera del CORE.

### Tarea 2 — probe v10 (marker 1320), D1 OANDA:EURUSD, 38 pools vivos
Midió la ESCALA EQUIVOCADA. Los pools nacen de `f_detectSwings(i_swingLen)` con `i_swingLen`=5 y se midió la amplitud contra ese pivote anterior; la máquina de la que sale el umbral `i_swingDomAtr`=8.0 usa `i_swingStructLen`=20. Se delató porque max(amp) del set = 6.07 < 8.0 (umbral existente inalcanzable). Auto-corregido dentro de la misma sesión. Anti-humo de v10: `P_nSinMatch`=0, `P_xcheckDump`=0, `P_nAlive`=`P_nPoolsDump`=38, `P_nPiv`=729, `P_nAmpCeroPiv`=1.

### Tarea 3 — probe v11 (marker 1321), barrido de 5 escalas de tramo
NINGUNA separa. Resultados (min amp del grupo A / max amp del grupo B / margen / max amp global):
- L=5: 3.06 / 4.80 / −1.74 / 6.07
- L=10: 2.70 / 6.21 / −3.51 / 9.10
- L=20: 4.08 / 7.55 / −3.48 / 13.48
- L=50: 3.30 / 22.46 / −19.16 / 25.78
- L=100: 10.47 / 15.54 / −5.06 / 42.61

P-A6 FALSA (era la que decidía). P-A7 mitad verde (el diagnóstico de desajuste de escala de v10 era correcto: en L=20 max(amp)=13.48 supera el 8.0 que en L=5 era inalcanzable; pero corregir la escala NO salvó la hipótesis). P-A8 VERDE (max(amp) crece monótona: 6.07/9.10/13.48/25.78/42.61). Anti-humo de v11: `P_nHitA`=5 en las 5 escalas (tras ampliar la tolerancia de 30 a 40 pips porque 1.60063 no casaba con el pool real 1.60389, a 32.6 pips), `P_nAmpCeroPiv`=1 por escala (solo el primer pivote de la historia), `P_nPiv` = 740/409/204/86/38.

### Tarea 4 — la premisa era fabricada
El "grupo B: 6 niveles que el usuario descarta" (1.036, 1.0733, 1.10654, 1.12105, 1.13246, 1.1473) lo afirmó el doc `DISENO-regla-de-pools-S131.md` §3bis.4; el usuario NUNCA lo dijo. Cita literal del usuario en S132: "yo no descarto nada, todo lo que he dicho es observación". Al enseñar sus capturas anotadas resultó ser AL REVÉS: sus líneas verdes (1.10640, 1.07408, 1.01814) SON esos pools (1.10654, 1.0733, 1.01779 — a 1.4, 7.8 y 3.5 pips respectivamente) y sostiene que DEBERÍAN ser los discount de las temporalidades menores. §3bis.4 de S131 quedó marcada como corregida. Tercera vez con la misma causa raíz (S129 midió la lectura equivocada; S130 discutió el ancla cuando era la escala). NORMA NUEVA: ninguna medición ni diseño arranca sin citar la frase literal del usuario que lo motiva.

### Tarea 5 — la observación real, medida en vivo (Visual limpio, una instancia, sin overrides, todo apagado salvo P/D + panel + herencia D1/H1)
Con `i_pdSwingLen`=1000 (el default del repo hoy): D1 [0.95360, 1.60389] Discount 30% (cuadra con el usuario); H1 [1.13246, 1.18492] Discount 27% = 525 pips (su lectura: [1.02108, 1.39437] = 3733 pips → 1100 pips de error en el suelo); M5 Premium 88%. En el chart H1 el indicador etiqueta: Premium 1.18492 / EQ 1.15869 / Discount 1.13246, y al fondo "D1: Discount 0.95360" heredado.

### Tarea 6 — doctrina vs implementación (docs/reglas-smc-ict.md)
§2.3 define el dealing range entre el último strong high y strong low, y su tabla dice "rango | strong high / strong low vigentes | se actualiza con la estructura" ⇒ la ventana de N barras YA VIOLA §2.3. §6.3.5 dice: "EL relevante = el rango dominante activo. Descarta (citable): medir P/D sobre un rango ya superado por estructura" ⇒ el rango fósil está PROHIBIDO por regla (= la objeción de operabilidad del usuario). §2.3 (MTF) dice "Transferible como bandas del HTF heredadas a M5" y §5.16 dice "los gradient levels de un rango-fuente HTF son globales (mismos en todo TF), no se recomputan por TF" ⇒ la cascada anidada por TF que propone el usuario EXTIENDE la doctrina ⇒ requeriría ADR.

### Tarea 7 — el fix de S130 (`i_pdSwingLen` 50→1000, commit `61dcc36`) es doctrinalmente incorrecto
`i_pdSwingLen` NO es un lookback: es la SENSIBILIDAD DEL PIVOTE (va a `f_detectSwings(pdLen)`, que exige superar pdLen barras a cada lado; luego `f_resetTrailingHigh/Low` en L1176-1186 ancla el rango a ese swing y `f_updateTrailing` lo expande). §5.16 dice literalmente "strong high ↔ strong low, escala pdSwingLen=50". Con 1000 casi ningún pivote califica ⇒ el reanclaje casi nunca se dispara ⇒ solo actúa el trailing ⇒ el rango tiende a extremos casi globales ⇒ es el rango fósil que §6.3.5 prohíbe. Cuadró con el ojo del usuario en D1 por accidente del mecanismo, no porque el ancla fuera estructural.

### Tarea 8 — barrido in_69 medido: 1000 → 50, cero código, vía `indicator_set_inputs`
Predicciones P-D1, P-D2, P-D3 escritas antes de medir, las TRES VERDES:
- D1: Discount 30% → Discount 18%, rango [1.13246, 1.20831] = 758 pips (líneas 1.21/1.17/1.13)
- H1: Discount 27% → Premium 82% (SE INVIERTE)
- M5: Premium 88% → Premium 76%

HALLAZGO NO PREDICHO (el importante): con la escala doctrinal, D1 Discount 18% y H1 Premium 82% SIMULTÁNEAMENTE = la lectura anidada que pide el usuario (barato en el rango grande, caro en el pequeño). **El P/D ROTA entre temporalidades** (del verbo *rotar*: cada TF da un veredicto distinto y útil), y sale **sin código**. Con 1000 era imposible: D1 y H1 salían casi iguales (30% y 27%) porque ambos eran rangos fósiles gobernados solo por el trailing — decir lo mismo en las 3 TF es no decir nada. El 1000 destruía esa rotación, que es la que hace operable el sistema; es justo lo que S130 perseguía con la "cascada de mitades" y que allí salió **rota** (del verbo *romper*: flapping monótono, L5 saltando cada ~4 velas).

P-D3: D1 doctrinal 758 pips vs lectura del usuario 6503 pips ⇒ hipótesis del supervisor (NO confirmada): son DOS OBJETOS DISTINTOS — su rango no es el dealing range, es el CONTEXTO MACRO. Mismo patrón que S130 (su H1 de 3780 y el H1 nativo de 1905 eran objetos distintos).

### Tarea 9 — la causa raíz (hallazgo principal de la sesión)
En `pine/SMC-Visual.pine:1641-1645`, dentro de `f_computeTFState` (que ESTÁ en el LIBRARY CORE): `if barstate.isconfirmed and not na(pdH)` → `f_resetTrailingHigh(trailTf, pdH, ...)` y lo mismo para pdL. `[pdH, pdL] = f_detectSwings(pdLen)` (L1635) = pivote simétrico estricto. NO hay ninguna condición de que el pivote sea FUERTE. EL CÓDIGO ANCLA EL RANGO EN CUALQUIER PIVOTE CONFIRMADO; LA DOCTRINA §2.3 EXIGE STRONG HIGH/LOW. Ningún valor de `pdLen` convierte un pivote débil en fuerte ⇒ el parámetro es la palanca equivocada ⇒ ni 50 ni 1000 funcionan.

Esto explica las dos objeciones del usuario a la vez: el techo 1.20831 no ganó a los altos superiores (1.23697, 1.39834, 1.49539, 1.60180), los SOBRESCRIBIÓ al reanclar; el suelo 1.13246 es un mínimo débil creado dentro de la caída actual y el origen de la pierna (1.02182) fue sobrescrito.

IRONÍA: el material ya existe — dos líneas antes, en L1638-1640, el mismo bucle llama a `f_setStructureHigh/Low`, o sea la estructura BOS/CHoCH ya está detectada y viva en `structTf`; el P/D simplemente no la usa.

El fix (anclar en el strong high/low que la estructura ya conoce) TOCA EL CORE ⇒ rompe el SHA ⇒ re-baseline ×3 ⇒ contrato MQL5 ⇒ ADR obligatorio. NO se implementó (norma: medir primero con predicción escrita).

## Citas literales del usuario en S132 (para el registro)
- "yo no descarto nada, todo lo que he dicho es observación"
- "cuestionamiento de dónde están marcándose en este minuto en el indicador los premium y discount de cada temporalidad y no dan"
- "¿cómo va a ser ese el discount si el precio viene de dos swings alcistas al rebotar? […] el discount debiese ser el bajo antes del swing y aquí está en el bajo que se está creando junto a la caída"
- "no necesariamente tiene que ser el siguiente pivote […] quizás el precio nunca vuelva a llegar ahí […] que queden en un rango que sea operable"
- "lo que siempre he dicho es lo que veo y me causa ruido; si tienes mejoras o ideas mejores para hacer este cálculo bien, implementémosla, pero que sea LA solución"

## Dossier para Fable
`docs/planes/DOSSIER-FABLE-premium-discount-S132.md`. Autocontenido. Entregable pedido a Fable: SOLO EL ESQUELETO de la solución + por qué esa solución + qué resuelve y qué NO + coste (CORE/SHA/ADR/MQL5/paridad LuxAlgo/presupuesto de tokens) + cómo medirlo antes de tocar código con predicción falsable y criterio de abandono propio. Incluye las 9 hipótesis refutadas para que no se re-propongan, y el aviso de método sobre la premisa fabricada. Evidencia visual en `docs/planes/evidencia-S132/` (`S132-D1-pd-motor.png`, `S132-H1-pd-motor.png`); las capturas anotadas a mano las entrega el usuario.

## Predicciones
S131 cerró con 18 vivas de 37. En S132: P-A6 falsa, P-A7 media, P-A8 verde, P-D1 verde, P-D2 verde, P-D3 verde.

## Gotchas nuevos
- El modal "¿Desea guardar este script antes de añadirlo?" bloquea el apply en silencio y hace falta un Ctrl+Enter adicional; la consola lo delata (muestra "Compilando..." repetido sin "Añadido al gráfico").
- TV solo deja 2 indicadores; con el cupo lleno el apply NO aterriza. Confirmado en vivo por el usuario. Hubo que remover instancias con `chart_manage_indicator` (requiere `indicator` Y `entity_id`).
- Las instancias aplicadas pueden quedar RANCIAS (marker viejo) y además arrastrar overrides de inputs de sesiones anteriores (una instancia daba 38 pools vivos y otra 33, por el override de `i_poolTol` de S131). Solución: remover todas y re-aplicar limpio.
- `data_get_pine_tables` devuelve `study_count`=0 mientras el chart re-renderiza tras cambiar de TF o inputs: hay que esperar (~50s) y re-consultar.
- El Visual completo tarda ~60-75s en compilar y aplicar.
- Mapeo de inputs re-verificado contando `input.` en orden: total 122 inputs. `i_pdSwingLen`=in_69, `i_poolTol`=in_81, `i_minTouches`=in_82, `i_densidad`=in_118, `i_showPD`=in_68, `i_showPanel`=in_0, `i_showD1`=in_104, `i_showH1`=in_105.

## Pendiente / Siguiente (S133)
1. Esperar/revisar el esqueleto de Fable (dossier entregado).
2. La causa raíz está identificada (ancla en pivote cualquiera vs strong high/low §2.3) pero NO medida en sombra: hay que medir con predicción escrita antes de tocar el CORE.
3. Decidir la tensión macro-vs-dealing-range (¿son dos objetos distintos?) — requiere confirmación del usuario.
4. Revertir o no el fix de S130 (`i_pdSwingLen` 1000→50): doctrinalmente 50 es lo correcto (§5.16) y produce la rotación, pero reancla en pivotes débiles ⇒ probablemente el parámetro deje de importar si se arregla la causa raíz.
5. NO repetir (9 hipótesis refutadas con medición): Opción B (S128), bandas 4/5 incapaces (S128), Opción C (S129), cascada de mitades (S130), mapeo nivel→TF (S130), fuerza-por-toques (S131), barrido de `i_poolTol` (S131), reglas aritméticas (S131), amplitud de swing en 5 escalas (S132).
6. Pendientes abiertas de antes: el fallback M2 (18% medido con el gate roto, re-medir), IFVG por banda/lado, gate MB/BPR, `elig` excluye ZS_MITIGATED en Visual, calibrar `LEG_ANCH_TOL_ATR`, deudas S123 #2/#3/#4, herencia MTF.

## Enlaces
[[Sesion-132]] · [[Sesion-131]] · [[Sesion-130]] · [[Sesion-129]] · [[Sesion-128]]

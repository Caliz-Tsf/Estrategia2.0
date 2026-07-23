# Sesión 141 — 2026-07-22

## Objetivo con el que arrancó
Plan de cierre de S140: revisar la familia FVG y sus variantes (FVG/CE, IFVG §5.2, BPR §5.3,
IR §5.4, IPR §5.9) en su TF nativo, luego comparación ENTRE variantes de FVG — mismo método
que la familia OB (S139-S140).

## Rama
`pine/sistema-completo`

## Qué se tocó
CORE intacto todo el tiempo: LIBRARY CORE SHA `9559a0d7fe58b213` (1776 líneas), EXTREMES
CORE SHA `5f851d87e5fda720` (148 líneas). check-core-sync OK ×3. Sin tag (F1-GATE sigue sin
firmar). Todos los cambios en la capa de dibujo del Visual (`pine/SMC-Visual.pine`), fuera
del CORE.

## Commits (5)
- `b5849a1` feat(pine-visual) — atenuado de FVG por antigüedad — paridad familia OB.
- `0682a4a` feat(pine-visual) — atenuado de IFVG por antigüedad — paridad familia FVG/OB.
- `2734dda` feat(pine-visual) — atenuado de BPR por antigüedad — familia FVG completa.
- `9d7f72f` feat(pine-visual) — filtro del IR por fuerza propia en vez de confluencia
  cruzada.
- `4c031e9` feat(pine-visual) — tarea 4: familia FVG curada entre variantes (anti-solape +
  anclaje).

## Método
Vistas AISLADAS por concepto vía `indicator_set_inputs`, censo con `data_get_pine_boxes`/
`data_get_pine_labels`, screenshots, A/B con inputs (`i_obAgeDim` 0 vs 40).

## FVG / IFVG / BPR (§5.2, §5.3)
Atenuado por edad con el helper `f_ageDim` (paridad OB S139-S140), aplicado en caja
(transparencia+dim, borde+dim) y en label (`color.new` con `min(f_ageDim*2, 85)`).
Verificado aislado en D1 EURUSD con A/B del input `i_obAgeDim` (0 vs 40): con 0 las cajas
viejas quedan a brillo pleno, con 40 se desvanecen.
- FVG: 32 cajas, span 0.92→1.56.
- IFVG: 15 cajas, span 1.01→1.44.
- BPR: 0 zonas en D1 (cross-check con FVG=32 en vivo lo confirmó); sí dibuja en M5 (1 caja
  verificada) → el fix se aplicó por paridad para TFs bajos.

## IR (§5.4)
El filtro de dibujo cambió de confluencia CRUZADA (`f_confDegree(ir.price)>=2`, co-ubicación
con ≥2 familias) a la fuerza PROPIA del evento: nueva constante `IR_MIN_STRENGTH=0.5`,
`ir.strength` viene de `f_eventStrength` (40% tamaño impulso ×ATR + 20% cuerpo + 20% sweep +
20% alineación bias). Fundamentado en reglas §5.4 y §6.3.25 (el IR es matiz de contexto
informativo, valor intrínseco no cruzado). Resultado: 20→16 IR en D1, incluye los
recientes/limpios que el gate cruzado ocultaba. Compila sin CE10117.

**Limitación aceptada por diseño:** la historia del IR se corta ~2017 por `MAX_EVENTS=100`
(constante del CORE, compartida por todos los eventos); extenderla tocaría el CORE y
multiplicaría memoria → no se hizo (IR es baja prioridad).

## IPR (§5.9)
Revisado, NO lleva código nuevo — solo dibuja el `currentIpr` (siempre el actual, nunca
viejo), no necesita age-dim. Cross-check en vivo (FVG=32 + IR=20 dibujando junto a IPR con
`i_showIPR` ON) confirmó que IPR está ENCENDIDO y SANO, no apagado ni desconectado.

**Pendiente:** verlo dibujado en vivo — no se logró porque su detección exige un cluster de
FVG de un solo lado SIN opuestos en la ventana (`f_detectIPR`), condición no presente en
EURUSD/BTCUSD M5 ni siquiera relajando `i_iprMinGaps`/`i_iprWindow`.

## Tarea 4 — comparación ENTRE variantes de FVG
(a) **Anti-solape de labels** compartido en la familia FVG con acumulador top-level
`fvgFamSeenY` (resetea cada barra), reemplazando los tres `SeenY` separados
(`fvgSeenY`/`ifvgSeenY`/`bprSeenY`); prioridad de orden de dibujo IFVG>BPR>FVG (el 1.º
conserva el nombre, el resto cede la etiqueta, la caja sigue). Medido en D1: 47→45 labels (2
colisiones cross-variante reales resueltas; el resto de "mismo precio" del censo eran falsas
por el redondeo a 2 decimales de `data_get_pine_labels`/`boxes`). Separado del `blockSeenY`
de OB a propósito (la unión FVG↔OB se decide en la tarea 6).

(b) **Anclaje de caja:** FVG/IFVG/BPR unificados a C2 (1.ª de las 3 velas, `z.barTime -
2*barMs`); antes IFVG/BPR arrancaban corridos +1 (sin offset) respecto al FVG.

## BUG/deuda nueva (documentada en el commit 4c031e9 y en comentarios del código)
El anclaje de caja por TIEMPO (`z.barTime - N*barMs`) se corre ~1-2 días en ~40% de los FVG
en D1 — los que cruzan el fin de semana del Forex (C0/3.ª vela en lunes o martes → el offset
cae en sábado/domingo sin vela). Vía por ÍNDICE (`z.barIdx-2`, `xloc.bar_index`) DESCARTADA:
da RE10026 ("bar index too far", TradingView no ancla dibujos >~5000 barras atrás); `time[N]`
dinámico tiene el mismo límite. El fix robusto exige guardar el timestamp de la vela origen en
el UDT `SMC_Zone` (cuando está a 2 barras) = cambio del LIBRARY CORE (replicar byte-idéntico
en Visual+Strategy+Context + check-core-sync). POSPUESTO por decisión del usuario ("dejémoslo
como está").

## Gotchas de método
Los censos `data_get_pine_boxes`/`labels` salen RANCIOS durante el recompile (~60s) — hay
que esperar el render y re-censar. TV (CDP) se cayó 2 veces, relanzado con `tv_launch`. Mapa
`in_N` de `indicator_set_inputs` regenerado fresco (`i_densidad` ahora `in_119`, corrido +1
desde S122).

## Estado de la familia FVG
Revisada concepto × TF nativo (FVG/IFVG/BPR atenuados por edad, IR con filtro por fuerza
propia, IPR verificado sano sin código nuevo) + tarea 4 de comparación entre variantes
(anti-solape de labels + anclaje unificado a C2). Pendiente ver IPR dibujado en vivo.

## Orden acordado para la próxima sesión (S142)
- Tarea 6: comparación FVG vs OB (ambas familias juntas: decidir si unificar `fvgFamSeenY`
  con `blockSeenY`) + revisión en modo Operación (`i_densidad=Operación`).
- Verificación visual de IPR cuando aparezca uno activo.
- Deuda del anclaje weekend-safe (cambio de CORE), pospuesta.

## Fase
Sigue FASE 1, F1-GATE ABIERTA.

## Referencias
[[Sesion-140]].

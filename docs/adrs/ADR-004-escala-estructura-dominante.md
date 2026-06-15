# ADR-004 — Escala de estructura DOMINANTE (swing 50), capa aditiva

- **Fecha:** 2026-06-15 (Sesion-022)
- **Estado:** Aceptado
- **Tarea:** F1-S1.2-T07B
- **Contexto DOC-01:** la escala de los swings es una definición de `docs/reglas-smc-ict.md` §1.1.

## Contexto

El sistema dibujaba estructura BOS/CHoCH solo en dos escalas: `swingLen=5` y `internalLen=3`.
Al comparar con la única referencia externa permitida (LuxAlgo SMC), el usuario notó que faltaba
la **estructura GRANDE** que LuxAlgo marca con `getCurrentStructure(50)` ("swing structure",
ref `pine/reference/LuxAlgo-SMC-base.pine` :782). Diagnóstico: **nuestro `swingLen=5` equivale al
*interno* de LuxAlgo**; la capa de swing grande (50) nunca se implementó para la ESTRUCTURA (sí se
usaba 50 para el rango Premium/Discount en T07, lo que dejaba una incoherencia: P/D a escala 50 pero
estructura a escala 5).

## Decisión

**Añadir una tercera escala de estructura, DOMINANTE (`i_majorLen=50`), como capa puramente
aditiva** (Opción C del task `docs/task-T07B-estructura-swing-dominante.md`).

- Reutiliza el CORE escala-agnóstico existente (`SMC_Structure`, `f_setStructureHigh/Low`,
  `f_detectStructure`, `f_detectSwings`) **sin modificar ni una línea** del bloque
  `// === LIBRARY CORE ===`. `check-core-sync` queda OK con el mismo SHA (`24c3a4a28fcf74c3`,
  415 líneas) y T01–T07 byte-intactos.
- Estado consumer-side: `var SMC_Structure structMajor` + array dedicado `SMC_eventsMajor`
  (NO el `SMC_events` compartido que consume el OB → sin contención ni efectos colaterales).
- Wiring de detección idéntico en Visual y Strategy. Dibujo solo en Visual
  (`f_drawStructureMajor`: línea width 3 anclada por `bar_time`, etiqueta `BOS +`/`CHoCH +`
  centrada por `bar_index`, teal alcista / rojo bajista, sin recuadro).
- Fila de panel "Bias dom. (50)".

## Alternativas descartadas

- **(B) Re-escalar `swingLen 5→50`, `internalLen 3→5`** (alinear nombres a LuxAlgo): descartada.
  Invalidaría todos los casos de prueba fechados de `reglas-smc-ict.md` §1.1–§1.5 y §2.1
  (construidos a escala 5), re-abriendo y re-validando T02–T06. Contradice **ADR-002**
  (escala/umbrales congelados hasta calibración de Fase 3) y la regla dura #8. Además perdería la
  estructura LOCAL (5/3), deseable como gatillo fino de entrada en ICT (HTF=contexto, LTF=entrada).
- **(A) Statu quo** (no mostrar la estructura grande): descartada por el usuario.

## Consecuencias

- El sistema evalúa estructura en **tres** escalas: dominante (50) / swing (5) / interna (3).
- **El bias headline NO cambia:** la capa dominante se DETECTA y DIBUJA pero **no** alimenta
  `f_updateTFState` (el bias del scoring sigue siendo el de la escala swing). Tocar eso
  modificaría T04 (validado) y el scoring tiene pesos congelados (ADR-002).
- **PENDIENTE para Fase 3:** decidir con datos OOS si el bias del scoring debe venir de la escala
  50 (contexto), de la 5 (gatillo), o de una combinación (50 = gate/contexto, 5 = trigger). Es
  calibración (Sprint 2.1 + Fase 3), no de este task.
- **Relación con T07 (P/D):** con la estructura dominante disponible, la Opción B de
  `docs/decisiones-pd-rango.md` (anclar el dealing range a los strong high/low dominantes) se vuelve
  natural; queda como nota de Fase 3.
- Latencia inherente: la estructura 50 confirma 50 velas tarde (~2 días en H1) y su ruptura puede
  tardar días — anti-repaint correcto [D-PINE-03], no un bug.

## Referencias

- Task: `docs/task-T07B-estructura-swing-dominante.md`
- Spec: `docs/reglas-smc-ict.md` §1.1/§1.3/§1.4
- Origen: `docs/pendiente-estructura-swing-grande.md`
- LuxAlgo: `pine/reference/LuxAlgo-SMC-base.pine` :409 (`getCurrentStructure`), :782-783
- Congelación de escala: ADR-002

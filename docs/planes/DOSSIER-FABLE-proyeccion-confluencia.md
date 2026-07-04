# DOSSIER PARA FABLE — Doctrina de proyección + confluencia (visual → score → enjambre → EA)

> Handoff de Claude Code a Fable. Objetivo: que Fable **ordene** todo lo que sigue y proponga un **esqueleto** para integrarlo al Pine/Visual **y** al modelo de pensamiento de los agentes (enjambre + decisor MT5) + la lógica de score. Nace de una conversación larga usuario↔Claude Code (Sesion-092). No implementar aún: primero el esqueleto ordenado, bajo los gates del proyecto.

## 0. Contexto mínimo del proyecto (para arrancar en frío)
- Bot SMC/ICT para Forex. Primero sistema completo en **TradingView Pine v6**, luego **EA MQL5** que replica el core validado. Ver `CLAUDE.md`, `WORKPLAN-MAESTRO-V2.md`.
- Arquitectura: **1 core de detección** (sección `LIBRARY CORE` byte-idéntica en Visual y Strategy) + 2 consumidores (`SMC-Visual.pine` dibuja; `SMC-Strategy.pine` scoring/entradas). El EA traduce el core función a función.
- Estado: **Fase 1, F1-GATE**. Eje 2 "Fuerza" con `strength` en el CORE (ADR-014). Modo de densidad visual `i_densidad` = Operación / Estudio / Todo. §10 checklist cerrado técnicamente (Sesion-092). CORE 1700 líneas SHA `5510361166844bd5`.
- Reglas duras: anti-repaint (`barstate.isconfirmed` + `lookahead_off`), core byte-idéntico (`check-core-sync`), umbrales relativos a ATR, símbolo-agnóstico, R:R ≥1:3, scoring direccional (42 confluencias §4.8), compila 0/0, ningún gate se salta. **RE10045**: `array.push` dentro de bucles de dibujo MTF revienta por recursos → dedup por string, no arrays (ver `memory/`).
- Docs clave: `docs/planes/ESQUELETO-FABLE-sistema-visual.md` (el sistema visual que Fable ya entregó: hue por familia, jerarquía por transparencia/grosor, §8.2 matriz modo×familia, §10 checklist, §11.2 orden de implementación), `docs/reglas-smc-ict.md`, `docs/METODOLOGIA-VERIFICACION-VISUAL.md` (Ejes 0/1/2/3), la doctrina ICT destilada en el vault (`Mentores/ict/knowledge/madre-2026.md`).

## 1. La problemática (qué disparó esto)
El modo **Operación** quedó limpio pero **demasiado agresivo**: el filtro por `strength` (solo Primario) + una sola ancla compartida deja **conceptos en cero** en un TF. En vivo: en H1 se ven los OB/FVG **heredados de D1** pero **no los propios de H1**; en D1 no se ve ningún OB/FVG/inducement. El usuario quiere un gráfico **curado pero completo para proyectar entradas** (como el LuxAlgo base): ver el 1–2–3 más importante de cada concepto por lado.

Al profundizar, el usuario reformuló el criterio de raíz. Lo que sigue es su modelo — **hay que ordenarlo y traducirlo a Pine + a la mente de los agentes**.

## 2. El principio rector (la tesis del usuario)
**La importancia NO es "fuerza × cercanía al precio". Es RELEVANCIA ESTRUCTURAL + CONFLUENCIA, leída como proyección.**

Un analista mira **hacia atrás** (contexto: dónde se tomó liquidez, dónde se rompió estructura, cuál es el rango) y **hacia adelante** (proyección: a dónde va el precio = draw on liquidity, y dónde REACCIONARÁ = origen del desplazamiento). Reglas que emergieron:

1. **Punto de giro / origen del desplazamiento.** Una instancia importa cuando está en un pivote que marca un giro/retroceso, o en el origen de la ruptura de estructura (la causa de la expansión). Lo interno / de media-tendencia se detecta pero no se resalta.
2. **Proyección por profundidad (el "3", que en realidad es N).** "3 por lado" es el **mínimo de escenarios de proyección** a distinta profundidad de retroceso: el más cercano al precio (retroceso corto→sigue), el de media, y el del **origen/inducement inicial** (soporte último, quizás no vuelve). PERO el usuario quiere poder ver un **4.º o 5.º** de una familia **más atrás en el tiempo y lejos del precio** cuando lo pida — son proyecciones/escenarios, no un cap rígido. Pensar como quien busca **patrones** (buscar confluencias = buscar patrones).
3. **No recortar por rango.** Fuera del Premium/Discount D1 hay **lugares a donde proyectar** (draws: pools, old-highs, EQ lejanos). NO se borran por estar lejos; se mantienen si son **objetivo de proyección bajo confluencia**. El rango D1 es **contexto** para razonar premium/discount, no una tijera. (Corrige un "adiós al BSL 1.51" que Claude Code había propuesto: el 1.51 puede ser un draw válido.)
4. **Confluencia = la métrica real de importancia.** Donde se **apilan varios conceptos** (OB + FVG + EQH + pool al mismo nivel) es donde el precio reacciona/proyecta. Resaltar esas zonas. (Conecta con el motor de 42 confluencias §4.8 y el scoring de Fase 2.)
5. **Granularidad: por concepto Y por variación, caso por caso.** No es "por familia". Una FVG normal, una **trueFVG** (displacement), una **IFVG** (invertida) y una BPR son la misma familia pero **doctrinas distintas**. Ejemplos que dio el usuario:
   - **FVG:** importa el **FVG de desplazamiento** que rompe acumulación+estructura (donde reacciona); los micro-internos son draws de paso.
   - **IFVG:** el **FVG invertido que calza con el FVG del inicio del swing** — el que se genera **antes del OB / antes de que se forme el LL** cuando el precio venía cayendo y va a girar. NO los IFVG de media tendencia.
   - **EQH/EQL:** los que están en un **HH/LL (giro)** donde se toma liquidez y el precio se desplaza; NO en media tendencia neutra. Si hay 3 ciclos desplazamiento-retroceso, importan los 3 EQH **de los HH significativos**.
   - **Sweep:** el que ocurre en el **HH/LL que antecede el giro** al lado contrario; no los internos.
   - **Pools BSL/SSL:** los draws relevantes across D1/H1/M5, en los extremos; lejanos válidos si hay confluencia.
   - **OB:** el que **originó la ruptura de estructura**, por lado (demanda↓/oferta↑), a distintas profundidades.
   - **Estructura:** el **CHoCH/MSS vigente** + la **dominante**; los HH/LL solo los de giro, no la traza.

## 3. El inventario a ordenar (familia → concepto → variación, ~40 entradas)
Cada entrada necesita: **Significa · Dónde vive · Qué casos importan (posición estructural + confluencia + profundidad de proyección) · Cómo transmite MTF · Modo mínimo (Op/Est/Todo)**.

- **Estructura:** swing interno · swing/dominante (HH/HL/LH/LL) · BOS (interno/swing/dominante+) · CHoCH · CHoCH-MSS · Flip
- **Order Block (azul):** OB · OB-propulsión (⇈) · Breaker · Mitigation Block · Vacuum · Rejection block
- **FVG (naranja):** FVG · trueFVG (displacement) · gradedFVG (·g) · **IFVG (invertida)** · BPR · VI · IPR
- **Liquidez (violeta):** Pool BSL/SSL (vivo/objetivo/barrido) · Sweep/Raid/Grab · IDM (inducement) · Judas · EQH/EQL
- **P/D + Gradient:** Premium/Discount+EQ · quadrants (LQ/EQ/UQ) · eighths · OTE/GP
- **Gaps:** NWOG · NDOG · NYMO · BAG (breakaway)
- **Contexto:** EMAs (rebote/cruce/stack) · Kill Zones+macros · Displacement · Legs IMP/CORR · Inside Day · CISD · Std-Dev · SMT

## 4. Infraestructura Pine existente a reutilizar (no reinventar)
- `f_renderScore(strength, distAtr)` = `strength × (1 − min(distAtr/6, 0.8))` — llave de orden (hoy cercanía-al-precio; hay que evolucionarla a **relevancia estructural + confluencia**).
- Bloque de **anclas §2.3** (`anchorHiIdx/anchorLoIdx`, 1 por lado sobre OB/FVG/Breaker) — generalizable a **top-N por lado por concepto/variación**.
- Patrón **registrar→recortar-en-`islast`** (estructura `STRUCT_OP_CAP`, EQHL `EQ_OP_CAP`) — replicable por concepto.
- **Desalojo global §6.5** (S090): budget de labels por modo; MTF+anclas mandatorios; recorta discrecionales por frescura. Reasignar hacia zonas de decisión.
- **Herencia MTF** (`f_nearestN`/`f_drawMTFZones`, ADR-009/010; buffer genérico etiquetado) — transporte HTF→LTF.
- Campo `strength` en UDTs (ADR-014) + `f_zoneStrength`/`f_eventStrength`/`f_strengthLevel` en el CORE.
- Flags ya existentes: `trueFvg`, `gradedFvg`, `propulsion`, `state`/`mitigatedPct` (ciclo de vida §5.4, ya implementado en Sesion-092: mitigada pierde fill).

## 5. LO QUE PEDIMOS A FABLE (entregables del esqueleto)
Que Fable ordene lo anterior y proponga un **esqueleto integral** (sin implementar; fichas `[impl]` + secuencia bajo gates), cubriendo:

**A. Doctrina visual por concepto/variación** — las ~40 entradas del §3 con el template, resolviendo: qué caso importa, cuántos por lado (mínimo 3 = escenarios de profundidad, con acceso opcional a 4.º/5.º más atrás), cómo se marca la confluencia (apilamiento), MTF, modo mínimo. Respetando §8.2 y sin inflar las 42 confluencias.

**B. Mecánica de selección en Pine/Visual** — cómo pasar de "fuerza×cercanía" a **relevancia estructural + confluencia + profundidad de proyección**: (i) definir "punto de giro / origen de desplazamiento" reutilizando swings/estructura ya detectados; (ii) un **score de render estructural** que combine posición (giro/origen), confluencia (conceptos apilados en ±tol×ATR) y profundidad; (iii) selección top-N por lado por concepto con "ver más atrás" bajo demanda (un input de profundidad de proyección); (iv) NO recortar draws lejanos con confluencia; (v) presupuesto/desalojo reasignado; (vi) RE10045-safe, anti-repaint, core byte-idéntico. Fichas `[impl]` sobre funciones existentes (§4).

**C. Lógica de SCORE (une visual↔Fase 2↔EA)** — cómo la "importancia visual" ES el mismo score de confluencia direccional: un nivel donde se apilan conceptos en el punto estructural correcto suma score; la **precisión de la proyección** (¿el precio reaccionó donde se proyectó?) retroalimenta el score. Pensar el score como **proyección verificable** (backward-read → forward-projection → outcome), no un peso estático.

**D. Modelo de pensamiento de cada AGENTE del enjambre** — cada agente debe, por cada concepto que ve: leer **qué pasó atrás** (contexto estructural) y **proyectar hacia adelante** (escenarios/casos posibles) bajo confluencia. Definir ese "protocolo de lectura+proyección" común (encaja con ADR-012 protocolo de razonamiento del agente) para que todos hablen el mismo idioma de proyección.

**E. Agente decisor en MT5** — tendrá un **"cuaderno de confluencias"**: debe saber proyectar y **tomar decisiones con el pasado + el futuro** (dónde reaccionará el precio, a qué draw apunta, con qué confluencia). Definir el formato del cuaderno y cómo consume la doctrina B/C.

**F. Impacto en el SWARM (debate + evolución de score)** — el enjambre debe **debatir**: cada agente entrega **su proyección**; la que se **cumple con mayor exactitud** sube su score (selección darwiniana por precisión de proyección). Definir el mecanismo (encaja con ESQUELETO-P2 del enjambre: confluencia no consenso, olas de 3, darwiniano por score) y cómo se mide "exactitud de proyección" contra el outcome real.

## 6. Restricciones que el esqueleto debe respetar
- CORE byte-idéntico (SHA `5510361166844bd5`); todo lo visual en Visual; lo que sea detección/score en el CORE (ADR-014, frontera).
- Anti-repaint (`isconfirmed`+`lookahead_off`); RE10045-safe (sin `array.push` en dibujo MTF); símbolo-agnóstico (todo ×ATR); no inflar las 42 confluencias; números congelados Fase 3 (defaults razonables); un commit = un concepto verificado; ningún gate se salta.
- El esqueleto se rellena luego bajo el gate `sprint16` (regla cuantificada + casos EURUSD antes de codificar).

## 7. Pregunta abierta para Fable
¿Cómo estructurar esto para que la **misma doctrina** (leer atrás + proyectar adelante bajo confluencia) sea la única fuente de verdad que alimente, sin duplicarse: (1) el render Pine, (2) el score direccional, (3) el cuaderno del EA, y (4) el protocolo de debate del enjambre? Ese es el orden que buscamos.

# DOSSIER PARA FABLE — Rediseño integral del SISTEMA VISUAL del indicador SMC/ICT

> **Documento autocontenido.** Fable no tiene acceso al repositorio; toda la información necesaria está embebida aquí. El usuario (Freddy) adjuntará **screenshots del chart en vivo** cuando entregue este dossier en el chat con Fable.
>
> **Rol de Fable en esta entrega:** revisor integral de la CAPA VISUAL. No implementa Pine. **Produce el ESQUELETO COMPLETO del sistema visual** (spec de diseño con slots `[impl]`) que elimine la problemática descrita. **Claude Code rellena/implementa** ese esqueleto después, bajo los gates del proyecto (patrón dossier→esqueleto→relleno ya usado en el proyecto).
>
> **Fecha:** 2026-07-02 · Sesión S083 · Rama `pine/sistema-completo`. CORE ~1647 líneas, SHA `0ae1f9de2ea3cd23`, compila 0 errores / 0 warnings los 3 archivos, core-sync OK. Archivos: `SMC-Visual.pine` (3790 líneas), `SMC-Strategy.pine` (2468), `SMC-Library.pine` (1531).

---

## 0. TL;DR — Qué te pedimos

El indicador **detecta y dibuja bien**, pero **dibuja DEMASIADO**: hoy el chart en vivo (OANDA:EURUSD H1) tiene **502 líneas + 502 etiquetas** simultáneas de ~40 conceptos en 12 familias. Los conceptos se **solapan** (el grid azul de Gradient/Premium-Discount cae encima del sombreado de Kill Zones; las etiquetas se amontonan al mismo precio) y **no hay jerarquía**: un swing menor grita igual de fuerte que un Order Block institucional con displacement y sweep previo.

Ya tenemos un plan interno (§6 de nuestro handoff, anexado en la **Parte E**) basado en un motor de "fuerza" (`strength`) → 3 niveles → modos de densidad → antisolape. **Queremos que lo critiques y, sobre esa base, entregues el esqueleto completo del sistema visual definitivo**, cubriendo cuatro frentes:

1. **Jerarquía por fuerza** — cómo se decide qué es Primario/Secundario/Terciario.
2. **Curación (anti-ruido)** — QUÉ conceptos merecen tinta y cuáles viven solo en el panel/colapsados.
3. **Sistema de color/estilo/etiquetas** — paleta coherente, tipografía de labels, formas, transparencias.
4. **Antisolape + z-order + panel T14** — cómo conviven las 12 familias sin taparse.

Todo respetando las **restricciones duras** (Parte D). Los pesos/umbrales quedan **congelados hasta la Fase 3** (calibración); tú defines la ESTRUCTURA, no los números finales.

---

## 1. Contexto mínimo del proyecto (para que entiendas el terreno)

**Estrategia 2.0** es un bot de trading **SMC/ICT** (Smart Money Concepts / Inner Circle Trader) para Forex. Primero se construye y valida un sistema completo en **TradingView (Pine Script v6)**; después se traduce a un **Expert Advisor nativo en MQL5**. Estamos en la **Fase 1** (detección de conceptos), con el gate visual F1 ya aprobado para los ejes 0/1/3; este trabajo es el **Eje 2 "Fuerza" / orden visual**, el último del gate visual.

**Arquitectura (no re-litigar):** 1 núcleo de detección + 2 consumidores.
- **`=== LIBRARY CORE ===`**: toda la detección como **funciones puras + UDTs**. No dibuja, no llama `request.security()`. Este bloque es **byte-idéntico** entre los dos consumidores (regla dura).
- **`SMC-Visual.pine`** (`indicator`): dibujo + panel de estado + alertas. **Todo el dibujo vive aquí, FUERA del CORE.**
- **`SMC-Strategy.pine`** (`strategy`): scoring direccional + entradas/SL/TP → Strategy Tester.

**Implicación clave para ti:** el motor de `strength` que grada las marcas debe vivir en el CORE (byte-idéntico, puro, anti-repaint); **el dibujo/estilo/jerarquía visual vive solo en Visual** y NO rompe la sincronización del core. Tu esqueleto debe respetar esa frontera.

---

## 2. LA PROBLEMÁTICA (el corazón del encargo)

### 2.1 Sobrecarga cuantificada
Estado vivo capturado hoy (OANDA:EURUSD, H1, indicador "SMC Engine — Visual"):
- **502 líneas horizontales** dibujadas simultáneamente.
- **502 etiquetas** (`label.new`) simultáneas.
- ~40 conceptos activos repartidos en 12 familias (inventario completo en Parte C).

### 2.2 Solapes concretos (síntomas)
- **Grid azul de Gradient Levels (§5.16) + Premium/Discount encima del sombreado de Kill Zones.** El grid (quadrants LQ/EQ/UQ + eighths 1/8…7/8 + Premium/Discount) y el sombreado de sesión ocupan la misma franja de precio/tiempo → se ensucian mutuamente.
- **Etiquetas amontonadas al mismo nivel de precio.** Ej.: al precio 1.14 conviven labels de OB, IFVG, BPR, NWOG, NDOG, NYMO, MB, FVG, BOS(D1), CHoCH(D1), EQH… todas apiladas.
- **Sin distinción de procedencia MTF.** Marcas heredadas de D1/H1 dibujadas en TF menor no siempre rotulan su timeframe origen (pendiente diferido, ver Parte D).

### 2.3 Falta de jerarquía (el problema de fondo)
No hay forma de que el ojo distinga **relevancia**. Un swing interno de 3 velas, un EQH tocado 2 veces y un Order Block con displacement + sweep previo + alineado al bias se dibujan con el mismo peso visual. El operador no puede leer "qué importa AHORA" de un vistazo.

### 2.4 Lo que NO es el problema
La **detección** está validada (scores ≥90 con `smc-validator-agent` en el gate F1). No te pedimos cambiar qué se detecta ni los umbrales de detección (§0–§5, congelados). El problema es **puramente de presentación**: cuánto se dibuja, con qué prioridad, con qué estilo y cómo se evita el solape.

---

## 3. Qué queremos como resultado (tu entregable)

Un **esqueleto completo del sistema visual** en Markdown, autosuficiente, que Claude Code pueda rellenar/implementar concepto a concepto. Debe incluir (mínimo):

1. **Modelo de jerarquía visual** — la regla determinista que mapea (fuerza + relevancia + presupuesto de tinta) → {Primario / Secundario / Terciario}. Critica o reemplaza nuestra propuesta §6.1.
2. **Política de curación por familia** — para cada una de las 12 familias: ¿se dibuja siempre / según fuerza / solo en panel / colapsada? Anti-ruido explícito.
3. **Sistema de color y estilo** — paleta por familia y por dirección (alcista/bajista/neutro), transparencias por nivel de jerarquía, formas (caja/línea/marca), tipografía y longitud de etiquetas.
4. **Reglas de antisolape** — z-order entre familias, alternado de etiquetas izquierda/derecha, presupuesto top-N por familia, desplazamiento vertical de labels colisionantes.
5. **Modos de densidad** — perfiles (p.ej. Operación / Estudio / Todo) y qué se ve en cada uno.
6. **Contrato con el panel T14** — qué se relega al panel cuando no se dibuja (contadores por familia).
7. **Slots `[impl]`** — cada sección marcada con lo que Claude Code debe decidir/cablear en Pine, sin implementación.
8. **Checklist de verificación visual** — criterios medibles de "quedó bien" (p.ej. "≤ N etiquetas por franja de precio", "0 familias solapadas en modo Operación").

**Formato:** sigue el estilo de nuestros esqueletos (fichas por concepto/familia, tablas de decisión, restricciones al final). Marca todo peso/umbral como **candidato CONGELADO hasta Fase 3**.

---

## PARTE C — INVENTARIO COMPLETO DE LO QUE SE DIBUJA HOY

12 grupos de inputs (`GRP_*`) y sus conceptos. Cada concepto tiene un toggle `i_show*` y, muchos, un cap `i_maxShow*` de marcadores recientes.

### C.1 Estructura (`GRP_STRUCT`)
- Swings HH/HL/LH/LL (`i_showSwings`); estructura dominante swing=50 (`i_showMajor`).
- BOS/CHoCH de swing (`i_showStruct`) e interno (`i_showInternal`, off por defecto).
- MSS = CHoCH + displacement (`i_showMSS`).
- Flips (cambio de rol §2.8, `i_showFlip`, cap 20).
- CISD (cambio estado de entrega §5.6, `i_showCISD`, cap 20).

### C.2 Contexto / ICT (`GRP_CTX`)
- Displacement (`i_showDisp`, cap 20).
- Rejections (rechazo en nivel §2.7, `i_showRej`, cap 20).
- EMAs 20/50/200 (`i_showEMA`) + cruces (`i_showEmaCross`, cap 20) + rebotes (`i_showEmaBounce`) + Stack Flip 20&50 vs 200 (`i_showEmaStack`).
- Tramos Impulsivo/Correctivo (§4.4, `i_showLegs`, cap 20).
- Inside Day (compresión D1 §5.12, `i_showInsideDay`, cap 10).

### C.3 Order Blocks (`GRP_OB`)
- Order Blocks (`i_showOB`).
- Breakers (OB invalidado §2.6, `i_showBreaker`).
- Mitigation Blocks (§2.8 #24, `i_showMB`).
- Vacuum Blocks (§5.7, `i_showVacuum`).
- (Propulsion = flag sobre OB, no dibujo propio.)

### C.4 Fair Value Gaps (`GRP_FVG`)
- FVG (`i_showFVG`) + nivel CE 50% (`i_showCE`).
- IFVG (FVG invertido §5.2, `i_showIFVG`).
- BPR (solape FVG opuestos §5.3, `i_showBPR`).
- Immediate Rebalance (§5.4, `i_showIR`, cap 20).
- Volume Imbalance (§5.5 micro, `i_showVI`, off por defecto, cap 15).
- IPR (rango desbalanceado §5.9, `i_showIPR`).
- (True FVG y gradedFvg = flags de calidad sobre el FVG, no dibujo propio; hoy añaden sufijo textual "·g".)

### C.5 Premium/Discount (`GRP_PD`)
- Premium/Discount/Equilibrium (`i_showPD`), swing rango dominante 50, banda equilibrium ±5%.

### C.6 Gradient Levels (`GRP_GRAD`, §5.16) — el que más solapa
- Grid del rango-fuente (`i_showGradient`): quadrants LQ/EQ/UQ + Premium/Discount + eighths 1/8, 3/8, 5/8, 7/8 (`i_gradEighths`).
- Selección de fuente P1 (dealing range) / P2 (suspension diario) / P3 (opening gaps) + ghost/persistencia.

### C.7 Equal Highs/Lows (`GRP_EQHL`)
- EQH/EQL clusterizados (`i_showEQHL`).

### C.8 Liquidez (`GRP_LIQ`)
- Pools BSL/SSL (`i_showPools`) + pools barridos historial (`i_showSwept`).
- Sweeps / trampa / Spring / Raid (`i_showSweeps`, cap 20).
- False Breakouts (§3.7 #14, `i_showFalseBreak`, cap 20).
- IDM (inducement interno, `i_showIDM`, cap 20).
- Judas (trampa de sesión §3.5, `i_showJudas`, cap 20).

### C.9 Kill Zones / Sesiones (`GRP_KZ`)
- Sombreado de Kill Zone activa (`i_showKZ`), perfil FX-London-NY / FX-Asia / None.
- Gaps de apertura NWOG/NDOG/NYMO (§5.10, `i_showOpenGaps`) + Breakaway Gaps (cap 10).
- Macros intradía ICT (§5.14, `i_showMacros`, off).
- RTH/ETH (§5.15, `i_rthEnable`, off; para índices/futuros).

### C.10 OTE / Golden Pocket (`GRP_OTE`)
- OTE / Golden Pocket (Fib 50/61.8/79, `i_showOTE`).
- Standard Deviation projections (§5.11, `i_showStdDev`, off).

### C.11 Mapa MTF (`GRP_MTF`)
- Zonas/eventos heredados de HTF (D1/H1) dibujados en el TF activo con anclaje temporal (`xloc.bar_time`), cap 0–10 por concepto (ADR-010).

### C.12 Panel (`GRP_PANEL`)
- Panel de estado T14 (`i_showPanel`) con columnas por TF (D1 | H1 | actual): Bias, Bias dominante, Premium/Discount, último BOS/CHoCH/MSS, OB/FVG/Pool cercano, último Sweep, EMA 20/50/200, EQ H/L, Kill Zone. Modo compacto disponible.

---

## PARTE B — SNAPSHOT DE DATOS VIVOS (evidencia textual; screenshots los pasa el usuario)

**Panel T14 en vivo (OANDA:EURUSD H1, hoy):**

| Fila | D1 | H1 (dom.50) | H1 |
|---|---|---|---|
| Bias | ▼ Bajista | ▼ Bajista | ▼ Bajista |
| Premium/Discount | Discount 9% | Discount 24% | Discount 24% |
| Último BOS | 1.14997 · 17-06 21:00 | — | 1.14095 · 30-06 14:00 |
| Último CHoCH | 1.16551 · 14-05 21:00 | — | 1.13827 · 01-07 12:00 |
| Último MSS | 1.18080 · 22-01 22:00 | — | 1.13827 · 01-07 12:00 |
| OB cercano | [1.15726, 1.16221] | — | [1.14150, 1.14367] |
| FVG cercano | [1.15283, 1.15748] | — | [1.14096, 1.14124] |
| Pool cercano | 1.13246 SSL | — | 1.14119 BSL ·3 |
| Último Sweep | 1.13604 ↓ | — | 1.13722 ↑ |
| EMA 20/50/200 | ⬇⬇⬇ | — | ⬇⬇⬇ |
| EQ H/L | 4 | — | 100 |
| Kill Zone | — | — | London (1ª½) |

**Grid Gradient (P1 dealing range, vivo):** Premium 1.16221 / UQ 1.15477 / 7/8 / 5/8 / EQ 1.14733 / 3/8 / LQ 1.13990 / 1/8 / Discount 1.13246. (Rango-fuente H1 [1.13246, 1.16221].)

**Nota:** la fila "EQ H/L = 100" en H1 y las 502 líneas/labels ilustran la sobrecarga: hay clusters EQH/EQL y niveles muy por encima de lo legible.

---

## PARTE D — RESTRICCIONES DURAS (innegociables; tu diseño debe cumplirlas)

1. **Anti-repaint.** Eventos solo en `barstate.isconfirmed`; nada del futuro. El `strength` solo cambia al cierre de vela (no recalcular intra-vela). `request.security(..., lookahead = barmerge.lookahead_off)` siempre.
2. **Core byte-idéntico.** El bloque `=== LIBRARY CORE ===` es idéntico entre Visual y Strategy. El motor de fuerza (si toca el CORE) exige `check-core-sync.ps1` + nuevo SHA. **El dibujo/estilo/jerarquía vive FUERA del CORE (solo en Visual).**
3. **Funciones puras en el CORE.** Nada de estado global oculto; todo entra por parámetros.
4. **Símbolo-agnóstico (ADR-001).** Nada hardcodeado a EURUSD ni a pips fijos. Umbrales relativos a **ATR(14)**. Lo por-símbolo va como input/perfil.
5. **No inflar confluencias.** Hay **42 confluencias canónicas**. Una variante que *refina* otro concepto (True FVG, Propulsion, gradedFvg) **NO** suma confluencia nueva: eleva la `strength` del concepto base (anti-doble-conteo, FIX P-05).
6. **Pesos/umbrales CONGELADOS hasta Fase 3.** Cualquier número que propongas es **candidato**; se calibra en Fase 3 con split IS/OOS. Tú defines la estructura y valores por defecto razonables, no los finales.
7. **Compila 0 errores / 0 warnings** o no se commitea. Un commit = un concepto verificado.
8. **Reutilizar, no reinventar.** Ya existen: `f_nearestN`/`f_nearestNPools` (top-N por cercanía, base del presupuesto de tinta), `SMC_Zone.state`/`mitigatedPct`/`trueFvg`/`propulsion`/`gradedFvg` (base de fuerza), `f_detectDisplacement` (primitivo de fuerza), panel T14 (destino de lo no dibujado), ~43 toggles `i_show*` (perfiles de densidad por familia), cadena de invalidación ADR-012 Q1–Q7. Tu diseño debe apoyarse en estos primitivos.
9. **3 pendientes MTF diferidos** (no bloquean, pero tu diseño debe contemplarlos): (a) rótulo de TF `(D1)`/`(H1)` en BOS/CHoCH heredados/fusionados; (b) cuadre fino de EQH/EQL HTF↔LTF; (c) exactitud vela-a-vela de OB/FVG heredados.

---

## PARTE E — NUESTRO PLAN INTERNO §5/§6 (ANEXADO PARA TU CRÍTICA)

> Esto es lo que ya diseñamos. **Critícalo, mejóralo o reemplázalo** — no estás obligado a respetarlo. Es el punto de partida para converger rápido.

### E.1 Motor de fuerza `strength` (CORE, byte-idéntico)
Añadir `float strength = 0.0` a los UDTs `SMC_Zone`, `SMC_Event`, `SMC_Swing`, `SMC_Pool`. Dos funciones puras nuevas, calculadas solo al cierre, reusando el `atr14` ya disponible:

- **`f_zoneStrength(zone, curPrice, atr14, biasDir)`** — suma ponderada normalizada a [0,1] de primitivos ya disponibles:

| Primitivo | Peso cand. | Mapa a [0,1] |
|---|---|---|
| rango ×ATR / displacement | 0.30 | `min(rangeAtr/3, 1)`; pleno si hay displacement |
| cuerpo% | 0.15 | `(bodyPct−0.5)/0.5` clamp |
| frescura / `state` (0/1/2/3) | 0.20 | activa=1 · parcial=0.5 · mitigada/inval=0 |
| sweep previo | 0.15 | binario |
| distancia al nivel ×ATR | 0.10 | `1 − min(distAtr/2, 1)` |
| alineación con bias | 0.10 | 1 coincide · 0.5 neutro · 0 en contra |
| flags refinamiento (trueFvg/propulsion) | bonus +0.10 | eleva el base (no suma confluencia) |

- **`f_eventStrength(event, rangeAtr, bodyPct, hadSweep, biasDir)`** — solo `rango×ATR`(0.40) + `cuerpo%`(0.20) + `sweep previo`(0.20) + `alineación`(0.20).
- **Swing/Pool** (inline): swing = escala(0.5) + frescura(0.3) + alineación(0.2); pool = `min(touches/3,1)`(0.5) + ¬swept(0.3) + cercanía(0.2).

### E.2 Quantización a 3 niveles
`f_strengthLevel(s) => s >= 0.66 ? 2 : s >= 0.33 ? 1 : 0` → alta/media/baja. (No confundir con el cap 0–10 MTF ni con el nivel visual.)

### E.3 Nivel visual (Visual, fuera del CORE)
`f_visualLevel(sLevel, withinCap) => not withinCap ? 0 : sLevel` → **Primario=2 / Secundario=1 / Terciario=0**:
- **Primario**: render completo (caja/línea sólida + etiqueta). Fuerza alta **y** dentro del cap top-N.
- **Secundario**: atenuado (~60% transparencia, etiqueta corta). Fuerza media o lejano.
- **Terciario**: oculto del chart, **contado** en panel T14. Fuerza baja **o** fuera del cap.

### E.4 Master input de densidad `i_densidad`
`["Operación", "Estudio", "Todo"]`:
- **Operación** (default): solo Primario → chart limpio para trading en vivo.
- **Estudio**: Primario + Secundario → análisis.
- **Todo**: + Terciario → depuración/verificación graduada.
- Filtro transversal: cada bloque de dibujo añade `and f_visualLevel(...) >= umbral` junto a su `i_show*` existente (los `i_show*` se mantienen; `i_densidad` es un filtro adicional).
- **Z-order por familia** (fondo→frente): contexto/PD → zonas → liquidez → estructura/eventos. Anti-solape de etiquetas: `style_label_left`/`right` alternado por lado del nivel.
- **Presupuesto de tinta:** top-N por familia con `f_nearestN`/`f_nearestNPools`; el resto incrementa el contador de la familia en el panel T14.

### E.5 Preguntas abiertas donde más necesitamos tu criterio
1. ¿Es correcto que la fuerza determine sola la jerarquía, o hay conceptos que deben ser Primarios siempre (p.ej. el bias dominante, la estructura grande) independientemente de su fuerza calculada?
2. El grid Gradient + P/D es un "fondo" de referencia continua, no marcas puntuales. ¿Cómo debe convivir con el sombreado de Kill Zones (mismo espacio precio/tiempo)? ¿Cambiar uno a un pane/estilo distinto, o reglas de transparencia/prioridad?
3. Con 12 familias, ¿el modo "Operación" debería mostrar TODAS las familias en Primario, o solo un subconjunto curado (p.ej. solo estructura + zonas cercanas + liquidez inmediata)?
4. ¿Cómo debe verse la procedencia MTF (D1/H1) sin duplicar tinta con lo nativo del TF activo?
5. Sistema de color: ¿por familia, por dirección, por fuerza, o una combinación? ¿Qué prioridad cuando chocan?
6. ¿Qué métricas objetivas definen "chart legible" (para el checklist de verificación)?

---

## PARTE F — GLOSARIO MÍNIMO (por si algún término no te es familiar)

- **BOS/CHoCH/MSS**: Break of Structure / Change of Character / Market Structure Shift (eventos de estructura).
- **OB/FVG/CE**: Order Block / Fair Value Gap / Consequent Encroachment (50% del FVG).
- **BSL/SSL**: Buy-side / Sell-side Liquidity (pools).
- **EQH/EQL**: Equal Highs / Equal Lows.
- **Gradient Levels**: grid de octavos (eighths) + quadrants de un rango-fuente (dealing range / suspension diario / opening gap) que pre-ubica las PD arrays (doctrina ICT 2026).
- **Kill Zone**: ventana horaria de alta probabilidad (London/NY).
- **Premium/Discount/Equilibrium**: mitades cara/barata/equilibrio de un rango.
- **MTF**: Multi-timeframe (herencia de conceptos de TF mayores).
- **strength / cap / nivel visual**: tres escalas distintas — fuerza 0–1 (scoring), cap 0–10 (relevancia MTF), nivel {Primario/Secundario/Terciario} (render).

---

*Fin del dossier. Entregable esperado de Fable: el esqueleto completo del sistema visual (§3), que Claude Code rellenará bajo los gates del proyecto.*

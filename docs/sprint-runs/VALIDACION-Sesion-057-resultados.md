# Validación visual graduada — Sesion-057 (resultados)

> Ejes **0/1/3** (Eje 2 fuerza diferido a Paso 4). Metodología: `docs/METODOLOGIA-VERIFICACION-VISUAL.md`. Lista: `PLAN-VALIDACION-Sesion-049.md`.
> EURUSD, MCP TV. Aislar concepto (todo `i_show*`=OFF salvo el suyo) → screenshot → datos Pine → score.

## Mapeo toggle → input id (MCP `indicator_set_inputs`, entity `JIXYBm`)
El MCP mapea por `id` interno `in_N` (orden de `input()` en el Pine), NO por nombre de variable.

| Variable | id | Variable | id | Variable | id |
|---|---|---|---|---|---|
| i_showPanel | in_0 | i_showOB | in_39 | i_showPD | in_73 |
| i_showMajor | in_5 | i_showBreaker | in_42 | i_showEQHL | in_76 |
| i_showSwings | in_6 | i_showMB | in_43 | i_showPools | in_79 |
| i_showStruct | in_7 | i_showVacuum | in_45 | i_showSwept | in_82 |
| i_showInternal | in_8 | i_showOTE | in_47 | i_showSweeps | in_83 |
| i_showMSS | in_9 | i_showStdDev | in_51 | i_showFalseBreak | in_86 |
| i_showFlip | in_10 | i_showFVG | in_56 | i_showIDM | in_89 |
| i_showCISD | in_12 | i_showCE | in_58 | i_showJudas | in_91 |
| i_showDisp | in_17 | i_showIFVG | in_59 | i_showKZ | in_95 |
| i_showRej | in_22 | i_showBPR | in_60 | i_showOpenGaps | in_96 |
| i_showEMA | in_26 | i_showIR | in_63 | i_showMacros | in_99 |
| i_showEmaBounce | in_31 | i_showVI | in_67 | i_rthEnable | in_100 |
| i_showEmaCross | in_32 | i_showIPR | in_70 | i_showD1 | in_103 |
| i_showEmaStack | in_33 | | | i_showH1 | in_104 |
| i_showLegs | in_35 | | | i_smtEnable | in_113 |
| i_showInsideDay | in_37 | | | | |

Config (no son toggles de dibujo): in_1 panel min, in_20 disp contracción, in_41 mitig cierre, in_112 sweep marca △, in_115 SMT inversa.

## Resultados por concepto

| # | Concepto | § | TF | Eje0 | Eje1 | Eje3 | Veredicto | Firma |
|---|---|---|---|---|---|---|---|---|
| 1 | Swings HH/HL/LH/LL | §1.1/1.2 | H1(+D1/M5) | ✅ | ✅ HH/HL/LH/LL coherentes | N/A primitivo | **PASS** | pend. |
| 2 | BOS/CHoCH swing | §1.3/1.4 | H1 | ✅ CHoCH 06-01 @1.161 | ✅ BOS≠CHoCH | ✅ sweep 05-27 ≠ BOS | **PASS** | pend. |
| 3 | Estructura interna | §1.4 | H1 | ✅ escala fina punteada | ✅ ≠ swing | N/A | **PASS** | pend. |
| 4 | Estructura dominante (50) | §1.4 | H1 | ✅ línea BOS▼ larga, confirma 06-05 | ✅ ≠ swing/interna | N/A | **PASS** | pend. |
| 5 | MSS | §1.5 | H1 | ✅ "CHoCH MSS" 06-01 13:00 (panel 1.16416) | ✅ MSS=CHoCH+disp | ✅ 05-29 cuerpo63% ≠ MSS | **PASS** | pend. |

**TIER 1 — smc-validator-agent: 96/100 APROBADO** (agentId ae6e51b1cb4d1d7b4). Coherencia MTF ✅ (panel D1/H1/M5 todos ▼ Bajista). Eje 2 (fuerza) diferido a Paso 4.

| 6 | Order Block | §2.1 | H1 pres | ✅ cajas OB/OB↑ | ✅ ≠ Breaker/MB | ✅ mitig. por cierre | **PASS** | pend. |
| 7 | FVG + CE | §2.2 | H1 pres | ✅ zonas FVG + CE 50% | ✅ | ✅ umbral 0.25×ATR | **PASS** | pend. |
| 8 | True FVG | §5.1 | H1 pres | ✅ etiqueta "T.FVG" | ✅ ≠ FVG normal (vela media disp) | N/A flag | **PASS** | pend. |
| 9 | Premium/Discount/Eq | §2.3 | H1 pres | ✅ líneas range (re-captura) | ✅ banda eq | N/A | **PASS** | pend. |
| 10 | EQH/EQL | §2.4 | H1 hist | ✅ EQH 05-27, EQL 06-03 conectores | ✅ ≠ HH/LL (umbral 0.1×ATR) | N/A | **PASS** | pend. |
| 11 | OTE/Golden Pocket | §2.5 | H1 pres | ✅ zona dorada en última pierna BOS | ✅ solo sobre BOS | ✅ expira con nuevo BOS | **PASS** | pend. |
| 12 | Breaker | §2.6 | H1 pres | ✅ caja "BRK↓" púrpura | ✅ ≠ OB/MB color | ✅ solo de OB invalidado | **PASS** | pend. |
| 13 | Rejection | §2.7 | H1 pres | ✅ ≥10 "Rej↑/↓" en mechas | ✅ | ✅ mecha≥2×cuerpo + toca nivel | **PASS** | pend. |
| 14 | Flip | §2.8 | H1 pres | ✅ "FLIP↓" nivel 1.1482 | ✅ por cierre limpio ≠ sweep | ✅ retest respetado | **PASS** | pend. |
| 15 | Mitigation Block | §2.8#24 | H1 pres | ✅ cajas "MB" azul-acero | ✅ ≠ OB/Breaker color | ✅ sin sweep previo | **PASS** | pend. |

**TIER 2 — smc-validator-agent: 94/100 APROBADO** (agentId a45c3b388f130fc95). Hallazgo método: **Bar Replay de TV es de PAGO/no disponible** → conceptos modo-presente (dibujan en `barstate.islast`) se validan en barras recientes (06-15→06-24), no encuadrando al pasado. Históricos (EQH/EQL) sí encuadrados a la ventana de casos. T09/T11 re-capturados con frame ajustado.

| 16 | Pools BSL/SSL | §3.1 | M5 pres | ✅ "BSL -3" + panel | ✅ touches≥2 | ✅ barrido deja de ser imán | **PASS** | pend. |
| 17 | Sweep (trampa) | §3.2 | M5 pres | ✅ "Sweep↑/↓"/"Raid" | ✅ Sweep/Spring/Raid texto | ✅ requiere pool confirmado | **PASS** | pend. |
| 18 | IDM inducement | §3.6 | M5 pres | ✅ cadena "IDM↑/↓" | ✅ ≠ sweep mayor | ✅ grab interno | **PASS** | pend. |
| 19 | Judas | §3.5 | M5 pres | ✅ (escaso, esperado §3.5) | ✅ sweep KZ+disp | ✅ ≤6 velas | **PASS** | pend. |
| 20 | False Breakout | §3.7 | M5 pres | ✅ "FB↑/↓" | ✅ | ✅ reversión ≤2 velas | **PASS** | pend. |
| 21 | Kill Zones | §3.4 | M5 pres | ✅ sombreado Londres(azul)/NY(naranja) | ✅ por sesión | N/A (no bloquea) | **PASS** | pend. |

**LIQUIDEZ (§3) — smc-validator-agent: 95/100 APROBADO** (agentId a0fa685f97238147b). Follow-up no bloqueante: §3.3 "Grab" no es función nombrada separada (implícito en IDM/sweep) — trazabilidad de nombre, no fallo funcional.

| 22 | Displacement | §4.1 | H1 pres | ✅ marcadores "⚡Disp↑/↓" | ✅ rango≥1.5×ATR+cuerpo≥70% | ✅ filtro contracción | **PASS** | pend. |
| 23 | EMAs estado 20/50/200 | §4.3 | H1 | ✅ 3 líneas, stack bajista | ✅ | N/A | **PASS** | pend. |
| 24 | EMA rebote #41 | §4.3 | H1 pres | ✅ "EMA↓" en rechazos | ✅ mecha≥2×cuerpo | ✅ alineado bias | **PASS** | pend. |
| 25 | EMA cruce par #40 | §4.3 | H1 pres | ✅ "×20x50/50x200" | ✅ ≤20 velas | N/A | **PASS** | pend. |
| 26 | EMA Stack Flip | §4.3 | H1 pres | ✅ "⊙Stack↓" en flip | ✅ ≠ cruce aislado | ✅ transición régimen | **PASS** | pend. |
| 27 | Impulsivo/Correctivo | §4.4 | H1 pres | ✅ "IMP/CORR↑↓" | ✅ disp+BOS alineado | N/A | **PASS** | pend. |

**CONTEXTO/EMAs (§4) — smc-validator-agent: 6/6 PASS.** Inicial 88 (agentId a13ea21145922f879) por T22 sin marcadores en ventana tendencial; re-validado T22 = 96/100 PASS (agentId a843ae3e489cd08ef): NO bug — el filtro `i_dispContraction` (default ON) exige 3 velas comprimidas previas; en tendencia fuerte rara vez se cumple (correcto, modelo ICT expansión-tras-acumulación). Con filtro OFF, displacement abundante y bien ubicado. **Nota protocolo:** al testear T22 en ventanas tendenciales, considerar `i_dispContraction`.

| 28 | IFVG | §5.2 | H1 pres | ✅ zonas "IFVG" | ✅ ≠ FVG | ✅ FVG→invalid | **PASS** | pend. |
| 29 | BPR | §5.3 | H1 pres | ✅ 0 cajas H1+M5 = ausencia legítima (S057) | (código ✅ agente) | — | **PASS** (sin instancia activa) | pend. |
| 30 | Immediate Rebalance | §5.4 | H1 pres | ✅ "IR↑/↓" | ✅ | ✅ cierre ≤50% | **PASS** | pend. |
| 31 | Volume Imbalance | §5.5 | M5 pres | ✅ 2 cajas micro (S057 verify) | ✅ ≠ Vacuum (micro) | — | **PASS** | pend. |
| 32 | CISD | §5.6 | H1 pres | ✅ "cisd↓" | ✅ | ✅ cierre cruza open-origen | **PASS** | pend. |
| 33 | Propulsion Block | §5.8 | H1 pres | ✅ "OB⇈" anidado | ✅ ≠ OB normal | ✅ solape≥50% | **PASS** | pend. |
| 34 | Vacuum Block | §5.7 | H1 pres | ✅ "VAC" ~1.148 (1 caja, S057 verify) | ✅ ≠ VI (salto grande) | — | **PASS** | pend. |
| 35 | IPR | §5.9 | H1 pres | ✅ 0 cajas H1+M5 = ausencia legítima (S057) | (código ✅ agente) | — | **PASS** (sin instancia activa) | pend. |
| 36 | Inside Day | §5.12 | D1 pres | ✅ marcadores "ID" | ✅ h1<h2 & l1>l2 | N/A | **PASS** | pend. |
| 37 | Std Dev (herramienta) | §5.11 | H1 pres | ✅ 4 líneas proyección k=−1/−2/−2.5/−4 (S057) | ✅ | N/A | **PASS** | pend. |
| 38 | Open Gaps NWOG/NDOG/NYMO | §5.10 | H1 pres | ✅ líneas etiquetadas | ✅ 3 tipos | ✅ gapMin 0.5×ATR | **PASS** | pend. |
| 39 | Macros intradía | §5.14 | M5 pres | ✅ bandas NY AM/Lunch | ✅ ventanas canónicas | N/A | **PASS** | pend. |
| 40 | SMT Divergence | §5.13 | M5 pres | ✅ "SMT↑/↓" vs GBPUSD | ✅ corr+ (ADR-011) | ✅ smtTol=3 | **PASS** | pend. |
| 41 | Herencia MTF D1/H1 | §4.2/ADR-010 | M5 pres | ✅ D1/H1 OB/FVG/PD/bias anclados bar_time | ✅ solo HTF→LTF | ✅ presupuesto top-N | **PASS** | pend. |

**TIER 3 GAP ICT (§5) + MTF — smc-validator-agent: 93/100 APROBADO** (agentId af9e05f1cd7db011e). Regla→código 100% correcto en las 14 funciones (umbrales idénticos). 4 "REVISAR" (BPR/VI/Vacuum-frontera/IPR/StdDev): NO fallos — condición intrínsecamente rara no presente en ventana reciente, o toggle OFF por diseño (VI/StdDev son herramientas no-confluencia). Candidatos a re-captura con ventana dedicada si se quiere evidencia visual extra. **#41 MTF** valida ADR-010 (D1/H1 anclados por bar_time en M5).

### Hallazgos de método (S057)
- **Captura validación = `region:full`** (incluye eje de tiempo+precio). `region:chart` recorta el eje X → agente no puede correlacionar píxel→fecha (causó rechazo previo 88/100).
- **Esperar 8s tras cada cambio de TF Y tras cada toggle** (3s da captura stale del concepto anterior).
- **MSS no visualizable aislado** (modificador que reetiqueta CHoCH→"CHoCH MSS"): capturar con i_showStruct+i_showMSS.
- Encuadrar con `chart_set_visible_range` a la ventana del caso (H1 Tier1: 05-26→06-09 cubre todos los casos+contraejemplos).
- `data_get_pine_labels verbose` → price redondeado 2 decimales + x=bar_index: insuficiente. Usar panel T14 (`data_get_pine_tables`) para fecha-hora exacta.

### Evidencia capturada (disco: `D:\CODE\BOT\Bot\tradingview-mcp-jackson\screenshots\`)
- **Tier 1 primaria (framed-full H1, 05-26→06-09):** `S057_T01_swings_H1_f.png`, `S057_T02_struct_H1_f.png`, `S057_T03_internal_H1_f.png`, `S057_T04_major_H1_f.png`, `S057_T05_mss_H1_f.png`.
- Escala MTF (region chart, D1/H1/M5 por concepto): `S057_T0[1-5]_*_D1/H1/M5.png`.

---

## Verificación post-validación (S057) — REVISAR resueltos + dudas del usuario

### Conceptos "REVISAR" del §5 — TODOS resueltos
Método: aislar toggle, comprobar instancia vía `data_get_pine_boxes`/`data_get_pine_lines` (no rounding-dependiente para presencia) en H1 y M5. El método se validó porque Vacuum/VI/StdDev SÍ devolvieron objetos (la detección por datos funciona) → los 0 de BPR/IPR son ausencia real.
- **BPR (§5.3):** 0 cajas en H1 y M5 → **ausencia legítima** (no hay solape FVG-opuesto activo en el mercado actual; concepto raro, código ya verificado por agente). Sin replay no se puede forzar un caso histórico.
- **IPR (§5.9):** 0 cajas en H1 y M5 → **ausencia legítima** (condición restrictiva ≥3 FVG mismo lado/10 velas no presente ahora).
- **Volume Imbalance (§5.5):** 2 cajas micro en M5 → **PASS** (instancias presentes; escala micro, visualmente sutiles). `S057_T31_vi_M5_verify.png`.
- **Vacuum Block (§5.7):** 1 caja "VAC" ~1.148 → **PASS**. `S057_T34_vacuum_H1_verify.png`.
- **Std Dev (§5.11):** 4 líneas horizontales de proyección (k=−1/−2/−2.5/−4) → **PASS** (proyecta objetivos; herramienta, no confluencia). `S057_T37_stddev_M5_verify.png`.

### Pools SSL/BSL — ciclo de vida y "siguiente target" (duda usuario)
- **Confirmado:** los pools persisten; tras un sweep el barrido deja de ser target activo y los **no barridos** (BSL arriba / SSL abajo) siguen dibujados; el panel "Pool cercano" avanza al siguiente. `S057_pools_lifecycle_M5_verify.png` (BSL-3 arriba + SSL-3 abajo simultáneos).
- **Asimetría (p.ej. 4 BSL arriba / 1 SSL abajo) = esperada en tendencia bajista:** el precio va barriendo SSL abajo (se los come) y deja BSL sin tocar arriba. Lectura SMC correcta, no bug.
- **Agotamiento de SSL locales → escalado MTF (CLAVE):** cuando se barren todos los SSL de la TF actual, el sistema NO queda a ciegas: la herencia MTF (`f_drawMTFZones`, [SMC-Visual.pine:3198-3200](pine/SMC-Visual.pine)) dibuja **"D1: SSL" / "H1: SSL"** como targets profundos. Verificado: con MTF on, "D1: SSL" ~1.121 (panel D1 SSL 1.12105) aparece abajo como el draw on liquidity profundo. `S057_pools_mtf_ssl_verify.png`. **Comportamiento deseado YA existe vía MTF (default on); en modo aislado de validación no se ve porque MTF está off.** Sin cambio de código.

### NWOG/NDOG/NYMO — follow-up T30 (decisión S057: aceptar single-level en Fase 1)
La spec §5.10 pide "**serie de niveles**" (múltiples gaps de apertura como S/R + estado de mitigación). La implementación guarda **un solo nivel por tipo** (`var float nwogLvl/ndogLvl/nymoLvl`, sobrescrito en cada frontera; sin tracking de mitigación ni historial). La línea es horizontal y correcta. **Decisión usuario: aceptar single-level en Fase 1; completar la "serie" + mitigación como follow-up T30** (cambio de consumidor Visual+Strategy, no toca `f_classifyOpenGap` de la Library). PASS condicionado de Fase 1.

### Premium/Discount — decisión S057: mantener Opción A
Observación del usuario (rango "camina" hacia el precio; 3 discounts amontonados; D1 con retraso de cierre diario) = **Opción A operando como diseñada**, no bug. Confirma el disparador de revisit Fase 3 hacia Opción B/híbrido. Documentado en [`decisiones-pd-rango.md` §"Nota S057"](../decisiones-pd-rango.md). Micro-pulido cosmético del "% fuera de rango" diferido/opcional.

**Estado F1-GATE:** 40 conceptos + #41 MTF validados (Ejes 0/1/3; Eje 2 fuerza diferido a Paso 4). **✅ FIRMADO POR EL USUARIO (2026-06-24, S057)** — gate cerrado, tag `fase-1-gate-completa`. Follow-ups NO bloqueantes: NWOG serie (T30); P/D Opción B revisit (Fase 3).

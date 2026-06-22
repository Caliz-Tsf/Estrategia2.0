# Plan de validación 1-a-1 (set completo) — Sesion-049

> **Metodología (decisión Freddy, S048):** validar cada concepto **aislado** — el supervisor (Claude) apaga TODOS los `i_show*` vía MCP `indicator_set_inputs` y enciende **solo** la familia/concepto en turno. Así se ve el caso real al 100% (dónde está, dónde debe verse, qué es y qué no), sin ruido de tarjetas/nombres de otros conceptos.
>
> **Clave:** apagar un toggle solo oculta el DIBUJO, **no la detección** (los arrays se siguen poblando; las dependencias entre conceptos quedan intactas). Por eso aislar es seguro y los cálculos reales no cambian.
>
> **Mecanismo:** Claude controla los toggles por MCP (no manual). Por cada concepto: símbolo **EURUSD**, TF de su § (abajo), `chart_scroll_to_date` a las fechas de los casos ✓/✗ documentados en `reglas-smc-ict.md`, `capture_screenshot`, y `smc-validator-agent` puntúa **≥90** contra la regla (criterio del workplan F1-GATE).
>
> **Aplica a TODOS los conceptos** (Tier 1 + Tier 2 + liquidez + contexto + Tier 3 gap), no solo los nuevos.

## Procedimiento por paso
1. Claude: `indicator_set_inputs` → todos los `i_show*` = false **excepto** el/los toggle(s) del concepto (y `i_showPanel` opcional para leer valores).
2. Claude: `chart_set_symbol EURUSD` + `chart_set_timeframe` (TF de la fila).
3. Claude: `chart_scroll_to_date` a la(s) fecha(s) del caso → `capture_screenshot`.
4. Claude: invoca `smc-validator-agent` con la captura + la § de la regla → score.
5. Freddy: confirma visualmente (✓ está donde debe / ✗ no aparece donde no debe). Si <90 → diagnóstico y retroceso (no se ajusta el criterio).

## Lista ordenada (toggle ON = solo ese; resto OFF)

### A. Tier 1 — Estructura (§1) · TF H1
| # | Concepto | § | Toggle(s) ON | Casos |
|---|---|---|---|---|
| 1 | Swings HH/HL/LH/LL | §1.1 | `i_showSwings` | pivotes visibles vs velas |
| 2 | BOS / CHoCH swing | §1.3/§1.4 | `i_showStruct` | §1 casos H1 |
| 3 | BOS / CHoCH interno | §1.4 | `i_showInternal` | escala fina |
| 4 | Estructura dominante (50) | §1.4 | `i_showMajor` | swing grande |
| 5 | MSS | §1.5 | `i_showMSS` | 06-01 13:00 (3.5×ATR) |

### B. Tier 2 — Zonas (§2) · TF H1
| # | Concepto | § | Toggle(s) ON | Casos |
|---|---|---|---|---|
| 6 | Order Block | §2.1 | `i_showOB` | §2.1 |
| 7 | FVG + CE | §2.2 | `i_showFVG`,`i_showCE` | §2.2 (etiqueta "FVG") |
| 8 | **True FVG** | §5.1 | `i_showFVG` | etiqueta "T.FVG" (vela media disp); 10/34 en H1 |
| 9 | Premium/Discount/Eq | §2.3 | `i_showPD` | rango dominante |
| 10 | EQH / EQL | §2.4 | `i_showEQHL` | §2.4 |
| 11 | OTE / Golden Pocket | §2.5 | `i_showOTE` | pierna 06-04→06-08; GP 1.15781 |
| 12 | Breaker | §2.6 | `i_showBreaker` | OB invalidado 06-01 13:00 |
| 13 | Rejection | §2.7 | `i_showRej` | 06-08 09:00, 05-27 12:00 |
| 14 | Flip | §2.8 | `i_showFlip` | nivel 1.16452 (05-27) |
| 15 | Mitigation Block | §2.8 #24 | `i_showMB` | 06-02 04:00 (sin sweep previo) |

### C. Liquidez (§3) · TF M5 (sweeps/pools también H1)
| # | Concepto | § | Toggle(s) ON | Casos |
|---|---|---|---|---|
| 16 | Pools BSL/SSL | §3.1 | `i_showPools` (+`i_showSwept`) | clusters ≥2 toques |
| 17 | Sweep (trampa) | §3.2 | `i_showSweeps` | + Spring/Raid (texto cambia) 06-11 17:15-17:25 |
| 18 | IDM (inducement) | §3.6 | `i_showIDM` | M5 06-11 06:05 / 17:25 |
| 19 | Judas | §3.5 | `i_showJudas` | M5 06-11 06:05 London |
| 20 | False Breakout | §3.7 | `i_showFalseBreak` | M5 06-11 17:20 |
| 21 | Kill Zones | §3.4 | `i_showKZ` | M5 ventanas London/NY |

### D. Contexto / ICT / EMAs (§4) · TF H1 (macros M5)
| # | Concepto | § | Toggle(s) ON | Casos |
|---|---|---|---|---|
| 22 | Displacement | §4.1 | `i_showDisp` | H1 06-05 12:00 (5.27×ATR) |
| 23 | EMAs estado | §4.3 | `i_showEMA` | alineación bajista 06-08→11 |
| 24 | EMA rebote #41 | §4.3 | `i_showEmaBounce` | mecha en EMA |
| 25 | EMA cruce par #40 | §4.3 | `i_showEmaCross` | 20×50 / 50×200 |
| 26 | EMA Stack Flip | §4.3 | `i_showEmaStack` | flip 06-02 20:00 / 05-29 12:00 |
| 27 | Impulsive/Corrective | §4.4 | `i_showLegs` | IMP 06-04→08 / CORR 06-09→10 |

### E. Tier 3 — Gap ICT (§5) · TF H1 (salvo nota)
| # | Concepto | § | Toggle(s) ON | Casos |
|---|---|---|---|---|
| 28 | IFVG | §5.2 | `i_showIFVG` | 27 FVG invalidados en H1 |
| 29 | BPR | §5.3 | `i_showBPR` | 15 solapes; 05-28, 05-29 |
| 30 | Immediate Rebalance | §5.4 | `i_showIR` | 11 en H1 (05-27 07:00…) |
| 31 | Volume Imbalance | §5.5 | `i_showVI` | 13 en H1 (micro; subir cap si hace falta) |
| 32 | CISD | §5.6 | `i_showCISD` | 8 en H1; 06-05 12:00, 06-09 08:00 |
| 33 | **Propulsion Block** | §5.8 | `i_showOB` | etiqueta "OB⇈" (OB anidado) |
| 34 | Vacuum Block | §5.7 | `i_showVacuum` | **frontera/fin de semana**: dom 05-31, 06-07 |
| 35 | IPR | §5.9 | `i_showIPR` | 5 ventanas; tramos de impulso |
| 36 | Inside Day | §5.12 | `i_showInsideDay` | 05-31, 06-02, 06-11 (marcador al cambio de día) |
| 37 | Std Dev (herramienta) | §5.11 | `i_showStdDev` | proyección de objetivos (no confluencia; validar que proyecte bien) |
| 38 | Gaps apertura NWOG/NDOG/NYMO + BAG | §5.10 | `i_showOpenGaps` | **frontera**: NWOG dom 05-31/06-07 |
| 39 | Macros intradía | §5.14 | `i_showMacros` | **M5**; ventanas NY canónicas |
| 40 | SMT Divergence | §5.13 | `i_smtEnable` (+ GBPUSD) | **requiere GBPUSD**; M5/H1 |
| — | RTH/ETH | §5.15 | `i_rthEnable` | **N/A en FX 24h** (validar en índice/futuro, Fase 5) |

### F. MTF (mapa cascada) · TF M5 con D1/H1 heredados
| # | Concepto | Toggle(s) ON | Casos |
|---|---|---|---|
| 41 | Herencia D1/H1 (bias+P/D+zonas) | `i_showD1`,`i_showH1` | EURUSD M5; ver D1/H1 anclados |

## Notas
- **Frontera/fin de semana** (Vacuum, NWOG): solo aparecen en el salto de sesión/semana; validar en domingos del dataset (05-31, 06-07).
- **SMT**: encender `i_smtEnable` + confirmar GBPUSD disponible en el feed (ADR-011, correlación positiva).
- **RTH/ETH**: no aplica a EURUSD (24h); queda para validar con un índice/futuro en Fase 5.
- **Std Dev**: es herramienta de SL/TP, no confluencia → la "validación" es que los niveles proyectados caigan donde la fórmula dice, no un score de confluencia.
- Cierre del set = **F1-GATE**: cada concepto ≥90 + anti-repaint (2 días) + performance (20k barras). Sin saltarse ningún gate (regla dura #8).

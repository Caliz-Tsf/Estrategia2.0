# Matriz de cobertura de conceptos — Mentores (ICT/SMC) vs sistema 2.0

> **Qué es:** inventario de TODOS los conceptos que enseñan los mentores cruzado contra `docs/reglas-smc-ict.md` (el núcleo codeable del sistema). Es el insumo que **Opus Max** integra al plan maestro de Pine: los conceptos que falten deben pasar por el **mismo proceso** que todos (spec cuantificada → detección Pine → validación ≥90 → confluencia en scoring §4.8), para que **Pine y el EA los vean, identifiquen y calculen**.
> **Base:** temario completo de "No soy liquidez" (64 eps — el más ICT-exhaustivo de los mentores). Profittrading/TJ/Fedex añaden pocos conceptos nuevos (más SMC-estándar); se reconcilian al analizar sus fichas. **Boxxocode = automatización-EA, va aparte** (no es concepto de gráfico).
> **Leyenda:** ✅ tenemos · 🔶 variante/parcial de un concepto que sí tenemos · ❌ falta. Cero invención: clasificación por el título/temario; el detalle fino lo confirma la ficha al transcribir.

---

## A. Resumen
- **✅ Cubiertos:** ~16 · **🔶 Variantes/parciales:** ~12 · **❌ Faltan:** ~24.
- El gap es real y grande: un mentor ICT habla de ~25-30 términos que hoy NO están en el gráfico. Hay que integrarlos para que el mentor no cite cosas que el sistema no detecta.

## B. Tabla maestra (concepto del mentor → estado vs reglas-smc-ict.md)

| # | Concepto (mentor) | Estado | Nuestro § | Tipo de integración |
|---|---|---|---|---|
| 1 | Order Block | ✅ | §2.1 | — |
| 2 | Mitigation Block | ✅ | §2.8 | — |
| 3 | Breaker Block | ✅ | §2.6 | — |
| 4 | Fractality / Market Structure | ✅ | §1.1–1.2 | — |
| 5 | FVG (SIBI/BISI) | ✅ | §2.2 | (SIBI/BISI = nombres ICT del imbalance) |
| 6 | MSS | ✅ | §1.5 | — |
| 7 | **Vacuum Block** | ❌ | — | **primitiva nueva** (gap por apertura/noticia) |
| 8 | Liquidity Run BSL/SSL | ✅ | §3.1 | — |
| 9 | Rejection Block | ✅ | §2.7 | — |
| 10 | EQH / EQL | ✅ | §2.4 | — |
| 11 | OTE / Fibonacci | ✅ | §2.5 | — |
| 12 | **Power of 3 (AMD)** | ❌ | — | **modelo/contexto** (acumulación-manipulación-distribución; compone Judas+displacement) |
| 13 | **Propulsion Block** | ❌ | — | **primitiva nueva** (OB dentro de OB, continuación) |
| 14 | **SMT Divergence** | ❌ | — | **primitiva nueva — requiere dato de símbolo correlacionado** |
| 15 | Premium / Discount | ✅ | §2.3 | — |
| 16 | **IPDA & PD Arrays** | ❌ | — | **framework/contexto** (lookback 20/40/60d; "PD array" = paraguas de nuestras zonas) |
| 17 | **Volume Imbalance** | ❌ | — | **primitiva nueva** (micro-gap entre cuerpos con solape de mechas) |
| 18 | Cómo se crean las velas | n/a | — | educativo, no concepto |
| 19 | NWOG (New Week Opening Gap) | 🔶 | §4.2 | extender §4.2 a nivel-gap de apertura semanal |
| 20 | MSS avanzado | ✅ | §1.5 | — |
| 21 | **IOFED** | ❌ | — | **modelo de entrada** (composición; razonamiento EA) |
| 22 | **IRL vs ERL** | 🔶 | §3.1+§1 | **framework** (liquidez interna/externa de rango; formalizar) |
| 23 | **SIVI / BIVI** | ❌ | — | **primitiva nueva** (variantes de volume imbalance) |
| 24 | Advanced Price Balancing | 🔶 | §2.2/§2.3 | balanceo (relacionado FVG/equilibrium) |
| 25 | Stop Raid | ✅ | §3.7/§3.2 | — |
| 26 | **IFVG (Inversion FVG)** | 🔶 | §2.2 | **variante con comportamiento propio** (FVG roto que invierte rol) |
| 27 | **Immediate Rebalance (IR)** | ❌ | — | **primitiva nueva** (vela sin gap, rebalance inmediato) |
| 28 | NY Lunch Macro | ❌ | §3.4 | **tiempo/macro** (ventanas de minutos; extender killzones) |
| 29 | NY Midnight Open (NYMO) | 🔶 | §4.2 | nivel de apertura específico |
| 30 | Opening Range Gap (ORG) | 🔶 | §4.2 | nivel-gap de apertura |
| 31 | **ICT Entry Model 2022** | ❌ | — | **modelo de entrada** (composición; razonamiento EA) |
| 32 | Turtle Soup | ✅ | §3.7 | (false breakout reversal) |
| 33 | **Low Hanging Fruit** | ❌ | — | **modelo de entrada** |
| 34 | The Order Block | ✅ | §2.1 | — |
| 35 | Reclaimed Order Block | 🔶 | §2.6/§2.1 | variante (OB recuperado) |
| 36 | **Standard Deviation** | ❌ | — | **primitiva/herramienta** (proyección por desviaciones) |
| 37 | Opening Range Macro | ❌ | §3.4 | **tiempo/macro** |
| 38 | NY Lunch Hour Macro | ❌ | §3.4 | **tiempo/macro** |
| 39 | Unicorn Model | 🔶 | §2.6+§2.2 | **composición** (Breaker + FVG solapados) |
| 40 | **PDArray Matrix** | ❌ | — | **framework** (matriz premium/discount de arrays) |
| 41 | **MMXM (Market Maker Model)** | ❌ | — | **modelo completo** (composición de fases) |
| 42 | NDOG (New Day Opening Gap) | 🔶 | §4.2 | nivel-gap de apertura diaria |
| 43 | **CISD (Change in State of Delivery)** | ❌ | — | **primitiva nueva** (cambio por cierre; pariente de CHoCH/MSS) |
| 44 | Killzones / Profiles | ✅ | §3.4 | — |
| 45 | **Breakaway Gap (BAG)** | ❌ | — | **primitiva nueva** (gap de ruptura) |
| 46 | **Balanced Price Range (BPR)** | ❌ | — | **primitiva nueva** (FVGs opuestos solapados) |
| 47 | Fair Valuation | 🔶 | §2.3 | (relacionado equilibrium) |
| 48 | Liquidity Swap vs Run | 🔶 | §3.1/§3.2 | formalizar distinción swap/run |
| 49 | **Draw on Liquidity (DOL)** | ❌ | — | **sesgo direccional clave** (hacia dónde es atraído el precio; alimenta bias/EA) |
| 50 | MSS vs MSB | ✅ | §1.4/§1.5 | — |
| 51 | Displacement Phase | ✅ | §4.1 | — |
| 52 | **Early Buyer & Early Seller** | ❌ | — | concepto del mentor (escrutar valor) |
| 53 | **Gray Pool Theory** | ❌ | — | teoría propia (escrutar valor) |
| 54 | **HRLR (High Resistance Liquidity)** | ❌ | — | **framework** (calidad de liquidez) |
| 55 | **LRLR (Low Resistance Liquidity)** | ❌ | — | **framework** (calidad de liquidez) |
| 56 | Dealing Range | ✅ | §2.3 | — |
| 57 | **RTH vs ETH** | ❌ | — | **tiempo/sesión** (horario regular/extendido; futuros) |
| 58 | **Event Horizon** | ❌ | — | teoría propia (escrutar valor) |
| 59 | **NFP Protocol** | ❌ | — | **NOTICIAS → gate determinista (ADR-005), no confluencia de gráfico** |
| 60 | **IPR (Imbalanced Price Range)** | ❌ | — | **primitiva nueva** (rango de precio desbalanceado) |
| 61 | True FVG (T.FVG) | 🔶 | §2.2 | variante (FVG "verdadero" dentro de rango) |
| 62 | **Price Delivery Continuum** | ❌ | — | teoría (escrutar valor) |
| 63 | **Silver Bullet** | ❌ | — | **modelo time-based** (ventanas de 1h específicas) |
| 64 | **Inside Day** | ❌ | — | **patrón diario** |

## C. Clasificación por TIPO de integración (para Opus Max)

Lo que falta NO es todo "primitiva nueva de Pine". Se separa así:

1. **Primitivas nuevas de detección (Pine debe verlas/calcularlas)** → entran por el pipeline estándar (spec §reglas-smc-ict.md → `f_detect*` → validación ≥90 → confluencia §4.8): Vacuum Block, Propulsion Block, Volume Imbalance (+SIVI/BIVI), Immediate Rebalance, BPR, CISD, Breakaway Gap, IPR, Standard Deviation, IFVG (variante propia), True FVG, niveles-gap de apertura (NWOG/NDOG/ORG/NYMO como serie). **SMT Divergence** = primitiva pero **requiere dato de símbolo correlacionado** (decisión de arquitectura aparte).
2. **Sesgo / contexto direccional** → alimentan el bias/scoring, no son zonas: Draw on Liquidity (DOL), IRL/ERL, HRLR/LRLR (calidad de liquidez), IPDA (rangos de lookback), PDArray Matrix.
3. **Modelos de entrada (composiciones)** → NO son primitivas; son cómo se COMBINAN primitivas + timing → encajan en el **motor de razonamiento del EA** (scoring que generaliza, ADR-007): IOFED, ICT Entry Model 2022, Low Hanging Fruit, Unicorn, MMXM, Silver Bullet, Power of 3.
4. **Tiempo / sesión / macro** → extender §3.4 Kill Zones: NY Lunch/Midnight/Opening-Range macros, RTH vs ETH.
5. **Noticias** → NO es confluencia de gráfico: NFP Protocol = el **gate funcional determinista** de ADR-005.
6. **Teorías propias del mentor (escrutar)** → Gray Pool, Event Horizon, Price Delivery Continuum, Early Buyer/Seller, Advanced Price Balancing, Fair Valuation: verificar contra la ficha si aportan algo medible o son reempaque de lo existente (campo 9 "Conflictos con el sistema").

## D. Reglas de integración (innegociables — para Opus Max)
- Cada concepto nuevo pasa por el **proceso completo** (no atajos): definición cuantificada en `reglas-smc-ict.md` con casos reales EURUSD → `f_detect*` puro (golden test MQL5) → compila 0/0 + core-sync → validación ≥90 → confluencia ponderada en §4.8.
- **ADR-002:** umbrales/pesos congelados hasta Fase 3 → se define la *mecánica* del concepto, su peso se calibra en Fase 3 (IS/OOS). NO se "ajusta" a ojo.
- **No inflar las 42 confluencias sin criterio:** Opus Max decide cuáles conceptos nuevos son confluencias propias y cuáles refinan una existente, sin romper el scoring ya validado.
- Símbolo-agnóstico (ADR-001); anti-repaint (D-PINE-03).

## E. Pendiente de confirmar
- Profittrading / TJ / Fedex: al analizar sus fichas, añadir a esta matriz los conceptos que aporten que no estén aquí (se espera que sean pocos y SMC-estándar).
- El detalle por concepto (definición exacta del mentor) se rellena con la transcripción + ficha (campo 9).

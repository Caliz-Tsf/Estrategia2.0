> ⚠️ **SUPERSEDED (2026-06-10):** este documento fue reemplazado por [WORKPLAN-MAESTRO-V2.md](WORKPLAN-MAESTRO-V2.md). Se conserva solo como histórico.

# Plan: Bot SMC/ICT — TradingView → MetaTrader 5

## Contexto

Construir un bot de trading completo basado en Smart Money Concepts (SMC) y SMC ICT para el mercado Forex. El punto de partida es un indicador Pine Script v5 de LuxAlgo (`Indicador Trading View SMC.txt`) que ya implementa los conceptos SMC básicos. El objetivo final es un Expert Advisor (EA) en MT5 que opere de forma autónoma.

**Restricciones clave:**
- Mercado: Forex (pares de divisas)
- Timeframes: D1 (contexto + confluencias grandes), H1 (bias principal + estructura), M5 (entrada)
  - **H1 es el timeframe de bias principal** para tomar decisiones de entrada
  - **D1 es bias complementario**: se considera cuando hay eventos/confluencias importantes sucediendo en D1 (BOS swing, CHoCH, toma de liquidez, FVG activo, etc.)
- Risk management: R:R fijo mínimo 1:3, con trailing hacia extensión máxima calculable
- Sistema de entrada: scoring de confluencias con umbral mínimo (pesos a definir al final, tras validación)
- Flujo: iterativo por fases — un solo par al inicio (EURUSD), validar antes de ampliar

---

## FASE 0 — Preparación del entorno (ANTES de cualquier código)

### 0.1 — Instalar herramientas (pendiente)
El usuario compartirá su lista de MCPs, agentes y skills a instalar:
- MCP de TradingView Desktop (para operar TV desde Claude directamente)
- Skills de investigación y otros que el usuario defina
- Agentes especializados si aplica

### 0.2 — Documento de Reglas de Mercado (`docs/reglas-smc-ict.md`)
Fuente de verdad antes de escribir una sola línea de código. Define exactamente:
- ¿Cuántas barras confirman un swing?
- ¿Qué % de ATR define un FVG válido vs ruido?
- ¿Qué distingue un CHoCH de un BOS?
- ¿Qué eventos se consideran "grandes" para transferencia entre TFs?
- Cada concepto con su regla de detección cuantificable

### 0.3 — Reglas de desarrollo (`docs/reglas-dev.md`)
1. **Modularidad**: cada concepto SMC en función propia, sin código inline
2. **Naming**: prefijo `SMC_` para todas las variables del sistema
3. **Control de versiones**: cada cambio funcional en commit separado con descripción
4. **Test**: validar visualmente en **un solo par** (EURUSD) hasta que toda la lógica esté estable; solo expandir a más pares una vez todo esté confirmado
5. **Sin cambios en funciones base** sin aprobación previa
6. **Arrays con límite explícito**: todos los arrays con `maxSize` definido (nunca ilimitados)
7. **Comentario en cada función**: propósito + parámetros de entrada + valor de retorno
8. **No romper alertas existentes**: las 16 alertas del indicador base se mantienen

---

## FASE 1 — Indicador Capa 1: Visualización SMC/ICT completa

### Objetivo
Identificar, calcular y dibujar TODOS los conceptos SMC/ICT relevantes en los tres timeframes, con un panel de estado que registre precio, fecha y hora de cada evento detectado.

### Archivo base
`Indicador Trading View SMC.txt` — Pine Script v5 LuxAlgo con:
- ✅ BOS/CHoCH (internos y swing)
- ✅ Order Blocks (internos y swing, con mitigación por close o high/low)
- ✅ Fair Value Gaps (con soporte MTF vía `request.security()`)
- ✅ Equal Highs/Lows
- ✅ Premium/Discount/Equilibrium
- ✅ Strong/Weak Highs & Lows
- ✅ Niveles diarios/semanales/mensuales
- ✅ 16 alertas configuradas

---

### 1.1 — Conceptos a agregar por Tier

**TIER 1 — Críticos (primer sprint)**

| Concepto | Estado | Descripción |
|----------|--------|-------------|
| Swing High/Low | ✅ base | Ya implementado |
| BOS interno/swing | ✅ base | Ya implementado |
| CHoCH interno/swing | ✅ base | Ya implementado |
| Order Blocks (internos + swing) | ✅ base | Ya implementado |
| OB Mitigation | ✅ base | Ya implementado |
| Fair Value Gaps | ✅ base | Ya implementado |
| FVG Mitigation | ⚠️ parcial | Agregar tracking explícito + marcado visual de FVGs mitigados (igual que OBs) |
| Equal Highs/Lows | ✅ base | Ya implementado |
| Premium/Discount/Equilibrium | ✅ base | Ya implementado |
| Strong/Weak Highs & Lows | ✅ base | Ya implementado |
| Liquidity Pool | ❌ nuevo | Zonas de stops acumulados sobre EQH / bajo EQL; detectar clustering de niveles |
| Liquidity Sweep | ❌ nuevo | Precio toca pool y cierra de vuelta adentro del rango (false breakout + wick) |
| Kill Zones | ❌ nuevo | Ventanas horarias: Tokyo (00-02 GMT), London (08-10 GMT), NY (13-15 GMT) |
| HTF Structure alignment | ⚠️ parcial | Existe MTF para FVG; extender para BOS/CHoCH/OB en todos los TFs |

**TIER 2 — Importantes (segundo sprint)**

| Concepto | Estado | Descripción |
|----------|--------|-------------|
| Market Structure Shift (MSS) | ❌ nuevo | Shift confirmado: patrón HH+HL pasa a LH+LL o viceversa |
| Impulsive / Corrective Move | ❌ nuevo | Detectar movimiento impulsivo (BOS consecutivos misma dirección) vs correctivo |
| Judas Swing | ❌ nuevo | Spike falso que captura stops antes del movimiento real; cierra de vuelta |
| Displacement | ❌ nuevo | Vela expansiva post-consolidación que confirma intención institucional |
| Breaker Block | ❌ nuevo | OB que fue roto: pasa a ser soporte/resistencia de rol opuesto |
| Rejection Block | ❌ nuevo | Candle de rechazo fuerte con wick largo en nivel clave |
| Mitigation Block | ❌ nuevo | OB o FVG parcialmente mitigado que sigue siendo válido |
| Role Reversal / Flip | ❌ nuevo | Resistencia que se convierte en soporte tras ruptura limpia (o viceversa) |
| Inducement (IDM) | ❌ nuevo | Trampa de liquidez menor antes del movimiento institucional real |
| Optimal Trade Entry (OTE) | ❌ nuevo | Zona de retroceso 61.8–79% del swing impulso con confluencia |
| Golden Pocket (Fib 50-61.8%) | ❌ nuevo | Zona Fibonacci 50–61.8% como nivel clave de retroceso |
| EMA 20 / 50 / 200 | ❌ nuevo | Bias con EMA200, momentum con EMA50/EMA20; soporte dinámico |
| EMA Crosses | ❌ nuevo | Cruces entre las 3 EMAs (20×50, 50×200, 20×200) |
| EMA Bounce | ❌ nuevo | Precio toca EMA y rebota → señal de entrada válida |

**TIER 3 — Suplementarios (tercer sprint, evaluar aporte)**

| Concepto | Estado | Descripción |
|----------|--------|-------------|
| Liquidity Grab | ❌ nuevo | Wick que toca nivel pero cierra sin superar (no hay cierre más allá) |
| Liquidity Void | ❌ nuevo | Zonas de precio donde no se ha operado (gaps de sesión) |
| False Breakout | ❌ nuevo | Cierre más allá del nivel seguido de reversión inmediata |
| Raid | ❌ nuevo | Movimiento deliberado con alto volumen a través de nivel y reversión |
| Spring / Shakeout | ❌ nuevo | Toque falso de soporte para disparar stops antes de subida |
| Wyckoff Accumulation / Distribution | ❌ nuevo | Fases A–E de acumulación o distribución |
| Power of Three (AMD) | ❌ nuevo | 3 fases del mercado: Accumulation → Manipulation → Distribution |
| Accumulation / Distribution Phase | ❌ nuevo | Lateralización de baja volatilidad antes del movimiento |
| Compression / Squeeze | ❌ nuevo | ATR muy bajo antes de expansión; velas de rango comprimido |
| Inside Bar | ❌ nuevo | Candle completamente contenida en el rango de la anterior |
| Engulfing | ❌ nuevo | Candle que engloba completamente la anterior (reversión) |
| Volume Surge | ❌ nuevo | Volumen ≥1.5× promedio en breakout → confirma convicción |
| Session Opens (W/M/Q) | ❌ nuevo | Precios de apertura semanal, mensual y trimestral como niveles |

---

### 1.2 — Sistema Multi-Timeframe D1 → H1 → M5

**Principio de transferencia (aplica igual de D1→H1 y de H1→M5):**

Los eventos del timeframe mayor se marcan visualmente en el menor como elementos de fondo diferenciados (color/opacidad/estilo distintos, etiqueta con prefijo "D1:" o "H1:"). Se transfieren **todos** los eventos y conceptos relevantes, incluyendo:

- BOS de swing confirmado (dirección + precio + hora)
- CHoCH de swing confirmado
- FVG activo (no mitigado) — zona sombreada
- OB activo (swing) — zona sombreada
- Liquidity Sweep ejecutado
- Liquidity Pool activo
- Judas Swing detectado
- Displacement detectado
- Kill Zone activa
- MSS detectado
- Inducement detectado
- Cualquier evento de Tier 1 que esté ocurriendo en el TF mayor

**Implementación:**
- D1→H1: `request.security("", "D", ...)`
- H1→M5: `request.security("", "60", ...)`

La representación visual debe ser claramente distinguible del TF propio (fondo semitransparente, borde punteado, etiqueta prefijada).

---

### 1.3 — Panel / Tabla de estado

**Posición**: esquina configurable por el usuario (default: top-right)

**Estructura de la tabla** — cada celda registra: nivel de precio + fecha (YYYY-MM-DD) + hora (HH:MM GMT)

```
| Concepto              | D1                  | H1                  | M5                  |
|-----------------------|---------------------|---------------------|---------------------|
| Bias                  | Bullish / Bearish   | Bullish / Bearish   | Bullish / Bearish   |
| Último BOS            | precio / fecha-hora | precio / fecha-hora | precio / fecha-hora |
| Último CHoCH          | precio / fecha-hora | ...                 | ...                 |
| FVG activo            | nivel / fecha-hora  | ...                 | ...                 |
| OB activo             | rango / fecha-hora  | ...                 | ...                 |
| Liquidity Pool        | nivel / fecha-hora  | ...                 | ...                 |
| Liquidity Sweep       | nivel / fecha-hora  | ...                 | ...                 |
| MSS                   | dirección / fecha   | ...                 | ...                 |
| Judas Swing           | nivel / fecha-hora  | ...                 | ...                 |
| Displacement          | — / sí-no           | nivel / fecha-hora  | sí / no             |
| Kill Zone activa      | —                   | sí / no             | sí / no             |
| EMA 200               | Sobre / Bajo        | Sobre / Bajo        | Sobre / Bajo        |
| EMA 50                | Sobre / Bajo        | Sobre / Bajo        | Sobre / Bajo        |
| EMA 20                | Sobre / Bajo        | Sobre / Bajo        | Sobre / Bajo        |
| EMA Cruce reciente    | par / fecha         | par / fecha         | par / fecha         |
| EMA Rebote reciente   | EMA / fecha-hora    | EMA / fecha-hora    | EMA / fecha-hora    |
| Score confluencia     | —                   | X / max             | X / max             |
```

---

### 1.4 — Almacenamiento de estructuras (arrays con timestamp)

Todos los arrays con `maxSize` explícito. Accesibles desde la Capa 2 vía `request.security()`. Cada concepto tiene su array de almacenamiento:

```pinescript
// Estructura de cada entry: [price_level, bias, bar_time, bar_index, is_active/mitigated, timeframe]

// Estructura de mercado
SMC_activeOBs[]            // OBs activos (internos + swing, todos TFs)
SMC_mitigatedOBs[]         // OBs mitigados (histórico)
SMC_activeFVGs[]           // FVGs activos (todos TFs, con estado de mitigación)
SMC_mitigatedFVGs[]        // FVGs mitigados (histórico)
SMC_recentBOS[]            // BOS recientes (dirección, TF, precio, tiempo)
SMC_recentCHoCH[]          // CHoCH recientes
SMC_recentMSS[]            // Market Structure Shifts
SMC_swingPoints[]          // HH/HL/LL/LH con precio y tiempo

// Liquidez
SMC_liquidityPools[]       // Pools activos (precio, bias, número de confirmaciones)
SMC_sweeps[]               // Liquidity sweeps ejecutados
SMC_liquidityGrabs[]       // Grabs (wick sin cierre más allá del nivel)
SMC_eqHighs[]              // Equal highs activos
SMC_eqLows[]               // Equal lows activos
SMC_judasSwings[]          // Judas swings detectados
SMC_springs[]              // Springs/shakeouts
SMC_falseBreakouts[]       // False breakouts
SMC_raids[]                // Raids detectados

// Imbalances y bloques
SMC_breakerBlocks[]        // Breaker blocks activos
SMC_rejectionBlocks[]      // Rejection blocks
SMC_mitigationBlocks[]     // Mitigation blocks (OB/FVG parcialmente mitigados)
SMC_roleReversals[]        // Flips confirmados (resistencia→soporte o viceversa)

// Premium/Discount/Fibonacci
SMC_oteZones[]             // OTE activos (61.8–79% retracement)
SMC_goldenPockets[]        // Golden Pockets activos (50–61.8%)
SMC_premiumZones[]         // Premium zones por TF
SMC_discountZones[]        // Discount zones por TF

// ICT específico
SMC_displacements[]        // Displacements detectados (precio, dirección, tiempo)
SMC_inducements[]          // IDM detectados
SMC_killZones[]            // Kill zones activas/pasadas del día (London/NY/Tokyo)
SMC_powerOfThree[]         // Fase AMD identificada (A/M/D, precio, tiempo)
SMC_wyckoffPhases[]        // Fases Wyckoff (A–E, tipo acum/distrib, tiempo)
SMC_sessionOpens[]         // Precios de apertura W/M/Q activos

// EMAs
SMC_ema20[]                // Valor EMA 20 + señales de toque/rebote
SMC_ema50[]                // Valor EMA 50
SMC_ema200[]               // Valor EMA 200
SMC_emaCrosses[]           // Cruces (par de EMAs, dirección golden/death, tiempo)
SMC_emaBounces[]           // Toques/rebotes de precio en EMA (nivel, qué EMA, tiempo)
```

---

## FASE 2 — Indicador Capa 2: Motor de decisión

### Objetivo
Indicador separado que consume los arrays de Capa 1 y genera señales de entrada basadas en scoring de confluencias, con R:R mínimo 1:3 y trailing hacia extensión máxima.

---

### 2.1 — Sistema de scoring

> Los pesos exactos se definen **después** de la validación visual en Fase 3. Aquí se establece la arquitectura — no los valores finales.

**Principio:**
- Cada concepto activo suma puntos (peso configurable individualmente por el usuario)
- Threshold de entrada configurable
- **No hay bias obligatorio**: una entrada contraria al bias momentáneo es válida cuando las confluencias (sweep, displacement, CHoCH) justifican el cambio — el scoring lo captura naturalmente
- El bias D1 y H1 suman como confluencias, no como requisitos duros

**Todos los conceptos detectados participan en el scoring — ninguno queda fuera:**

*Estructura de mercado:*
1. CHoCH H1 (swing) confirmado en dirección de entrada
2. BOS H1 (swing) confirmado en dirección de entrada
3. CHoCH M5 confirmado
4. BOS M5 confirmado
5. MSS (Market Structure Shift) detectado
6. Secuencia HH/HL o LL/LH confirmada
7. Impulsive move detectado previo
8. Corrective move detectado (retroceso esperado)

*Liquidez:*
9. Liquidity Pool activo en dirección
10. Liquidity Sweep ejecutado (pool barrido antes de la entrada)
11. Liquidity Grab detectado
12. Equal Highs barridos
13. Equal Lows barridos
14. Judas Swing detectado
15. Spring / Shakeout detectado
16. False Breakout detectado
17. Raid detectado

*Imbalances y bloques:*
18. FVG H1 activo (precio retrocede hacia él)
19. OB H1 activo (precio retrocede hacia él)
20. FVG M5 activo (mitigación como trigger de entrada)
21. OB M5 activo
22. FVG D1 activo (confluencia de gráfica grande)
23. OB D1 activo (confluencia de gráfica grande)
24. Breaker Block detectado en dirección
25. Rejection Block detectado en nivel
26. Mitigation Block detectado
27. Role Reversal (Flip) confirmado en nivel
28. FVG mitigado recientemente (posible zona de rechazo)

*Premium/Discount/Fibonacci:*
29. OTE activo (61.8–79% retracement del swing)
30. Golden Pocket activo (50–61.8%)
31. Precio en Discount Zone H1 (para longs)
32. Precio en Premium Zone H1 (para shorts)
33. Precio en Discount Zone D1 (confluencia grande)
34. Precio en Premium Zone D1 (confluencia grande)
35. Precio en Equilibrium (potencial chop — resta o neutraliza)

*ICT específico:*
36. Displacement previo al setup
37. Inducement (IDM) detectado previo
38. Kill Zone activa (London / NY / Tokyo)
39. Power of Three fase identificada (A / M / D)
40. Wyckoff phase identificada (acumulación → markup, etc.)
41. Session open relevante activo (W/M/Q open como nivel)
42. Evento D1 transferido activo (BOS/CHoCH/Sweep/OB/FVG de D1 en mismo sentido)

*EMAs — todas las combinaciones:*
43. EMA 200: precio por encima (bias alcista largo plazo)
44. EMA 200: precio por debajo (bias bajista largo plazo)
45. EMA 50: precio por encima
46. EMA 50: precio por debajo
47. EMA 20: precio por encima
48. EMA 20: precio por debajo
49. Cruce EMA 20 × EMA 50 (golden = alcista / death = bajista)
50. Cruce EMA 50 × EMA 200 (golden = alcista / death = bajista)
51. Cruce EMA 20 × EMA 200
52. Precio toca EMA 200 y rebota → soporte/resistencia dinámica (entrada válida)
53. Precio toca EMA 50 y rebota → soporte/resistencia dinámica
54. Precio toca EMA 20 y rebota → soporte/resistencia dinámica
55. Las 3 EMAs alineadas en misma dirección (tendencia fuerte confirmada)
56. Confluencia EMA + OB (precio en OB y EMA en el mismo nivel)
57. Confluencia EMA + FVG (precio en FVG y EMA en el mismo nivel)

---

## FASE 2 — Lógica de entrada

```
SI score >= threshold:
  → Generar señal de entrada (LONG o SHORT)
  → SL: debajo/encima del OB o swing más reciente que justifica la entrada
  → TP1: precio SL × 3 (R:R mínimo 1:3)
  → TP_ext: siguiente estructura significativa no mitigada
             (FVG TF mayor, OB TF mayor, swing anterior relevante)
  → Mostrar en gráfico: dirección + score total + lista de confluencias activas
  → Disparar alerta con detalle completo de confluencias (para webhook / MT5)
```

**Nota sobre bias**: el bias D1 y H1 suman al score como confluencias. No son requisitos bloqueantes. Una entrada contra el bias momentáneo puede ser válida si hay sweep + displacement + CHoCH que justifiquen el cambio estructural.

---

## FASE 2 — R:R y gestión de trade

- **R:R mínimo**: 1:3 obligatorio — si no se puede calcular, no se genera señal
- **TP extendido**: calculado hacia siguiente OB/FVG/swing no mitigado en TF mayor
- **Trailing stop**: seguir la estructura (mover SL a BOS previos en M5/H1 conforme avanza el precio)
- **Parciales opcionales**: cerrar 50% en TP1 (1:3), dejar correr el resto con trailing hasta TP_ext

---

## FASE 2 — Señal visual

- Label en barra de entrada con: dirección + score + confluencias listadas
- Líneas horizontales: SL (rojo), TP1 (verde sólido), TP_ext (verde punteado)
- Box de zona de entrada válida

---

## FASE 2 — Registro histórico de confluencias

Array de señales generadas para análisis posterior:
```
{barTime, direction, score, confluences_list[], SL_price, TP1_price, TP_ext_price,
 shadow: "win" | "loss" | "open", RR_achieved}
```
*Nota: Reemplazado "result" por "shadow" en la descripción del objeto para evitar conflictos.*

Tabla secundaria en gráfico: últimas 20 señales con win rate por tipo de confluencia.

---

## FASE 3 — Validación en TradingView

### 3.1 — Backtesting visual (EURUSD únicamente)
- Revisar últimas 500 velas H1
- Documentar cada señal: qué confluencias activaron, resultado, R:R real alcanzado
- Identificar qué confluencias aparecen consistentemente en entradas ganadoras

### 3.2 — Definición de pesos del scoring
- Análisis estadístico de señales ganadoras vs perdedoras
- Asignar pesos proporcionales a la frecuencia de aparición en ganadoras
- Ajustar threshold mínimo
- Documentar en `docs/scoring-weights-v1.md`

### 3.3 — Paper trading
- 30 días mínimo en demo EURUSD
- Registrar cada entrada: confluencias activas, entrada, resultado, R:R

### 3.4 — Criterio de avance a Fase 4
- Win rate ≥ 55% (mínimo 50 señales evaluadas)
- R:R promedio alcanzado ≥ 2.0
- Cero bugs de visualización o cálculo

### 3.5 — Expansión a más pares
- Solo después de cumplir criterios en EURUSD
- Probar en GBPUSD, USDJPY, AUDUSD, USDCAD
- Ajustar si hay diferencias de comportamiento por par

---

## FASE 4 — Expert Advisor MT5 (MQL5)

### 4.1 — Arquitectura EA (reimplementación, no traducción directa de Pine)

```
EA_SMC_ICT/
├── SMC_Structures.mqh    — Detección de todas las estructuras SMC/ICT
├── SMC_MTF.mqh           — Transferencia D1→H1→M5
├── SMC_Scoring.mqh       — Motor de scoring con pesos validados en Fase 3
├── SMC_RiskManager.mqh   — Cálculo lotes, SL, TP (R:R 1:3+), trailing stop
├── SMC_Display.mqh       — Panel visual en MT5
└── EA_SMC_ICT.mq5        — Lógica principal + ejecución de órdenes
```

### 4.2 — Pipeline de validación MT5
1. Strategy Tester con datos históricos (mínimo 2 años EURUSD, tick data)
2. Forward test en cuenta demo live (mínimo 60 días)
3. Live con lote mínimo (0.01) para confirmar ejecución real
4. Escalar capital gradualmente según resultados

---

## Agentes especializados (crear si se necesitan)

| Agente | Responsabilidad |
|--------|----------------|
| SMC Validator Agent | Verifica que el código implemente cada concepto según `docs/reglas-smc-ict.md` |
| Backtesting Analyst Agent | Analiza tabla de señales históricas y sugiere ajustes al scoring |
| MQL5 Translator Agent | Convierte lógica Pine Script a MQL5 preservando semántica exacta |

---

## Verificación por fase

| Fase | Criterio de completitud |
|------|------------------------|
| 0 | Herramientas instaladas, `docs/reglas-smc-ict.md` y `docs/reglas-dev.md` creados y aprobados |
| 1 | Todos los conceptos Tier 1+2 visibles en EURUSD H1; tabla con precio/fecha/hora funcional; sin errores de compilación Pine Script |
| 2 | Señales generadas con score + lista de confluencias + SL/TP dibujados; alertas activas; registro histórico funcionando |
| 3 | Win rate ≥55% con ≥50 señales; R:R promedio ≥2.0; pesos de scoring documentados |
| 4 | EA supera backtesting MT5 con resultados comparables a TradingView; forward test en demo OK |

---

## Siguiente paso inmediato

**FASE 0**: El usuario compartirá la lista de MCPs, agentes y skills a instalar. Una vez instaladas las herramientas, se construirá el documento de reglas SMC/ICT (`docs/reglas-smc-ict.md`) como fuente de verdad antes de modificar cualquier línea de Pine Script.

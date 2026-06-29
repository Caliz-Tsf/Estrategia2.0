# Sesion-063 (2026-06-28)

**Módulo:** MENTOR ICT (paralelo a Pine) — Market Maker Primer + OTE + 2024 iniciado  
**Objetivo:** Continuar BUILD mentor ICT madre (MMP, OTE, 2024 parcial)  
**Fecha:** 2026-06-28

## Completado

**MENTOR ICT (madre) — MAP de MMP (24/24) + OTE (20/20) COMPLETOS ✅ + 2024 INICIADO**

### (A) MMP — Market Maker Primer (24/24 transcripciones destiladas)

**Archivo:** `Mentores/ict/knowledge/mmp.md`  
**Extensión:** ~50KB, 21 secciones  
**Método:** MAP/REDUCE por lotes a disco

#### Conceptos nuevos vs 2022

- **Framework 3-TF por estilo de trader:** estructura múltiple escalas simultáneamente
- **OPENING PRICE como fulcro:** monthly/weekly/daily bias determinado por apertura
- **Key levels rodantes:** yearly (12m) / quarterly / monthly / weekly
- **Asian Range:** 7pm-medianoche NY, reset IPTA, narrow→tendencial
- **OTE Fib settings EXACTOS:** 62/70.5/79, stop EN el low, targets 0/−0.62/−0.27/−1, regla 2:1 primer scaling
- **Niveles algorítmicos:** 00/20/50/80
- **ATM method:** técnica definida
- **COT (Commercials):** rol en estructura
- **Range contraction:** cuerpos > wicks, lookback 5-7d
- **Ventanas KZ exactas NY:**
  - London 2-5am
  - NY 7-9am
  - London Close 10-12
  - London Lunch 5-7am (no-trade)
- **SMT USDX-vs-divisa:** criterio divisa
- **Judas:** secuencia exacta medianoche-5am
- **Money management flat-line drawdown:**
  - 8-loss math
  - Halving strategy
  - Escalera recuperación

### (B) OTE — Pattern Recognition (20/20 vols, modelo refinado)

**Archivo:** `Mentores/ict/knowledge/ote.md`  
**Extensión:** ~30KB  
**Vols leídos en profundidad:** 01, 02, 03, 20  
**Método:** Vol 01 = modelo canonical, Vol 02-20 = ejemplos aplicados

#### Modelo OTE refinado

**Estructura entrada:**
1. Bias PDH/PDL (previous day high/low)
2. Ventana NY 8:30-11am (apertura estricta)
3. Encuadre nivel institucional ±10pips
4. Fibonacci exacto: 62/70.5/79
5. Stop EN el low (no encima)

**Targeting y escalado:**
- 3 parciales obligatorios
- Escalado −0.5/−1/−2
- Regla 100 pips: si supera, siguiente setup
- 3 parciales o no se toma (NO parciales incompletos)

**Stop management:**
- Midpoint (primera liquidez)
- BE (break-even tras primer parcial)
- Market structure (invalidación técnica)

**Aplicación:**
- Funciona en futuros (handles ES/NQ)
- Big-figure-sweep bounce confirmado
- Precisión temporal: ±2 min NY open

#### Divergencia fuerte con proyecto

**OTE dice:** "forget R:R, 1:1 vale por frecuencia"  
**Proyecto dice:** R:R mínimo 1:3 sin excepción (regla dura 5, CLAUDE.md)

**Resolución:** NO adoptar relación 1:1 de OTE. Mantener 1:3. La frecuencia de OTE (entrada múltiple ventana) compensa ratio R:R inferior en su método, pero el proyecto exige cofre determinista. Anotado en memory.

### (C) 2024 Mentorship — MAP INICIADO (50/50 vols, lote 1 completado)

**Archivo:** `Mentores/ict/knowledge/2024.md`  
**Extensión:** scaffold ~15KB + lote 1 contenido  
**Vols totales:** 50  
**Lote 1 completado:** `how-to-avoid-seek-destroy` (1 vol)

#### Era 2024 — Diferencias vs 2022/MMP

- **Instrumento:** NQ/index futures (NO Forex, énfasis handles)
- **Tape-reading:** novedad absoluta (2022/MMP = chart-only)
- **Vocabulario propio:**
  - FPFVG (Fair Price Fresh VG)
  - NDOG (New Day Open Gap)
  - ORG (Opening Range Gap)
  - Consequent-Encroachment
  - IFVG (Internal Fair Value Gap)
  - Silver-Bullet (entrada de precisión)
  - HRLR (High Resistance Low Resistance)

#### Reglas núcleo 2024

- **Displacement obligatorio:** debe salir de PD array para ser válido
- **Time-distortion:** NO operar dentro de inefficiencies (trap zona)
- **Capital preservation 1ª lección:** drawdown management radicalizado

#### Lote 1 contenido

- `how-to-avoid-seek-destroy` — mecánica de trampa institucional + cómo reconocerla (anti-liquidación)

#### Siguientes lotes (51 vols restantes)

**Lectures conceptuales núcleo (estimado 20 vols):**
- how-to-trade-fvgs-correctly
- how-ict-picks-winning-fvgs-orderblocks
- high-resistance-low-resistance-conditions
- how-to-identify-high-resistance-liquidity
- missed-entries
- decoupled-markets
- premarket-concepts
- limit-orders-pinball
- cfds-vs-futures
- micro-vs-mini
- nonfarm-payroll

**Muestra:** lectures 1-21 + muestra tape-reading (especificación pendiente)

### Módulo paralelo

- **0 commits Pine**
- **CORE INTACTO:** 1517 líneas SHA `80fad14dd8d03758`, compila 0/0 los 3, core-sync OK
- **Memoria:** `[[ict-mentor-madre-build]]` actualizada con BUILD state actual

## Bloqueos

Ninguno.

## ADRs

Ninguno (divergencia R:R 1:1 vs 1:3 anotada, NO requiere ADR nuevo).

## Decisiones

- **Divergencia OTE:** mantener R:R 1:3 del proyecto; OTE su justificación = multientrada compensa
- **2024 prioridad:** lectures núcleo > tape-reading > muestra (determinismo antes que cantidad)
- **Documentación:** Vault Obsidian es origen, NO repo

## Pendiente

**SIGUIENTE: 2024 lotes 2+ (lectures conceptuales núcleo + muestra lectures 1-21 + muestra tape-reading) → REDUCE a `ficha-mentor.md`**

- **Ficha-mentor.md:** 9 campos (nombre, especialidad, R:R característico, ventanas preferidas, dinero management, validación setup, frase/muletilla, track-record relativo, lo que opinan compañeros)
- **Integración final:** 2026 + 2022 + MMP + OTE + 2024 → visión 360 mentor ICT

## Notas

- Método MAP/REDUCE mantiene divisas en disco: Sesion-062 (2022), Sesion-063 (MMP+OTE+2024 lote 1)
- 2024 es salto tecnológico: tape-reading + index futures + nuevas reglas
- OTE es patrón standalone (no fusion de prior), Vol 01 es la especificación completa
- MMP es contexto macro + sesiones + money management avanzado
- IPTA = Interbank Transaction Price Authority (reset Asian Range)

# VER-09 — Handoff a Fable (Revisión integral pre-Pine)
> Gate bloqueante antes de Fase 1. Decisión de Freddy (Sesion-001): Fable revisa el sistema
> completo ANTES de escribir una sola línea de Pine. Este doc es el índice de revisión +
> las decisiones abiertas que Freddy quiere que Fable resuelva.

## Qué se entrega (paquete completo Fase 0)
- **DOC-01** [docs/reglas-smc-ict.md](reglas-smc-ict.md) — fuente de verdad SMC, 42 confluencias, **casos reales poblados** (Sesion-008).
- **DOC-02..07** reglas-dev, WORKFLOW-ARQUITECTURA, TV-SMC-WORKFLOW, CLAUDE.md, WORKPLAN-MAESTRO-V2 + docs/workplan/*.
- **ADR-001** multi-símbolo sin filtro horario duro.
- **Infra:** `.mcp.json` (6 MCPs), `rules.json` (morning_brief), 9 skills, 8 agentes, workflow Archon `smc-sprint`, scripts (`scripts/` + `scripts/ver05/` extractor de casos).
- **Verificación Fase 0:** VER-01..08 (ver WORKPLAN §3 y memory/ESTADO-ACTUAL.md).

---

## ⚠️ DECISIONES ABIERTAS PARA FABLE (Freddy pide tu criterio)

Durante VER-05 (poblar los casos reales de `reglas-smc-ict.md` desde el gráfico EURUSD vía TV MCP)
se extrajeron datos reales para los 24 conceptos. **3 conceptos resultaron escasos** en la ventana
de datos disponible. Los casos están poblados con lo real encontrado y marcados in-situ. Freddy quiere
que **leas, apruebes (o no) y le digas la mejor opción** para cada uno antes de pasar a Pine.

**Contexto técnico de la limitación:** `data_get_ohlcv` del TV MCP devuelve solo las ~300 velas
más recientes por timeframe (no alcanza las 2196 históricas ni con `chart_scroll_to_date`). Ventana
efectiva: H1 = 2026-05-25→06-11 (300 velas); M5 = 2026-06-10→06-11 (300 velas, único tramo M5 disponible).
La detección es 100% reproducible: `scripts/ver05/detect*.py` sobre `eurusd_h1.csv` / `eurusd_m5.csv`.

### Decisión 1 — MSS swing (§1.5): 1 ocurrencia limpia
- **Hallazgo real:** 1 MSS swing canónico (2026-06-01 13:00, CHoCH swing + displacement 3.51×ATR, cuerpo 98%).
  El doc pide ≥3. Se añadieron 2 apoyos a escala **interna** (mismo mecanismo, menor escala) + 1 contraejemplo limpio.
- **Lectura propia:** el MSS es por diseño un evento **raro y de alta convicción**; 1 en 300 velas H1 es plausible y
  hasta deseable (si fuera frecuente, el filtro displacement+cuerpo no estaría discriminando).
- **Pregunta a Fable:** ¿aceptas el caso único + apoyos internos como suficiente para la spec, o exiges
  ampliar la ventana (más sesiones H1 históricas, vía otra fuente de datos) antes de codificar `f_detectMSS`?

### Decisión 2 — Judas Swing (§3.5): 1 ocurrencia limpia
- **Hallazgo real:** 1 Judas canónico (London 2026-06-11 06:05: sweep SSL en 1ª mitad de KZ → displacement +1 contrario).
  El barrido épico de las 17:25 (sweep a 1.15030 + rally 6×ATR) es Judas-like pero **fuera de ventana KZ**, así que se
  clasificó honestamente como Spring/sweep (§3.7), no Judas.
- **Causa de escasez:** el Judas requiere (sweep) ∩ (1ª mitad de KZ) ∩ (displacement contrario ≤6 velas M5), y solo hubo
  ~3 sesiones M5 disponibles.
- **Pregunta a Fable:** ¿1 caso limpio basta para fijar la definición, o quieres que la spec de `f_detectJudas` se valide
  con más sesiones M5 en Fase 1 (cuando ya haya gráfico continuo)?

### Decisión 3 — Breaker (§2.6): invalidación sí, retest escaso
- **Hallazgo real:** la **invalidación + flip de polaridad** está documentada con datos reales (OB alcista del 05-29
  invalidado por el `close` 1.16101 del 06-01). Lo que escasea es el **retest limpio** del breaker desde el otro lado,
  porque la ventana fue fuertemente bajista (sin pullbacks profundos a la zona invertida).
- **Pregunta a Fable:** ¿la mecánica de invalidación/flip es suficiente para especificar `f_detectBreaker`, dejando el
  retest para validación visual en Fase 1, o prefieres un caso de retest completo antes?

### Pregunta transversal
¿Hay algún concepto **mejor** poblado de lo necesario, o alguna definición que, vista con casos reales, convenga
**ajustar numéricamente** (umbrales) antes de Pine? Y la pregunta de Freddy: **¿cuál es la mejor opción global**
— proceder a Fase 1 con estas 3 notas como deuda conocida, o invertir una sesión extra en ampliar datos primero?

---

## Estado de las verificaciones al entrar a VER-09
| Check | Estado |
|---|---|
| VER-01 tv_health_check | ✅ |
| VER-02 startup ≤2 ⚠️ | ✅ |
| VER-03 morning_brief | ✅ |
| VER-04 skills/agentes | ✅ (Sesion-007) |
| VER-05 reglas-smc-ict.md | ✅ poblado + aprobado por Freddy (con estas 3 notas a criterio de Fable) |
| VER-06 check-core-sync | ✅ (SCR-03) |
| VER-07 git limpio | ✅ |
| VER-08 Fase 0 COMPLETADA | ✅ |

**Ningún código Pine debe escribirse hasta que Fable cierre este gate.**

---

# ✅ VEREDICTO DE FABLE — GATE VER-09 CERRADO (2026-06-11, Sesion-009)

**APROBADO con correcciones menores (aplicadas en esta misma sesión).** El sistema es coherente: definiciones cuantificadas, casos reales verificables y reproducibles, arquitectura sólida, 42 confluencias direccionales consistentes entre documentos. Nada bloquea Fase 1. Registro formal: `docs/adrs/ADR-002-cierre-gate-ver-09.md`.

## Respuesta a las 4 decisiones

### Decisión 1 — MSS swing: ✅ SUFICIENTE, no ampliar datos ahora
El MSS es un concepto **compuesto**: CHoCH de nivel swing (≥3 casos propios, §1.4) + displacement (≥3 casos propios, §4.1). Cuando los componentes están bien evidenciados, la composición no necesita 3 casos independientes para fijar la spec — la mecánica ya está anclada. Además, 1/300 velas H1 es exactamente la frecuencia esperable de un evento diseñado como "giro con convicción"; si apareciera seguido, el filtro displacement+cuerpo no discriminaría nada.
**Mitigación convertida en criterio medible:** el done de **F1-S1.3-T12** exige acumular **≥3 MSS swing reales** durante la validación visual. Clave técnica: el límite de ~300 velas es **solo del API `data_get_ohlcv`** — el gráfico sí tiene la historia completa vía `chart_scroll_to_date` + screenshots + replay, que es justo lo que usa `smc-validator-agent`.

### Decisión 2 — Judas: ✅ SUFICIENTE, validar con más sesiones M5 en Fase 1
Mismo razonamiento composicional: sweep (§3.2, ≥3 casos) ∩ primera mitad de KZ (§3.4, determinista) ∩ displacement contrario ≤6 velas (§4.1, ≥3 casos). La escasez vino de tener solo ~3 sesiones M5 de ventana — cada día de Fase 1 aporta 2 sesiones KZ nuevas. La clasificación honesta del barrido de las 17:25 como Spring (fuera de KZ) y no como Judas demuestra que la definición discrimina bien, que es lo que importa.
**Criterio medible:** el done de **F1-S1.5-T18** exige **≥3 Judas reales** detectados en sesiones M5 antes de aprobar el concepto.

### Decisión 3 — Breaker: ✅ la invalidación/flip basta para la spec
Lo algorítmicamente nuevo del breaker es la **transición de estado** (OB `state=3` → KIND_BREAKER con `dir` invertido), y eso está documentado con datos reales. El retest no introduce código nuevo: reutiliza la máquina de mitigación del OB (§2.1), validada con ≥3 casos. Esperar un retest limpio solo retrasa sin reducir riesgo de spec.
**Criterio medible:** el done de **F1-S1.5-T19** exige documentar **≥1 retest real** de breaker cuando el mercado lo dé (validación visual, sin bloquear el concepto si la mecánica de flip está correcta).

### Pregunta transversal: ✅ PROCEDER A FASE 1 — no invertir sesión extra en datos
1. Los 3 conceptos escasos son composiciones de primitivos bien evidenciados (arriba).
2. La validación de Fase 1 accede a TODA la historia del chart (scroll/replay) y producirá los casos faltantes **como subproducto natural** del trabajo que igual hay que hacer — una sesión extra de datos ahora duplicaría ese esfuerzo.
3. **Ningún umbral se ajusta antes de Fase 3.** Recalibrar con 300 velas sería ajustar parámetros sobre muestra mínima: exactamente el overfitting que R-03/P-03 prohíben. Los defaults actuales (swingLen 5/3, disp 1.5×ATR/70%, FVG 0.25×ATR, eq 0.1×ATR, etc.) vienen de convenciones LuxAlgo/ICT contrastadas y los casos reales los respaldan; se congelan hasta la calibración IS/OOS.
4. ¿Conceptos mejor poblados de lo necesario? Sí — sweeps, grabs, displacement, EQH/EQL y estructura quedaron con evidencia abundante y de calidad. Ninguna definición necesita ajuste numérico visto lo extraído.

### Decisión derivada — MCP-06 (task-master): ⛔ SE SALTA definitivamente
El WORKPLAN §3 ya es el backlog ejecutable (ID·tarea·ejecutor·done); Archon aporta el motor DAG. Una DB paralela de tareas solo añade riesgo de divergencia. Saltarlo es la salida correcta del gate, como anticipaba la nota de MCP-06.

## Correcciones aplicadas en la auditoría (Sesion-009)
| # | Archivo | Problema → Fix |
|---|---|---|
| C1 | PINE-PLAN §3.1 | `f_detectMSS` descrito como secuencia HH+HL→LH+LL (contradecía reglas §1.5) → alineado a CHoCH swing + displacement |
| C2 | PINE-PLAN §3.4 | `f_sessionOpens` "semanal/mensual/trimestral" → diaria+semanal+mensual (reglas §4.2) |
| C3 | PINE-PLAN §6 | "~50 confluencias" → 42 canónicas (§4.8) |
| C4 | WORKFLOWS.md | Nota de instalación Archon desactualizada → estado real v0.4.x (D:\CODE\Archon, wrapper, issue #1067) |
| C5 | reglas-smc-ict.md | "EN CONSTRUCCIÓN"/aprobación pendiente → POBLADO Y APROBADO + gate cerrado |

## Mejora aportada — paridad Python↔Pine (prefigura los golden tests de Fase 4)
El extractor `scripts/ver05/detect*.py` queda como **herramienta de cross-check algorítmico** en Fase 1: para los conceptos que ya cubre (swings, BOS/CHoCH, MSS, OB, FVG, EQH/EQL, sweeps), correr el detector Python sobre la misma ventana CSV y comparar con las detecciones del Pine en esas velas. Dos implementaciones independientes que coinciden = validación fuerte y barata, y el patrón es exactamente el de los golden tests Pine→MQL5 de Fase 4. Anotado como criterio opcional-recomendado en F1-S1.1/S1.2.

**Limitación de datos registrada:** `data_get_ohlcv` ≈ 300 velas/TF. Para historia: `chart_scroll_to_date` + screenshots + replay (la validación visual NO está limitada). El backtesting masivo va por Strategy Tester (server-side, historia completa — no afectado).

**🔓 Queda desbloqueado F1-S1.1-T01.** Próxima sesión: `/smc-session-startup` → workflow `smc-sprint` con el primer concepto.

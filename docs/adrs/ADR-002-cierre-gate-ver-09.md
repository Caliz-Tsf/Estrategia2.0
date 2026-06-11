# ADR-002 — Cierre del gate VER-09: revisión integral de Fable pre-Pine

- **Estado:** Aceptado
- **Fecha:** 2026-06-11
- **Decisores:** Fable (revisor del gate) + Freddy (usuario)
- **Contexto de fase:** Fase 0 → Fase 1 · gate VER-09 REVISIÓN-FABLE

## Contexto

Al completar la Fase 0 (Bloques A–F + VER-01..08, tag `fase-0-completa`), el gate VER-09 exigía que Fable revisara el sistema completo (DOC-01..07, MCPs, 9 skills, 8 agentes, workflows, scripts) ANTES de escribir una línea de Pine. El handoff (`docs/VER-09-handoff-fable.md`) planteaba 3 decisiones de escasez de casos reales (MSS swing ×1, Judas ×1, breaker sin retest) + la pregunta transversal (proceder vs. ampliar datos), originadas en la limitación del API `data_get_ohlcv` (~300 velas/TF).

## Decisión

**Gate APROBADO con correcciones menores (aplicadas en Sesion-009). Se procede a Fase 1 sin sesión extra de datos.**

1. **MSS, Judas y Breaker se aceptan con la evidencia actual.** Principio aplicado: un concepto **compuesto** cuyos componentes tienen ≥3 casos reales cada uno (CHoCH §1.4, displacement §4.1, sweep §3.2, KZ §3.4, mitigación OB §2.1) no necesita 3 casos independientes propios para fijar su spec. La rareza observada es además coherente con el diseño (eventos de alta convicción).
2. **La deuda se convierte en criterios de done medibles en Fase 1** (no en deuda difusa): T12 acumular ≥3 MSS swing reales · T18 ≥3 Judas reales en sesiones M5 · T19 documentar ≥1 retest de breaker. La validación visual NO sufre el límite de 300 velas: `chart_scroll_to_date` + screenshots + replay acceden a toda la historia del chart.
3. **Ningún umbral se recalibra antes de Fase 3.** Ajustar parámetros con 300 velas = overfitting sobre muestra mínima (P-03/R-03). Los defaults (swingLen 5/3, displacement 1.5×ATR/70%, FVG 0.25×ATR, eqThreshold 0.1×ATR, etc.) quedan **congelados** hasta la calibración IS/OOS.
4. **MCP-06 (task-master) se salta definitivamente.** El WORKPLAN §3 ya es el backlog ejecutable; Archon aporta el motor DAG; una DB paralela solo añade riesgo de divergencia.
5. **Mejora incorporada — paridad Python↔Pine:** `scripts/ver05/detect*.py` queda como herramienta de cross-check algorítmico en Fase 1 para los conceptos que cubre (swings, BOS/CHoCH, MSS, OB, FVG, EQH/EQL, sweeps). Mismo patrón que los golden tests Pine→MQL5 de Fase 4.

### Correcciones aplicadas (alineación entre documentos, no de diseño)
| # | Archivo | Fix |
|---|---|---|
| C1 | PINE-PLAN §3.1 | `f_detectMSS` alineado a la definición canónica (CHoCH swing + displacement; antes describía secuencia HH+HL→LH+LL) |
| C2 | PINE-PLAN §3.4 | `f_sessionOpens` = diaria+semanal+mensual |
| C3 | PINE-PLAN §6 | "~50 confluencias" → 42 canónicas |
| C4 | WORKFLOWS.md | Nota de instalación Archon actualizada al estado real v0.4.x |
| C5 | reglas-smc-ict.md | Estado → POBLADO Y APROBADO; cierre DOC-01 completo |

## Alternativas consideradas

- **Invertir una sesión en ampliar datos (otra fuente histórica) antes de Pine:** descartada. Duplica trabajo que la validación de Fase 1 hace como subproducto, retrasa el arranque, y tienta a recalibrar umbrales sobre muestra insuficiente.
- **Exigir 3 casos canónicos para TODO concepto sin excepción:** descartada como regla absoluta — para conceptos compuestos de primitivos bien evidenciados es rigor aparente sin reducción real de riesgo; el riesgo residual se cubre con los criterios de done de Fase 1.
- **Hacer MCP-06 "por si acaso":** descartada (riesgo de divergencia > beneficio nulo).

## Consecuencias

- **F1-S1.1-T01 queda DESBLOQUEADO.** Próxima sesión: `/smc-session-startup` → workflow `smc-sprint` con el esqueleto de los 3 archivos Pine.
- Los criterios de done de T12/T18/T19 quedan registrados en WORKPLAN §3 Fase 1 y son parte del gate F1.
- La limitación del API de datos queda documentada; cualquier extracción masiva futura usa los CSV de `scripts/ver05/` o el Strategy Tester, no `data_get_ohlcv` en bucle.
- Si en Fase 1 los casos adicionales de MSS/Judas/breaker contradicen las definiciones, se vuelve aquí con diagnóstico (regla 8: el gate se retrocede, no se ajusta el criterio).

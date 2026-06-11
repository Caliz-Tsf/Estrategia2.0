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

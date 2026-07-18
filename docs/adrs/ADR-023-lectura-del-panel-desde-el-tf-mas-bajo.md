# ADR-023 — El defecto chart-TF se acota por REGLA DE OPERACIÓN, no con `pdWindow`

- **Fecha:** 2026-07-18 (Sesion-135)
- **Estado:** **ACEPTADA** — decisión del usuario en S135 entre 3 opciones. **Cero código.**
- **Precisa (no contradice):** **ADR-021** (el 2.º extremo estructural sigue intacto; esto acota *cómo
  se lee*, no *qué se calcula*). **§2.3.2** de `reglas-smc-ict.md` — resuelve la contradicción
  `pdWindow` "obligatoria" vs "OPCIONAL" a favor de **OPCIONAL**.
- **Desbloquea:** **F1-GATE**, bloqueada desde S133 por este defecto.
- **Difiere a Fase 3:** la reevaluación de `pdWindow` (ver §Deuda aceptada).

---

## Contexto

S133 midió que la columna **M5** del panel da **Discount 21%** con el chart en H1 y **Premium 90%** con
el chart en M5: el mismo TF, dos veredictos. Se concluyó que `pdWindow` era **obligatoria** y que sin
ella el rango no es determinista (regla dura #1).

S134 midió la **matriz completa de 9 celdas** (EURUSD, instancia limpia, sin overrides) y cambió el
problema:

| Columna | Chart D1 | Chart H1 | Chart M5 |
|---|---|---|---|
| **D1** | Discount 34% | Discount 34% | Discount 34% |
| **H1** | *Discount 34%* | Premium 74% | Premium 74% |
| **M5** | *Premium 58%* | *Discount 21%* | **Premium 91%** |

**Una columna se lee correcta si y solo si `chart-TF <= TF de la columna`.** Y desde **chart M5 las
tres dan 34/74/91 = la tabla del gate de §2.3.2, celda por celda.**

⇒ **La regla del §2.3.1 no está rota.** Lo que falla es leer un TF bajo desde un chart alto:
`request.security("5", …)` desde H1 recibe mucha más historia M5 que un chart M5 nativo (5253 barras)
⇒ más strong ⇒ el 2.º extremo se va más lejos. **Es un artefacto de `request.security`.**

Esto abrió una opción de coste cero que S133 no había considerado, frente a la ventana real.

---

## Decisión

**`pdWindow` sigue OPCIONAL. El defecto se acota con una regla de operación, no con código:**

> **El panel y el dibujo del P/D son válidos leídos desde el TF más bajo de los que se muestran.**
> Con las 3 columnas activas (D1/H1/M5) ⇒ el chart debe estar en **M5**. Leído desde un chart más alto,
> las columnas por debajo del chart-TF quedan **truncadas y no deben usarse.**

### Por qué esta y no la ventana real

1. **No alcanza al motor de decisión.** La Strategy de Fase 2 corre sobre **un** chart-TF —el de
   entrada, M5— donde las 3 columnas ya son correctas. El defecto es de lectura visual multi-TF.
2. **El artefacto no existe en MQL5.** El EA lee barras por TF con conteo fijo, sin `request.security`
   ⇒ arreglarlo en el CORE sería pagar SHA roto + re-baseline ×3 + contrato MQL5 por algo que
   desaparece en Fase 4.
3. **Puede no caber.** La ventana real es un array de strong con `barIdx` **en el CORE**: arrastra el
   riesgo OOM de S105 y tokens contra el `CE10117`, donde el headroom medido es **~0** (100615 vs
   límite 100256, y la §6.5 ya está gastada — S125).

### Alternativas consideradas y descartadas

- **Ventana real (`pdWindow` obligatoria, array de strong en el CORE).** Descartada por los 3 costes
  de arriba. **No se descarta la idea, se descarta el momento**: se reevalúa en Fase 3.
- **Regla de operación + guardia en panel** (marcar en el propio panel las celdas no fiables cuando
  `chart-TF >` columna). Descartada **por ahora** — coste bajo y fuera del CORE, pero es dibujo nuevo
  sin necesidad operativa una vez declarada la regla. Queda como mejora disponible.

---

## Consecuencias

**Positivas**
- **F1-GATE desbloqueada** sin tocar `pine/`. CORE SHA `9559a0d7fe58b213` intacto.
- §2.3.2 deja de contradecirse (6.ª y última corrección del hilo `pdWindow`).
- Cero parámetros nuevos ⇒ la cascada sigue anidando y rotando sin calibración por símbolo (ADR-001).

**Deuda — BLOQUEANTE, NO ACEPTADA** *(corregido por decisión del usuario, S135)*
- El 2.º extremo sigue dependiendo de **cuánta historia sirva TV en el TF más bajo** — una violación de
  la **regla dura #1** (determinismo). **NO se acepta como deuda permanente: hay que cerrarla.**
- **Criterio de cierre medible:** el dealing range debe ser **reproducible dado un conteo mínimo de
  barras declarado por TF**. Mientras no se verifique, la regla dura #1 no está satisfecha.
- **Es precondición de dos gates**, no un detalle de Fase 1 (ver §Riesgo aguas abajo).

### ⚠️ Riesgo aguas abajo — corrección a la §Decisión

El argumento *"el artefacto no existe en MQL5"* de arriba es **cierto solo del artefacto chart-TF**
(leer M5 desde un chart D1). **La dependencia de la profundidad de historia NO desaparece en MQL5, y
además se agrava:**

- **Fase 3 — reproducibilidad del backtest.** Si el rango depende de la historia servida, dos corridas
  separadas en el tiempo pueden diferir, y los pesos se calibran contra eso. El corte IS/OOS
  (`F3-T01`) presupone determinismo.
- **Fase 4 — paridad de golden tests.** Los golden tests comparan Pine contra MQL5. Si Pine calcula el
  2.º extremo sobre la historia que TV le sirvió y el EA sobre un conteo de barras fijo, **no tienen
  por qué coincidir**. `F4-GATE-A` exige golden tests al 100%. ⇒ la dependencia de historia es
  **exactamente** un riesgo de paridad, no algo que Fase 4 resuelva sola.

⇒ La decisión de **no construir `pdWindow` en S135** sigue en pie (no cabe en el presupuesto de tokens
y no hay datos de calibración), pero **la justificación de que la deuda era inocua era demasiado
cómoda y queda corregida aquí.**
- **Restricción operativa nueva:** validaciones visuales y capturas del P/D multi-TF deben hacerse
  **desde chart M5**. Leer desde D1 o H1 produce celdas truncadas que parecen datos válidos — es
  exactamente cómo S133 entregó un gate correcto que pareció defectuoso.

---

## Evidencia

- `docs/planes/MEDICION-matriz-chart-tf-S134.md` — la matriz de 9 celdas.
- `docs/reglas-smc-ict.md` §2.3.2 — regla de lectura + tabla de parámetros, ya coherentes.
- ADR-021 — el motor del 2.º extremo, que esta decisión **no** modifica.

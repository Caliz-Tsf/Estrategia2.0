# METODOLOGÍA DE VERIFICACIÓN VISUAL GRADUADA + CAPA DE DISCRIMINACIÓN

> Estrategia 2.0 · Bot SMC/ICT · DOC de metodología (Sesion-054, 2026-06-23).
> **Estado: ESQUELETO** — estructura + framework escritos; los recuadros `[RELLENAR: …]` se completan en la fase de ejecución (cualquier IA, con el HANDOFF + PLAN-049 + reglas-smc-ict.md).
> **Relación con docs existentes:** *supersede-y-extiende* (NO borra) [`PLAN-VALIDACION-Sesion-049.md`](sprint-runs/PLAN-VALIDACION-Sesion-049.md). Apoya `ADR-010` (MTF anclado) y `ADR-012` (protocolo de razonamiento). No crea ADR nuevo.
> **Regla de oro (heredada de reglas-smc-ict):** cada eje se mide con **números + evidencia**, no con prosa. Si no se puede medir, no se puede verificar.

---

## 0. Propósito y relación con PLAN-049 (esto disuelve el dilema "dos caminos")

PLAN-049 verifica una cosa: **¿el concepto aparece donde debe y no donde no debe?** (presencia binaria). Es necesario pero insuficiente: hoy el Pine detecta 40+ conceptos y el gráfico es ilegible porque **nada está jerarquizado** — no se sabe cuál OB/FVG es EL relevante, cuáles marcas son fuertes vs. ruido, ni cuáles están externamente invalidadas aunque cumplan la regla.

Esta metodología **no reemplaza** PLAN-049: lo **absorbe como su Eje 0** y añade 3 ejes más. Consecuencia operativa clave:

> **No hay que elegir entre "validar el F1-GATE" (camino B) y "ejecutar el diseño de discriminación" (camino A).** Correr la verificación graduada **una sola vez** satisface el F1-GATE binario (Eje 0) **y** la capa de discriminación (Ejes 1–3). Son la misma pasada.

| | Pregunta | Origen | Gate |
|---|---|---|---|
| **Eje 0** | ¿Aparece donde debe / no donde no debe? | PLAN-049 (binario) | F1-GATE (≥90 presencia) |
| **Eje 1** | ¿Es la **variante correcta**? (de N candidatos, ¿EL relevante?) | esta metodología | graduado |
| **Eje 2** | ¿La **fuerza** calculada coincide con lo que se ve? | esta metodología | graduado |
| **Eje 3** | ¿Se respeta la **invalidación externa**? | esta metodología + ADR-012 | graduado |
| **Eje MTF** | ¿Coherencia descendente D1→H1→M5? (§4) | esta metodología + ADR-010 | graduado |

---

## 1. Columna vertebral del diseño

> **Detectar (marca todo) → Graduar (fuerza) → Contextualizar (confluencia/secuencia) → Decidir.**

Hoy el sistema se detiene en **Detectar** y trata cada marca como combustible de probabilidad **igual**. Las dos capas que faltan, **Graduar** y **Contextualizar**, deben ser **explícitas y compartidas** entre los dos consumidores (Strategy/EA-scoring y enjambre/ADR-012) — así ninguno traza probabilidades sobre marcas que no importan. La **refacción visual** (limpiar el gráfico) es el **subproducto de Graduar**: la misma fuerza/relevancia que decide qué importa decide qué se dibuja fuerte.

**Los 3 fallos de la lluvia de ideas mapean a 3 mecanismos distintos** (esto debe quedar escrito para que no se vuelvan a mezclar):

| # | Fallo | Ejemplo | Mecanismo | Dónde vive |
|---|---|---|---|---|
| 1 | **Variante equivocada** | ¿es EL OB de las N variantes? | corrección de detección + **regla de desempate** | Pine (CORE) |
| 2 | **Válido pero débil/ruido** | cruce EMA pegado al precio; mecha sin nivel; BOS de rango normal | **score de fuerza 0–1** | Pine tag (barato) + scoring (peso) |
| 3 | **Regla cumplida, externamente invalidada** | 1er rebote no, 2º sí; toca y luego cruza | **contexto/secuencia** — se marca, decide la cadena | scoring + cadena ADR-012 (Q1–Q7) |

> **Decisión Freddy (HÍBRIDA), no re-litigar:** Pine añade un **tag de fuerza barato por marca** (reusa primitivos existentes: cuerpo%, ×ATR, displacement, mitigado, sweep, distancia al nivel). El **grading/peso completo** vive aguas abajo (scoring + cadena ADR-012). **Se marca todo, pero cada marca lleva su señal de fuerza.** El fallo #3 **NO se hardcodea** como "no marcar": se marca y la cadena (Q3 ¿rompió por cierre?, Q4 ¿barrieron tempranos?) o los pesos deciden.

---

## 2. Vocabulario de calidad (3 magnitudes distintas — no confundirlas)

| Magnitud | Rango | Qué es | Dónde se calcula | Para qué |
|---|---|---|---|---|
| **`strength` (fuerza)** | 0–1 (quantizable a 3: alta/media/baja) | calidad **de una marca individual** | Pine CORE (tag barato) | Eje 2 + peso del scoring |
| **`cap` por concepto** | 0–10 (entero) | **cuántas** marcas de ese concepto se transfieren/dibujan | ya existe (MTF, ADR-010) | presupuesto de tinta |
| **nivel visual** | {Primario, Secundario, Terciario} | **cómo** se rinde una marca | Visual, derivado de `strength × cercanía` | refacción del gráfico (§5) |

Relación: `strength` (0–1) y la cercanía al precio **alimentan** el nivel visual (§5) y el orden del `cap` (las N más fuertes/cercanas se quedan). Una marca de `strength` baja existe en los arrays (la detección no cambia) pero cae a Terciario (oculta/colapsada al panel T14).

---

## 3. Verificación graduada por concepto — los 4 ejes

Para **cada** concepto (T01–T40, lista en PLAN-049 §"Lista ordenada" y en el HANDOFF §8), se verifican los 4 ejes con criterio medible + evidencia. Evidencia = `capture_screenshot` + `data_get_pine_labels/boxes/lines` + `data_get_pine_tables` (panel T14) + `quote_get` / `data_get_ohlcv` (valores numéricos). Nada se afirma sin dato extraído del gráfico real (no se inventa).

### Plantilla de verificación (se rellena por concepto)

```
CONCEPTO: <nombre> · § <ref reglas-smc-ict> · TF <de PLAN-049> · Toggle(s) ON: <i_show…>
Eje 0 — Presencia:   <PASS/FAIL ≥90>  evidencia: <screenshot + caso fecha-hora GMT de reglas-smc-ict>
Eje 1 — Variante:    <¿es EL relevante? regla de desempate aplicada · qué descartó>  evidencia: <…>
Eje 2 — Fuerza:      <strength calculado vs. lo que se ve · ¿coinciden?>  evidencia: <valores: cuerpo%, ×ATR, mitigado, sweep, dist×ATR>
Eje 3 — Invalidación: <contexto que lo anula · DÓNDE se chequea (Pine/scoring/ADR-012 Qn)>  evidencia: <…>
Veredicto: <PASS global ≥90 / FAIL+diagnóstico>   Firma usuario: <…>
```

### Criterios de cada eje

- **Eje 0 — Presencia** *(de PLAN-049)*: aislar el concepto (apagar todos los `i_show*` salvo el suyo vía `indicator_set_inputs`), `chart_scroll_to_date` a los casos ✓/✗ de reglas-smc-ict.md, screenshot, `smc-validator-agent` ≥90. **Apagar un toggle oculta el dibujo, NO la detección** (los arrays se siguen poblando) → aislar es seguro.
- **Eje 1 — Variante correcta / desempate**: cuando hay N candidatos del mismo tipo (N OB en una pierna, FVG vs True FVG vs IFVG), verificar que la **regla de desempate determinista** (§6 de reglas-smc-ict) elige EL relevante y descarta el resto **con razón visible**. Criterio: el desempate produce 1 ganador reproducible; los descartados son citables.
- **Eje 2 — Fuerza calculada vs. visible**: el `strength` (0–1) del tag debe **coincidir con la percepción visual**. Una vela enorme con cuerpo 98% que barre liquidez → `strength` alta; un cruce EMA pegado al precio en neutro → `strength` baja. Criterio: para ≥3 casos por concepto, el `strength` extraído (`data_get_pine_labels`) ordena igual que el ojo. Discrepancia = FAIL → revisar fórmula (§6.1 reglas-smc-ict).
- **Eje 3 — Invalidación externa**: identificar el contexto que **anula** la marca aunque la regla se cumpla, y **dónde** se chequea (Pine / scoring / ADR-012 Q1–Q7). Criterio: el caso de invalidación documentado (p.ej. rejection cuyo retorno cruza el nivel) está **marcado** (no suprimido) y la capa correcta lo degrada. NO se exige que Pine lo borre.

> `[RELLENAR durante ejecución]` — tabla de resultados por concepto (40+ filas), una por T01–T40, con los 4 ejes + evidencia a disco. Plantilla arriba.

---

## 4. Eje de coherencia MTF descendente (D1 → H1 → M5) — orden obligatorio

> Apoya `ADR-010` (transporte MTF + dibujo geométrico anclado, ya implementado en T13c/S042).

1. **Orden de revisión obligatorio:** cada concepto se revisa **primero en D1, luego H1, luego M5**. En cada TF se valida (a) los conceptos **propios de esa foto** y (b) los **heredados/refinados desde el TF mayor** (mapa MTF, ADR-010).
2. **Filtro de relevancia, NO de presencia:** solo se transfieren/dibujan hacia abajo **los que realmente valen** (alta `strength` + alineados con el bias del TF mayor), no todos los detectados. El `cap` por concepto (0–10) + el `strength` deciden cuáles bajan.
3. **Prueba de visibilidad cruzada:** un concepto marcado importante en un TF alto debe **aparecer en su rango de precio en los TF bajos**, en las mismas coordenadas. *Ejemplo del usuario:* un FVG D1 importante en 1.000–2.000 → en H1 debe verse en ese rango → verificar que también se ve en M5, mismo nivel/barra (por `bar_time`, nunca `bar_index` del contexto HTF).
4. **Criterio de aprobación del eje:** el objeto heredado cae en la **misma barra/nivel** que su origen en el TF alto. Se compara el dibujo MTF en M5 contra el cambio manual del chart a D1/H1 (`chart_set_timeframe`).

> `[RELLENAR durante ejecución]` — por concepto transferible: capturar en M5 (heredado) y en D1/H1 (nativo), confirmar mismo `bar_time` + nivel. Tabla.

---

## 5. Especificación de jerarquía visual (refacción "limpio y ordenado")

Subproducto de **Graduar**: la fuerza/relevancia que decide qué importa decide qué se dibuja.

- **3 niveles de relevancia → 3 niveles visuales:**
  - **Primario** = zona activa cercana al precio + alineada al bias + alta `strength` → **render completo** (color sólido, etiqueta).
  - **Secundario** = válido pero no inmediato → **atenuado/pequeño** (opacidad alta, etiqueta corta).
  - **Terciario** = histórico/débil/mitigado → **oculto por defecto o colapsado al panel** T14.
- **Presupuesto de tinta:** top-N por familia (criterio = `strength × cercanía`); el resto **NO se dibuja**, se **cuenta en el panel T14** (que ya muestra "X cercano" por familia). Reusa `f_nearestN` ([SMC-Library.pine ~1385](../pine/SMC-Library.pine)).
- **Decaimiento histórico:** mitigado/viejo se atenúa o se oculta; eventos viejos se colapsan.
- **Perfiles de densidad:** un master input `i_densidad` con 3 modos → **Operación** (solo Primario) / **Estudio** (Primario+Secundario) / **Todo** (los 3). + z-order por familia.
- **Anti-solape de etiquetas:** continúa el patrón `style_label_left` ya usado.

| Familia (toggles reales `i_show*`) | Primario | Secundario | Terciario |
|---|---|---|---|
| OB / FVG / zonas | `[RELLENAR]` | `[RELLENAR]` | colapsa a panel T14 |
| Estructura (BOS/CHoCH/MSS) | `[RELLENAR]` | `[RELLENAR]` | `[RELLENAR]` |
| Liquidez (pools/sweep/EQH-EQL) | `[RELLENAR]` | `[RELLENAR]` | `[RELLENAR]` |
| Contexto (EMA/displacement/legs) | `[RELLENAR]` | `[RELLENAR]` | `[RELLENAR]` |
| Gap ICT (T26–T40) | `[RELLENAR]` | `[RELLENAR]` | `[RELLENAR]` |

> Mapeo 1:1 con los ~43 toggles `i_show*` agrupados por familia (`GRP_*`) y con el panel T14 — verificación de coherencia #3 (§9).

---

## 6. Arreglo de errores de dibujo MTF (ESTADO REAL CORREGIDO)

> ⚠️ **Corrección respecto al borrador del plan:** los **5 síntomas de [revision-T13b §2](sprint-runs/revision-T13b-mtf-dibujo-nativo.md) YA fueron arreglados** en **T13c / Sesion-042** (dibujo geométrico anclado, commit `88500fd`). NO están abiertos. Lo que queda abierto son los **3 pendientes diferidos de S042**. Esta sección verifica el cierre de los 5 y resuelve los 3.

### 6.a Verificación de cierre (los 5 síntomas históricos de revision-T13b)

Confirmar (no re-implementar) que cada uno quedó cerrado en T13c; criterio = cae en la misma barra/nivel que el manual en el TF alto:

| Síntoma histórico | Arreglo en T13c (S042) | Verificación |
|---|---|---|
| OB/FVG como líneas, no cajas | `box.new` + `xloc.bar_time` | `[RELLENAR: confirmar caja]` |
| Sweep como línea lateral | marca ▲/▼ en la barra `tA` | `[RELLENAR: confirmar marca]` |
| EQH/EQL no en su sitio | línea tramo `tA→tB` por `bar_time` | `[RELLENAR]` |
| BOS/CHoCH no transferidos | línea origen→ruptura en LTF | `[RELLENAR]` |
| Conteo de velas al bajar TF | `xloc.bar_time` siempre | `[RELLENAR]` |

### 6.b Pendientes diferidos REALES (abiertos desde S042) — entran al alcance

| # | Síntoma | Causa | Arreglo propuesto | Criterio de verificación |
|---|---|---|---|---|
| (a) | Tag `(D1/H1)` ausente en BOS/CHoCH **fusionados** con estructura nativa | el anti-duplicado deja la nativa sin etiqueta de TF | `[RELLENAR: dónde añadir el prefijo sin reintroducir duplicado]` | la línea fusionada muestra su TF de origen |
| (b) | EQH/EQL cuadre fino de líneas | cálculo velas pivote-a-pivote impreciso | `[RELLENAR: revisar tramo tA→tB del 1er/2º toque]` | la línea cae toque-a-toque exacto |
| (c) | OB/FVG exactitud vela-a-vela | caja cubre "lo necesario" pero no cuadra a la vela origen | `[RELLENAR: cuadrar top/bottom a la vela origen]` | la caja cuadra a la vela del TF alto |

---

## 7. Procedimiento operativo por concepto (runbook)

Extiende el procedimiento de PLAN-049 §"Procedimiento por paso" con los ejes graduados. Por cada T01–T40:

1. **Aislar:** `indicator_set_inputs` → todos los `i_show*` = false **excepto** el/los del concepto (+ `i_showPanel` para leer valores).
2. **Contexto:** `chart_set_symbol EURUSD` + `chart_set_timeframe` (TF de la fila en PLAN-049). Para el eje MTF: revisar D1 → H1 → M5 en ese orden.
3. **Navegar + capturar:** `chart_scroll_to_date` a los casos ✓/✗ de reglas-smc-ict.md → `capture_screenshot` (a disco, ruta por concepto).
4. **Extraer datos:** `data_get_pine_labels/boxes/lines` + `data_get_pine_tables` (T14) + `quote_get` / `data_get_ohlcv` → valores numéricos (cuerpo%, ×ATR, dist×ATR, mitigado, sweep, `strength`).
5. **Puntuar:** `smc-validator-agent` con captura + datos + la § de la regla → score por eje.
6. **Registrar:** PASS / FAIL<90 + diagnóstico, en la tabla §3. Firma usuario por concepto o lote.

---

## 8. Gate de aprobación (cierre del set = F1-GATE ampliado)

Cada concepto **≥90 en los 4 ejes** (Eje 0 presencia + Ejes 1–3 graduados) + coherencia MTF (§4) + **anti-repaint** (2 días EURUSD histórico) + **performance** (20k barras). Sin saltarse ningún gate (regla dura #8): si un eje <90 → **retroceso con diagnóstico**, NO se ajusta el criterio. Firma del usuario obligatoria.

Cumplir este gate **desbloquea Fase 2** (scoring) — y de paso entrega la capa de discriminación + la refacción visual.

---

## 9. Verificación de coherencia de ESTA metodología (antes de ejecutar)

Checklist de que el diseño es consistente (no es ejecución, es coherencia del documento):

1. [ ] La plantilla del sub-bloque (reglas-smc-ict §6.0) cubre los **3 tipos de fallo** (variante / fuerza / invalidación) en los 5 ejemplos trabajados.
2. [ ] Cada ejemplo trabajado cita **primitivos existentes** (cuerpo%, ×ATR, mitigado, sweep, displacement) — nada que el CORE no calcule hoy (reglas-smc-ict §6.1).
3. [ ] La jerarquía visual (§5) mapea **1:1** con familias/toggles reales (`i_show*`, `GRP_*`) y con el panel T14.
4. [ ] El HANDOFF es **autocontenido**: una IA sin esta conversación puede rellenar los 40+ conceptos solo con el brief + PLAN-049 + reglas-smc-ict.md.
5. [ ] El eje MTF descendente (§4) y el arreglo de errores de dibujo (§6, estado real) están reflejados en la metodología **y** en el HANDOFF.
6. [ ] El Eje 0 = presencia de PLAN-049 está explícitamente integrado (no se duplica ni se contradice PLAN-049).

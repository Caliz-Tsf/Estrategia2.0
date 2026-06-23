# ADR-012 — Protocolo de razonamiento del agente: snapshot determinista + cadena de auto-preguntas → ESPERAR/ENTRAR/DESCARTAR

- **Fecha:** 2026-06-23 (Sesion-052, módulo Enjambre — PARALELO a Pine).
- **Estado:** **ACEPTADO** (2026-06-23, Freddy) — decisiones de fondo elegidas por el usuario: **(1) snapshot de fuente DETERMINISTA (leído de las salidas Pine vía MCP), COMPLETO multi-TF D1/H1/M5, cero invención**; **(2) una decisión `ESPERAR` obliga a `gatillo` + `invalidación` explícitos y medibles.** Quedan `[impl]` menores abiertos (§6 del doc de detalle) que NO bloquean la aceptación del contrato.
- **Spec de detalle:** `docs/planes/PROTOCOLO-razonamiento-agente.md` (esquema YAML del snapshot, las 7 preguntas, el contrato de salida y el encaje en runtime). Este ADR fija la **decisión**; el doc es la **referencia viva**.
- **Relacionado:** ADR-005 (enjambre = laboratorio + copiloto, NO runtime EA) · ADR-007 (el EA razona confluencias / enjambre continuo) · `ESQUELETO-P2-hermes-enjambre.md` §2.1/§2.3/§2.4/§2.8 · `PLANTILLA-agente-mentor.md §C` (voto que este ADR extiende) · `docs/reglas-smc-ict.md` §4.8 (confluencias canónicas, fuente que NO se recalcula).

## Contexto

El enjambre (ADR-005/007) necesita que **todos** sus agentes de razonamiento (mentores, expertos-concepto, escéptico) trabajen sobre el **mismo molde**: la misma foto del mercado, la misma secuencia de razonamiento y el mismo formato de salida. Hasta ahora existían piezas sueltas: el Vigía vuelca "algo" al Kanban (`ESQUELETO-P2 §2.1`, prompt sin cerrar) y el voto §2.4 captura el resultado, pero **faltaba el puente**: qué información exacta recibe el agente y por qué cadena de decisión pasa para emitir ese voto.

Sin un contrato común aparecen tres problemas: (a) cada agente improvisa qué mira → votos no comparables, scoring sucio (regla §0.7: basura entra → basura sale aguas abajo a Pine/EA); (b) el LLM **inventa niveles** si describe el gráfico "a ojo" → choca con §0.8 (no recalcular confluencias); (c) las decisiones `ESPERAR` quedan sin condición medible → no se pueden re-disparar ni auditar contra el árbitro real (la acción del precio, §2.6).

Preguntas que este ADR resuelve antes de instanciar el 2º agente y montar el piloto E2E (`ESQUELETO-P2 §step`):
1. **¿De dónde salen los datos** que mira el agente (determinista vs LLM-visión)?
2. **¿Qué secuencia de razonamiento** corre, idéntica para todos?
3. **¿Qué contrato de salida** extiende el voto §2.4, y qué obliga una decisión `ESPERAR`?

## Decisión

### 1. SNAPSHOT determinista, completo y multi-TF — fuente Pine vía MCP (cero invención)
El Vigía (único lector de TV, §0.3) arma una tarea-evento en el Kanban con un snapshot **estructurado** cuyos datos se **LEEN de las salidas del indicador Pine** (`data_get_pine_tables` = panel T14 D1/H1/chart-TF; `data_get_pine_lines/labels/boxes` = niveles/zonas/eventos dibujados; `quote_get`/`data_get_ohlcv` = precio). El Vigía **formatea, no estima**: si un dato no está dibujado → `n/d`, nunca inventado. El snapshot **relata todo lo vivo en D1, H1 y M5** (estructura, bias, premium/discount, pools sin barrer, zonas OB/FVG, eventos críticos de la vela) — la foto completa, no un recorte cercano al precio. Esquema YAML cerrado en el doc §1.2.

> **Por qué determinista (decisión Freddy):** el sistema Pine ya calcula y dibuja todos los conceptos; el LLM solo debe **razonar** sobre ellos, no medir. Esto honra §0.8 (el enjambre no recalcula confluencias) y elimina la divergencia entre lo que "ve" el LLM y lo que el sistema marca.

### 2. Cadena de 7 auto-preguntas — compartida y ordenada (doc §2)
Q1 ¿la zona importa? → Q2 draw on liquidity (dirección) → Q3 ¿rompió/no rompió (BOS/CHoCH/MSS confirmado por cierre)? → Q4 ¿ya liquidaron a los tempranos (sweep)? → Q5 confluencias presentes/faltantes (§ref) → **Q6 R:R ≥ 1:3 GLOBAL y calculable** → Q7 sesión + gate de noticias. Cada paso puede cortar hacia la decisión. Idéntica para todos los agentes; lo que cambia es **cómo responde** cada uno según su ficha/grounding.

### 3. Contrato de salida = voto §2.4 EXTENDIDO (doc §3)
Al voto base (`agente/direccion/postura/confianza/concepto/criterio/evidencia`) se añade: `decision: ESPERAR|ENTRAR|DESCARTAR` + `razonamiento` (respuestas Q1–Q7, auditable) + `proyeccion{gatillo, invalida, objetivo}` + `q6_rr{entrada,sl,tp,ratio}`. Reglas duras del contrato:
- **`ESPERAR` ⇒ `gatillo` + `invalida` obligatorios y medibles** (un nivel/condición que el Vigía re-chequea cada vela). Sin ellos, voto inválido.
- **`ENTRAR` ⇒ `q6_rr.ratio ≥ 3`** o el validador de Norms lo degrada antes de mostrar.
- El **umbral 1:3 de Q6 es el GLOBAL del sistema**, no el del mentor: un mentor con R:R base 1:2 (NSL) puede proponer, pero su <1:3 se degrada/descarta (resuelve el conflicto del campo 9 de NSL sin que el mentor recalcule §4.8).

### 4. Compartido vs por-agente, y re-disparo de ESPERAR
- **Compartido (este ADR):** esquema del snapshot, orden/enunciado de las 7 preguntas, campos del contrato de salida, umbral 1:3 de Q6.
- **Por agente:** las respuestas a cada pregunta (ficha/grounding) y el modelo LLM (§2.9: mentores nemotron-120b/glm; escéptico = modelo distinto).
- **Re-disparo:** los votos `ESPERAR` persisten con su `gatillo/invalida`; en la siguiente corrida el Vigía los re-evalúa contra el nuevo snapshot → si se cumple el gatillo reabre la discusión (puede pasar a ENTRAR); si se cumple la invalidación cierra la hipótesis como negativa en el track-record (§2.6). Esto hace cada ESPERAR **medible y auditable** por el árbitro real (el gráfico).

## Consecuencias

- **A favor:** votos comparables entre agentes → scoring limpio aguas abajo (IS/OOS → Pine/EA, §0.7); cero invención de niveles (honra §0.8); cada ESPERAR es una hipótesis con condición de cierre → alimenta el track-record sin autoadjudicación (§2.6); el contrato extiende §2.4 sin romperlo; resuelve el conflicto R:R 1:2 de NSL vía Q6 global + Norms.
- **En contra / coste:** el Vigía debe leer y formatear muchas salidas Pine por corrida (más tokens/latencia que un `[SILENT]` simple) — mitigado por el gating "accionable" estricto y el cron 15m (§0.5); el contrato de salida es más verboso (7 respuestas + proyección) → más a parsear en el Kanban; el snapshot depende de que el indicador Pine esté **completo y validado** (gate F1 pendiente) para que la foto sea fiable.

## Alternativas descartadas

- **Snapshot por LLM-visión** (el Vigía "mira" el chart y describe a ojo): más flexible pero **inventa niveles** y diverge del Pine determinista → viola §0.8. Rechazada. (El LLM-visión sí cabe para contexto cualitativo no-numérico en el futuro, no para los niveles.)
- **Snapshot recortado a la zona cercana al precio:** más barato, pero priva al agente del contexto D1/H1 que decide si la zona importa (Q1). El usuario pidió explícitamente la foto completa multi-TF. Rechazada.
- **ESPERAR como solo-tesis** (sin gatillo/invalidación): más simple pero deja la decisión sin condición medible → no se re-dispara ni se audita. Rechazada (decisión Freddy: gatillo+invalidación obligatorios).
- **Cadena/snapshot por mentor:** rompe la comparabilidad de votos y el scoring. Rechazada (la voz va en la ficha, el molde es común).

## Checklist / `[impl]` abiertos (NO bloquean la aceptación)

- [x] Freddy elige fuente del snapshot → **determinista (Pine), completo multi-TF** (2026-06-23).
- [x] Freddy elige contrato de ESPERAR → **gatillo + invalidación obligatorios** (2026-06-23).
- [x] Estado de este ADR → **Aceptado**.
- [ ] `[impl]` `k` de proximidad del Vigía para "accionable" (arranque `0.5·ATR_H1`, medir RPD/ruido).
- [ ] `[impl]` dónde se calcula el SL/TP de Q6 (¿lo aporta el Pine determinista y el agente lo cita?).
- [ ] `[impl]` validar el YAML del voto extendido contra el formato real de comentarios `kanban_show`.
- [ ] `[impl]` centralizar la normalización de huso de la sesión (NSL usa horas Colombia).
- [ ] `[impl]` re-evaluador de gatillos abiertos del Vigía (persistencia + consulta de los ESPERAR vivos).
- [ ] Probar el protocolo end-to-end en el **piloto mínimo** (1 Vigía + Kanban + 2 mentores + orquestador, EURUSD) cuando el indicador Pine pase el gate F1.

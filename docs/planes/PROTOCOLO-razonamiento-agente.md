# Protocolo de razonamiento del agente — snapshot + cadena de auto-preguntas → ESPERAR/ENTRAR/DESCARTAR

> **Sesión:** S052 (2026-06-23) · módulo Enjambre (PARALELO a Pine). **Estado: ACEPTADO como `ADR-012`** (Freddy, 2026-06-23). Este doc = referencia viva del contrato; la decisión vive en `docs/adrs/ADR-012-protocolo-razonamiento-agente.md`.
> **Qué es:** la **pieza COMPARTIDA** del enjambre que define (1) el **snapshot** que el Vigía vuelca al Kanban y (2) la **cadena de auto-preguntas** que TODO agente de razonamiento corre sobre ese snapshot para emitir una decisión `ESPERAR / ENTRAR / DESCARTAR`. **Extiende** el voto §2.4 de `ESQUELETO-P2` / §C de `PLANTILLA-agente-mentor.md` — no lo reemplaza.
> **Qué NO es:** NO es por-mentor (la voz/criterio de cada mentor vive en su ficha; aquí va el *molde* común). NO recalcula confluencias (regla §0.8) ni inventa niveles. NO da órdenes (ADR-005: laboratorio/copiloto, el árbitro es TradingView).
> **Léelo junto a:** `ESQUELETO-P2-hermes-enjambre.md` (§2.1 Vigía, §2.3 rondas, §2.4 voto, §2.8 push), `PLANTILLA-agente-mentor.md §C`, `docs/reglas-smc-ict.md` (§4.8 confluencias canónicas + las §ref por concepto), `ADR-005` (modos), `ADR-007` (EA razona confluencias).

---

## §0 — Principios (reglas duras de este protocolo)

1. **Compartido, no por mentor.** El snapshot, la cadena de preguntas y el contrato de salida son **idénticos** para todo agente que razona (mentor, experto-concepto, escéptico). Lo que cambia es **CÓMO responde** cada uno (su ficha/grounding), no la estructura.
2. **Cero invención — fuente determinista.** Los datos del snapshot **se LEEN de las salidas del indicador Pine** vía MCP TV (el sistema ya dibuja BOS/CHoCH/OB/FVG/pools/PD/EQH-EQL/sweeps/kill zones + panel multi-TF). El Vigía **formatea**, no estima. Si un dato no está en el gráfico → se marca `n/d`, no se inventa.
3. **Snapshot COMPLETO multi-TF.** Relata **todo lo que está vivo** en el mercado en **D1, H1 y M5**: estructura, bias, niveles, zonas dibujadas y **eventos críticos** de la vela en curso. El agente razona con la foto completa, no con un recorte cercano al precio.
4. **Un solo lector de TV (§0.3).** Solo el Vigía/Router abre TradingView (CDP 9222). Los demás razonan sobre el snapshot del Kanban. Nadie más toca TV en paralelo.
5. **Norms global decide lo que se muestra.** El gate `R:R ≥ 1:3` (y demás Norms en código) filtra **después** del voto, **antes** de mostrar al humano. Un mentor cuyo R:R base es 1:2 (p.ej. NSL) puede proponer, pero el validador degrada/descarta lo que no llega a 1:3. La pregunta Q6 usa el **1:3 global del sistema**, no el del mentor.
6. **El gráfico es el árbitro (§2.6).** Ni el agente ni el enjambre se autoadjudican el resultado; lo resuelve la acción del precio en TV (replay/seguimiento) por las reglas de salida deterministas.

---

## §1 — El SNAPSHOT (lo que el Vigía vuelca al Kanban)

Contrato de la **tarea-evento** que crea el Vigía (§2.1) en Triage. Es un YAML/markdown estructurado, **derivado de las salidas Pine** (no narración libre). El consumidor (cualquier agente) lo lee del comentario raíz de la tarea.

### §1.1 — Fuente de cada bloque (MCP TV → Pine)
| Bloque del snapshot | De dónde se LEE (determinista) |
|---|---|
| Bias / estructura por TF | `data_get_pine_tables` (panel de estado T14: columnas **D1 / H1 / chart-TF**) |
| Niveles (pools, PDH/PDL, EQ) | `data_get_pine_lines` + `data_get_pine_labels` (etiquetas "BSL/SSL/PDH/PDL/EQH/EQL") |
| Zonas (OB, FVG/CE, breaker…) | `data_get_pine_boxes` (cajas {high,low} con su tipo) |
| Eventos de la vela (BOS/CHoCH/MSS/sweep) | `data_get_pine_labels` de la barra confirmada + alertas `// === ALERTAS ===` |
| Premium/Discount/Equilibrium | `data_get_study_values` / panel (zona actual del rango dominante) |
| Precio / OHLC / sesión-hora | `quote_get` + `data_get_ohlcv` (último) + normalización de huso |
| Gate de noticias | fuente del Funcional-Noticias (ADR-005, gate determinista — NO confluencia) |

> El **panel multi-TF (T14)** ya entrega D1/H1/chart-TF de un tiro vía `data_get_pine_tables`: es la espina dorsal del snapshot. El **mapa MTF (T13c, ADR-010)** aporta la geometría anclada (OB/FVG/BOS de HTF proyectados en M5).

### §1.2 — Esquema del snapshot
```yaml
snapshot:
  meta:
    simbolo: EURUSD
    tf_chart: M5
    timestamp_utc: 2026-06-23T13:15:00Z
    sesion: "Londres"          # killzone activa normalizada a huso | "fuera"
    hora_local_ref: "08:15 COT"
    precio: 1.08423
    atr_h1: 0.00112            # referencia para distancias relativas a ATR

  gate:
    noticias: "despejado"      # despejado | ventana_alto_impacto(±Nmin) -> bloquea ENTRAR
    spread_ok: true            # guardián universal (ADR-001)

  por_tf:                      # relato COMPLETO D1 / H1 / M5 (§0.3)
    D1:
      bias: bajista            # de structure high/low dominante (extensor vs protector)
      ultimo_evento: "CHoCH bajista confirmado @1.0980 (hace 3 velas)"
      premium_discount: "precio en PREMIUM del rango D1 (0.71)"
      estructura: { swing_high: 1.1010, swing_low: 1.0805 }
      pools_sin_barrer: [ {tipo: SSL, nivel: 1.0805, edad_velas: 12} ]
      zonas: [ {tipo: OB_bajista, rango: [1.0965,1.0982], ce: 1.0973, mitigado: false} ]
    H1:
      bias: bajista
      ultimo_evento: "BOS bajista confirmado @1.0905"
      premium_discount: "discount (0.34)"
      estructura: { swing_high: 1.0905, swing_low: 1.0832 }
      pools_sin_barrer: [ {tipo: SSL, nivel: 1.0840, edad_velas: 5},
                          {tipo: BSL, nivel: 1.0905, edad_velas: 2} ]
      zonas: [ {tipo: FVG_bajista, rango: [1.0856,1.0849], ce: 1.08525, mitigado: false} ]
    M5:
      bias: rango
      ultimo_evento: "sweep de SSL 1.0840 EN ESTA VELA (mecha, sin cierre debajo)"
      premium_discount: "equilibrium"
      estructura: { swing_high: 1.0858, swing_low: 1.0838 }
      zonas: [ {tipo: FVG_alcista, rango: [1.08405,1.08455], ce: 1.0843, mitigado: false} ]

  eventos_criticos:           # lo URGENTE de la vela en curso (gatillos potenciales)
    - "M5: barrido de SSL H1 1.0840 sin cierre debajo (posible Judas / liq run)"
    - "M5: FVG alcista recién formado en 1.08405-1.08455"

  confluencias_presentes:     # SOLO lectura del §4.8 ya dibujado, con §ref (no se recalcula)
    - { concepto: sweep_SSL, ref: "§3.2", tf: M5 }
    - { concepto: FVG, ref: "§2.2", tf: M5 }
    - { concepto: discount_H1, ref: "§2.5", tf: H1 }

  refs_aplican: ["§3.2","§2.2","§2.5","§1.x BOS/CHoCH"]
```

> **Accionable vs `[SILENT]` (§2.1).** El Vigía crea la tarea-evento **solo** si hay al menos un `evento_critico` o proximidad relevante (precio a ≤ `k·ATR` de una zona/pool del §4.8). Si no → responde `[SILENT]` y no genera ruido/cuota.

---

## §2 — La cadena de auto-preguntas (compartida, ordenada)

Todo agente de razonamiento corre **la misma secuencia** sobre el snapshot, en orden. Cada paso puede **cortar** hacia una decisión. El agente responde cada pregunta **citando** el snapshot + su §ref/ficha (auditable).

| # | Pregunta | Qué evalúa | Corte posible |
|---|---|---|---|
| Q1 | **¿La zona/nivel importa?** | ¿Es un PDArray/pool relevante dado el bias D1/H1 y premium/discount, o es ruido en equilibrium contra-tendencia? | Si no importa → **DESCARTAR** |
| Q2 | **¿Cuál es el draw on liquidity?** | ¿Hacia qué pool no barrido apunta la liquidez? Fija la **dirección candidata**. | — (define dirección) |
| Q3 | **¿Rompió / no rompió?** | ¿Hay BOS/CHoCH/MSS **confirmado por cierre** que valide el cambio, o sigue en rango? | Sin confirmación → tiende a **ESPERAR** |
| Q4 | **¿Ya liquidaron a los tempranos?** | Early buyers/sellers: ¿hubo **sweep** del pool antes de la entrada? (NSL: MSS en 2º rompimiento). | Sin sweep esperado → **ESPERAR** el barrido |
| Q5 | **¿Qué confluencias hay y cuáles faltan?** | Lista las presentes (§ref del snapshot) y las que faltarían para su modelo. | Pocas/contradictorias → baja confianza |
| Q6 | **¿R:R ≥ 1:3 (global) y calculable?** | Entrada en PDArray, SL tras invalidación **estructural**, TP al siguiente pool/objetivo. Usa el **1:3 del sistema**, no el del mentor. | No calculable o <1:3 → no hay ENTRAR (queda ESPERAR si falta gatillo, o DESCARTAR) |
| Q7 | **¿Sesión / gate de noticias permiten?** | Killzone activa (peso, no bloqueo — ADR-001) y gate de noticias determinista (ADR-005). | Gate de noticias bloquea → **ESPERAR/DESCARTAR** |

**Mapeo pregunta → decisión:**
- **ENTRAR** ⟺ Q1 importa · Q3 confirmado · Q4 liquidez ya tomada (o no requerida por el modelo) · Q5 confluencias suficientes · **Q6 R:R≥1:3** · Q7 gate ok.
- **ESPERAR** ⟺ la tesis es válida (Q1/Q2 ok) pero **falta un gatillo concreto** (sweep, cierre de confirmación, llegada del precio a la zona, cierre de ventana de noticias).
- **DESCARTAR** ⟺ la zona no importa (Q1), está invalidada, va contra el draw/estructura sin tesis, o el R:R es imposible por geometría.

---

## §3 — Contrato de salida (voto §2.4 EXTENDIDO)

El agente emite el voto §2.4 **+** los campos de razonamiento. Todo va al comentario de su tarea en el Kanban.

```yaml
# --- base §2.4 (sin cambios) ---
agente: mentor-no-soy-liquidez
direccion: long | short | none
postura: a_favor | en_contra | neutral
confianza: 0.0-1.0
concepto: "barrido de SSL H1 + FVG M5 de retorno en discount"
criterio: "video <id> mm:ss + reglas-smc-ict.md §3.2 §2.2"
evidencia: "SSL 1.0840 barrido sin cierre; FVG alcista 1.08405-1.08455 sin mitigar"

# --- extensión de este protocolo ---
decision: ESPERAR | ENTRAR | DESCARTAR
razonamiento:                # respuestas compactas y auditables de la cadena §2
  q1_importa: "sí — pool SSL H1 alineado con draw alcista en discount"
  q2_draw: "BSL H1 1.0905 (liquidez de compradores arriba)"
  q3_rompio: "no aún — falta CHoCH M5 al alza que confirme"
  q4_tempranos: "sweep de SSL 1.0840 hecho esta vela (mecha)"
  q5_confluencias: "presentes: sweep §3.2, FVG §2.2, discount §2.5 | falta: CHoCH confirmación"
  q6_rr: { entrada: 1.0843, sl: 1.0836, tp: 1.0905, ratio: 8.9 }   # null si no calculable
  q7_gate: "Londres activa; noticias despejado"
proyeccion:                  # OBLIGATORIO si decision=ESPERAR (gatillo + invalidación)
  gatillo: "CHoCH M5 alcista por cierre sobre 1.0858 tras el sweep"
  invalida: "cierre M5 debajo de 1.0836 (anula el sweep / continúa bajista)"
  objetivo: "BSL H1 1.0905"
```

**Reglas del contrato:**
- `decision: ESPERAR` ⇒ `proyeccion.gatillo` y `proyeccion.invalida` son **obligatorios y medibles** (un nivel/condición que el Vigía pueda re-chequear en la siguiente vela). Sin ellos el voto es inválido.
- `decision: ENTRAR` ⇒ `q6_rr` debe existir con `ratio ≥ 3` (si no, el Norms lo degrada antes de mostrar).
- `decision: DESCARTAR` ⇒ basta `razonamiento`; `proyeccion` opcional.

---

## §4 — Qué es COMPARTIDO vs qué varía por agente

| Pieza | Compartida (este protocolo) | Varía por agente |
|---|---|---|
| Esquema del snapshot | ✅ idéntico para todos | — (lo produce el Vigía, único) |
| Orden y enunciado de las 7 preguntas | ✅ | — |
| Contrato de salida (campos del YAML) | ✅ | — |
| **Respuestas** a cada pregunta | — | ✅ según ficha/grounding (NSL prioriza liquidez/imbalance; un experto-OB mira su §) |
| Umbral R:R en Q6 | ✅ **1:3 global** (Norms) | el R:R *base* del mentor informa su confianza, no el gate |
| Modelo LLM | — | ✅ por rol (§2.9): mentores razonan con nemotron-120b/glm; escéptico = modelo distinto |

---

## §5 — Encaje en el runtime (cómo fluye + cómo se re-dispara un ESPERAR)

1. **Vigía (cron 15m)** lee TV → arma el **snapshot §1** → `kanban_create` tarea-evento en Triage (o `[SILENT]`).
2. **Ronda 1 (§2.3):** cada agente corre la **cadena §2** sobre el snapshot → emite el **voto extendido §3** en su comentario.
3. **Ronda 2 (rebate):** cada agente reacciona a los votos de los colegas (el valor está en la discrepancia, §3 espejismo de consenso).
4. **Supervisor de Confluencia** consolida **determinista** (cuenta a favor/en contra × confianza × track-record) y mapea a §4.8 **sin recalcular**.
5. **Norms (código)** filtra R:R<1:3 / gate de noticias **antes** de mostrar.
6. Si la síntesis es **accionable** → **push CallMeBot (§2.8)**; siempre → registro en `DIARIO` + `track-record` (§2.5/§2.6).
7. **Re-disparo de ESPERAR:** los votos `ESPERAR` quedan en la tarea con su `proyeccion.gatillo/invalida`. En la siguiente corrida, el Vigía **re-evalúa los gatillos abiertos** contra el nuevo snapshot: si el gatillo se cumple → reabre la discusión (puede pasar a ENTRAR); si se cumple la invalidación → cierra la hipótesis como negativa en el track-record. *(Esto es lo que hace medible y auditable cada ESPERAR.)*

---

## §6 — Decisiones abiertas (`[impl]`)
- `// TODO [impl]` **k de proximidad** (Q "accionable" del Vigía): ¿a cuántos ATR de una zona se crea tarea? (arrancar `k=0.5·ATR_H1`, medir ruido/RPD).
- `// TODO [impl]` **dónde corre Q6** (cálculo R:R): lo propone el agente, pero el SL/TP "estructural" podría calcularlo el Pine (determinista) y el agente solo citarlo → menos invención. Evaluar.
- `// TODO [impl]` **formato exacto del comentario Kanban** (validar el YAML §3 contra el formato real de `kanban_show`).
- `// TODO [impl]` **normalización de huso** de la sesión (NSL usa horas Colombia; confirmar y centralizar la conversión a UTC/sesión).
- `// TODO [impl]` **re-evaluador de gatillos** del Vigía (§5.7): cómo persiste/consulta los ESPERAR abiertos.

## §7 — Por qué es candidato a ADR-012
Fija un **contrato transversal** del enjambre (snapshot + cadena + salida) del que dependen TODOS los agentes y el scoring aguas abajo (IS/OOS → Pine/EA, regla §0.7). Cambiarlo después rompe a todos los consumidores → merece quedar registrado como decisión arquitectónica, con su alternativa (snapshot por LLM-visión, descartada por invención) y su relación con ADR-005 (modos) y ADR-007 (EA razona confluencias).

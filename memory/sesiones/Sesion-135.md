# Sesión 135 — 2026-07-18

## Objetivo con el que arrancó
Heredado de S134: (1) decidir el remedio del defecto chart-TF (regla de operación de coste cero vs ventana real en el CORE) — bloquea la F1-GATE; (2) arreglar `chartState.pdMid` (Hallazgo 3 de S134); (3) resolver la contradicción viva de §2.3.2 sobre si `pdWindow` es obligatoria u opcional.

## Rama
`pine/sistema-completo`

## Commits (9 + cierre)
- `5094d2a` fix(pine-visual): F1-S135 `chartState.pdMid` nunca se asignaba en el bloque chart-TF. **Revertido después en la misma sesión por `f9357a4`.**
- `16600dd` docs(doctrina): F1-S135 ADR-023 — el defecto chart-TF se acota por operación, no con `pdWindow`. Crea `docs/adrs/ADR-023-lectura-del-panel-desde-el-tf-mas-bajo.md` y reescribe `docs/reglas-smc-ict.md` §2.3.2.
- `e860553` test(probe): F1-S135 arnés de verificación en vivo del fix de `chartState.pdMid`. Crea `scripts/gen_probe_pdmid.py` (probe v15, marker 1350).
- `f9357a4` revert(pine-visual): F1-S135 el fix de `pdMid` NO CABE — CE10117 medido, y el fix es INERTE. Deja `pine/SMC-Visual.pine` idéntico a `e427bbf`.
- `d1166d4` docs(cierre): Sesion-135 — ADR-023 decidido; el fix de pdMid no cabe (por 6 tokens) y es inerte. **Cierre inicial de la sesión (luego continuó, ver segundo bloque).**
- `e033dd3` test(audit): F1-S135 auditoría estática de código muerto en los 3 consumidores. Crea `scripts/audit_codigo_muerto.py`.
- `42207ea` test(ablacion): F1-S135 MEDIDO — en Pine una función NO LLAMADA cuesta CERO tokens. Crea `scripts/gen_ablacion_core.py`.
- `df2cf72` test(ablacion): F1-S135 MEDIDO — Context usa ~15k tokens y tiene ~85k libres. Mide la capacidad de Context.
- `3e1b448` test(audit): F1-S135 auditoría de código muerto con cierre transitivo y cruce de los 3. Crea `scripts/audit_muerto_transitivo.py`.
- `2667d45` docs(fable): F1-S135 dossier de auditoría — capacidad, código muerto y reparto del dibujo. Crea `docs/planes/DOSSIER-FABLE-capacidad-y-codigo-muerto-S135.md` y `docs/planes/PROMPT-FABLE-S135.md`.
- (Y un commit final de cierre que añade avisos a ADR-020 y ADR-022 y esta documentación.)

## Estado técnico
LIBRARY CORE INTACTO. SHA `9559a0d7fe58b213` (1776 líneas). EXTREMES CORE SHA `5f851d87e5fda720` (148 líneas). check-core-sync OK ×3 + EXTREMES CORE OK. Sin tag (no se completó ninguna fase). F1-GATE: el bloqueante doctrinal se levanta con ADR-023, pero la gate NO está firmada (siguen pendientes los conceptos de la lista de pendientes).

## Punto 1 — decisión del usuario: ADR-023
El defecto chart-TF (medido en S134: una columna del panel se lee correcta si y solo si `chart-TF <= TF de la columna`) se acota con una REGLA DE OPERACIÓN, no con código.

Regla adoptada: el panel y el dibujo del P/D son válidos leídos desde el TF más bajo de los que se muestran; con las 3 columnas activas el chart debe estar en M5; las columnas por debajo del chart-TF quedan truncadas y no deben usarse.

El usuario eligió esta opción entre 3 (las otras: ventana real con array de strong en el CORE; regla de operación + guardia visual en el panel).

Razones registradas en el ADR: la Strategy de Fase 2 corre sobre un solo chart-TF (el de entrada, M5) donde las 3 columnas ya son correctas; el artefacto es de `request.security` y no existe en MQL5 (el EA lee barras por TF con conteo fijo); la ventana real rompería el SHA + re-baseline ×3 + riesgo OOM de S105 + tokens del CE10117.

**Deuda aceptada y explícita:** queda una holgura del determinismo (regla dura #1) acotada al TF más bajo; se reevalúa en Fase 3 con datos de calibración reales (ADR-002).

## Punto 3 — resuelto como consecuencia del punto 1
La contradicción viva de §2.3.2 (`pdWindow` "obligatoria" vs "OPCIONAL") se resuelve a favor de OPCIONAL. §2.3.2 reescrita: el aviso "LA VENTANA ES OBLIGATORIA" se sustituye por la regla de lectura del panel; la tabla de parámetros conserva `pdWindow` = OPCIONAL con referencia cruzada. Es la 6.ª corrección del hilo `pdWindow`.

## Punto 2 — `chartState.pdMid`: fix hecho, verificado en vivo, y revertido (hallazgo principal)
Contexto: el bloque chart-TF asignaba `pdLow`/`pdHigh` pero nunca `pdMid`, que quedaba en su default `na` ⇒ las lecturas de `f_wickNearLevel` (Rejection §2.7) recibían `na` ⇒ el borde EQ nunca participaba en la confluencia de mecha. Muerto desde el Sprint 1.5 (commit `5bc4828`).

Verificación en vivo — probe v15, marker 1350, OANDA:EURUSD, chart en M5, 5759 barras confirmadas. A/B de `f_wickNearLevel` con `pdMid` (fix) vs con `na` (bug), en el mismo punto del script. Predicciones escritas ANTES de medir, 3 verdes de 4:

- **P1 VERDE** (fácil, declarada de antemano): `pdMid`=1.14036 = esperado 1.14036, `nMidNa`=0 en 5759 barras.
- **P2 VERDE** (la que decide): `nDiffLow`=2, `nDiffHigh`=9, suma 11 > 0 ⇒ el fallo silencioso era real.
- **P3 VERDE**: impacto 0.19% < 5%. Confirma el modelo del cortocircuito de `f_wickNearLevel` (zonas → pools → EQH/EQL → P/D → EMAs; el borde EQ es la 4.ª comprobación).
- **P4 FALSA**: `nRejDiff`=0, con `nRejTotal`=1235 (no es un cero trivial). En 5759 barras, las 11 en que el ancla difiere nunca coinciden con una que además cumpla la geometría de rechazo ⇒ CERO rejections cambian.

**Por qué se revirtió — dos razones independientes, ambas medidas:**

1. **NO CABE.** Medido en `pine_get_console` con apply real, límite 100256: fix original (con guard `na(...) ? na :`) = 100300 (+44); fix adelgazado (aritmética pura, sin guard) = 100262 (+6). El guard costaba 38 tokens. Ni la versión mínima entra: falla por 6 tokens.
2. **ES INERTE.** P4 falsa (0 rejections cambian).

Hallazgo adicional verificado en pantalla: el DIBUJO del EQ nunca estuvo afectado, porque `:4467` ya tiene el fallback `na(s.pdMid) ? (s.pdHigh + s.pdLow) / 2.0 : s.pdMid`. La etiqueta "EQ 1.14036" en pantalla coincide con el `pdMid` medido por el probe. El único consumidor sin red era `f_wickNearLevel`.

**Deuda abierta (no se pierde):** `chartState.pdMid` sigue sin asignarse; el borde EQ no participa en la confluencia de mecha (§2.7). Defecto real de doctrina, medido como inocuo en EURUSD M5. Se retoma cuando haya headroom (solo RETIRAR código lo da — ADR-020/ADR-022). Forma correcta cuando se retome: `chartState.pdMid := (chartState.pdHigh + chartState.pdLow) / 2.0`, SIN guard, porque la aritmética de Pine ya propaga `na`. **Faltan 6 tokens.**

## Error de método propio (norma nueva)
Se commiteó `5094d2a` afirmando "compila 0/0" como si eso validara el cambio. `pine_check.py` es server-side y NO CUENTA TOKENS — ya estaba en la memoria del proyecto junto con "el número real de tokens está en `pine_get_console`". El commit rompió el apply en vivo y se dio por bueno.

**Norma nueva:** con el presupuesto de tokens en ~0, ningún cambio a `pine/` se da por bueno sin un APPLY REAL en TradingView.

## Gotchas de método confirmados (ya conocidos, se reconfirman)
- `pine_inject.py` solo GUARDA y devuelve `CLICK: Pine Save` (busca botones en inglés, el TV está en español).
- El apply real = remove del estudio + inject + clic en el botón "Añadir al gráfico"/PLAY (localizado en x=1791,y=79 vía `ui_evaluate` en vez de adivinar coordenadas) + confirmar en `pine_get_console`.
- El clic puede quedarse solo en "guardado" y hay que repetirlo (pasó una vez).
- El Visual completo tarda ~60-75s en aplicar.

## Segundo bloque — auditoría de capacidad y de código muerto

Continuación de la sesión tras el cierre inicial (`d1166d4`). `pine/` NO se tocó en todo el segundo bloque. CORE SHA `9559a0d7fe58b213` (1776 líneas) intacto. EXTREMES CORE `5f851d87e5fda720` (148 líneas). check-core-sync OK ×3 + EXTREMES CORE OK. Sin tag.

**Restricción nueva y dura (dato del usuario):** el usuario está en el plan gratuito de TradingView = máximo 2 indicadores por gráfico. Hoy aplicados Visual + Context; no hay tercer hueco. El usuario pidió además que el código quede totalmente limpio y auditable y que se reordene si hace falta, sin quedar spaghetti.

**Verificado en vivo:** Context está aplicado en el chart y es la versión del repo — el legend muestra 13 valores numéricos y el repo tiene 17 inputs de los que 4 son booleanos (no aparecen en el legend); los 13 coinciden uno a uno y en orden: 6 · 0,5 · 1 · 5 · 50 · 1,5 · 0,7 · 3 · 0,1 · 2 · 0,25 · 0,1 · 2. Sin error rojo, dibuja 8 líneas.

**Hallazgo principal del segundo bloque — en Pine una función NO LLAMADA cuesta CERO tokens.** Medido tres veces con apply real (OANDA:EURUSD, límite 100256), lastre idéntico en los tres builds: Visual + lastre = 107986; Visual + lastre MENOS 3 funciones sin call-site (101 líneas) = 107986; Visual + lastre MÁS 36 funciones duplicadas y no llamadas (590 líneas) = 107986. Tres builds distintos, el mismo número exacto. ⇒ Pine hace tree-shaking completo de las funciones sin call-site. CONTRADICE ADR-020 y ADR-022 ("en Pine una función no-llamada SÍ cuenta tokens"); CONCUERDA con S121 ("la dieta S120 fue no-op"). El proyecto arrastraba dos hallazgos incompatibles sin que nadie los cruzara. Se añadió un aviso "PREMISA CUESTIONADA POR MEDICIÓN" en la cabecera de ADR-020 y ADR-022 (verificado presente en ambos archivos); NO se revoca ninguno de los dos, porque queda sin explicar por qué el fix de ADR-022 resolvió el CE10117 en S133. La formulación provisional correcta es "solo retirar código QUE SE EJECUTA ahorra".

**Capacidad medida de Context:** Context + 2500 unidades de lastre = bajo el techo (sin número); + 3000 = 103355; + 3800 = 126892. ⇒ unidad de lastre 29.42 tokens ⇒ Context solo ≈ 15.100 tokens (15% del techo) ⇒ hueco libre ≈ 85.000 tokens (85%). Cross-check que pasa: la corrida de 2500 predice 88.644 < 100256, coherente con que saliera bajo el techo. Reparto del Visual por líneas (no medido en tokens, solo en líneas): LIBRARY CORE ~1776, DETECCIÓN TF PROPIO ~953, MTF ~455, DIBUJO ~1411, PANEL+ALERTAS ~236.

**Contradicción abierta, NO resuelta:** la retro-cuenta del Visual da ≈99.160 tokens pero las medidas de `pdMid` del primer bloque lo situaban en ≈100.250. Diferencia ≈1.100 tokens, que una sola sentencia no explica. Dos hipótesis, NINGUNA MEDIDA: (a) el coste del lastre no es perfectamente lineal (hay un término por función de troceo, ~84 tokens, que un modelo de 2 puntos no separa); (b) interacción de tree-shaking: asignar `chartState.pdMid` mantendría vivo código que hoy se elimina, y entonces el fix no costaría una línea sino la cadena que revive. Si fuera la (b), reencuadra el episodio de `pdMid` entero. El número de Context se considera sólido; el del Visual NO se usa para decidir nada hasta re-medirlo.

**Auditoría de código muerto (cierre transitivo, sobre código sin comentarios ni strings):** Visual 120 funciones / 3 muertas / 4 constantes sin uso; Strategy 71 / 1 / 3 y un input sin uso (`i_scoreThresh`); Context 71 / 43 muertas / 53 constantes sin uso. Resultado que manda: NINGUNA función está muerta en los 3 consumidores ⇒ ninguna se puede borrar sin romper la regla dura #2 (CORE byte-idéntico). Las 43 que Context no llama están vivas en Visual o Strategy: eso es RELOCALIZACIÓN (patrón ADR-020/ADR-022), no limpieza — y tras el hallazgo del tree-shaking, no compra ni un token. Lo único borrable son 3 constantes (`KIND_GRAB`, `KIND_GRADIENT`, `MTF_SLOT`) y 1 input (`i_scoreThresh`), verificados a mano uno a uno incluyendo strings y comentarios. NO SE BORRARON: son andamiaje deliberado — los `KIND_*` son IDs de la taxonomía de eventos que el EA MQL5 replicará en Fase 4 (borrarlos arriesga que se reutilice un ID y los golden tests diverjan) e `i_scoreThresh` lleva la etiqueta literal "Score threshold (calibrar Fase 3)". Además borrarlos ahorra 0 tokens. Queda como decisión del usuario/Fable.

**Hallazgo de auditabilidad más serio:** `pine/SMC-Library.pine` (1498 líneas) no lo importa nadie — cero `import` en los 3 consumidores — y está desincronizado con el CORE vivo: le faltan 6 funciones del CORE (`f_farthestEvent`, `f_farthestPool`, `f_farthestZone`, `f_pdBottom`, `f_pdRelatch`, `f_pdTop` — el motor del 2.º extremo de ADR-021) y conserva 2 que el CORE ya no tiene (`f_resetTrailingHigh`, `f_resetTrailingLow`), que son exactamente las de la Opción A que ADR-021 sustituyó. Último commit S120; `check-core-sync.ps1` NO lo verifica, así que deriva en silencio. No está solo rancio: encierra el diseño del P/D ya superado. Tres opciones planteadas y NO decididas: (1) resincronizarlo y añadirlo a check-core-sync, (2) borrarlo, (3) congelarlo con aviso de SUPERSEDIDO. Se recomienda la (1).

**Problema estructural identificado:** el alcance completo de Fase 1 que exige el usuario (todas las familias de concepto, sus variantes, los 3 TF y la herencia MTF) NO CABE en un solo indicador. Visual a ~0 de headroom, Context con ~85% libre, solo 2 slots, y los indicadores no pueden comunicarse en ejecución (restricción de TV) ⇒ mover el dibujo de una familia a Context obliga a llevar también su detección. La única vía que escala parece repartir el DIBUJO vivo entre los 2 consumidores, pero no está decidido: se entregó a Fable.

**Entrega a Fable:** `docs/planes/DOSSIER-FABLE-capacidad-y-codigo-muerto-S135.md` (autocontenido, cada afirmación marcada [MEDIDO]/[NO MEDIDO]/[OPINIÓN], con 7 preguntas concretas) y `docs/planes/PROMPT-FABLE-S135.md` (prompt copiable). Se le pide auditoría ADVERSARIAL: verificar los [MEDIDO], resolver las 2 contradicciones abiertas, responder las 7 preguntas y recomendar el camino con coste y medición previa.

**Seis trampas de método atrapadas y medidas:**
1. `pine_check.py` no cuenta tokens, el número real está en `pine_get_console`.
2. Un lastre que se asigna y nunca se lee lo tree-shakea Pine entero ⇒ el build sale bajo el techo y NO hay medición ("Compilando... → guardado" sin número) ⇒ debe desembocar en un `plot`.
3. Demasiadas sentencias en el cuerpo principal ⇒ "The main body of the script is too long. Try wrapping code in functions".
4. Una sola función gigante vuelve a topar ese límite ⇒ trocear en funciones de 200 sentencias.
5. `pine_inject.py` solo GUARDA y el clic de apply a veces se queda en "guardado" y hay que repetirlo.
6. El CDP se cae y hay que relanzar con `tv_launch`.

## Pendiente / siguiente (S136)
1. Esperar la revisión de Fable (dossier + prompt entregados) — bloquea las decisiones sobre reparto del dibujo, `SMC-Library.pine`, los 4 placeholders y el criterio de cierre del determinismo.
2. Tras Fable: sesión de revisión de conceptos — matriz concepto × TF × {nativo, heredado}, qué hay y qué falta.
3. Después: tareas pendientes de la F1-GATE — fallback M2, IFVG por banda/lado, gate MB/BPR, `elig` excluye ZS_MITIGATED, calibrar `LEG_ANCH_TOL_ATR`, deudas S123, herencia MTF.
4. Deuda de `pdMid` (faltan 6 tokens, pendiente de la contradicción del Visual).
5. No repetir las hipótesis ya refutadas con medición de S128-S135.
6. Toda validación visual del P/D multi-TF se hace DESDE CHART M5 (ADR-023).

## Referencias
`docs/adrs/ADR-023-lectura-del-panel-desde-el-tf-mas-bajo.md` · `docs/reglas-smc-ict.md` §2.3.2 · Sesion-134.

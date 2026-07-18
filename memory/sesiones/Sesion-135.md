# Sesión 135 — 2026-07-18

## Objetivo con el que arrancó
Heredado de S134: (1) decidir el remedio del defecto chart-TF (regla de operación de coste cero vs ventana real en el CORE) — bloquea la F1-GATE; (2) arreglar `chartState.pdMid` (Hallazgo 3 de S134); (3) resolver la contradicción viva de §2.3.2 sobre si `pdWindow` es obligatoria u opcional.

## Rama
`pine/sistema-completo`

## Commits (4)
- `5094d2a` fix(pine-visual): F1-S135 `chartState.pdMid` nunca se asignaba en el bloque chart-TF. **Revertido después en la misma sesión por `f9357a4`.**
- `16600dd` docs(doctrina): F1-S135 ADR-023 — el defecto chart-TF se acota por operación, no con `pdWindow`. Crea `docs/adrs/ADR-023-lectura-del-panel-desde-el-tf-mas-bajo.md` y reescribe `docs/reglas-smc-ict.md` §2.3.2.
- `e860553` test(probe): F1-S135 arnés de verificación en vivo del fix de `chartState.pdMid`. Crea `scripts/gen_probe_pdmid.py` (probe v15, marker 1350).
- `f9357a4` revert(pine-visual): F1-S135 el fix de `pdMid` NO CABE — CE10117 medido, y el fix es INERTE. Deja `pine/SMC-Visual.pine` idéntico a `e427bbf`.

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

## Pendiente / siguiente (S136)
1. Pendientes de la F1-GATE: fallback M2, IFVG por banda/lado, gate MB/BPR, `elig` excluye ZS_MITIGATED, calibrar `LEG_ANCH_TOL_ATR`, deudas S123, herencia MTF.
2. La deuda de `pdMid` (faltan 6 tokens).
3. No repetir las hipótesis ya refutadas con medición de S128-S134.
4. Toda validación visual del P/D multi-TF se hace DESDE CHART M5 (ADR-023).

## Referencias
`docs/adrs/ADR-023-lectura-del-panel-desde-el-tf-mas-bajo.md` · `docs/reglas-smc-ict.md` §2.3.2 · Sesion-134.

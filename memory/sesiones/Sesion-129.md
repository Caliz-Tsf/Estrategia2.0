# Sesion-129 — 2026-07-15 — Opción C: la medida rompe el propio diseño de S128

## Objetivo sesión
Paso 1 del orden dejado por S128: construir el probe de la Opción C en sombra y medir P-C1..P-C5, sin
tocar `pine/`.

## Resultado
F1-GATE SIGUE BLOQUEADA. `pine/` NO se tocó. **CORE SHA `752b4083a7db419d`** (1866 líneas) INTACTO.
core-sync OK ×3. `pine_check` 0/0 en los 4 probes. SIN ADR (la Opción C sigue en PROPUESTA). SIN tag.

## Commits (3, todos solo scripts)
- `6c7b8cd` — arnés de la Opción C (rango pegajoso) + test de convergencia por semilla
- `c2b85df` — arnés C1 (latch) vs extremo de la ventana
- `96e379f` — la Opción C LITERAL = min/max de la ventana + 2 correcciones propias

## Arneses creados (4 scripts)
- `scripts/gen_probe_rango_pegajoso.py` (marker 129)
- `scripts/gen_probe_rango_pegajoso_semilla.py` (marker 1292)
- `scripts/gen_probe_c1_vs_extremo_ventana.py` (marker 1293)
- `scripts/gen_probe_c_literal.py` (marker 1294)

## Tarea 1 — C1 en sombra (probe v1, marker 129), D1/H1/M5 OANDA:EURUSD

| TF | n barras | cHi | cLo | ampC (pips) | ampA (pips) |
|---|---|---|---|---|---|
| D1 | 6283 | 1.60195 | 0.95360 | 6483.45 | 758.5 |
| H1 | 9535 | 1.20831 | 1.01779 | 1905.2 | 85.3 |
| M5 | 6426 | 1.16221 | 1.13246 | 297.5 | 46.6 |

D1: pctC=29.4% discount. reachLo_C=0.95360 vs reachLo_A=1.13246. H1: nLoViol=0. M5: nHiViol=0.

- **P-C3 (la que decide) VERDE:** el alcance de abajo cae 1.13246 → 0.95360, dentro de lo predicho
  (0.95-1.02).
- **P-C1 casi:** el low sale exacto vs la lectura del usuario (0.9536); el high queda 36 pips corto
  (1.60195 vs 1.60554).
- **P-C2 se cumple** (D1 6483 > H1 1905 > M5 297) **PERO la Opción A vigente también ordena monótono**
  (758 > 85 > 46.6) — ver corrección al diseño de S128 más abajo.
- **P-C4 NO medido** sobre historia, solo en la última barra. Queda pendiente.
- **P-C5 mitad FALSA:** D1 reancla 6 veces (predicho ≲5); M5 solo 8 (predicho "muchas").
- **HALLAZGO:** H1 nLoViol=0 y M5 nHiViol=0 → esos extremos nunca se violaron, son el primer pivote de
  la ventana, no un evento medido.
- La otra mitad de P-C3 (que los 5 OB + 11 FVG + 1 BRK + 3 IFVG del censo S127 entren en banda 1-3) NO
  se midió: el probe va truncado en `// === DIBUJO ===` y el band-pick vive después.

## Tarea 2 — test de convergencia por semilla (probe v2, marker 1292)
D1 EURUSD, 4 sombras al 0/25/50/75% de la historia, las 4 con `sSeeded=2`:
- cLo: 0.95360 en las 4. spreadLo = 0.0 pips.
- cHi: 1.60195 / 1.60195 / 1.39937 / 1.23496. spreadHi = 3669.85 pips.
- Veredicto P/D según semilla: 29.3% discount / 29.3% discount / 42.7% discount / 67.6% PREMIUM.
- P-S1 y P-S2 CONFIRMADAS (escritas antes de medir).

## Tarea 3 — el mismo test en OANDA:NAS100USD D1 (probe v2), n=6021, las 4 con `sSeeded=2`
- spreadHi = 0.0 (las 4 convergen en cHi=26288.1). spreadLo = 9410.9 (cLo: 1016.1 / 1016.1 / 3689.2 /
  10427.0).
- **Patrón INVERTIDO respecto a EURUSD** → el lado fósil cambia de bando según la tendencia secular del
  símbolo. Predicción escrita antes de medir, CONFIRMADA.
- Con probe v1 en NAS100USD: pctC=1.1 (precio FUERA del rango), pctA=0.9, nHiViol=2803/6021=46.6%.

## Tarea 4 — C1 (latch) vs extremo de la ventana (probe v3, marker 1293), D1 EURUSD n=6283

| Lado | cLo/cHi | runMin/MaxLo/Hi | Acuerdo | dif. máx |
|---|---|---|---|---|
| low | 0.95360 | 0.95360 | 93.7% (5889/6283) | 0.0 pips |
| high | 1.60195 | 1.60389 | 24.8% (1560/6283) | 19.4 pips |

nHiDown=0, nLoUp=0 → el latch NUNCA bajó/subió el extremo. nPivHi=42, nPivLo=36 (pivotes de escala 50
en 24 años). P-E1 mitad ✅ (abajo 93.7%) / mitad ❌ (arriba 24.8%). P-E2 ❌. P-E3 ❌.

## Tarea 5 — HALLAZGO PRINCIPAL: la Opción C LITERAL (probe v4, marker 1294), D1 EURUSD n=6283
El diseño de S128 §3 se CONTRADICE: su pseudocódigo dice "strongHigh: se queda" (sin expansión) pero
su texto dice "lo único que cambia es CUÁNDO se llama al reset" (⇒ `f_updateTrailing` SE CONSERVA). Los
probes v1/v2/v3 midieron la PRIMERA lectura.

Con la expansión conservada: rango `[0.90275, 1.60389]`, 7011.35 pips, pctC=34.3% discount.

**`nHiReset=0` y `nLoReset=0` en 6283 barras: close > top es IMPOSIBLE** (top>=high>=close) → la
violación NUNCA se dispara → `i_pdSwingLen` es IRRELEVANTE para el rango. **La Opción C literal es el
MÁXIMO Y EL MÍNIMO DE LA VENTANA.** Ni latch, ni semilla, ni pivotes participan.

nOutOfRange=0 → conserva el invariante pct ∈ [0,1]. P-F1 ❌ FALSA (se predijo `[0.95360, 1.60554]`,
salió `[0.90275, 1.60389]`). P-F2 ✅. P-F3 ✅.

## Tres auto-correcciones (hallazgos propios de esta misma sesión que quedaron refutados)
1. Corrige `c2b85df`: "16.5 pips son del pivote estricto que no ve el pico de 2008" es FALSO. El máximo
   absoluto de OANDA:EURUSD D1 ES 1.60389 (= el runMaxHi de pivotes del v3) → el pivote SÍ capturó el
   máximo real. El 1.60554 del usuario NO EXISTE en este feed; ninguna regla puede producirlo.
2. Corrige `6c7b8cd`: "C1 es robusta por abajo y arbitraria por arriba" describe la VARIANTE CON LATCH,
   no la Opción C. En la C literal AMBOS lados son el extremo de la ventana → los dos dependen al 100%
   de la historia disponible.
3. El pctC=1.1 (precio fuera del rango) de NAS100USD era defecto de la variante con latch (que quita la
   expansión), NO de la Opción C.

## Corrección al diseño de S128
Su §2 afirma que "la jerarquía está INVERTIDA". No se sostiene: la Opción A vigente también ordena
monótono (D1 758 > H1 85 > M5 46.6 pips). El defecto es la ESCALA, no el orden. S128 comparaba el D1
implementado contra el H1 deseado del usuario, que son cosas distintas.

## Verificación en código (leída, no inventada)
`f_premiumDiscount` (:1200-1206) NO clampea el pct; el invariante pct ∈ [0,1] lo garantiza
`f_updateTrailing` al expandir cada barra (comentario en :2249-2251).

## Recomendación al usuario (multi-símbolo; sigue en PROPUESTA, sin ADR)
Ventana DECLARADA en D1 (input explícito en barras) + HERENCIA hacia abajo (la maquinaria S115/ADR-018
`f_tfExtremes` y §5.16 ya existen, cero código) + declarar en el panel cuando el símbolo no tiene
historia suficiente. Descartada la "asimetría honesta" (C1 abajo + A arriba) porque el lado fósil
cambia de bando según la tendencia del símbolo → hardcodearlo viola ADR-001. "Caducidad por antigüedad"
y "ventana por contrato" son la misma cosa. Declarar la ventana no añade un grado de libertad: quita
uno descontrolado (hoy la fija TV). La lectura H1 del usuario `[1.02175, 1.39970]` NO es obtenible
nativamente (1.39970 es de 2014 → ~75.000 barras H1; TV da 9.535) → el macro no se recalcula por TF, se
hereda de D1.

## Coste nuevo detectado
Si el rango es min/max histórico, PIERDE SIGNIFICADO ESTRUCTURAL — §2.3 habla de strong high/low
(pivotes) y esto es "el punto más alto jamás visto". Es una contradicción con la doctrina DISTINTA de la
que S128 anticipó. El ADR debe DESAMBIGUAR §3 del diseño antes que nada.

## Balance de predicciones
P-C1 casi, P-C2 ✅ con matiz, P-C3 ✅, P-C4 no medido, P-C5 mitad falsa, P-S1 ✅, P-S2 ✅, P-M1
(NAS100) ✅, P-E1 mitad, P-E2 ❌, P-E3 ❌, P-F1 ❌, P-F2 ✅, P-F3 ✅. Van **9 predicciones vivas de 21**.

## Gotchas de método (nuevos o reconfirmados)
- **RECONFIRMADO (S126):** `data_get_study_values` sigue el CROSSHAIR. Una lectura dio P_nBars=5543 y
  P_close=1.07966 (barra histórica, no la última). El plot de control `P_close` lo delató. Antídoto:
  mover el ratón al borde derecho del chart (`ui_mouse_click move_only`) antes de leer.
- **RECONFIRMADO (S128):** el marcador `P_marker` por build es lo único que distingue un build fresco de
  uno rancio. Salvó la sesión 2 veces (leí marker 129 cuando esperaba 1292/1294).
- El patrón de apply real: `pine_inject.py` solo GUARDA ("CLICK: Pine Save"); hacen falta 1-3 Ctrl+Enter
  nativos con re-foco de Monaco entre medias. La consola dice "guardado" vs "Compilado." + "Añadido al
  gráfico".
- Cada apply crea una instancia NUEVA; la vieja queda pinneada al bytecode anterior y sigue devolviendo
  valores del probe viejo → hay que removerla con `chart_manage_indicator` (requiere `entity_id` Y
  `indicator`).
- Confirmado (S116): un estudio aplicado rastrea su slot EN VIVO → guardar el slot muta la instancia.

## CORE
- **SHA `752b4083a7db419d`** (1866 líneas) — **INTACTO**
- core-sync OK ×3 · `pine_check` 0/0 en los 4 probes

## Estado
- **F1-GATE BLOQUEADA** · SIN ADR · SIN tag · rama `pine/sistema-completo`

## Pendiente S130 (orden sugerido)
1. **DECISIÓN DEL USUARIO (bloquea todo):** desambiguar §3 del diseño de S128 (¿con o sin expansión?) y
   decidir qué ancla el rango. Es doctrina (§2.3 strong high/low vs paridad LuxAlgo) y toca el CORE.
2. La otra mitad de P-C3: que los 5 OB + 11 FVG + 1 BRK + 3 IFVG del censo S127 entren en banda 1-3. No
   medible con el probe truncado.
3. P-C4 (anidamiento D1 ⊇ H1 ⊇ M5) sobre historia, no en un punto.
4. Si se decide C → ADR (desambigua §3, sustituye T07/S021, decide doctrina vs paridad LuxAlgo) +
   rederivar los casos de prueba de §2.3 + CORE + re-baseline SHA ×3.
5. Deudas heredadas de S127 que no se tocaron: IFVG disciplina por banda/lado; MB/BPR gate de banda;
   calibrar `LEG_ANCH_TOL_ATR`; `elig` excluye ZS_MITIGATED del band-pick en Visual; deudas S123
   #2/#3/#4; auditoría de herencia MTF.

## Enlaces
[[Sesion-128]] · [[Sesion-127]] · `docs/planes/DISENO-opcion-C-rango-pegajoso-S128.md`

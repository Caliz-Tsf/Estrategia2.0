# Sesión 145 — DOL: escalera de liquidez del máximo histórico al mínimo histórico

- **Fecha:** 2026-07-25 / 27
- **Rama:** `pine/sistema-completo`
- **CORE:** INTACTO todo el tramo — SHA `7ad95b3e612d041a` (1783 líneas). `check-core-sync` OK ×3 en cada commit.
- **TV:** `SMC_Library` v416 (Visual) · `SMC_Context` v22. Compila 0/0, sin error de tokens.

## Objetivo

Heredado de S144: arrancar **DOL (Draw On Liquidity)** para resolver de raíz (a) el **marcador de
borde** para objetivos lejanos sin romper la escala y (b) la **escalera de old highs/lows**. Luego
retomar la curación de la familia Liquidez.

## Resultado

**DOL implementado y verificado en vivo en D1 EURUSD.** La escalera cubre del **máximo histórico
(1.60389, jul-2008)** al **mínimo (0.90275)**, con 35 de 36 niveles anclados en su pivote y su línea.
La curación de Liquidez **no se retomó** (ver hilos abiertos).

---

## 1. El defecto original, medido

Con la familia Liquidez aislada y auto-escala ON en D1:

| | |
|---|---|
| Escala impuesta | 1.10000 → 1.54000 (4400 pips) |
| Velas reales | 1.135 → 1.185 (500 pips) |
| Velas ocupan | **~11% del panel** |
| Niveles horizontales vivos | **`[1.51]` — exactamente UNO** |

**Una sola primitiva consumía el 89% del espacio vertical.** Eso descartó de raíz que se arreglara con
cuotas, caps o modos de densidad: ninguno toca el problema. Solo cambiar *dónde se emite la línea*.

## 2. ADR-026 — decisiones

- **D1** La escalera se ancla en los **extremos** (alto más alto / bajo más bajo) y se lee hacia el
  precio. Corrección del usuario: anclarla en el precio dejaba el far pivot como cola, o sea el primero
  en caer si algo capa. Si `N` recorta, recorta **por el medio**.
- **D2** Sustituye a los 3 selectores ad-hoc de `f_drawPools` (más cercano / más lejano alineado /
  top-2 por `strength`). El orden **geométrico** manda: un objetivo se alcanza en orden, ordenar por
  `strength` daba una lista que el precio no puede recorrer.
- **D3** **Puerta de banda + marcador de borde**: fuera de banda no se emite primitiva a ese precio.
- **D7** La puerta aplica también al dibujo **heredado**, y ahí importa más (cuanto más bajo el TF, más
  estrecha la banda). Cascada: **D1 → sin contexto; H1 → solo D1; M5 → D1+H1**.
- **D8** **Escalera de extremos no barridos**: un pivote que ninguna vela posterior perforó. Recorrido
  nuevo→viejo con el extremo corrido ⇒ secuencia de récords.
- **D9** **Detector de pivotes propio** (`ta.pivothigh/pivotlow`, len 2, cap 400) — la única palanca
  que densifica, sin tocar `i_swingLen` (congelado hasta Fase 3, ADR-002).
- **D10** Columna de marcadores **fuera de la banda y del lado que toca** + separación mínima.
- **D11** Separación **creciente con la distancia** (`max(0.5·ATR, 4% de la distancia)`): fino cerca,
  grueso lejos. Tope 26.
- **D12** La escalera **cierra en el extremo real** del histórico (rastreado aparte): el mínimo
  absoluto cae en las primerísimas barras, donde `ta.pivotlow` no puede confirmar pivote.
- **D13** La banda sigue el **rango visible**, no un lookback fijo.
- **D14** Fuera de banda ⇒ **una etiqueta resumen por lado**, no una columna. Apilarlas las **desancla
  de su pivote** y el lector ve niveles donde no los hay: información falsa.

## 3. Hipótesis REFUTADAS con medición (no re-litigar)

| palanca probada | resultado |
|---|---|
| `i_ctxMitigated = true` (rescatar barridos) | **0 SSL nuevas** |
| Tope 12 → 18 | +6 arriba, **0 abajo** |
| Encadenar fuentes con el récord corrido | **incorrecto por construcción**: solo añade más profundo, nunca rellena huecos |
| Fundir + `SMC_eqhl` | **0 cambios** — un EQ está *por definición* al mismo precio que un pivote ya conocido ⇒ nunca es récord nuevo |
| `i_swingMaxKeep` 350 → 600 | **0 cambios** — capa OTRO array (dominante), no el de la escalera |
| `swingLen` 5 → 3 | +1 |
| `swingLen` 5 → 2 | **+2** ⇒ la granularidad de pivote SÍ era la palanca |

**Predicciones propias muertas en la sesión: 3** (que la escalera no cabría en tokens; que
`i_ctxMitigated` rescataría las SSL; que `swingLen=3` refutaba la detección — era prematuro, con 2 sí).

## 4. Gotchas de método (caros)

- **DOS editores Monaco.** `pine_inject.py` escribe en `getEditors()[0]`, que puede ser el **oculto**.
  **Sobrescribí el Visual con el Context dos veces** (v393, v395); restaurado desde el repo (v394, v396).
  Antídoto: elegir el visible por `offsetParent` y copiar `[0]`→visible con `executeEdits` (marca dirty;
  `setValue` NO ⇒ Ctrl+S no-op). Ni `pine_open` ni `pine_new` cambian el script destino: el que sí lo
  hace es **"Abrir script… Ctrl+O"** del menú del editor.
- **`pine_check` 0/0 + consola "guardado" NO garantizan un estudio sano.** Dos errores de *runtime*
  seguidos que ninguna de mis dos sondas vio y que el usuario detectó en pantalla:
  - `Invalid value of the 'length' argument in 'highest'. It must not be na` — en bar 0 no existe
    `time[1]`; faltaba `nz()`.
  - **RE10143** `The requested historical offset (1421) is beyond the historical buffer's limit (1420)`
    — longitud **dinámica** en `ta.highest`. Pine dimensiona el buffer con las primeras barras y
    revienta si luego crece. Fix: tres llamadas de longitud **fija** (200/1200/5000) y selección.
- **`ta.highest(high, N)` mira N velas atrás desde la vela ACTUAL**, no dentro de la ventana visible.
  Calcular N como el *ancho* de la ventana no sirve: hay que medir **desde el borde izquierdo hasta hoy**.
- **Escribir ids `in_N` sin mapear corrompió inputs dos veces** (6 numéricos puestos a `false`).
  Restaurados. Mapear siempre los 48 toggles antes de escribir.
- Cada apply crea **instancia nueva** del estudio con inputs por defecto ⇒ hay que rehacer el
  aislamiento y borrar la vieja (solo 2 slots).

## 5. Hilos abiertos (para S146)

### 5.1 ⭐ El indicador NO regenera SSL/BSL al avanzar la tendencia — PRIORITARIO

Planteado por el usuario y **con base medida**: S144 registró *"4 pools vivos en D1 = CORRECTO"*; en
S145 quedaba **1 solo pool vivo (BSL) y CERO SSL**. En las sesiones intermedias el precio se comió los
SSL que quedaban y **no apareció ninguno nuevo**.

La preocupación del usuario, textual: *"si el precio llegase a caer y romper esos bajos y no los
tenemos calculados sería pérdida igual"*. Y el fondo: **cuando el swing termine y el precio gire, el
indicador tendrá que ir creando los SSL/BSL que la pierna completada va dejando** — que es justo lo
que hace falta para saber a dónde apuntar tras el giro.

**A verificar en S146:** que al completarse una pierna y girar el precio, los pools de esa pierna pasen
a ser objetivos vivos con prontitud. Hoy no está comprobado.

### 5.2 Menores del DOL

- El escalón más profundo es **0.90275**, no el **0.90179** que el usuario marcó a mano. Sin resolver:
  o 0.90275 es el mínimo real de la serie cargada, o el cierre D12 no dispara.
- **Coste de rendimiento sin medir**: leer el rango visible hace recalcular en cada scroll/zoom
  (ADR-026 D4-1). Si el gráfico va pesado, revertir a lookback fijo.
- `▲ OH 1.51441` y `▲ BSL 1.51421` son **el mismo techo contado dos veces** (extremo estructural vs
  pool). Fusionar o marcar el solape.
- Distancia en **ATR del TF de origen** (el Context ya transporta `ctxD1_atr`/`ctxH1_atr`): hoy el mismo
  nivel dice `72×ATR` en D1 y `2507×ATR` en M5.

### 5.3 Heredado, sin tocar

- **Puerta de banda para P/D y Gradient Levels.** Con todo encendido hay 61 niveles horizontales entre
  0.92 y 1.59; los pools ya están gestionados, esos no. **Es lo que hace M5 ilegible hoy.**
- **Curación de la familia Liquidez** (el objetivo original de S144): aislar sweeps / IDM / Judas /
  False Breakouts, hue violeta sobrecargado, anti-solape EQL↔Sweep.
- Transporte MTF: hereda los pools **más cercanos**, no las anclas. Fuera del camino crítico porque el
  Context ya trae los extremos por su propio canal (`f_tfExtremes` → `f_farthestPool`).
- Con todo encendido el Visual llega a **500 etiquetas** = tope duro de Pine.

## 6. Commits (18)

`2519ee4` ADR-026 · `842d8db` Paso 1 · `1d9fbae` I-0 verificado · `dc6b5f6` distancia + confluencia ·
`e49be2d` D7 escalera MTF · `ce8b838` banda en Context · `0afe142` opción A · `ff88a6e` cascada ·
`dd799d5` labels aparcadas · `2d7eedd` escalera D8 · `32f6cde` tope 12 · `3ac0595` encadenado ·
`5fb25c1` tope 18 · `9b89808` fundir fuentes · `1fa4ba0` detector propio D9 · `66f8eef` D10 ·
`e0d67f8` D11 · `f99a14b` D12 · `519e01c` D13 · `6aac68d` bar 0 · `610eeec` FIX-2 · `68e11a1` FIX-3 ·
`4133685` D14

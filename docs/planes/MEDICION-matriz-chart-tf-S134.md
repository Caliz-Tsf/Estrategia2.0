# MEDICIÓN — La matriz chart-TF × columna del P/D, y el bug del dibujo (S134)

> **Estado:** MEDIDO en vivo, no inferido. OANDA:EURUSD, Visual del repo recién inyectado,
> instancia única en el chart, sin overrides de inputs.
> **Contexto:** S134 arrancó para "calibrar `pdWindow`" (plan heredado de S133). No se calibró nada:
> la medición cambió el problema.

## 0. Cómo arrancó: el diagnóstico que era humo

La sesión empezó **leyendo docs y código, sin medir**, y concluyó que el defecto del M5 estaba en el
acumulador de `f_pdRelatch` y que `pdWindow` no cabía en el UDT. **El estudio estaba caído en rojo en
TradingView** y nadie lo había mirado: se iba a calibrar contra un indicador muerto. Lo destapó el
usuario ("no está renderizando, está con un error rojo").

**El error NO era del repo.** El slot de TV tenía un build roto. Inyectado el Visual del repo:
`pine_check` **0/0**, consola `Compilando... → Compilado. → Añadido al gráfico.`, panel vivo.

> **NORMA NUEVA (gemela de la de S132):** ninguna conclusión sobre el comportamiento en vivo se emite
> sin haber mirado la pantalla. `study_count=0` **no** significa "renderizando"; puede ser un estudio
> en error. Screenshot **antes** de esperar.

## 1. La matriz de 9 celdas (lo que nadie había medido)

Veredicto P/D del panel, por columna × chart-TF. Precio ~1.1467.

| Columna | Chart **D1** | Chart **H1** | Chart **M5** |
|---|---|---|---|
| **D1** | Discount 34% | Discount 34% | Discount 34% |
| **H1** | *Discount 34%* | Premium 74% | Premium 74% |
| **M5** | *Premium 58%* | *Discount 21%* | **Premium 91%** |

*(cursiva = lectura truncada)*

### 1.1 La regla

> **Una columna se lee correcta si y solo si `chart-TF <= TF de la columna`.**

Pedir vía `request.security` un TF **más bajo** que el chart ⇒ TV sirve historia recortada ⇒ el
acumulador de strong ve menos eventos ⇒ el 2.º extremo no llega tan lejos ⇒ rango estrecho.

### 1.2 El sistema FUNCIONA

Desde **chart M5** las tres columnas dan **34 / 74 / 91**, que es celda por celda la tabla del gate de
`reglas-smc-ict.md` §2.3.2 (D1 0.344 · H1 0.733 · M5 0.929). **La cascada anida y rota, con cero
parámetros.** Lo que S133 entregó estaba bien; se leyó desde un chart H1, que es donde D1 y H1 son
válidos.

### 1.3 Dos correcciones

1. **§2.3.2 dice que el defecto es solo del M5. FALSO: el H1 también falla** (34% desde chart D1).
   El alcance es mayor del documentado.
2. La hipótesis de esta sesión ("solo M5 sufre; D1/H1 a salvo") era **mitad falsa**: D1 sí es estable
   (34% en las tres), H1 no.

### 1.4 Qué le hace al remedio

"Calibrar `pdWindow`" deja de ser obviamente la respuesta. Aparece una opción de **coste cero** que no
estaba sobre la mesa: **declarar que el panel es válido leído desde el TF más bajo** — regla de
operación, no código. La cara (ventana real + array de strong con `barIdx` en el CORE, con el riesgo
OOM de S105 y los tokens contra el CE10117) solo hace falta si el panel debe ser correcto desde
**cualquier** chart-TF. **DECISIÓN ABIERTA — no se implementó nada.**

## 2. BUG ENCONTRADO Y ARREGLADO: el dibujo se quedó en la Opción A

La tarea "nadie ha visto los 3 P/D dibujados" (pendiente desde S133) **no era cosmética**.

**Medido, chart D1, antes del fix** — etiquetas dibujadas:

| | Dibujado | Correcto (ADR-021) | Error |
|---|---|---|---|
| Premium | **1.60389** | 1.51441 | **~900 pips** |
| EQ | 1.25332 | 1.23400 | |
| Discount | **0.90275** | 0.95360 | ~508 pips |

`[0.90275, 1.60389]` es el **trailing range** (min/max de toda la historia D1 — el mismo que S129 midió
como "Opción C literal"). El EQ cuadraba con el rango equivocado: (0.90275+1.60389)/2 = 1.25332 exacto.

**Causa:** `pine/SMC-Visual.pine:3516` leía `trailing.top`/`trailing.bottom` y **nunca miraba**
`chartState.pdHigh`/`pdLow`. El ADR-021 cambió el motor y el panel **y se olvidó del dibujo**. El
comentario de encima seguía describiendo el diseño viejo (citando `lastTopTime` de LuxAlgo).

### 2.1 Por qué sobrevivió una sesión entera — la lección de método

**En porcentaje casi no se nota: 35% dibujado vs 34% del panel.** Dos rangos completamente distintos
producen casi el mismo `pct`. ⇒ **El `pct` es un discriminador PÉSIMO; solo los NIVELES delatan.**
El gate de S133 se pasó con un probe **truncado antes del bloque de dibujo**, y el panel —correcto—
tapaba el resto. Además **es invisible en M5** (ahí trailing ≈ pd range: dibujaba 1.14824/1.13246 =
pct 0.906 ≈ el 91% del panel) ⇒ **hay que probar en D1**.

### 2.2 El fix

`:3516` pasa a dibujar `chartState.pdHigh`/`pdLow`. **Visual-only, fuera del LIBRARY CORE** (termina en
L1850) ⇒ **no rompe el SHA `9559a0d7fe58b213`**, sin re-baseline ni ADR. `pine_check` 0/0,
`check-core-sync` OK ×3 + EXTREMES CORE OK.

**Ancla:** `chart.left_visible_bar_time` (neutra). `SMC_PdRange` no guarda el tiempo del extremo y el
UDT vive **en el CORE** (`:1176`) ⇒ añadírselo rompería el SHA. Dibujar desde el borde visible no
afirma una barra de origen que no tenemos. **DEUDA anotada:** ancla real al 2.º extremo si algún día
se re-baselinea.

**Verificación en vivo, con predicción escrita ANTES:**

| | Predicho | Medido | |
|---|---|---|---|
| Premium | 1.51441 | **1.51441** | ✅ |
| EQ | 1.23401 | **1.23400** | ≈ (redondeo mintick de 1.234005) |
| Discount | 0.95360 | **0.95360** | ✅ |
| Panel D1 | Discount 34% sin moverse | **Discount 34%** | ✅ |

## 3. Bug ABIERTO (no tocado): `chartState.pdMid` nunca se asigna

`chartState.pdMid` se **lee** en `:2741`/`:2742` (`f_wickNearLevel`, Rejection §2.7) pero **nunca se
asigna**: el bloque chart-TF (`:2193-2198`) solo pone `pdHigh`/`pdLow`. Queda en su default `na`
(`:296`) ⇒ **el nivel EQ nunca participa en la confluencia de mecha de rechazo. Fallo silencioso.**

`f_computeTFState` (`:1748`) y `f_m5Light` (`:2873`) sí lo asignan; y `:4464` ya se defiende del `na`
con un fallback — `:2741` no.

**NO lo introdujo el ADR-021:** `git log -S "chartState.pdMid"` devuelve **un solo commit**, `5bc4828`
(T20 Rejection), el que **añadió las lecturas** ⇒ la asignación **nunca existió**. Muerto desde
Sprint 1.5. Concepto distinto ⇒ commit distinto (regla dura #7).

## 4. Estado al cierre de esta medición

- `pine/SMC-Visual.pine` tocado **solo** en el bloque de dibujo P/D. CORE **intacto**.
- `pine_check` 0/0 · `check-core-sync` OK ×3 · SHA `9559a0d7fe58b213` (1776 líneas) · EXTREMES CORE
  `5f851d87e5fda720`.
- **F1-GATE sigue BLOQUEADA**: la decisión de `pdWindow` (§1.4) está abierta y el bug de `pdMid` (§3)
  también.

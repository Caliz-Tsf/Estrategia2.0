# S138 · EXPERIMENTO 3 — `base_V` por regresión LOCAL del Visual

> Experimento pendiente de `RESPUESTA-FABLE-S135.md` §3, punto 2. S137 ejecutó los
> experimentos 1 y 2; este cierra el último hueco del presupuesto de tokens.

## Qué hueco cierra

Hoy `base_V = 100217` se deriva de **una resta** (`100262 − 45`, S137/exp2), donde el
`45` se midió con un lastre de 300 unidades **cuyo coste unitario no se conoce en el
Visual**. Todas las conversiones lastre→tokens hechas hasta ahora heredan la pendiente
de **Context** (`29.42 tok/unidad`), calibrada entre 3000 y 3800 unidades — **10× fuera
de rango y cruzando de script**. Fable la marcó explícitamente como no firme (§3).

Un segundo punto **local del propio Visual** da pendiente e intercepto propios, sin
transferir nada de Context.

## Aritmética

Con `T300 = 107986` (medido S135, revalidado por S137: el Visual no cambió desde `42207ea`)
y `T600` = lo que mida este experimento:

```
unit_V  = (T600 − T300) / 300
base_V  = T300 − 300 · unit_V   =   2·T300 − T600
```

Nótese que `base_V = 2·T300 − T600` no depende de conocer `unit_V`: es una recta por dos
puntos. Es la primera vez que `base_V` se obtiene **sin** heredar nada de Context.

## PREDICCIONES — escritas ANTES de aplicar

Las dos ramas están separadas por ~1050 tokens ⇒ el experimento discrimina limpio.

**RAMA 1 — `base_V ≈ 100217` (lo que afirma S137/exp2).**
Implica `unit_V = (107986 − 100217)/300 = 25.90` ⇒ **`T600 ≈ 115755`**.
Banda aceptada **115700–115900** (el margen superior cubre el término fijo del 3.er chunk
de troceo: `lastre(600)` crea 3 funciones `zz_lastre*` y `lastre(300)` solo 2).
⇒ La pendiente de Context **NO transfiere** al Visual (25.90 ≠ 29.42), la hipótesis (a)
de S135 queda confirmada, `headroom = 39 tokens` se sostiene, y el hilo de tokens se cierra.

**RAMA 2 — `base_V ≈ 99160` (la retro-cuenta con la pendiente de Context).**
Implica `unit_V ≈ 29.42` ⇒ **`T600 ≈ 116800`**.
⇒ El `45` del exp2 estaría mal escalado, `headroom = 39` cae, y reaparecen los ~1100
tokens sin explicar que S135 dejó abiertos. Habría que rehacer el exp2.

**RAMA 3 — cualquier otro valor.** Mecanismo no identificado; no decidir nada y medir un
tercer punto (900) antes de tocar conclusiones.

## Anti-humo (regla del lastre desplazado, `docs/reglas-dev.md` §1.6b)

`T600` esperado (~115.8k) es **distinto de todos los números conocidos** de la campaña
— 107986, 108031, 108071, 107929, 100262, 100300 — con un margen de miles de tokens.
Cualquier lectura que caiga en uno de esos valores es consola rancia, no un resultado.
Verificar además el **timestamp** en `pine_get_console` y el conteo de líneas del build.

## Resultado del punto 600 — **RAMA 2**

`T600 = 116818` (00:58:53). Timestamp nuevo y valor a miles de tokens de todos los
conocidos ⇒ anti-humo pasa. La predicción de rama 2 era 116800: acierto al 0,015%.

```
unit_V = (116818 − 107986) / 300 = 29.44 tok/unidad
base_V = 2·107986 − 116818     = 99154
```

**`unit_V` = 29.44 ≈ 29.42, la pendiente de Context.** Es decir: la pendiente **SÍ
transfiere** entre scripts — exactamente lo contrario de lo que asumía la rama 1. Y
`base_V ≈ 99154` reproduce la retro-cuenta de S135 (99160) con 6 tokens de diferencia.

⇒ **La retro-cuenta de S135 era correcta y la derivación del exp2 (S137) es la que falla.**
`headroom del Visual ≈ 100256 − 99154 ≈ 1100 tokens`, **no 39**.

## La contradicción que esto abre (y que hay que resolver, no tapar)

Ambas cosas no pueden ser verdad a la vez:

| Vía | `coste(fix-slim de pdMid)` |
|---|---|
| Resta con lastre (S137/exp2): `108031 − 107986` | **45** |
| Aplicaciones directas de S135: `100262 − base_V(99154)` | **~1108** |

El mismo fix, dos costes que difieren ×25. Como `base_V ≈ 99160` sale de **dos vías
independientes** (regresión local del Visual y pendiente de Context), la pieza sospechosa
son los números directos de S135 (100300 / 100262).

**Hipótesis principal:** son lecturas contaminadas — el mismo modo de fallo que el build
fantasma "100952" de ADR-022. S135 midió esos dos números en el mismo bloque en que
trabajaba con el probe v15 de `pdMid`; un buffer con código de probe vivo explicaría el
exceso (~1060 tokens, del mismo orden que los ~700 del fantasma de ADR-022). Nótese que
los dos números son internamente coherentes entre sí (difieren en 38 = el guard), lo cual
NO los exonera: una contaminación constante entre las dos lecturas produce justo eso.

**Consecuencia si se confirma:** el fix de `pdMid` (45 tokens) **cabe de sobra** en ~1100
de headroom, y la deuda abierta desde S135 se puede cerrar.

## Punto de control 400 — separar el término de troceo

`lastre(300)` y `lastre(600)` no tienen el mismo número de funciones de troceo (2 vs 3),
así que la recta por dos puntos mezcla el coste por unidad `u` con un término fijo por
chunk `F`:

```
T300 = base + 2F + 300u
T600 = base + 3F + 600u    ⇒   T600 − T300 = F + 300u   (u y F NO separables)
```

`lastre(400)` tiene **2 chunks, igual que `lastre(300)`** ⇒ `T400 − T300 = 100u` aísla `u`
sin término fijo. Predicciones escritas ANTES de leer:

- **`T400 ≈ 110930`** (`u = 29.44`, `F = 0`) ⇒ el troceo no cuesta nada fijo y `base_V = 99154`.
- **`T400 ≈ 110576`** (`u = 25.90`, `F = 1062`) ⇒ hay término fijo por chunk y `base_V` es
  aún MENOR (98092) ⇒ el headroom sería todavía mayor, la conclusión no se salva por aquí.
- Separación entre ramas: 354 tokens. Cualquier `T400` fuera de ambas bandas ⇒ modelo
  incompleto, medir un cuarto punto antes de concluir.

Obsérvese que **las dos ramas dan `base_V` muy por debajo de 100256**: el término de troceo
no puede rescatar el "headroom = 39". Este punto refina el modelo, no cambia el veredicto.

### Lectura: `T400 = 110869` (01:01:34, fresco)

Cae a 61 tokens de la rama `u=29.44` y a 293 de la rama `u=25.90` ⇒ **rama de pendiente
alta**, pero ninguna de las dos exacta: hay término de troceo, pequeño.

Resolviendo el sistema con los 3 puntos:

```
u     = (110869 − 107986) / 100        = 28.83 tok/unidad
F     = (116818 − 107986) − 300·u      = 183 tok/chunk
base_V = 107986 − 2F − 300u            = 98971
headroom = 100256 − 98971              = 1285 tokens
```

⚠️ **Caveat de método:** 3 ecuaciones y 3 incógnitas ⇒ el ajuste es exacto **por
construcción** y no hay residuo que valide el modelo. Lo que sí es robusto es `base_V`,
porque **tres vías independientes lo sitúan en el mismo sitio**:

| Vía | `base_V` |
|---|---|
| Recta 300/600 sin término de troceo | 99154 |
| Modelo de 3 puntos (300/400/600) | 98971 |
| Pendiente de Context (29.42) sobre `T600` fresco | 99166 |
| Retro-cuenta de S135 | 99160 |

Las cuatro caen en **98971–99166**. Ninguna se acerca a 100217.

## VEREDICTO PROVISIONAL (escrito antes del experimento 4 — resultó FALSO, se conserva)

> Se conserva tachado como registro honesto: fue la conclusión que saqué de los 3 puntos
> de lastre, y el experimento 4 la refutó en el acto.

1. ~~`base_V ≈ 99.000`, `headroom ≈ 1.100–1.300 tokens`~~ — **FALSO**.
2. ~~`headroom = 39` (S137) queda refutado~~ — **al revés: se confirma la parte que importa**.
3. La pendiente del lastre transfiere entre scripts (28.83 vs 29.42) — **esto sí se sostiene**.
4. `coste(fix-slim) = 45` con lastre — **se sostiene**.

## EXPERIMENTO 4 — el resultado que manda

`Visual(HEAD) + fix-slim`, **sin lastre**, aplicado fresco:

```
1:05:08   Compiled code contains too many tokens: 100262. The limit is 100256
```

**100262 — el número EXACTO que midió S135.** Reproducido en sesión distinta, build
distinto, timestamp fresco. ⇒ **el 100262 NO era una lectura contaminada.** La hipótesis
del fantasma queda descartada para este número, y con ella todo mi veredicto provisional.

**Hecho operativo, independiente de cualquier modelo: el fix de `pdMid` NO CABE, por 6
tokens.** Medido directo, dos veces, en dos sesiones.

## VEREDICTO REAL — el hallazgo es de MÉTODO, no de presupuesto

La contradicción no se resuelve a favor de ninguna de las dos ramas: se resuelve
**contra el instrumento**.

```
intercepto de la recta de lastre        = 98971
predicción para Visual+fix-slim         = 98971 + 45 = 99016
medido                                  = 100262
ERROR DE LA EXTRAPOLACIÓN               = 1246 tokens
```

⇒ **Las DIFERENCIAS con lastre igual son válidas; el INTERCEPTO no.** La recta ajusta
perfectamente sus tres puntos (300/400/600) y aun así extrapola a `N=0` con 1.246 tokens
de error. Sea cual sea el mecanismo (coste por unidad no constante a escala pequeña, coste
del propio aparato de lastre absorbido en el intercepto), el resultado empírico es firme:

> **REGLA NUEVA — el lastre mide restas, no absolutos.** `coste(bloque)` se obtiene
> restando dos builds con el **mismo** lastre. Extrapolar la recta a lastre cero para
> obtener el tamaño absoluto de un script **está medido como inválido** (1.246 tokens de
> error en el único caso donde hay un valor directo con el que contrastar).

## Lo que esta regla arrastra — hay que revisarlo antes de usarlo

- **La retro-cuenta de 99.160 de S135 y mi 98.971 son el MISMO error**, no una
  confirmación mutua: ambas son extrapolaciones al origen de la misma recta. Que dos vías
  malas coincidan no las valida — coinciden porque comparten el defecto.
- ⚠️ **`Context ≈ 15.100 tokens, ~85.000 libres` (S135) es una extrapolación del mismo
  tipo** — intercepto de una recta calibrada entre 3.000 y 3.800 unidades, llevada a cero.
  Por lo medido aquí, ese número **no es de fiar**, y es justamente el que sostiene el plan
  del **reparto del dibujo**. Antes de construir sobre él hay que medir el hueco de Context
  por una vía que no extrapole (p. ej. añadirle dibujo real por bloques hasta ver el
  CE10117: da una cota inferior directa, sin modelo).
- `headroom del Visual = 39` (S137) queda **sin verificar de forma independiente**, pero su
  consecuencia accionable — *"para meter el fix hay que liberar ≥6 tokens de código que se
  EJECUTA"* — está **confirmada por medición directa** y no depende del valor de `base_V`.

## Estado de la deuda de `pdMid`

Sigue abierta y sigue sin caber, por 6 tokens. Vencimiento sin cambios: antes de capturar
los golden tests de Fase 4 (`RESPUESTA-FABLE-S135.md` §5).

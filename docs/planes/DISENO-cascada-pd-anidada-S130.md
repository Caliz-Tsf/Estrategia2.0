# DISEÑO — Cascada premium/discount anidada desde D1 · S130

> Sucede a [DISENO-opcion-C-rango-pegajoso-S128.md](DISENO-opcion-C-rango-pegajoso-S128.md), cuya §3
> resultó ambigua y cuya medida (S129) degeneró la Opción C al máx/mín de la ventana.
> **Estado: PROPUESTA — nada implementado. `pine/` intacto, CORE SHA `752b4083a7db419d`, core-sync OK ×3.**
> Fuentes: [reglas-smc-ict.md §2.3](../reglas-smc-ict.md) · [§5.16](../reglas-smc-ict.md) ·
> [decisiones-pd-rango.md](../decisiones-pd-rango.md) · [[Sesion-128]] · [[Sesion-129]].

## 1. El problema que resuelve (planteado por el usuario en S130)

El rango D1 es **contexto, no señal**. Si el precio tardó 18 meses en llegar al discount de D1, el
veredicto "discount D1" dura meses o años y muchas veces **nunca** vuelve al otro extremo. Un veredicto
que no rota no dice cuándo entrar. Por eso la **herencia pura** (H1/M5 usando el rango D1 con rejilla más
fina, §5.16) **no sirve**: congela el veredicto en H1 y M5.

Requisito literal del usuario:

> "se debe mover con el precio pero quedarse estancado en un tramo entre el premium de D1, H1 y M5"

Es decir: cada TF menor tiene **su propio premium/discount**, quieto dentro de su tramo, que **salta**
al tramo contiguo cuando el precio se lo come. Y al saltar hacia arriba, el precio entra por abajo del
tramo nuevo → **vuelve a discount en ese TF** mientras el TF superior sigue en premium. Eso es lo que
hace que rote y sea operable.

## 2. La regla (cascada de mitades)

```
L0 (macro D1) = [lo0, hi0] = min/max de la ventana declarada     (= Opción C literal, ya medida en S129)
Lk+1: mid = (lok + hik)/2
      close >= mid  ->  [mid, hik]      (mitad premium  del nivel k)
      close <  mid  ->  [lok, mid]      (mitad discount del nivel k)
```

Cada nivel aplica `f_premiumDiscount` **sobre el nivel anterior**. Cero parámetros nuevos salvo el
número de niveles. El anidamiento `L0 ⊇ L1 ⊇ ... ⊇ Ln` es **garantizado por construcción**, no una
propiedad a esperar.

**Si el precio supera el máx/mín de D1:** `f_updateTrailing` ya expande (`top := max(high)`), y S129
midió que `close > top` es imposible → `pct` nunca sale de [0,1]. Un máximo nuevo en D1 **es** el evento
(BOS de D1): el precio queda en pct≈1 y el techo del ciclo se reescribe. Cae solo del diseño.

## 3. La consecuencia que hay que dejar por escrito ANTES de medir

**La cascada de mitades ES la expansión BINARIA de `pct`.** El veredicto del nivel *k* es el *k*-ésimo
bit de `pct` en base 2. Consecuencias, todas verificables:

1. **No hace falta recursión** para saber el veredicto de un nivel: sale de `pct` directamente.
2. Los veredictos **alternan sin tendencia** entre niveles (son los bits de un número).
3. **Los niveles NO tienen contenido estructural.** Un "premium de H1" así es un **corte aritmético**
   del rango D1 — no guarda relación con ningún swing, pivote ni BOS de H1. Esto **agrava** el coste que
   S129 ya señaló para la Opción C literal (el rango pierde el *strong high/low* de §2.3): allí solo el
   macro perdía significado estructural; aquí lo pierden **todos los niveles**.
4. **Flapping / histéresis:** si el precio oscila alrededor de un `mid`, ese nivel salta entre
   discount-extremo y premium-extremo **cada tick**. El salto es la *feature* pedida, pero sin histéresis
   es también el modo de fallo. Los niveles bajos deberían flapear más que los altos → se mide.

Nada de esto invalida el diseño: es lo que el usuario pidió y **rota**, que es lo que la herencia pura no
hacía. Pero el ADR tendrá que decidir explícitamente si se acepta un P/D **aritmético** por TF.

## 4. Predicciones (escritas ANTES de medir — van 9 vivas de 21)

Con el rango D1 medido en S129 `[0.90275, 1.60389]` (7011.4 pips) y close ≈ 1.14399 (pct 34.3%):

| ID | Predicción | Falsa si |
|----|-----------|----------|
| **P-G1** | L1 amplitud ≈ **3505.7 pips**, rango `[0.90275, 1.25332]`. La lectura H1 del usuario fue `[1.02175, 1.39970]` = **3780 pips**: la **amplitud coincide dentro del 10%** pero los **niveles NO** (difieren >1000 pips). | amplitud difiere >10%, o los niveles coinciden <100 pips |
| **P-G2** | Anidamiento `Lk+1 ⊂ Lk` en **100%** de las barras: `nNestViol = 0`. | `nNestViol > 0` |
| **P-G3** | `pct ∈ [0,1]` en **todos** los niveles: `nOutOfRange = 0`. | algún `nOutOfRange > 0` |
| **P-G4** | Flapping **monótono creciente** hacia abajo: `nFlip(L1) < nFlip(L3) < nFlip(L5)`. | el orden se rompe |
| **P-G5** | Amplitudes = mitades exactas: L2≈1752.9, L3≈876.4, L4≈438.2, L5≈219.1, L6≈109.6 pips. El TF M5 (rango local 100-300 pips) cae en **L5 o L6**. | alguna amplitud difiere >1% de la mitad |

**P-G1 es la que decide.** Si la amplitud de L1 reproduce la lectura H1 del usuario, la regla de corte es
partir en **mitades** y el modelo es correcto. Si no, la cascada de mitades no es lo que su ojo leía.

## 4bis. RESULTADO MEDIDO (S130, probe v5 marker 1301, D1 OANDA:EURUSD, n=6283)

Build fresco verificado (`P_marker`=1301 en ambas instancias), `P_nBars`=6283 (cuadra con S129),
`P_close`=1.14424 contra precio real (crosshair en la barra viva), `P_tSeeded`=2.

| ID | Veredicto | Medido |
|----|-----------|--------|
| **P-G1** | ✅ **VIVA (la que decide)** | L1 = `[0.90275, 1.25332]`, **3505.675 pips**. Usuario H1 = 3780 → **7.3% de error**. Niveles desplazados 1190 pips (abajo) y 1464 (arriba) → NO coinciden, como se predijo. |
| **P-G2** | ✅ pero **TAUTOLÓGICA** | `nNestViol`=0. Sale por construcción; confirma el código, no descubre mercado. |
| **P-G3** | ✅ **con matiz no predicho** | `nOutRange`=0 sobre confirmadas. **PERO `pctL5`=1.02 en la barra VIVA**: el invariante `pct∈[0,1]` **no se conserva intrabarra** en niveles bajos. La Opción A no tiene este comportamiento (`f_updateTrailing` expande incl. la vela viva). El ADR debe aceptarlo explícitamente. |
| **P-G4** | ✅ **VIVA** | `nFlip1`=36 · `nFlip3`=390 · `nFlip5`=1536. Monótono creciente. L5 salta cada ~4 velas. |
| **P-G5** | ✅ pero **TAUTOLÓGICA** (amplitudes) | L2 1752.84 · L3 876.42 · L4 438.21 · L5 219.10 · L6 109.55. M5 (100-300 pips) cae en **L5**. `errBin` **NO medido** (es local, `na` en la barra viva) — pero la identidad binaria quedó verificada por otra vía: `pctL1` = 0.68885 = **exactamente 2 × `pctL0`** (0.34443). |

**El hallazgo que importa — la cascada SÍ rota:** `pctL0`=0.344 → **DISCOUNT de D1**; `pctL1`=0.689 →
**PREMIUM del nivel 1**, simultáneamente. Es la alternancia que el usuario describió. Contraste con la
Opción A vigente: `pctA`=0.155, discount profundo y congelado.

**El caso del usuario, ocurriendo en vivo:** L5 = `[1.12185, 1.14377]` con `pct`=1.02 → el precio
**acaba de comerse el techo de su tramo** y saltará al de arriba al cerrar la vela, entrando por abajo
del tramo nuevo (→ discount de L5 con L1 aún en premium).

**Reserva honesta sobre P-G1.** Es **una** coincidencia de amplitud, con 7% de error y niveles
desplazados >1200 pips. Que el tamaño coincida y la ubicación no, puede significar que el ojo del
usuario leía "la mitad de D1" — o puede ser casualidad: una cascada de mitades ofrece pocos tamaños
posibles y uno tenía que caer cerca. **Con n=1 no se distinguen esas dos hipótesis.** Discriminarla
exige repetir el test en otros símbolos/fechas (ver §7).

## 5. Anti-humo

Aprendido en S128/S129: `P_nBars` denominador explícito; `P_tSeeded` delata el arranque; contadores
**por lado y por nivel** separados; `P_marker` por build (único distintivo fresco/rancio);
`P_close` de control (`data_get_study_values` sigue el **crosshair**). Nada se lee en `islast` (gotcha
S128: `legExtHi/Lo` solo viven en `islast` → contadores históricos midieron humo).

## 6. Coste (si se implementara — NO en esta sesión)

Toca el **LIBRARY CORE** (`f_premiumDiscount` consumida por `f_computeTFState`) → rompe el SHA,
re-baseline ×3, contrato MQL5 → **ADR obligatorio**. Rompe la paridad LuxAlgo (la Opción A *es* su
`trailingExtremes`). Requiere rederivar los casos de prueba de §2.3 (validados al 5.º decimal).

## 7. DISCRIMINACIÓN DE P-G1 — MEDIDA (probe v6, marker 1302): **el modelo de mitades NO se sostiene**

**El agujero del test obvio.** La referencia de P-G1 es el **ojo del usuario**, y solo existe para
EURUSD. No se puede repetir contra el H1 **nativo**: S129 ya midió que el nativo no reproduce la lectura
del usuario (1905 vs 3780 pips). Lo que sí es falsable es la afirmación estructural que sostiene el
mapeo "nivel 1 = H1": que el rango de H1 sea **sistemáticamente ~la mitad** del de D1.

Medido, 5 símbolos, misma ventana disponible por TF (D1 n≈5623-6284, H1 n≈9036-9537), marker 1302:

| Símbolo | amp D1 | amp H1 | **ratio H1/D1** |
|---------|--------|--------|-----------------|
| OANDA:EURUSD | 0.70114 | 0.19052 | **0.272** |
| OANDA:GBPUSD | 1.08024 | 0.17703 | **0.164** |
| OANDA:USDJPY | 87.285 | 22.951 | **0.263** |
| OANDA:AUDUSD | 0.58015 | 0.13637 | **0.235** |
| OANDA:NAS100USD | 29757.1 | 14438.1 | **0.485** |

| ID | Veredicto | Medido |
|----|-----------|--------|
| **P-H1** | ✅ VIVA (pero fácil) | EURUSD ratio 0.2717 vs 0.27 predicho. Era aritmética sobre un número ya medido en S129 (1905.2 = idéntico por otra vía → valida el método). |
| **P-H2** | ❌ **FALSA — LA QUE DECIDÍA** | Recorrido de ratios = 0.485 − 0.164 = **0.321** > 0.20. **No se agrupan.** |
| **P-H3** | ❌ FALSA | NAS100USD = 0.485, dentro de 0.5 ± 0.05. |
| **P-H4** | ❌ FALSA, **y con el signo invertido** | Predicho: NAS100 el ratio más BAJO por su tendencia secular. Salió el **más ALTO**. El razonamiento estaba al revés: en unidades absolutas, un índice exponencial mueve en ~1.5 años (ventana H1) casi la mitad de lo que movió en 24 (ventana D1). |

### Conclusiones

1. **El mapeo nivel→TF NO tiene base estructural.** No existe constante "H1 = tal fracción de D1": va de
   0.164 a 0.485 según el símbolo. **P-G1 queda refutada: el 7.3% de EURUSD fue casualidad.**
2. **Ni en EURUSD el nivel 1 es H1.** Los 4 pares de forex agrupan cerca de **0.23** → eso apunta al
   **nivel 2** (25%), no al nivel 1 (50%). *(Que los 4 forex agrupen y NAS100 sea outlier es observación
   POST-HOC, no predicción — y viene de quien acaba de predecir el signo al revés en P-H4. No usar como
   explicación sin medirla aparte.)*
3. **HALLAZGO CONCEPTUAL (lo que más importa):** la lectura del usuario en H1 (3780 pips, 54% de D1) y el
   H1 nativo (1905, 27%) **son dos objetos distintos**. No es un error del ojo: el usuario lee un rango
   que incluye el extremo de 2014, que **el feed H1 no contiene** (necesitaría ~75.000 barras, TV da
   9.535). Lo que llama "rango de H1" es **el rango macro mirado en H1** — es más D1 que H1. Por eso
   ninguna medición nativa de H1 podía coincidir nunca con él, y por eso **"¿qué nivel es H1?" no tiene
   respuesta empírica**: depende de qué se DEFINA como rango de H1. Es una **definición, no un hecho**.

### Qué sobrevive y qué cae

- **SOBREVIVE:** la cascada **rota y anida** (medido, §4bis) — resuelve el problema real que planteó el
  usuario (el macro D1 no rota → no es operable).
- **CAE:** derivar del mercado **qué nivel corresponde a cada TF**. Hay que **decidirlo** (input,
  amplitud objetivo declarada, etc.), no medirlo.

## 8. Lo que falta antes de un ADR (no medido)

1. **Decidir el mapeo nivel→TF** — ya no es medible (ver §7.3). Opciones: nº de niveles como input;
   amplitud objetivo declarada por TF; o abandonar el mapeo a TFs y exponer la cascada como tal.
2. **Decidir el flapping.** `nFlip5`=1536 (salta cada ~4 velas) es el modo de fallo. ¿Se acepta o se
   añade histéresis? La histéresis cuesta parámetros nuevos — justo lo que la Opción C prometía evitar.
3. **La doctrina (§3.3).** Un P/D aritmético por TF no tiene contenido estructural. Decisión del
   usuario, no técnica.
4. La otra mitad de P-C3 de S129 (censo S127 en banda 1-3) y P-C4 siguen sin medir.

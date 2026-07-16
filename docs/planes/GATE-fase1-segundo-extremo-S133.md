# GATE FASE 1 — El 2.º extremo estructural: **PASA**

> Resultado del probe en sombra que exige la Fase 1 del plan `1-la-ventana-de-giggly-blum.md`.
> **`pine/` NO se tocó.** CORE SHA `752b4083a7db419d` intacto. `pine_check` 0/0. **S021 sigue congelada.**
> Arnés: `scripts/gen_probe_segundo_extremo.py` (marker 1340). Regla medida: `reglas-smc-ict.md` §2.3.1/§2.3.2.

---

## 1. Veredicto

**Ninguno de los tres criterios de abandono pre-comprometidos se dispara. El gate PASA: 5 predicciones
verdes de 6.**

Y lo hace por el motivo correcto: **la regla es doctrina, no ajuste**. Ninguno de los umbrales se calibró
contra las marcas del usuario — sus niveles solo se usaron como *sanity check* a posteriori.

---

## 2. Los números

| | **EURUSD D1** (bajista) | **NAS100USD D1** (alcista) |
|---|---|---|
| n barras | 6284 | 5752 |
| `bias` (swing / major) | **−1 / −1** | **+1 / +1** |
| `histLow` | 0.90275 | 1016.1 |
| **`pdLow`** | **0.95360** | 1021.1 |
| `histHigh` | 1.60389 | 22248.0 |
| **`pdHigh`** | **1.51441** | 16771.6 |
| `nStrongLo` / `nStrongHi` | 23 / 18 | 22 / 11 |
| `nRelatchMin2` | 2 | **2** ← *strong (alcista)* |
| `nRelatchMax2` | **3** ← *strong (bajista)* | 10 |
| `nOutRange` | **0** | **0** |
| fallback: case2 / case3 (abajo) | 27 / 0 | 155 / 0 |
| fallback: case2 / case3 (arriba) | 434 / 312 | 1094 / **2913** |
| `nDisagree` vs Opción A | 363/6284 = **5.8%** | 238/5752 = **4.1%** |

## 3. Predicciones (escritas en el arnés ANTES de medir)

| # | Predicción | Resultado |
|---|---|---|
| P1 | `histLow` EURUSD = 0.90275 ±10 pips | ✅ **VERDE — exacto** *(declarada fácil de antemano; es cross-check del arnés)* |
| P2 | `pdLow` EURUSD = 0.95360 ±20 pips | ✅ **VERDE — EXACTO** |
| P3 | **LA QUE DECIDE:** `nRelatchMax2` ≤ 10 (Fable dio **41**) | ✅ **VERDE — 3** |
| P4 | `nOutRange` = 0, incluida la franja histórica | ✅ **VERDE — 0 en ambos símbolos** |
| P5 | **ADR-001:** NAS100 congela el lado que dicta el bias, sin tocar código | ✅ **VERDE** |
| P6 | `nDisagree` ≥ 15% de las barras | ❌ **FALSA — 5.8% y 4.1%** |

**Marcador S133: 9 vivas de 17.**

---

## 4. Lo que confirma cada verde

**P3 — el techo NO camina.** 3 re-fijaciones en 6284 barras, contra **41** del esqueleto de Fable en la
misma escala. Esa era la causa raíz que arrastramos desde S057 (*"el rango camina hacia el precio"*).
Tomar **el 2.º más alto de todos** en vez de **el último** la elimina: no hay nada que lo re-fije salvo
un strong high nuevo que supere al 2.º.

**P2 — la doctrina reproduce su nivel sin que nadie lo ajuste.** `pdLow` = **0.95360 exacto** = el nivel
que el usuario lee como suelo de D1. No se calibró contra él: sale de "el 2.º strong low más bajo".
Bonus no predicho: `histHigh` = 1.60389 queda a **21 pips** de su rojo anotado (1.60180) ⇒ **su rojo de
arriba era el histórico**, tal y como su modelo predice.

**P4 — el invariante se sostiene, y NO trivialmente.** `nOutRange`=0 en los dos símbolos, con el fallback
**ejercido en 773 barras (EURUSD) y 4162 (NAS100)**. Si case2+case3 hubieran salido 0, el verde no
probaría nada; salen altos ⇒ las tres ramas de la cascada §2.3.2 se recorren de verdad.

**P5 — ADR-001 gratis, y la asimetría emerge sola.** Mismo código, **cero ramas por símbolo**:

- EURUSD (bias −1) → strong = **high** → `nRelatchMax2` = 3 *(congelado)*
- NAS100 (bias +1) → strong = **low** → `nRelatchMin2` = 2 *(congelado)*, weak = high → 10

Y el "caminar" del lado weak **no lo hace el latch: lo hace el fallback**. En NAS100 alcista el precio
supera el histórico constantemente ⇒ `case3Hi` = **2913** ⇒ el techo expande. Es exactamente el régimen
que el usuario describió (*"si sale del premium... se expande hasta el nuevo alto más alto"*), operando
sin código específico.

---

## 5. P6 falsa — por qué, y por qué NO es un problema

Predije ≥15% de cambio de veredicto; salió **5.8% / 4.1%**. Falla su umbral pero **no dispara el abandono**
(ese era <5%, y solo EURUSD lo supera; NAS100 queda por debajo).

**La causa está medida, no supuesta:** el rango nuevo `[0.95360, 1.51441]` **comparte suelo** con la Opción
A vigente `[0.95360, 1.60389]` — solo cambia el techo, y el precio está abajo ⇒ los dos veredictos
coinciden casi siempre. En NAS100 pasa algo análogo: el precio está sobre el histórico (`case3Hi`=2913)
⇒ el techo nuevo **es** el trailing ⇒ **converge con A por construcción**.

**Lectura honesta:** la Opción A con `pdLen`=1000 ya acertaba el suelo **por accidente** (el pool tiene
edad 984 < 1000, ver `decisiones-pd-rango.md` nota S133(b)). El diseño nuevo llega al mismo suelo **por
doctrina**, y además: (a) elimina el accidente, (b) elimina el input, (c) **elimina el caminar del techo**
(P3), que es lo que el usuario reporta desde S057 y que el % de desacuerdo **no mide**.

⇒ **P6 medía la métrica equivocada.** El desacuerdo con A era el listón correcto para la Opción B (S128:
3.2%, misma mecánica que A ⇒ no compraba nada). Aquí la mecánica **sí** difiere, y lo que compra es
estabilidad del strong (P3) + una regla doctrinal sin parámetro de escala — no un veredicto distinto
cada día. **Se registra como predicción FALSA** (no se re-escribe a posteriori), con esta lectura al lado.

---

## 6. Anti-humo

- `P_marker`=1340 **fresco verificado en cada lectura** (en la corrida previa un modal bloqueó el apply
  y devolvió marker rancio 1333; se detectó y se corrigió).
- `nStrongLo`=23 / `nStrongHi`=18 (EURUSD) y 22 / 11 (NAS100) ⇒ **ningún lado muerto**: los dos acumulan.
- `nBars` como denominador explícito en todos los ratios.
- `lastEvT` = 2026-06-22 = el evento del panel D1 (cross-check que exigía Fable).
- case1/case2/case3 desglosados ⇒ P4 verificable como no-trivial.
- Instancia vieja removida con `chart_manage_indicator` antes de leer (TV solo deja 2).

---

## 7. Siguiente

**Fase 2 del plan, y su primer paso es un gate humano: descongelar S021.** La medición no lo decide.

Lo que la Fase 1 aporta a esa decisión: la regla es doctrinal (§2.3.1/§2.3.2), reproduce el nivel del
usuario sin ajuste (P2), elimina el defecto de S057 (P3), conserva su invariante (P4), es multi-símbolo
sin ramas (P5), y **retira** código (`f_detectSwings(pdLen)` + 4 resets + `i_pdSwingLen` ⇒ −1 input, 0
nuevos). Coste: CORE roto ⇒ SHA re-baseline ×3 ⇒ **ADR-021** ⇒ golden tests MQL5 del rango rederivados
(`f_premiumDiscount` intacta ⇒ los suyos sobreviven).

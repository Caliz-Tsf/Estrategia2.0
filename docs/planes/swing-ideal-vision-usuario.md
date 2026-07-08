# Visión del "swing ideal" — poblar la pierna por banda (input del enjambre)

> Aclaración del usuario (S103, 2026-07-07) con ejemplo visual **XAUJPY D1** (LuxAlgo SMC + SMC Engine).
> No es una nueva regla: **cuantifica el objetivo visual** de `depthBand`/band-pick (§7) + "cola del swing" (#8).
> Alimenta S104 (transporte de geometría con ventana) y el debate del enjambre (Fase 4).

## Qué quiere el usuario
Para **cada swing** (dealing range desde su **origen** hasta el extremo vigente), ver **poblada a lo largo de la
pierna, por banda de profundidad**, la lista de **conceptos importantes generados dentro de ese swing**, de modo que:
- parado en el momento actual ya se pueda **proyectar** hacia dónde puede ir (arriba/abajo), y
- el **enjambre** pueda debatir **dónde entrar y en qué parte de la pierna**.

**Regla estética:** "limpio pero NO vacío". Pocos por banda, pero los que importan.
**Cada swing es distinto** → bandas **relativas al rango vigente** (adaptativas), nunca niveles fijos.

## Ejemplo de referencia (foto XAUJPY D1 del usuario)
En la pierna mostrada se ven, a lo largo del rango:
- **origen (abajo):** un **OB pegado al EQL** (zona discount).
- **medio:** **2 OB** más arriba (con sus OTE/fibs 0/0.5/1 internos).
- **premium (arriba):** **2 OB rojos** (bajistas) + **Strong High**.
- marcas de estructura del swing: **BOS / CHoCH**, **EQH/EQL**, **Weak Low**.
Con eso el trader/enjambre ya tiene los puntos de decisión de toda la pierna en un vistazo.

## Cómo mapea a nuestro diseño (ya existente)
- **`depthBand` + band-pick (§7):** parte el rango vigente en bandas y elige el/los mejor(es) por banda por
  `score_render_v2 = strength × wPos(posRole) × (1 + kConf·confDegree)`. = "lo que más importa por banda".
  Estaba muerto por **BUG#1** (`chartState.atr14 = na`); **revivido en S103** (commit `1164ed4`).
- **"Cola del swing poblada en ambas direcciones" (#8):** este requisito, literal.

## Refinamiento del usuario (S105, 2026-07-08) — foto EURUSD D1/H1
Elegida **Opción 1** (anclar a rango HTF heredado) con estas precisiones que la completan:
1. **Extremo de pierna = swing dominante.** En TFs menores se ancla al **rango HTF heredado**
   (H1 → Premium/Discount D1; M5 → rango H1/D1). En el **TF techo (D1)** no hay herencia →
   se ancla a la **estructura dominante propia** (el HH donde está p.ej. `BSL-3`, y el HH
   histórico más arriba). En la práctica: extremo = **el más lejano** entre {rango vigente,
   swing dominante propio `structMajor`, rango HTF heredado}.
2. **Ambas direcciones.** Arriba **y** abajo: las zonas **no mitigadas** deben verse para
   proyectar hacia los dos lados (no solo hacia el objetivo del bias).
3. **"Importante" = fuerza (strength) + clustering.** Si en una pierna hay p.ej. 6 inducement
   pero 3 están **juntas**, esas 3 colapsan a **la más importante del cluster** (1 representante).
   Aplica a **todos** los conceptos del Pine (FVG, OB, CHoCH, BOS, pool, IDM, …).
4. **Nativos + heredados por TF y por familia.** Cada TF muestra sus conceptos nativos MÁS los
   heredados de cada TF mayor, por familia, dentro del rango de la pierna, solo **no mitigados**.
5. **1–3 por concepto por banda** (top-N por celda con clustering), no solo 1.

### Plan de implementación (PASO 6 redefinido, S105+)
- **Paso 1 [S105]:** extremo de pierna en `f_depthBand` = max/min de {chart P/D, `structMajor`
  highLevel/lowLevel, rango HTF heredado d1State/h1State}. Hace elegibles los conceptos de arriba
  de la pierna (hoy banda 0). Mayor impacto visible.
- **Paso 2:** top-N (1–3) por celda concepto×lado×banda con **clustering** (colapsar instancias
  cercanas del mismo concepto → la de mayor strength). Requiere rediseño del store de celdas
  (hoy 40 escalares top-1) sin arrays en islast (RE10045).
- **Paso 3:** extender filtro **no-mitigado** a todos los conceptos (hoy solo OB/FVG/Breaker).
- **Paso 4:** reconciliar con budget — el ≤25 deja de ser guillotina por recencia; el cap real
  es "1–3 por banda por concepto". Budget crece; aceptado por el usuario.

## Estado final visual — referencias del usuario (S105, 3 indicadores de ejemplo)
El usuario mostró 3 indicadores que capturan CÓMO quiere que se vea (no las señales, el estilo):
1. **"Liquidity Pools Pro" (LP Pro):** SSL/BSL = líneas horizontales a la derecha, cada una con
   **fuerza/tamaño** (p.ej. "BSL [33] 128.9K") y estado **swept vs no-swept** (mitigada = swept).
   Panel lateral: Active Pools, **Strong SSL/BSL**, **Nearest Above/Below**, Stats (Mit/Sig).
   → Nuestra liquidez debe mostrarse así: pocas, las **fuertes** + la más cercana por lado, con
   magnitud y estado. **Sin** señales long/short.
2. **SMC + Fib (LuxAlgo):** **HH/LL solo en los pivotes importantes** (no todos), **BoS y CHoCH
   de estructura GRANDE y CHICA** etiquetados, cajas demand/supply (verde/roja), y un **fib de
   proyección** sobre el swing vigente (0.236/0.382/0.5/0.618/0.786/0.886/1.13/1.27/1.41/1.618).
3. **Vista limpia:** aun con varios dibujos es legible; cada concepto se distingue; permite
   **proyectar** hacia dónde va el precio y qué liquidez/POI tomará.

**Objetivo funcional (para el enjambre):** "ver la imagen" y poder decir → *"el precio cae, llega
a ~X zona (banda), luego va a tomar los SSL de arriba / el OB / FVG"*. Proyección arriba y abajo.

**Principios de render derivados:**
- Por familia y por banda: los **importantes** (fuerza/score), **no mitigados**, nativos + heredados.
- Estructura: HH/LL de pivotes mayores; BoS/CHoCH de escala grande y chica (ya existen ambas).
- Liquidez: pools con magnitud + estado swept; fuertes + nearest por lado.
- **Fib de proyección** sobre el swing dominante vigente (candidato nuevo, estilo img 2/3).
- Limpio pero no vacío; sin señales de entrada en el Visual (las entradas son del Strategy/enjambre).

## Regla del cluster (representante) — decidida S105
Dentro de un cluster (mismas instancias de un concepto en velas cercanas, ±tolConf×ATR) se muestra
**UNA** = la que **generó el impulso/reacción**. Prioridad (recomendación Claude, usuario delegó):
1. **Anclada a displacement:** la instancia seguida de la vela de displacement que rompió estructura.
2. Si ninguna/empate: **mayor `score_render_v2`** (strength × posRole × confluencia) = origen del impulso.
3. Desempate: **la primera** (cronológica), como "el primero que muestra el verdadero impulso".

## Pendientes que esto define (S104+)
1. **Transporte de geometría con VENTANA:** poblar la pierna **M5** también desde charts D1/H1 (detección M5
   limitada a ventana reciente → sin "Memory limits exceeded"; ver [[s103-bug1-fix-y-m5-panel-memoria]]).
2. **Calibrar el cap por banda:** cuántos "importantes por banda" (LuxAlgo apila varios OB; nosotros cortamos
   top-N). Tensión directa con el **budget ≤25** → afinar cap por banda = poblado pero no saturado (PASO 6).
3. **Input del enjambre (Fase 4):** la pierna poblada → cuaderno del orquestador + plantillas `confluencias/`
   ("dónde entrar, en qué parte de la pierna").

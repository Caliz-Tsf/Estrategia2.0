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

## Pendientes que esto define (S104+)
1. **Transporte de geometría con VENTANA:** poblar la pierna **M5** también desde charts D1/H1 (detección M5
   limitada a ventana reciente → sin "Memory limits exceeded"; ver [[s103-bug1-fix-y-m5-panel-memoria]]).
2. **Calibrar el cap por banda:** cuántos "importantes por banda" (LuxAlgo apila varios OB; nosotros cortamos
   top-N). Tensión directa con el **budget ≤25** → afinar cap por banda = poblado pero no saturado (PASO 6).
3. **Input del enjambre (Fase 4):** la pierna poblada → cuaderno del orquestador + plantillas `confluencias/`
   ("dónde entrar, en qué parte de la pierna").

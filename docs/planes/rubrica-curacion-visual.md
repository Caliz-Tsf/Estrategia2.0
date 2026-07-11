# Rúbrica de curación visual — auditoría F1 (D1→H1→M5)

> Criterio de diseño **estático** para la auditoría concepto-por-concepto y la curación de ruido.
> Destilado de principios aplicables (Apple HIG / "Designing Fluid Interfaces", vía la skill de Emil Kowalski)
> **adaptados al medio Pine** (cajas/líneas/labels estáticos; sin animación/CSS). NO es teoría de animación.
> Uso: aplicar en cada celda de la matriz `concepto × variante × TF × {nativo, heredado}`.

## 0. El medio manda
Pine solo tiene: `color` + **transparencia 0–100**, estilo de línea (solid/dashed/dotted), **grosor**,
tamaño de label (5 tiers), estilo de label. Toda jerarquía visual se construye SOLO con esos canales.
No hay easing, blur, sombras ni movimiento. Descartar el 90% de la skill (es para UI web).

## 1. Los 5 principios que SÍ aplican
1. **Jerarquía por peso+color, no solo por presencia.** Lo dominante (punta swing 50, concepto vigente)
   se dibuja con más contraste/grosor/tamaño; lo menor se **atenúa**, no se elimina de golpe.
2. **Dim-to-focus en vez de show/hide binario.** Curar ruido = subir transparencia / bajar saturación de
   lo secundario para que lo dominante resalte — no necesariamente ocultarlo. Alinea con gris-traspaso
   (S108/S113) y transparencia escalonada (S111).
3. **Encoding consistente en todo el sistema** (ver §2 — regla dura).
4. **Restraint — cada elemento se gana su lugar.** Si un dibujo no aporta lectura, es chart-junk. El default
   debe mostrar lo dominante; el detalle se revela bajo demanda (toggle).
5. **Simplicidad ≠ minimalismo; camino común primero.** El panel de toggles nativo/heredado debe traer un
   default legible (dominante encendido, ruido menor atenuado/apagado), no "todo encendido".

## 2. Regla dura de encoding: invariante al origen
**El hue de familia identifica el CONCEPTO. El origen {nativo, heredado} se codifica en un canal SECUNDARIO
(transparencia / estilo de borde / tag D1▲), NUNCA cambiando el hue.**

Familias canónicas (del Visual, fuente de verdad):
- **OB / Breaker / MB / Vacuum → azul** (`COL_OB #2962FF`, bull/bear `4A82EB`/`1A48B8`)
- **FVG / IFVG / BPR / IR / IPR / opening-gaps / Displacement → naranja** (`COL_FVG #FF9800`)
- **Estructura / swings / legs / stack / flips / CISD / SMT → teal/rojo** (`COL_BULL #089981` / `COL_BEAR #F23645`)
- **Premium/Discount → rojo/verde** (`COL_PREM`/`COL_DISC`)
- **OTE / Golden Pocket → ámbar** (`COL_OTE_GP`/`COL_OTE`)
- **Marco / mitigado / herramientas → gris** (`COL_FRAME_Q`/`COL_GHOST`/`CTX_MIT`)

### Colisiones detectadas (S116) — a resolver en la auditoría
- **Pools cambian de color por origen (BUG de consistencia):** nativo = rojo/verde direccional
  (`COL_BSL #E56363`/`COL_SSL #5EC470`, Visual); heredado = **violeta** (`CTX_LIQ #9C27B0`, Context L2159).
  → Un pool BSL debe leerse igual sea nativo o heredado. Elegir UNA familia para "pool" y codificar el
  origen por transparencia/tag, no por hue.
- **Violeta sobrecargado:** en el Visual `COL_LIQ #9C27B0` = *eventos* de liquidez (IDM/Judas/sweeps/rejections);
  en el Context el mismo violeta = *pools + EQ* heredados. Dos conceptos distintos, mismo hue.
  → Separar: "evento de liquidez" (violeta) vs "pool/EQ" (definir familia propia, p.ej. mantener direccional
  o asignar un hue de familia "liquidez-nivel" distinto del de "liquidez-evento").
- **Rojo/verde muy reutilizado:** estructura bull/bear, P/D y pools nativos comparten rojo/verde. Vigilar
  que en un mismo punto del chart no colisionen dos lecturas rojo/verde sin desambiguar por forma/posición.

Decisión concreta de familias/origen: **pendiente de la auditoría** (se fija concepto por concepto, se
documenta aquí y, si toca el CORE o rompe SHA, va a ADR).

## 2bis. Jerarquía de 3 niveles por peso+estilo (L1/L2/L3)
Los 40 conceptos se ordenan en 3 niveles de importancia; el nivel se codifica por **grosor + estilo de línea
+ tamaño de label** (canal ortogonal al hue de familia). Ya implementado en estructura (`SC_MAJOR/SC_SWING/
SC_INTERNAL`); esta tabla lo generaliza a toda la Visual:
- **L1 Macro** (pivote dominante 50, estructura HTF, P/D vigente): línea **solid w3**, label `size.normal`, texto
  descriptivo (BOS+/CHoCH+). Máximo contraste.
- **L2 Intermedio** (swing 5 con rol, BOS/CHoCH swing, OB/FVG vivos cercanos): **solid/dashed w2**, `size.small`.
- **L3 Micro** (zonas menores, gaps, EQ, heredados de fondo): **dotted / dashed w1** o caja alta transparencia,
  `size.tiny`. Contexto, no foco.

## 2ter. Anti-solapamiento y densidad (práctica confirmada — checklist Gemini/Tufte, ya vigente)
- **Nunca `label.new` por vela.** Repintar en `barstate.islast` desde el array (patrón sweeps/CISD/swings-rol),
  o `label.set_*` sobre slots fijos. Evita RE10045 y acumulación.
- **Objetos finitos:** las zonas mueren al mitigarse (estado), no `extend.right` infinito.
- **Offset por ATR** cuando dos marcas caen en la misma vela (desfase vertical ~ATR) — despeja solape.
- **GC estricto:** caps por array (`MAX_ZONES/POOLS=50`, top-N por banda) + `delete` de lo desalojado.
- **Anclaje `xloc.bar_time`** (no `bar_index`) en historia profunda (RE10026-safe).
- **RECHAZADO** (regla Gemini §4): *"solo 3 colores, diferenciar 40 conceptos por opacidad"*. 40 conceptos NO se
  distinguen por opacidad; se distinguen por **hue de familia** (§2) + estilo/nivel (§2bis) + opacidad para
  ORIGEN/variante. La opacidad es canal secundario, no el primario.

## 3. Heurística de "pivote importante" (Workstream B, ruido de swings)
- Punta **dominante** = extremo de la pierna del swing 50 → label prominente (size normal, contraste alto).
- **Pullback con rol** (crea OB/FVG/pool o barre liquidez) → menor, atenuado.
- Pivote menor sin rol → candidato a ocultar o a gris tenue (dim-to-focus).
- Clustering: varios pivotes menores contiguos → colapsar a la representación dominante (regla solape S111).

## 4. Procedimiento por celda de la matriz
Para cada `concepto × variante × TF × {nativo, heredado}`:
1. Apagado → confirmar que no queda residuo.
2. Poblado solo → ¿el hue es el de su familia (§2)? ¿nativo y heredado se leen como el MISMO concepto?
3. ¿La jerarquía distingue dominante vs. menor sin saturar (§1, §3)?
4. Anotar hallazgo (OK / ajustar knob / colisión de encoding). Knob-first; código solo si el knob no basta.

## Apéndice — Cuándo SÍ usar la skill de Emil Kowalski (guardar para Fase 4 / artifacts)
La skill (`github.com/emilkowalski/skills`: `emil-design-eng`, `apple-design`, `review-animations`,
`animation-vocabulary`) es **UI web animada** (CSS/JS/Framer Motion: easing `cubic-bezier`, springs,
duraciones <300ms, `transform`/`opacity` GPU, translucidez `backdrop-filter`, gestos con momentum).
**No aplica al indicador Pine.** Sí aplicaría, tal cual, si construimos:
- un **artifact/dashboard web** (mockup del panel de config, docs interactivas, visor de resultados);
- una **UI acompañante del EA en Fase 4** (MT5 no la usa, pero cualquier panel web sí).
No instalar como skill del proyecto (metería ruido de animación web en trabajo Pine). Reevaluar en Fase 4.

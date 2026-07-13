# Sesion-119 — Fase PALETA de auditoría visual F1: familia OB+FVG (2026-07-13)

## Objetivo
Arrancar la matriz de auditoría visual F1 desde D1. Método acordado: **todo apagado en bloque → medir concepto por concepto** (determinista, S116). Decisión de proceso del usuario: **paleta de toda la familia primero, luego curación** (evita retrabajo — el contraste "con sus pares" solo se juzga con la familia completa visible). Alcance de la sesión: **rediseño de paleta de la familia OB+FVG** completa.

## Nuevo encoding (pedido usuario) — la dirección se lee por familia verde/rojo
Rompe el esquema previo (azul=bloque / naranja=imbalance, dirección por tono). Ahora:
- **Bloque (OB/Breaker/MB/Vacuum):** relleno **oscuro sólido**. Verde=alcista / rojo=bajista.
- **Imbalance (FVG/IFVG/BPR/IR/IPR/gaps):** **claro/neón**. Verde neón=alcista / ámbar=bajista.
- **Bloque vs Imbalance** se separan por el eje **oscuro-sólido vs brillante-neón** (+ estilo de borde + label), aunque compartan hue por dirección.

## Cambios (commit `6dee986`, Visual-only, pine/SMC-Visual.pine)
**CORE byte-idéntico ×3 SHA `d86bf37aacbd25cf` INTACTO · pine_check 0/0 · core-sync OK ×3.**

### Constantes (fuera del CORE, ~L3093)
- `COL_OB_BULL` #0C3A14 (verde muy oscuro) · `COL_OB_BEAR` #7A1212 (rojo muy oscuro) · `COL_OB` #2E7D32 (bloque base verde medio)
- `COL_FVG_BULL` #00E676 (verde neón) · `COL_FVG_BEAR` #FFC400 (ámbar) · `COL_FVG` #FFC400
- **Nuevas:** `COL_OB_TXT_BULL` #81C784 / `COL_OB_TXT_BEAR` #EF9A9A (texto legible sobre relleno oscuro) · `COL_OB_GLOW_BULL` #39FF14 / `COL_OB_GLOW_BEAR` #FF3131 (borde fosforescente re-rol)

### Dibujantes
- **OB (`f_drawOB`):** transp bajada **75/83/90 → 45/62/78** (menos transparente, "más oscuro sólido" pedido usuario) + borde 50→25. Label a `COL_OB_TXT_*` (legible).
- **FVG:** el borde fosforescente sale gratis (relleno transp 80-92 tenue, borde transp 60 del mismo neón = brilla). Sin cambio de dibujante, solo la constante.
- **Breaker (`f_drawBreaker`):** borde **rayas fosforescentes** `color.new(glow, 45)` (antes dark f_mitBorder). Label a `COL_OB_TXT_*`.
- **MB (`f_drawMB`):** borde **puntos fosforescentes** `color.new(glow, 45)`. Transp **direccional**: bull 50/65/80 (más opaco — el verde muy oscuro se difuminaba más que el rojo con el fondo), bear 80/86/92 (igual, ya gustaba). Label a `COL_OB_TXT_*`.
- **Vacuum:** label a `COL_OB_TXT_BULL`.
- **IR (`f_drawIR`):** de **etiqueta ruidosa "IR ↑/↓" ámbar → EVENTO terciario**. Es evento, no zona (no hay rango que encajonar; §6.3.25 "contexto, no zona operable"). Marca = glifo triángulo pequeño **▲/▼** (`style_none`, `size.tiny`) **FUERA de la vela** (bull `yloc.belowbar` verde #00C853 / bear `yloc.abovebar` rojo #FF1744). **Filtro:** recorre TODOS los IR (poblar hacia atrás) pero solo dibuja los de **`f_confDegree(ir.price) >= 2`** (≥2 familias activas apiladas). Mata el ruido del ejemplo del usuario (swing bajista con 2 IR arriba + 2 abajo sueltos que no significan nada). `i_maxShowIR` queda sin uso (input in_64, sin warning).

## Aprendizajes / GOTCHAs
- **`data_get_pine_boxes` devuelve color en ABGR** (no ARGB): 0x80**20 5E 1B** = alpha 80, RGB **1B 5E 20** = #1B5E20. Decodificar invirtiendo bytes.
- **`f_confDegree` (§7.0.2)** cuenta 6 familias con instancia ACTIVA (no mit/invalid) en ±0.25×ATR: {OB/Breaker}·{FVG/IFVG/BPR}·{pool vivo}·{EQH/EQL}·{IDM}·{OTE/GP}. NO cuenta estructura/sweeps/displacement. Para IR: pool + OB + EQ = las confluencias que importan; FVG es flojo (IR es el anti-FVG).
- **Ritual apply confiable esta sesión:** `pine_inject.py` clicka "Pine Save" → actualiza la instancia aplicada EN SITIO (botón "Deshacer actualizar el script…" lo confirma). No hizo falta remover+re-añadir. Editor tenía el slot Visual abierto (verificado por cabecera antes de inyectar).
- **`size.tiny` es el mínimo para SHAPE de label** (triángulo); para más chico usar glifo de texto (▲/▼) con `style_none`. ▴/▾ salió demasiado chico; ▲/▼ a tiny = punto medio.
- Render lag 15-20s post `indicator_set_inputs`/inject → esperar antes de medir/capturar.

## Estado
- **F1-GATE BLOQUEADA.** Fase paleta de la familia OB+FVG **COMPLETA**. Sin ADR nuevo (Visual-only bajo ADR-002/ADR-016). Sin tag.
- Instancia aplicada `gRWnMq` (Visual), Context `zirOQD` oculto durante la medición.

## PENDIENTE S120
1. **Fase CURACIÓN de la familia OB+FVG** (knob-first): densidad/solape/jerarquía dim-to-focus + comportamiento con pares, en modos Operación/Estudio/Todo. Resolver el amontonamiento de labels cerca del precio (visto en "Todo").
2. Luego **siguientes familias** (estructura, liquidez/pools+colisión paleta nativo-vs-heredado violeta, etc.) con misma lógica paleta→curación.
3. Al final: herencia MTF H1/M5 + firma F1-GATE + tag `fase-1-completa`.

Ver [[Sesion-118]] · [[rubrica-curacion-y-colision-paleta]] · commit `6dee986`.

# Sesión 022 — 2026-06-15

## Objetivo
F1-S1.2-T07B — Estructura BOS/CHoCH DOMINANTE (swing 50), sesión dedicada (task
`docs/task-T07B-estructura-swing-dominante.md`, origen `docs/pendiente-estructura-swing-grande.md`).

## Arranque
- ESTADO-ACTUAL ✅ (T07 cerrado) · git limpio y sincronizado, `HEAD == origin == af87164` ✅
  (corregido el mito de "12 commits colgando" de S021: nunca existió).
- Decisión del usuario: **saltar la ratificación con smc-architect** (Opción C ya muy documentada);
  ir directo a check-rule + implementación.
- TV MCP: lanzado vía `tv_launch` (CDP 9222), EURUSD H1, con LuxAlgo de fondo para comparar.

## Trabajo

### check-rule (docs antes de codear)
- `reglas-smc-ict.md` §1.1: tercera escala `majorLen=50` + tabla de 3 escalas + mapeo a LuxAlgo
  (nuestro swing 5 ≈ interno de LuxAlgo; majorLen 50 = swing de LuxAlgo) + nota de latencia.
- §1.3 (BOS) y §1.4 (CHoCH): nota de las 3 escalas + 3 casos dominantes fechados del usuario.

### Implementación (Opción C — capa aditiva, ADR-004)
- **CORE NO tocado** (ni una línea de `// === LIBRARY CORE ===`). Reutiliza `SMC_Structure`,
  `f_setStructureHigh/Low`, `f_detectStructure`, `f_detectSwings` (ya escala-agnósticos).
- Inputs: `i_majorLen=50` (ambos consumidores) + `i_showMajor`/`i_showMajorSwings` (Visual).
- Estado consumer-side: `var SMC_Structure structMajor` + array dedicado `SMC_eventsMajor`
  (NO el `SMC_events` compartido del OB → sin contención).
- Wiring de detección (pivotes 50 → set structure → `f_detectStructure(true,true)` → push a
  `SMC_eventsMajor`) **idéntico en Visual y Strategy**. **NO** llama `f_updateTFState` → el bias
  headline (swing 5) NO cambia.
- Dibujo solo Visual: `f_drawStructureMajor` (línea width 3 por `bar_time`, etiqueta por `bar_index`
  midpoint) + fila de panel "Bias dom. (50)".

### Verificación
- **Compila 0/0** en Visual, Strategy y Library (TV, EURUSD H1).
- **check-core-sync OK, MISMO SHA** `24c3a4a28fcf74c3` (415 líneas) → CORE byte-intacto, T01–T07
  sin tocar.
- Validación VISUAL vs LuxAlgo en el mismo chart: los 3 casos del usuario presentes con
  dirección/color correctos (CHoCH baj ~1.17225, BOS baj ~1.15762, CHoCH ~1.15777). Sin regresión
  de swings(5)/interno(3)/OB/FVG/P-D. **Aprobado por Freddy.**

### Ajustes visuales pedidos por Freddy (iterados en vivo)
1. Color de la estructura dominante = **teal alcista / rojo bajista** (igual que BOS/CHoCH swing),
   no azul/naranja. También el panel "Bias dom.".
2. Etiqueta **centrada por `bar_index`** (no por tiempo): los gaps de fin de semana comprimen el
   eje temporal y corrían el midpoint en tiempo. Aplica a swing y dominante.
3. **Sin recuadro** pero con gap como los LL/HH: `style_label_*` direccional + fondo transparente
   (`color.new(col,100)`) → **ALCISTA encima** de la línea (`style_label_down`), **BAJISTA debajo**
   (`style_label_up`). Aplica a BOS/CHoCH grande y chicos.
4. **Nombres "OB" y "FVG"** añadidos a esas zonas (no tenían): tag de texto a la derecha del origen,
   centrado en la mitad de la zona, sin recuadro.

## Resultado
- T07B ✅ COMPLETO. ADR-004 escrito. Docs (reglas-smc-ict §1.1/§1.3/§1.4 + casos) y task marcados.
- Pendiente Fase 3 anotado: **bias dominante en el scoring** (50=contexto vs 5=gatillo vs
  combinación, decidir con OOS) — ADR-004 §Consecuencias.

## Nota importante para Sesion-023
- La conexión **CDP de TV se cayó** justo tras inyectar el último ajuste (estilo de etiqueta
  direccional alcista-arriba/bajista-abajo). El cambio es **trivialmente válido** (forma idéntica a
  `f_drawSwing`, que ya compila), pero **NO quedó recompilado/guardado en TV**. Al arrancar S023:
  re-lanzar TV (`tv_launch`), re-inyectar `pine/SMC-Visual.pine`, **confirmar 0/0** y re-guardar el
  slot. El archivo en disco es la fuente de verdad y está correcto.
- Slot TV: durante la sesión se usó el slot `SMC_Library` como buffer de compilación (cada
  `smart_compile` guarda en el slot abierto). Quedó con el código de Visual. La gestión de los 3
  slots nombrados es manual del usuario.

## Siguiente
T08 EQH/EQL (Sprint 1.2, PINE-PLAN §7).

# Sesion-104 — 2026-07-07

## Objetivo
Ejecutar el punto 1 de la agenda de S104 (decisión usuario): implementar geometría M5 con ventana, sustituyendo el transporte ligero que causaba OOM por el mecanismo `calc_bars_count` de Pine v6.

## Contexto
**S103 completó PASO 1-3** (BUG#1 fixeado, re-barrido exhaustivo, panel M5 ligero).  
**S103 hallazgo:** el transporte M5 al panel (3.ª columna cuando chart ≠M5) usaba `f_m5Light` (17 escalares, solo campos escalares SIN geometría OB/FVG/pool/sweep) porque invocar `f_computeTFState` COMPLETO desde D1/H1 sobre contexto M5 daba "Memory limits exceeded" (~200k velas M5 acumuladas).

**Decisión usuario (AskUserQuestion S104):** empezar por resolver la geometría M5 en lugar del PASO 6 (reducir budget a ≤25 labels).

## Completado

### Punto 1 — Geometría M5 CON VENTANA (1 commit `7c9e6e7`)

**Problema:** `f_m5Light` transportaba solo 17 escalares (campos de estado/posición/sesgos), sin los 12 slots de geometría (OB/FVG/pool/sweep/EQ/BOS/CHoCH etc.). Resultado: panel M5 mostraba "—" (guión) en las celdas de geometría cuando el chart no estaba en M5.

**Solución implementada:**  
Reemplazar `f_m5Light` por **`f_computeTFState` COMPLETO con `calc_bars_count`** (parámetro Pine v6).

**Cambios CORE:**
- `f_computeTFState(string tf, int calc_bars_count)` — nuevo parámetro limita cálculo a últimas N velas del TF solicitado. Devuelve tuple completo: 17 escalares + 12 slots × 6 campos = 89 elementos totales.
- Sin modificar la firma ni el cuerpo existente de `f_computeTFState` (ya aceptaba `calc_bars_count` por defecto = `na`, que significa "todas las velas").

**Cambios Visual:**
1. **Nuevo input `i_m5Window`** (input.int, grupo GRP_MTF, default 3000, minval 300, maxval 20000).
   - Permite al usuario ajustar la ventana de cálculo si es necesario (mayor = más memoria, mejor precisión histórica; menor = menos memoria).

2. **Transportes M5 re-poblados:**  
   Buffers `m5Kind`, `m5Top`, `m5Bot`, `m5Dir`, `m5TA`, `m5TB` (antes vacíos) ahora reciben los 12 slots de geometría desde el tuple de `f_computeTFState(..., "5", i_m5Window)`.

3. **Celdas panel M5 restituidas:**  
   - Panel T14 fila M5 muestra ahora OB/FVG/pool/sweep/EQ/BOS con valores reales.
   - Usa `f_bufZoneCell` y `f_bufNear` (funciones existentes) en lugar de "—" (guión placeholder).

4. **Eliminación de código muerto:**  
   `f_m5Light` ELIMINADA (completamente reemplazada).

5. **Anti-repaint:**  
   lookahead_off SIEMPRE en `request.security(..., lookahead=barmerge.lookahead_off)` — regla dura #1.

**Validación viva (OANDA:EURUSD, chart H1, indicador aplicado):**
- **SIN crash OOM.** Indicador renderiza sin errores.
- **Panel M5 poblado:** geometría real observada:
  - OB [1.14001, 1.14024]
  - FVG [1.14024, 1.14044]
  - Pool 1.14001 SSL
  - Sweep 1.14107 ↓
- **Valores M5-granulares:** distintos de D1/H1, confirman transporte correcto.
- **Diagnóstico temporal `geoN=12`:** confirma los 12 slots de geometría poblados (retirado en versión final).

### Hallazgo clave

La causa del OOM **no era el tamaño del tuple** (89 vs 17 escalares) sino el **número de velas M5 procesadas**.  
- Sin `calc_bars_count`: `f_computeTFState(..., "5")` recorría ~200k velas M5 acumuladas desde el inicio del gráfico → pico memoria.
- Con `calc_bars_count = i_m5Window` (default 3000): procesa solo las últimas 3000 velas M5 → memoria acotada, suficiente para la geometría.

El "—" que aparecía tras re-aplicar era **estado M5 aún sin cargar** (datos intradía frescos), no fallo del código — al recargar volvió normal.

### GOTCHA de tooling (documentado en auto-memoria)

Re-aplicar indicador Pine tras inyectar+guardar requiere ritual completo:
1. Tener slot `SMC_Visual` abierto en editor ANTES de inyectar.
2. Inyectar + Guardar (Ctrl+S).
3. Remover instancia aplicada del gráfico.
4. Pollear botón PLAY junto al nombre del script (ref e19 vía agent-browser CDP) hasta no-disabled (compilación lenta).
5. agent-browser click e19 en el tab correcto del gráfico (ref CDP efímero, cambiar tras re-render).

Refs agent-browser son efímeros → hacer snapshot DOM fresco justo antes de click.

---

## Pendiente (S105 agenda)

### PASO 6 — Reducir budget a ≤25 labels (BLOQUEANTE DURO F1-GATE)

Estado actual: D1 26 / H1 35 / M5 36 labels (vs presupuesto ≤25 por TF en modo Operación).

**Nota operativa:** la instancia S104 quedó en modo "Todo" (default). Budget ≤25 se mide en modo "Operación" (conmutar input `Densidad`).

### PASO 4 — Verificar herencia MTF D1→H1→M5

Tras cambios S104, revisar que la dirección de herencia es correcta y no hay regresión.

### Firma F1-GATE

Bloqueada hasta que PASO 6 cierre (budget ≤25 confirmado en Operación).

---

## Commits

- **`7c9e6e7`** feat(pine-visual): F1 S104 — geometría M5 CON VENTANA (calc_bars_count) sustituye f_m5Light

## Estado CORE

- **Líneas:** 1700 SHA `5510361166844bd5`
- **Compilación:** 0 errores / 0 warnings (pine_check.py server-side)
- **core-sync:** OK (SMC-Visual.pine, SMC-Strategy.pine, SMC-Library.pine)
- **SIN ADR nuevo**
- **SIN gate/tag**

## Enlaces

- [[Sesion-103]] — PASO 1-3 ejecutados (BUG#1 fix + barrido + panel M5 ligero)
- [[Sesion-102]] — REVISIÓN FABLE + esqueleto 6 pasos para Opus
- [[bug-ob-cercano-no-dibuja-operacion]] — BUG #1 antes de ser fixeado
- [[mt5-esqueleto-timing-fase2]] — contexto F1-GATE y F4 timing

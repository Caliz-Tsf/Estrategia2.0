# Sesion-087 — Eje 2 "Fuerza" Paso 5 COMPLETO + Hallazgo Gate §8.2/T14

**Fecha:** 2026-07-02 | **Fase:** Fase 1 | **Rama:** `pine/sistema-completo` | **Eje:** 2 (Fuerza) | **Plan:** §11.2 Pasos 5-9

---

## Objetivo
- **Primario:** Completar Paso 5 del esqueleto Fable (ribbon KZ + reorden capas L0→L4).
- **Secundario:** Validar en vivo comportamiento de Paso 4 (filtro §8.2) en Operación.

---

## Completado

### Paso 5 — Ribbon KZ + Z-Order Capas (2 commits Visual-only)

**Commit `9be569a` — Paso 5a: KZ full-height → ribbon + bgcolor gateado**

Cambios al dibujo de Kill Zones (sección `=== KILL ZONES ===`):

1. **Ribbon en lugar de `bgcolor` full-height:**
   - Antes: `bgcolor()` con color de sesión cubriendo todo el chart (KZ activa completa)
   - Ahora: **ribbon delgado** anclado en borde superior, solo para sesión EN CURSO
   - Anclaje: `y1 = ta.highest(high, 100) + 0.6×ATR`, altura ~0.35×ATR
   - Coloreado por sesión: `COL_KZ_London`, `COL_KZ_NY`, `COL_KZ_Asia` (heredadas de S084)
   - Nueva var global `kzActiveStart` rastrea `bar_index` de inicio de sesión para transición suave

2. **Gateado por modo (`i_densidad`):**
   - `bgcolor` KZ SOLO en modo Estudio+ (transparencia ≥93, invisible en Operación)
   - Macros (opening gaps, RTH/ETH) SOLO en Estudio+
   - Modo Todo: muestra RTH/ETH adicionales

3. **Anti-repaint:**
   - Ribbon se crea/actualiza SOLO en `barstate.isconfirmed`
   - La sesión activa se toma del cierre de la barra actual (no del futuro)

4. **Grid Verificado SIN fill:**
   - Grid Gradient (quadrants + eighths) comprobado: SOLO líneas (`line.new`), sin fill de área grande
   - Resuelve colisión "grid azul solapa Kill Zones": ahora son **ejes ortogonales** (grid = precio/líneas, KZ = tiempo/ribbon)
   - Checklist §10-#4 ("0 fills solapados en Operación"): ✅ PASADO

5. **Sección L0 etiquetada:**
   - Comentario de banner: `// === L0: FONDO TEMPORAL (Kill Zones, RTH/ETH) ===`
   - Facilitará reordenamientos futuros

**Compila 0 errores / 0 warnings, core-sync OK.**

---

**Commit `6cc4a84` — Paso 5b: Reorden capas L0→L1 (z-order back)**

Movimiento de bloques de dibujo en Visual para respetar z-order (L0 atrás, L4 adelante):

1. **Reorden mecánico:**
   - Identificadas las 5 capas (L0/L1/L2/L3/L4) en el código actual (§3 esqueleto)
   - Bloques dependientes (`f_drawOTE`, `f_drawPDLine`, `f_drawGradientGrid`, etc.) viajan juntos sin reorden interno
   - **Nuevo orden global:**
     1. L0: Kill Zones (`f_drawKZ`, `bgcolor`)
     2. L1: Marco de precio (P/D `f_drawPDLine`, gradient grid `f_drawGradientGrid`, OTE/GP `f_drawOTE`)
     3. L2: Zonas (OB/Breaker/MB `f_drawOB`, FVG/IFVG `f_drawFVG`)
     4. L3: Liquidez/estructura (pools `f_drawPools`, EQH/EQL, sweeps, BOS/CHoCH, etc.)
     5. L4: Panel T14 + labels consolidadas (diferido Paso 6-8)

2. **Verificación de dependencias:**
   - Ningún bloque L2+ llama a funciones de L1/L0 (estructuralmente independiente)
   - Funciones de dibujo puras respecto al orden de ejecución

3. **Banners de sección añadidos:**
   - `// === L0: FONDO TEMPORAL ===`
   - `// === L1: MARCO DE PRECIO ===`
   - `// === L2: ZONAS ===`
   - `// === L3: LIQUIDEZ + ESTRUCTURA ===`
   - `// === L4: PANEL + OVERLAY ===`

**Resultado:** Chart más legible, grid y Kill Zones ya NO compiten por z-order visualmente.

**Follow-up NOTA (no bloquea):** Swap fino L2↔L3 diferido. Se verificó visualmente que estructura grande (BOS/CHoCH) dibujada al final NO oculta zonas, pero se anotó para pasada de validación completa (Paso 9).

**Compila 0 errores / 0 warnings, core-sync OK.**

---

### Estado de Compilación
- **3 archivos (Visual + Strategy + Library):** 0/0 errores y warnings ✅
- **CORE SHA:** `5510361166844bd5` — **1700 líneas INTACTAS** (no cambió vs S085/S086)
- **core-sync.ps1:** OK — byte-idéntico Visual/Strategy en sección `// === LIBRARY CORE ===`

---

## Hallazgo Crítico — Validación Vivo (NO bloquea Paso 5, RE-SECUENCIA S088)

**En TradingView OANDA:EURUSD H1, indicador inyectado, modo Operación:**

### Filtro §8.2 (Paso 4) Incompleto

**Tabla Matriz Operación (§8.2):**

| Familia | Operación (esperado) | Operación (observado) |
|---|---|---|
| F1 Estructura | BOS/CHoCH/MSS vigente + flips-P | ✅ **BOS/CHoCH vigente visible, flips ocultos OK** |
| F2 Contexto | SOLO EMAs líneas + panel | ✅ OK |
| F3 OB | P | ✅ OK |
| F4 FVG | P (FVG/IFVG) | ✅ OK |
| F5 P/D | Ancla | ✅ OK |
| F6 Gradient | Quadrants | ✅ OK |
| **F7 EQH/EQL** | **P solo** | ❌ **INUNDACIÓN: ~50 EQH/EQL históricos sin gatear** |
| **F8 Liquidez** | **pool objetivo + sweep último** | ❌ **INUNDACIÓN: sweeps/IDM/Judas históricos sin gatear** |
| **F9 KZ** | **Ribbon + gaps-P** | ✅ OK (ribbon nuevo funciona) |
| F10 OTE | OTE activo | ✅ OK |
| F11 MTF | Primarios heredados | ✅ OK |
| F12 Panel | ON | ✅ OK |

**Resumen visual:**

- **Ocultan bien (~7 familias):** Rej/IDM/IR/CISD/⊗Stack (Stack), CORR/IMP, Judas, MB
  - Mecanismo: `f_famOK(FAM_EST)` + `f_visualLevel()` pisos MTF funcionan

- **Inundan SIN gatear (~200+ labels medidos):**
  - Estructura histórica: **BOS/CHoCH/EQH vigentes** + ~120 labels de barras pasadas sin cap/pisos
  - EMA: ↩EMA crosses (OK en Estudio+, NO gateados en Operación)
  - Liquidez: FLIP, FB, ID, ⚡Disp (Displacement), ⚡Raid/Sweep, BAG, EQHL (Equal Highs/Lows)
  - **TOTAL Operación MEDIDO: ~505 labels vs BUDGET ≤25 (§6.5)**

### Análisis: ¿Por qué pasa esto?

**Gate #1 del checklist §10:** "Presupuesto Operación ≤25 labels"

NO es bloqueado por **consolidación §6.2** (fundir labels de nivel grid/P/D/D1), sino por:

1. **Completar §8.2 para familias sin gatear:**
   - EQH/EQL, Liquidez: el `i_show*` existe pero NO tienen canería a matriz modo×familia
   - Entrada actual: `f_famOK(FAM_EST)` solo revisa si familia ON, no revisa modo
   - Necesario: `matriz[familia][modo]` → Primario/Secundario/Terciario directo, NO cálculo post-hoc

2. **Top-N a estructura (solo vigente):**
   - Estructura histórica (BOS/CHoCH de 20+ barras) NO tiene `f_strongestN` ni cap de distancia
   - Necesario: aplicar top-N SOLO al vigente (últimos ~4 eventos) + cap cercanía

3. **Contador "Ocultos" en panel T14 (Paso 8):**
   - Ocultar sin contar = viola §1-7 ("todo lo oculto se cuenta")
   - Necesario: familias sin gatear cargan "Ocultos: 120" en panel
   - **Paso 8 está acoplado a this.**

### Impacto en Plan §11.2

| Paso | Estado | Nota |
|---|---|---|
| 5 | ✅ COMPLETO | Ribbon + z-order OK; filtro §8.2 DESCUBIERTO pero NO bloquea Paso 5 |
| 6 | Diferido | Consolidación §6.2 (fundir labels) ahora SECUNDARIA vs completar §8.2 + Paso 8 |
| 7 | Diferido | Tag TF, herencia (§7.2/§7.1) siguen en plan |
| 8 | ⚠️ **CRÍTICA** | Panel T14 "Ocultos" — acoplado a §8.2 completado |
| 9 | Diferido | Validación final con todo gateo listo |

### Re-secuencia Recomendada (S088)

**En lugar de Paso 6 aislado, ejecutar BLOQUE acoplado:**

```
S088 Sesion:
 (a) Completar canería §8.2 (familia × modo)
     para F1/F7/F8/F2-resto: matriz explícita o getter OK
 (b) Aplicar top-N + pisos a estructura
     (solo vigente, f_strongestN o variante)
 (c) Implementar contador "Ocultos" en panel T14 (Paso 8)
     con loop: suma todas familias Terciarias por modo
 (d) Validación EN VIVO (TV H1 Operación)
     confirmar ≤25 labels + contador correcto
 (e) §6.2 (consolidación labels) como PULIDO MENOR
     después, si presupuesto permite
```

**Beneficio:** Cierra gate #1 en una pasada; evita vueltas pendiente-corrección-pendiente.

---

## GOTCHAs Nuevos (Validación Vivo)

### GOTCHA-1: `mcp__tradingview__indicator_set_inputs` NO matchea clave `"Densidad"`

**Situación:** Re-inyectamos con `pine_inject.py` tras cambio de código. Esperábamos cambiar `i_densidad` a `"Operación"` por MCP.

**Resultado:** `data` devuelve:
```json
{
  "input_key": "Densidad",
  "updated_inputs": {}
}
```
Input NO cambió → modo sigue en valor anterior guardado.

**Causa:** Key exacta en Pine: `i_densidad = input.string("Todo", options=[...], title="Densidad", group="DENS")`
- MCP busca por `title` exacto?
- O por `input.string` y posición?
- O el nombre interno `i_densidad` vs nombre de UI `Densidad`?

**Workaround:** Usuario cambió a mano en TV (Ajustes→Inputs→Densidad=Operación). Funcionó inmediatamente.

**Action:** Documentar qué hace matcheo MCP; si es `title` exacto, OK. Si es nombre interno, usar `i_densidad`.

---

### GOTCHA-2: `pine_check.py` vs `pine_inject.py` 

- **`pine_check.py`:** Compila server-side de TradingView SIN necesidad de abrir TV. Resultado inmediato, 0 warnings.
- **`pine_inject.py`:** Inyecta vía Chrome DevTools Protocol (CDP). Requiere `tv_launch` (Desktop abierto + conectado a puerto 9222).

**Workflow S087:**
1. Compile checks: `pine_check.py` (sin TV)
2. Inyectar cambios: `tv_launch && pine_inject.py`

---

## Evidencia Visual

**Screenshot:** `D:\CODE\BOT\Bot\tradingview-mcp-jackson\screenshots\S087-operacion-baseline.png`

- Chart OANDA:EURUSD H1
- Modo Operación (i_densidad=Operación)
- Ribbon KZ visible arriba (nuevo, funciona)
- Grid quadrants visibles (sin fill de área)
- Labels de estructura + liquidez: ~505 (inundación medida)

---

## Commits Git

```bash
9be569a feat(pine-visual): F1-Eje2 Paso 5a — KZ full-height a ribbon + bgcolor gateado (§F9/§6.3)
6cc4a84 feat(pine-visual): F1-Eje2 Paso 5b — reorden capas L0/L1 + banners de seccion (§3)
```

---

## Sin Gate de Fase | Sin ADRs Nuevos | Firma Usuario F1-GATE Pendiente

---

## Siguiente (S088)

**Plan confirmado por usuario:**

1. **Completar §8.2 (Paso 4) + Paso 8 (T14 Ocultos) acoplados**
   - Canería matriz modo×familia
   - Top-N estructura (vigente solo)
   - Contador "Ocultos" en panel

2. **Validación en vivo TV**
   - Gate #1 ≤25 labels en Operación
   - Contador refleja realidad

3. **Pulido §6.2 después** (si presupuesto permite)

---

## Notas de Memoria

**Nueva entrada:** `[[eje2-paso5-ribbon-y-hallazgo-gate]]`
- Ribbon KZ = éxito de diseño
- §8.2 incompleto descubierto por validación vivo (hallazgo bueno)
- Re-secuencia reduce riesgo (una pasada, no vueltas)

---

*Sesion-087 · Claude Code · 2026-07-02*

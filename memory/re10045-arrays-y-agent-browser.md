# RE10045 — Crash de runtime por arrays en `f_drawMTFZones`

**Fecha:** 2026-07-03 (Sesion-089)
**Severidad:** CRÍTICO (hoy resuelto) / reocurrencia: MEDIA (patrón idéntico en otros bloques draw MTF)
**Estado:** ✅ DIAGNOSTICADO + ARREGLADO

## Síntomas
- Commits `dbf5459`, `ee4d8e2`, `87abab1` **compilan 0/0** en Pine (error checking server-side con `pine_check.py`).
- **AL APLICAR al chart, TradingView Desktop 3.3 crashea** (indicador desaparece, chart vacío).
- Ni error logs ni advertencias visibles (SE NECESITA runtime trace, no disponible en TV MCP).

## Causa raíz
Cualquier combinación `array.new` + `array.push` **dentro de `f_drawMTFZones`** (que corre CADA tick en `barstate.islast`) **dispara límite de recursos runtime de Pine**.

**Bisect empírico (Sesion-089):**
```
✅ array.new(int, 10)                           → OK
✅ array.new(int, 10) + array.size()            → OK
❌ array.new(int, 10) + array.push(valor)       → CRASH INMEDIATO
```

**Contexto:** `f_drawMTFZones` es **5 niveles de profundidad** en la pila de llamadas (main loop → barstate.isconfirmed → sección `=== DIBUJO ===` → `f_drawMTFZones` → dentro de for-loop); corre ~1700 líneas de script ANTES en la misma vela. Pine aloca stack/heap para cada recurso (líneas, labels, boxes, etc.); el push en arrays dentro de esa función **rebasa el limit de instancia runtime**.

**Datos de Pine v6:**
- Máximo ~5000 objects on chart (cumplido: ~500 labels).
- Máximo ~10MB de código compilado (cumplido: ~4KB).
- **Máximo ~128MB de memoria runtime por indicador** (← aquí choca el array.push).

## Solución
**Reemplazar arrays por acumulador string + `str.contains()`.**

Antes (crashea):
```pine
var array<[string, float]> dedupBuf = array.new<[string, float]>()
for cap in capN
  ...
  if not array.includes(dedupBuf, ...)
    array.push(dedupBuf, [key, val])  // ❌ CRASH
```

Después (funciona):
```pine
var string dedupStr = ""
for cap in capN
  ...
  key = str.format("%s_%f", family, level)
  if not str.contains(dedupStr, key)
    dedupStr += key + ";"  // ✅ OK
    // dibujar
```

**Rendimiento:** string concatenation en Pine es O(n), pero con caps tipicamente <30 por TF, n es negligible.

## Commits afectados / arreglados (Sesion-089)
| Commit | Problema | Estado |
|--------|----------|--------|
| `dbf5459` | Paso 6 §6.2 dedup array | ❌ CRASHEA |
| `ee4d8e2` | Paso 6 §6.5 presupuesto array | ❌ CRASHEA (consecuencia) |
| `87abab1` | Guard (innecesario) | ❌ SIGUE CRASHEANDO |
| `ed0c46e` | FIX string-dedup | ✅ FUNCIONA |

Commits `9c146d3` (Paso 7) y `862928b` (Paso 8) **nunca usaron arrays**, por eso funcionaron.

## Lecciones aprendidas
1. **No usar `array.push` dentro de funciones que corre cada tick en `barstate.islast`.**
2. **Pine compiler está limitado en recursos runtime**, no solo en errores sintácticos. Error checking **server-side no lo detecta**.
3. **Arrays en Pine son costosos en memoria** — alternativas: strings (concatenation), maps (si disponibles v6+), globales `var` (pre-alocados).

## Reocurrencia potencial
**RIESGO MEDIO:** otros bloques `f_draw*` que usan `barstate.islast` y pueden tener lógica array similar (ej. `f_drawStructure`, `f_drawEQHL`, `f_drawOB`, etc.). **Acción preventiva:** revisar codebase por patrón `array.push.*barstate.islast` antes de cerrar Fase 1.

## Aplicación autónoma del indicador (Sesion-089 bonus)
**Hallazgo:** `pine_inject.py` + `pine_smart_compile` **NO refresca la instancia aplicada** (solo hacen "Pine Save"). El botón "Agregar al gráfico" en TV Desktop 3.3 **NO es `<button>` accesible por CDP** (buscado por texto, aria-label, data-name, ref-number, no aparece en DOM).

**Solución:** usar **agent-browser con CDP 9222** para clickear el ref-id del botón directamente. Automatizado en `scripts/launch-tv-agent.ps1`. **Capacidad nueva:** TV **SIEMPRE se lanza con agent-browser**, indicador se aplica solo, usuario **NO necesita re-aplicar manualmente** tras inyección.

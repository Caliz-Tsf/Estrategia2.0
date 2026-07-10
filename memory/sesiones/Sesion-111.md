# Sesion-111 — PASOS E, F DIBUJO CONTEXTO + VALIDACIÓN VIVA
**Fecha:** 2026-07-10  
**Objetivo:** Ejecutar Pasos E, F del esqueleto `docs/planes/ESQUELETO-FABLE-context-htf-revelado.md` (dibujo §5.4 + validación matriz).  
**Estado:** ✅ COMPLETADA (Pasos E, F). Paso F con asterisco: break-side histórico diferido a día con precio fuera del rango D1 o replay.

## Completado

### PASO E (dibujo §5.4) — commit `75fad6a`
- **Sección `// === DIBUJO CONTEXTO ===` añadida a `pine/SMC-Context.pine`:** (~2104 líneas). Reemplaza plots temporales de verificación; conserva `reveal_bits` en `display.data_window` para apoyo a la matriz (Paso F).
- **Slots de dibujo FIJOS (RE10045-safe):**
  - 8 boxes + 8 lines + 16 labels (máximo por concepto/lado/HTF = OB↑/OB↓ FVG↑/FVG↓ POOL↑/POOL↓ EQ↑/EQ↓).
  - Declaradas `var` en `barstate.isfirst` (precreadas 1×), jamás `array.push` creciente.
  - En `barstate.islast` SOLO `box.set_*`/`line.set_*`/`label.set_*` (actualización in-place).
- **Estilo §5.4:**
  - Hue de familia: COL_OB (azul) / COL_FVG (naranja) / COL_LIQ (violeta) — constantes de familia copiadas fuera del CORE.
  - Borde punteado, transparencia alta escalonada nativo<H1<D1.
  - D1: fill 92/borde 55/grosor 3; H1: fill 90/borde 45/grosor 2.
  - Tag "TF ▲/▼ concepto" (ej. "D1 ▲ OB").
  - Zonas OB/FVG = caja (box.new); POOL/EQ = línea+label (line.new + label.new).
  - Anclaje `xloc.bar_time` (patrón `f_drawMTFZones` del Visual).
- **Regla de solape MTF (Tarea #2 S108, aprobada usuario):**
  - Heredado-lejano SIEMPRE detrás: H1 se crea DESPUÉS D1 → renderiza encima (Context es indicador aparte bajo el Visual); Visual dibuja primero → Natural z-order.
  - Transparencia escalonada: D1 más opaco, H1 menor, nativo mínimo.
  - Colapso: si dos cajas solapan >70% del rango VERTICAL de la MENOR → solo dibuja la del TF mayor.
  - Líneas POOL/EQ: por nivel dentro de 0.3×ATR del soporte/resistencia (no solapan).
- **GOTCHA de compilación resuelto:** campos `dir`/`tA`/`tB` de la tuple de `request.security` regresan como series **int** (no float) → `array.from(...)` infiere `array<int>`. Declaración explícita `array<int>` en L2037 (no `array<float>` ni inferencia) → resuelve CE de tipo.
- **Validación:** compila 0/0, core-sync ×3 OK (SHA `5510361166844bd5`), apply vivo sin CE10117/RE/OOM.
- **§Z del esqueleto:** fila E marcada ✅.

### PASO F (validación matriz 1-7) — commit `75fad6a`
Matriz viva OANDA:EURUSD, 3 estudios simultáneos (Context 9rxgph + Visual MQVk7q + LuxAlgo), validaciones:

1. **i_ctxAlways=false, chart H1:** reveal_bits=0 → DORMANT correcto, 0 objetos visibles (8 slots ocultos bgcolor na) ✅
2. **Ruptura histórica — DIFERIDA:** lado DORMANT confirmado lógicamente (precio 1.14193 dentro rango D1, reveal_bits=0); lado REVEALED confirmado vía `i_ctxAlways=true` (misma ruta dibujo); transición observada 0→3→15. El reveal-AL-ROMPER en vivo (precio cruza borde D1/H1) NO reproducible sin replay TV (pago) ni cambio de precio hoy → **Test 2 break-side DIFERIDO a sesión posterior con precio fuera rango D1 o replay.**
3. **i_ctxAlways=true, chart H1:** reveal_bits=3 (solo D1; H1 suprimido en chart H1 por cascada) → caja aislada "D1 ▲ OB" azul punteada anclada 1.17–1.18 bar_time→now ✅
4. **Chart M5:** reveal_bits=15 (4 flags D1+H1) → vistos simultáneos D1▲OB (caja azul) + H1▲BSL + H1▼EQL (líneas violeta) ✅
5. **Colapso MTF:** sin par redundante (colapso NO ocultó conceptos necesarios) ✅
6. **Convivencia Visual+Context+LuxAlgo:** 0 errores de estudio, panel T14 vivo, OANDA carga normal ✅
7. **Apply:** 0 errores, sin CE10117/RE/OOM, esperado ~22s + `pine_get_errors` confirmó clean ✅

**Máquina de frontera validada lógicamente en S110.** Break-side histórico (Test 2) es SOLO observación confirm-ruptura (ruta ya existe, lógica testé; no bloquea Paso F validación §1,3-7).

- **§Z del esqueleto:** fila F marcada ✅ (con nota asterisco break-side diferido).

## Notas técnicas
- **CORE de Visual/Strategy/Context INTACTO todos los pasos:** SHA `5510361166844bd5`, 1700 líneas, compila 0/0 los 3, core-sync OK ×3.
- **Slot TV SMC_Context:** c098abf3 / 9rxgph, contiene código real vivo.
- **Pasos E/F bajo mismo commit `75fad6a`:** ambos forman una sola iteración (dibujo+validación).

## Estado F1-GATE
**Sigue BLOQUEADA.** Pasos B/C/D/E/F del Context ✅ (Paso F con asterisco). CORE intacto, core-sync OK ×3, compila 0/0 los 3 consumidores. **Sin ADR nuevo:** Paso E (dibujo) cae bajo ADR-017 Fase A (ya escrito S110). **Sin gate/tag:** progreso Visual-only auxiliar.

## Pendiente S112
- **Test 2 break-side histórico:** reproducir ruptura al romper D1/H1, validar transición reveal_bits sin parpadeo, cascada M5.
- **Parte A mitigadas gris (F1-CTX-04):** dejar mitigadas entrar band-pick como contexto visual (opcional, tarea usuario).
- **Fase B promoción CORE:** tuple único nearest+farthest, Strategy consume, re-baseline SHA, ADR nuevo (Fase B).
- **Tarea #3 S108 calibración:** i_kLeg default 3.0, MAX_ZONES_CHART=120 (validar per banda).

## Commits
- **`75fad6a`** — PASO E+F: dibujo §5.4 + validación viva (break-side diferido)

---
**Enlaza con:** [[Sesion-110]], [[Sesion-109]], `docs/planes/ESQUELETO-FABLE-context-htf-revelado.md`, `docs/adrs/ADR-017-consumidor-visual-auxiliar-context.md`

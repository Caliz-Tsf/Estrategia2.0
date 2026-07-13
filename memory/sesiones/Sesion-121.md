# Sesion-121 — Headroom CE10117 recuperado + curación anti-solape viva (2026-07-13)

## Objetivo
Restaurar del git stash el WIP de curación anti-solape de labels OB+FVG (S120), verificar que ahora cabe sin CE10117 con el headroom que supuestamente dejó la dieta S120, y resolver el amontonamiento de labels cerca del precio.

## Lo que pasó (hallazgo central)
1. **PREMISA DE ADR-020 INCORRECTA:** S120 reportaba que "funciones no-llamadas SÍ cuentan tokens en Pine" (memoria S107), y por eso ejecutó una dieta: borró 5 muertas + movió `f_detectVolumeImbalance` fuera del CORE. Verificación de S121: **Pine YA tree-shakea funciones nunca llamadas** (no incluye su código compilado si nadie las llama) → **funciones no-llamadas NO contribuyen token count**.

2. **DIETA S120 FUE NO-OP DE TOKENS:** Recompilando el commit c35e918 (dieteado limpio) + el WIP de curación S120 contra una **instancia fresca post-reinicio anti-caché** (el ritual correcto: remover, re-añadir botón ▶, esperar ~30s): ambos versiones daban exactamente **100819 tokens > techo 100256** — IDÉNTICO al número pre-dieta de S119. La "validación viva" que S120 reportó fue contra instancia **cacheada** (GOTCHA conocido pero re-confirmado).

3. **DIAGNÓSTICO CORRECTO DEL SINK:** Análisis de perfil de tokens (proxy local que ignora strings/comentarios):
   - 68% del peso es **código Visual-only** (no CORE compartido):
     - 32% dibujo drawers (OB, FVG, Breaker, IFVG, BPR, MB, Vacuum, OTE, IPR)
     - 16% detección TF propia del Visual
     - 9% MTF + rainbow
     - 6% panel T14
   - El CORE byte-idéntico compartido NO es el sink; cuando se compila junto al Visual, el compilador tree-shakea funciones que solo Strategy/Context usan (incluyendo las 5 borradas en S120).
   - El proxy incluso sobre-cuenta el CORE, metiendo funciones que solo Strategy/Context llaman que el Visual tree-shakea.

4. **FIX REAL (COMMIT `d36d1c6`):** Refactor feature-preserving SIN tocar CORE (sin romper core-sync, sin perder features). Dos helpers nuevos tras f_mitStyle (~L3510):
   - `f_zBox(leftT, top, bottom, bg, bc, bs)` → unifica boilerplate idéntico de 9 `box.new()` (OTE/OB/Breaker/IFVG/BPR/MB/Vacuum/FVG/IPR). Devuelve el objeto para que el `array.push()` quede en top-level (RE10045-safe).
   - `f_zLbl(x, y, txt, tc)` → unifica 8 `label.new()` centrados (OTE + las 7 familias). Devuelve objeto.
   - Render byte-idéntico (mismas cajas, mismos labels, mismo dibujo).
   - **Ahorro:** −485 tokens proxy ≈ ~1130 tokens reales (factor 2.33×) por factor compresión Pine.

## Verificación viva (ground truth)
- **Instancia fresca post-reinicio completo (kill_existing) anti-caché:** OANDA:EURUSD 1D.
- Dibujo: 99 cajas + panel de estado completo renderizadas, SIN CE10117 visible en console.
- Compilación: `pine_check` server-side 0/0. Apply: `pine_get_errors` = 0.
- Core-sync ×3 OK, SHA CORE `752b4083a7db419d` intacto (1866 líneas, vs. baseline pre-S121 1952).
- Instancia se **MUEVE CON EL PRECIO** (validación live el indicador actualiza).

## Curación anti-solape (incluida en commit)
La curación WIP de S120 (f_ySlot por ranuras de 0.5×ATR + acumulador `seen` string RE10045-safe) quedó incluida en el refactor y **ahora SÍ aplica en vivo**:
- Reparte labels en la pierna histórica sin colisiones y-on-screen.
- Se leen todos los nombres (antes: pila ilegible).
- PENDIENTE (diferir S122): cerca del precio el amontonamiento se alivió pero NO se eliminó. Competencia: la regla "el importante band-pick/ancla se rotula SIEMPRE" compite con el anti-solape por espacio → la pila cercana al precio sigue densa (sub-óptima pero legible).

## Aprendizajes / GOTCHAs nuevos
- **Token count CE10117 solo se ve en DESKTOP y solo cuando está SOBRE el techo.** Bajo techo no muestra número, solo renderiza sin error. Pine Save y re-aplicar sin cambios de código NO actualiza el número (instancia cacheada).
- **pine_check.py server-side NO aplica CE10117.** Usa `translate_light` que no cuenta tokens; solo la aplicación desktop (`pine_get_errors` tras apply) ve el count real. Endpoint `translate/compile` completo da 404 con Guest.
- **TV cachea bytecode dentro de sesión.** Inyectar código distinto y leer el mismo número de tokens = caché. Único bust fiable = reinicio completo (`tv_launch kill_existing`), que recompila todos los estudios del layout al recargar.
- **Pine tree-shakea funciones NUNCA llamadas.** Borrar código muerto NO baja tokens si es código inalcanzable. Solo baja tokens **recortar código ALCANZABLE** (llamado). ADR-020 fue basada en premisa incorrecta.
- **pine_inject.py clickea "Pine Save" no "Add to chart".** Porque su CLICK busca texto en inglés y TV está en español ("Añadir al gráfico"). Añadir instancia fresca = clickear por title "Añadir al gráfico" vía ui_evaluate (solo visible con editor enfocado y estudio fuera del chart).

## NOTA ADR-020
- Código sigue compilando y es válido (funciones borradas no se usan, layout limpio).
- **El headroom CE10117 correcto viene de refactor S121 (helpers), no de la dieta S120.**
- Marcar ADR-020 como "basado en premisa incorrecta sobre token count; ejecución válida pero no resolvió headroom; solución real = S121 refactor".

## PENDIENTE S122
1. **Afinar amontonamiento cercano al precio:** banda-pick vs anti-solape. Pila densa aún legible pero no óptima. Opciones: (a) ranking knob-first dentro banda-pick, (b) heurística de salto si densidad > threshold, (c) aceptar densidad + resolver después Fase 3.
2. **Siguientes familias:** auditoría visual OB+FVG completa D1 → otros conceptos (estructura/extremos/events/liquidez) por variante → herencia MTF D1→H1→M5.
3. **Firma F1-GATE:** recién después que la matriz de auditoría pase.

Ver [[Sesion-120]] · ADR-020 · docs/adrs/ADR-020-dieta-tokens-core-funciones-un-consumidor.md

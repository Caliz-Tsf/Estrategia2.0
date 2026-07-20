# Sesión 137 (S136-A) — 2026-07-20

## Objetivo con el que arrancó
Sesión de instrumento y medición programada al cierre de S136: ejecutar los 3 experimentos pendientes de `RESPUESTA-FABLE-S135.md` §2.3 con applies reales en TradingView — (1) par histórico `aee69a7` vs `f91a2bd` con lastres desplazados, para zanjar la paradoja ADR-022; (2) coste real del fix de `pdMid`; (3) segundo punto local del Visual para `base_V`.

## Rama
`pine/sistema-completo`

## Commits (2)
- `58fde0d` refactor(pine): S136 borrar `pine/SMC-Library.pine` — sin consumidores y rancio. Toca `CLAUDE.md`, `docs/workplan/PINE-PLAN.md` (D-PINE-01b en §1 y tabla §8) y elimina `pine/SMC-Library.pine` (1498 líneas). check-core-sync verificado OK tras el borrado (sin cambios: 1776 líneas, SHA `9559a0d7fe58b213`).
- `8f243ce` feat(scripts): S136 modo `hist` en `scripts/gen_ablacion_core.py` — permite pasar un artefacto git arbitrario como origen (en vez de solo HEAD) para medir blobs históricos. Reutiliza `lastre()` existente.

## Decisión ejecutada: borrado de `pine/SMC-Library.pine`
Motivo verificado con grep en los 4 `.pine`: cero `import` que lo consuma. Rancio desde `c35e918` (13-jul) mientras Visual/Strategy/Context avanzaban a 16-18 jul; le faltaban las 6 funciones del motor ADR-021 y conservaba 2 de la Opción A muerta (`f_resetTrailingHigh/Low`) — contradecía al código vivo. `check-core-sync.ps1` no lo vigilaba (solo Visual/Strategy/Context). Resincronizar habría institucionalizado una 4ª copia a mano (contra regla dura #2) y no cabía en check-core-sync (lleva `export` + anotaciones de tipo ⇒ comparación transformada, no byte-a-byte). Es derivable desde el CORE vivo; histórico íntegro en git `45449f3..c35e918`. Fase 4 no lo usa (cero menciones en `docs/workplan/MQL5-PLAN.md`). Anclado como **D-PINE-01b** en `docs/workplan/PINE-PLAN.md` §8 (tabla de decisiones) + árbol de §1 corregido + línea de arquitectura en `CLAUDE.md` actualizada. Se regenerará desde el CORE al cerrar Fase 2. Coincide con la recomendación de Fable (`RESPUESTA-FABLE-S135.md` §7), en contra de lo que decía el dossier de S135.

## Experimento 1 — par histórico (decisivo para la paradoja ADR-022)
Premisa verificada independientemente: `aee69a7` (5117 líneas) vs `f91a2bd` (4978 líneas), diff exactamente +139/-0.
- A = `aee69a7:pine/SMC-Visual.pine` + lastre(305) ⇒ 108071 tokens (00:32:43)
- B = `f91a2bd:pine/SMC-Visual.pine` + lastre(300) ⇒ 107929 tokens (00:35:43)
- ΔT = 142. Predicciones pre-registradas en `RESPUESTA-FABLE-S135.md` §2.3: rama 1 = 130-150 si el muerto cuesta cero; rama 2 = 830-850 si costaba. Resultado ⇒ **RAMA 1**, rama 2 excluida por un factor ~6.

**Conclusión:** las 139 líneas muertas costaban CERO tokens en los artefactos exactos del episodio ADR-022. El build "100952" que justificó la dieta de ADR-022 fue una lectura fantasma (contaminada). Confirma S135 y cierra, con los artefactos originales, la paradoja que S135 había dejado abierta para Fable. La regla del lastre desplazado (S136, `docs/reglas-dev.md` §1.6b) funcionó como antídoto: números Y timestamps distintos en A y B descartaron consola rancia.

## Experimento 2 — coste real del fix de `pdMid`
Verificación previa: `git log 42207ea..HEAD -- pine/SMC-Visual.pine` vacío ⇒ el Visual no cambió desde que se midió la referencia 107986 ⇒ la resta es legítima.
- Visual(HEAD) + lastre(300) + fix-slim ⇒ 108031 tokens (00:45:09)
- coste(fix-slim) = 108031 − 107986 = **45 tokens**
- ⇒ base_V = 100262 − 45 = 100217; **headroom real del Visual = 39 tokens**

El "falla por 6" que dejó S135/la auditoría de Fable era numéricamente correcto pero por la razón equivocada (señalada por Fable en su §3): no es que el fix cueste 6, es que cuesta 45 y solo había 39 libres. Para que quepa hace falta liberar ≥6 tokens de código QUE SE EJECUTA — retirar código muerto no sirve, medido en cero dos veces (S135 y el experimento 1 de esta sesión). Descartada en vivo la hipótesis de un mecanismo oculto de ~1100 tokens que había quedado abierta en S135.

## Estado del entorno al cierre
Visual restaurado a HEAD, aplicado con el botón PLAY y verificado vivo en pantalla (sin error rojo, dibujo completo, panel de 4 columnas). Chart en su configuración original de 2 slots (Context `47j1gF` + Visual `yCpNSa`). check-core-sync OK: CORE 1776 líneas SHA `9559a0d7fe58b213`; EXTREMES CORE 148 líneas SHA `5f851d87e5fda720`. El CORE no se tocó en esta sesión.

## Gotchas de método nuevos
- Ctrl+Enter crea una 3ª INSTANCIA del estudio en el chart en vez de refrescar la existente (lo detectó el usuario mirando la pantalla). El ritual correcto tras inyectar es el botón PLAY: selector `[title="Actualizar en el gráfico"]` (TV en español; `pine_inject.py` busca "Add to chart"/"Update on chart" y cae al saveButton, que solo guarda).
- Verificar una ablación con `indexOf('nombre_funcion')` en Monaco es un CHECK FALSO: casa con comentarios supervivientes. En esta sesión B tenía 1 mención (comentario) y aun así era correcto. Verificar contra el blob con `grep -c`.
- Para MEDIR tokens no hace falta el play: el Save ya dispara la compilación y el número sale en `pine_get_console`. El play es solo para refrescar la instancia del chart.

## Pendiente / siguiente
- **Experimento 3 (no ejecutado esta sesión):** `Visual + lastre(600)` para obtener `base_V` por regresión directa en el propio Visual, en vez de heredar la pendiente de Context (calibrada en 3000-3800 unidades, 10x fuera de rango — Fable la había marcado como no firme). Instrumento listo: `python scripts/gen_ablacion_core.py hist 600 pine/SMC-Visual.pine`.
- **Anexar a ADR-020 y ADR-022** la resolución de la paradoja (NO revocarlos: la decisión arquitectónica se sostiene por mantenibilidad; lo que cae es la justificación por tokens). Queda para el supervisor, no ejecutado en esta sesión de cierre de documentación.
- **NUEVO (corrección del usuario, no medido):** falta medir el coste de PARSEO/CARGA del código muerto — "cero tokens" no es "cero coste": el compilador igual parsea lo que luego tree-shakea. Dato débil, no concluyente, observado esta sesión: tiempos de compilación ~70s planos (A 5435 líneas=71s, B 5290 líneas=72s, fix-slim 5294 líneas=70s, HEAD 4982 líneas=69s), pero el rango de tamaños es solo ~9%, demasiado estrecho para concluir nada. Requiere una ablación grande (los 36 detectores) — sin diseñar aún.
- Matriz concepto × TF × {nativo, heredado} (pendiente heredada de S135/S136, no arrancada).
- ADR del reparto del dibujo (pendiente heredada, no arrancado).
- F1-GATE sigue sin firmar.

## Referencias
`docs/planes/RESPUESTA-FABLE-S135.md` §2.3 · `docs/reglas-dev.md` §1.6b · `docs/workplan/PINE-PLAN.md` §1/§8 (D-PINE-01b) · `scripts/gen_ablacion_core.py` · ADR-020 · ADR-022 · Sesion-136.

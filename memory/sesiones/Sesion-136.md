# Sesión 136 — 2026-07-18

## Objetivo con el que arrancó
Recibir y evaluar la auditoría adversarial de Fable sobre el dossier de S135 (`docs/planes/DOSSIER-FABLE-capacidad-y-codigo-muerto-S135.md` + `docs/planes/PROMPT-FABLE-S135.md`). Sesión corta y de una sola cosa: NO se tocó Pine, NO se hicieron applies en TradingView, NO se midió nada nuevo.

## Rama
`pine/sistema-completo`

## Commits (2)
- `a13d550` docs(fable): F1-S135 respuesta de la auditoría adversarial. Crea `docs/planes/RESPUESTA-FABLE-S135.md` (349 líneas).
- `95bef51` docs(reglas): S136 regla del lastre desplazado. Añade sección 1.6b a `docs/reglas-dev.md` (verificado presente: "### 1.6b Medición de tokens `[S136 — regla del lastre desplazado]`").

## Estado técnico
CORE INTACTO. `pine/` no se tocó en toda la sesión. check-core-sync OK ×3. CORE 1776 líneas, SHA `9559a0d7fe58b213`. EXTREMES CORE 148 líneas, SHA `5f851d87e5fda720`. Sin cambios respecto a S135. Sin tag.

## Qué verificó Fable
Auditoría estática + arqueología git, 10 comprobaciones, sin applies en TradingView. Los 10 hallazgos [MEDIDO] verificables del dossier S135 son CORRECTOS: la Library desincronizada, los call-sites de `f_farthest*`/`f_wickNearLevel`, el fallback de `pdMid` en `:4467`, los 4 placeholders, el diseño de los dos arneses.

## Tres hallazgos que corrigen trabajo de S135

### 1. Crítica de método (la más importante)
La medición ×3 = 107986 de S135 tiene un agujero de diseño: su resultado esperado (tres números idénticos) es indistinguible de la firma de la consola rancia, un fallo del instrumento ya documentado por el proyecto. Un experimento cuyo éxito luce igual que el fallo del aparato no puede autovalidarse.

Fable cree que la conclusión del tree-shaking ES correcta igualmente, con dos atenuantes: en la misma sesión los builds de Context SÍ dieron números distintos, y S121 corrobora por otra vía. Propone la REGLA DEL LASTRE DESPLAZADO. Ya aplicada en `docs/reglas-dev.md` §1.6b (commit `95bef51`).

### 2. "Falla por 6" era una etiqueta FALSA
`base_V + coste(fix) = 100262` es una ecuación con dos incógnitas; el 6 es la distancia del build al límite, NO el coste del fix, que nunca se midió (queda en [6, ∞)). El único delta real medido fue el del guard (38 tokens). La decisión no cambia: el revert `f9357a4` sigue siendo correcto (100262 > 100256 está medido directo).

### 3. Paradoja ADR-022, resuelta EN HIPÓTESIS (no cerrada)
El patrón "aparece CE10117 → retiro código muerto → aplica → causa aislada" ocurrió dos veces (S120 y S133) y choca con las mediciones cuidadosas (S121 y S135). Dos datos nuevos la inclinan: el propio ADR-022 admite en su sección PENDIENTE que el Visual final nunca llegó a aplicarse en S133, y S134 encontró después el slot con un build roto en rojo. Hipótesis: los 100952 eran lecturas rancias o buffers contaminados con código vivo de probes (~700 tokens ≈ el exceso de +696). PENDIENTE DE MEDICIÓN.

## Decisiones de Fable (una discrepa del dossier de S135)
- **Library `pine/SMC-Library.pine` → BORRAR**, no resincronizar (discrepa de la recomendación del dossier S135). Razón: es derivable del CORE, nadie la importa hasta cerrar Fase 2, y una 4ª copia sincronizada a mano es el anti-patrón que la regla dura #2 existe para matar. **NO EJECUTADO — pendiente de decisión del usuario.**
- **Placeholders** (`KIND_GRAB`=24, `KIND_GRADIENT`=53, `MTF_SLOT`=6, `i_scoreThresh`) → conservar los 4, documentar la reserva en docs, no con comentarios dentro del CORE (romperían el SHA ×3). **NO EJECUTADO.**
- **Reparto del dibujo** → sí es el camino, con eje TF/rol (Context = dibujo HTF vía `request.security`, Visual = operación chart-TF/M5), lo que evita el muro OOM de S105. Coste corregido a la baja: Context ya contiene el CORE byte-idéntico, así que mover una familia son call-sites, no código copiado. Requiere ADR nuevo (ADR-017 declaró Context "reversible"; el reparto lo vuelve pieza estructural).
- Hallazgo nuevo de Fable: el tercer slot existe EN EL TIEMPO — la Strategy solo ocupa slot cuando se backtestea. La restricción es 2 slots por MOMENTO, no por proyecto.
- Los 2 slots son restricción del plan gratuito de TradingView, no de la técnica. Debe quedar nombrado sin disfraz en el ADR del reparto.
- Determinismo → añadir invariancia al prefijo con `W(TF)` declarado; el test ya existe (la matriz de 9 celdas de S134); cierre en la frontera F2→F3, no "antes de F4" (si Fase 3 se calibra sobre un motor historia-dependiente, toda la Fase 3 es irrepetible y los goldens de F4 heredan el vicio).
- `pdMid` → no reabrir ahora, pero con vencimiento duro: antes de capturar los golden tests de Fase 4 (riesgo de construir el EA bug-compatible).

## Pendiente / siguiente (S136-A, sesión de instrumento y medición, ~6 applies en TV)
1. Par histórico `aee69a7` (con `f_tfExtremes`) vs `f91a2bd` (sin) con lastres desplazados (305 y 300) — zanja la paradoja ADR-022 con los artefactos originales. Ambos difieren en exactamente las 139 líneas (verificado por numstat).
2. `Visual + lastre(300) + fix-slim` → coste real del fix = T − 107986.
3. `Visual + lastre(600)` → segundo punto LOCAL de Visual ⇒ `base_V` medido de verdad sin transferir la pendiente de Context.

Luego: anexar la resolución a ADR-020/ADR-022 (no revocar) → matriz concepto × TF × {nativo, heredado} (inventario que el reparto necesita) → ADR del reparto → `pdMid` dentro → pendientes F1-GATE.

## Bloqueos / deuda abierta
- F1-GATE sigue sin firmar.
- La paradoja ADR-022 sigue abierta (hipótesis, no medición).
- La decisión sobre borrar `SMC-Library.pine` está pendiente del usuario.
- No repetir las hipótesis ya refutadas con medición de S128-S135.

## Referencias
`docs/planes/RESPUESTA-FABLE-S135.md` · `docs/reglas-dev.md` §1.6b · `docs/planes/DOSSIER-FABLE-capacidad-y-codigo-muerto-S135.md` · ADR-020 · ADR-022 · ADR-023 · Sesion-135.

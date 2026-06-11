# ADR-001 — Bot multi-símbolo, sin filtro horario duro

- **Estado:** Aceptado
- **Fecha:** 2026-06-10
- **Decisores:** Freddy (usuario) + Claude Code
- **Contexto de fase:** Fase 0 · DOC-01 (definición de reglas-smc-ict.md §3.4 Kill Zones)

## Contexto

El WORKPLAN-MAESTRO-V2 aprobado tenía dos premisas que entran en conflicto con la finalidad real del producto:
1. **Kill Zone como filtro DURO:** "sin KZ activa → no hay entrada" (F2-T02, regla de señal §4.8, PINE-PLAN §6).
2. **Alcance "solo EURUSD"** como si fuera el objetivo final, no solo el campo de pruebas.

El usuario aclaró la finalidad real: **el bot debe operar en CUALQUIER símbolo, gobernado por confluencias y datos**, no solo EURUSD. EURUSD es el instrumento de **validación inicial**, no el límite.

Un filtro horario fijo (London 08–10 GMT, etc.) es intrínsecamente EURUSD/FX-céntrico: sabotea símbolos con otras sesiones (USDJPY→Tokyo), con DST distinto, o sin sesiones (cripto/índices 24h). Y un bloqueo binario por reloj descarta señales A+ solo por la hora.

## Decisión

**El sistema es símbolo-agnóstico por diseño. La Kill Zone deja de ser filtro duro y pasa a confluencia ponderada + perfil de sesión configurable. El guardián universal de calidad de liquidez es un filtro de spread, no el reloj.**

Componentes:
1. **Todo umbral relativo a ATR** (ya adoptado en §0) — fundamento de la portabilidad entre símbolos y escalas de precio.
2. **`sessionProfile` configurable por símbolo** (`FX-London-NY` default · `FX-Asia` · `None`). `f_killZone(time, sessionProfile)` informa qué sesión está activa; alimenta la confluencia #34 con peso calibrado **por símbolo**. No bloquea.
3. **Filtro de spread** (rechaza entrada si spread real > máximo configurable) — guardián de liquidez agnóstico al símbolo y a la hora.
4. **Perfiles de pesos del scoring por símbolo** — los pesos validados en EURUSD no transfieren 1:1; cada símbolo tiene su set (o re-validación).
5. **Lo inherentemente por-símbolo va como input:** pip/point, spread típico, sessionProfile, pesos.

## Alternativas consideradas

- **Mantener KZ como filtro duro (plan original):** rechazada — incompatible con multi-símbolo y demasiado rígida (bloquea señales válidas por reloj).
- **Ignorar la sesión por completo:** rechazada — descarta una variable con edge real y deja al bot operar la sesión muerta de EURUSD sin contrapeso.
- **Umbral dinámico por sesión:** válida pero subsumida — el peso por sesión calibrado por datos logra lo mismo de forma más principista.

## Consecuencias

**Positivas:**
- Un solo codebase operable en FX, metales, índices y cripto.
- La calidad la gobiernan score + spread + datos, no un dogma horario.
- Fase 3 mide empíricamente cuánto aporta cada sesión (IS/OOS), por símbolo.

**Negativas / costes:**
- Más superficie de configuración (perfiles por símbolo).
- Riesgo de operar mercados thin si el filtro de spread está mal calibrado → mitigado validando spread por símbolo.
- **Disciplina obligatoria:** se valida EURUSD primero (gate Fase 3); cada símbolo nuevo repite validación abreviada (Fase 5). NO se optimiza para N símbolos a la vez (overfitting).

## Items del workplan afectados — ✅ TODOS APLICADOS (2026-06-11, Sesion-003, revisión Fable)

- **§4.8 regla de señal:** quitar `KZ activa ∧` como precondición dura; KZ pasa a confluencia #34 ponderada. La señal = `score_dir ≥ threshold ∧ score_dir > score_opuesto ∧ R:R≥3 ∧ spread ≤ máx`.
- **F2-T02 "Filtros duros":** sustituir "KZ obligatoria" por "spread ≤ máx" + "R:R≥3" + "sin posición duplicada". KZ ya no es filtro.
- **PINE-PLAN §3.4 `f_killZone`:** firma pasa a `(time, sessionProfile)`.
- **PINE-PLAN §6 Strategy:** añadir input `maxSpread` y filtro; añadir `sessionProfile`.
- **MQL5-PLAN (Fase 4):** SMC_Scoring y SMC_RiskManager deben soportar perfiles por símbolo; SMC_MTF parametriza sessionProfile.
- **Fase 5:** ya contempla expansión par a par — se confirma como el mecanismo de validación por símbolo.
- **reglas-smc-ict.md:** §0 (principio símbolo-agnóstico) y §3.4 (Kill Zones) ya actualizados.

> ~~Estos cambios al WORKPLAN se aplican cuando se toque cada sección.~~ **Aplicados en Sesion-003** (revisión Fable pre-Bloque C): WORKPLAN §4.8 + F2-T02 + descripción DOC-07, PINE-PLAN §3.4/§6, MQL5-PLAN (inputs EA, OnTick guard, flujo, tabla de mapeo). Este ADR sigue siendo la fuente de verdad de la decisión.

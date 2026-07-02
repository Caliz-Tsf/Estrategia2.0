# ADR-013 — Confluencia exponencial de Gradient Levels (T42, #52) = multiplicador del score, no voto plano

- **Fecha:** 2026-07-01 (Sesion-080)
- **Estado:** Aceptado (mecanismo); **wiring al scoring DIFERIDO a Fase 2 (F2-T01)**.
- **Precisa (no contradice):** ADR-002 (umbrales/pesos congelados hasta calibración Fase 3, split IS/OOS 70/30). Añade una **forma funcional** nueva al scoring; los valores siguen congelados.
- **Tarea:** relleno del ESQUELETO-P4 (Gradient Levels), concepto **T42** — regla `docs/reglas-smc-ict.md §5.17`. Familia T41 (grid) → T42 (confluencia exponencial) → T43 (FVG válido).

## Contexto

La doctrina 2026 (`madre-2026.md:92,:287`, verbatim) dice que la probabilidad de que el precio corra a un nivel (REH/REL, FVG, pool) **aumenta EXPONENCIALMENTE** cuando ese nivel coincide con un **quadrant** del rango mayor (grid T41 §5.16). Esto NO es una confluencia más que "suma un peso": es un **efecto multiplicativo** sobre la calidad de las confluencias de zona que YA existen.

La arquitectura de scoring del proyecto (WORKPLAN §4.8, regla dura #6) es hasta hoy **puramente aditiva**: `scoreDir = Σ(peso_i × activa_i)`, con pesos direccionales (scoreLong/scoreShort) calibrados en Fase 3. Meter T42 como una confluencia aditiva plana (#52 con un peso fijo) **traicionaría la doctrina** (el efecto es no-lineal en el nº de confluencias sobre el quadrant) y además arriesgaría doble-conteo (las confluencias de zona ya suman por sí solas; el quadrant las *amplifica*, no las repite).

Se necesita decidir el mecanismo **antes** de tocar `f_scoreConfluences` en Fase 2, para que la implementación del motor de decisión no lo re-litigue ni lo improvise.

## Decisión

### 1. T42 es un MULTIPLICADOR post-agregación, no un sumando
El bonus de gradient se aplica **después** de la suma ponderada, como factor sobre el score direccional ya agregado:
```
scoreDir_raw   = Σ(peso_i × activa_i)                              // §4.8, SIN cambios
gradientBonus  = f_gradientConfluenceBonus(nSobreQuadrant, gradMultMax, k)   // 0 .. (gradMultMax−1)
scoreDir_final = scoreDir_raw × (1 + gradientBonus)
```
- `nSobreQuadrant` = nº de confluencias de **zona** ya activas en `scoreDir_raw` (OB #17/#19, FVG #18/#20, pool #9) cuyo nivel cae dentro de `gradTol×ATR14` de un punto **isQuadrant=true** del grid T41 vigente. Los **eighths NO** disparan el bonus (la doctrina lo liga a "quadrant level de la entereza del rango"; los eighths sí valen para T43 FVG-válido, que admite cualquier punto del grid).
- Forma funcional **creciente saturante**: `f_gradientConfluenceBonus = (gradMultMax − 1)·(1 − e^(−k·n))`. `n=0 → bonus=0 → multiplicador=1` (neutro). `n→∞ → multiplicador→gradMultMax` (tope). Monótona, sin discontinuidades, acotada.

### 2. El contrato de `f_scoreConfluences` pasa de aditivo a aditivo+multiplicativo
En Fase 2 (F2-T01), el motor de decisión aplica el factor `(1 + gradientBonus)` al `scoreDir_raw` **antes** de comparar contra umbrales de entrada. Es el **único** término multiplicativo del scoring; todo lo demás sigue aditivo. Se documenta explícitamente para no confundir con un peso más de §4.8.

### 3. Valores congelados hasta Fase 3 (ADR-002 intacto)
`gradMultMax` (tope del multiplicador) y `k` (velocidad de saturación) son **parámetros de calibración**, congelados hasta el split IS/OOS 70/30 de Fase 3. La **forma** se fija aquí; los **números** no. `gradTol` reusa el input de T41/T43 (§5.16, default 0.12×ATR14).

### 4. Fase 1 entrega SOLO la función pura + spec; CERO wiring al scoring
En Fase 1, T42 aporta la función pura `f_gradientConfluenceBonus` en el CORE (golden-test MQL5 directo) y su regla §5.17. **No** se cablea a `f_scoreConfluences` (que aún no existe: es Fase 2). Esto respeta la regla dura #8 (no adelantar gates) y el gate `sprint16` (regla antes de código).

## Alternativas descartadas

- **T42 como confluencia aditiva plana (#52 con peso fijo):** descartada — contradice la doctrina (efecto exponencial, no lineal) y arriesga doble-conteo con las confluencias de zona que amplifica.
- **Multiplicar cada peso de zona individualmente sobre el quadrant** (en vez del score agregado): descartada — enreda la trazabilidad del scoring (no se sabría cuánto aportó cada confluencia) y complica el golden test. El multiplicador post-agregación es auditable (un solo factor).
- **Función escalón / lineal en n:** descartada — la doctrina dice "exponencial" y una lineal no satura (2 confluencias no deberían valer el doble que 1 sin techo). La saturante `1 − e^(−k·n)` captura "crece rápido y luego se aplana".
- **Wire directo en Fase 1:** descartada — no hay motor de scoring en Fase 1; violaría el gate de fases (#8).

## Consecuencias

- **`f_scoreConfluences` (Fase 2) nace ya con el término multiplicativo previsto** — no se re-litiga en F2-T01.
- **Core-sync cambia de SHA** al añadir `f_gradientConfluenceBonus` — esperado, documentado en el commit de T42.
- **#52 queda reservada** para T42 en el catálogo §4.8, con la nota de que es multiplicador (no sumando). T41/T43/T44 NO inflan el conteo (herramienta / refinamiento / opcional).
- **Anti-overfitting intacto:** `k`/`gradMultMax` entran por IS/OOS (ADR-002); la forma funcional no introduce parámetros libres fuera de calibración.
- **MQL5 (Fase 4):** el multiplicador se traduce 1:1 (función pura + un factor sobre el score agregado); golden test verifica `f_gradientConfluenceBonus` dado un `nSobreQuadrant` fijo.

## Referencias

- Regla: `docs/reglas-smc-ict.md §5.17` (T42) + §5.16 (T41 grid, del que depende) + §0.9 (herramienta vs confluencia).
- Esqueleto: `docs/planes/ESQUELETO-P4-gradient-levels.md` §3 (mecanismo) / §7.3 (naturaleza de confluencia).
- Doctrina: `Mente/Mentores/ict/knowledge/madre-2026.md:92,:287` (verbatim exponencial).
- ADRs base: ADR-002 (congelación umbrales/pesos + IS/OOS), ADR-011 (SMT, otro concepto con gate de arquitectura previo al wiring).
- Confluencias: `WORKPLAN-MAESTRO-V2.md §4.8` (#52 candidata). Reglas duras: `CLAUDE.md` (#6 scoring direccional, #8 gates, #2 core-sync).

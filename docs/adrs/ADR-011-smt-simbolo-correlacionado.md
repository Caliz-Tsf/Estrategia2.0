# ADR-011 — SMT Divergence: símbolo correlacionado como input por perfil (no hardcode)

- **Fecha:** 2026-06-21 (Sesion-047, Sprint 1.6 Fase 0)
- **Estado:** **ACEPTADO** (2026-06-21, Freddy) — **default elegido: EURUSD ↔ GBPUSD, correlación POSITIVA.** Preferencia explícita por pares **positivamente correlacionados** (no usar el inverso DXY como vía principal). Desbloquea T38 para su codificación cuando llegue su turno en Sprint 1.6 (tras la Fase 0 de reglas y la validación de Tier 2). El resto de Sprint 1.6 (T26–T37, T39, T40) nunca dependió de este ADR.
- **Regla asociada:** `reglas-smc-ict.md` §5.13 (SMT Divergence, confluencia candidata #51).
- **Relacionado:** ADR-001 (símbolo-agnóstico, sin hardcode) · ADR-009 (transporte MTF: buffer plano por `request.security`, sin UDT/array).

## Contexto

SMT Divergence (§5.13) compara los **swings de dos símbolos correlacionados**: cuando uno hace un higher-high (o lower-low) y el otro **no lo confirma**, hay manipulación institucional. Es la única primitiva del set que **necesita datos de un segundo ticker** → un 2º `request.security` a otro símbolo.

Esto choca de frente con **ADR-001 (símbolo-agnóstico, nada hardcodeado a EURUSD)**: no podemos fijar "el par correlacionado es GBPUSD" en el código, porque el sistema debe correr en cualquier símbolo. Tres preguntas abiertas que este ADR resuelve antes de escribir una línea de T38:

1. **¿Qué símbolo correlaciona con cuál** y cómo se configura (hardcode vs input)?
2. **¿Cómo se transporta** la serie de swings del correlacionado sin romper la regla de que `request.security` no mueve UDT/array (R-P3-2 / ADR-009)?
3. **¿Coste de performance** del 2º (o 3º) `security`?

## Decisión (propuesta)

### 1. El par correlacionado y el SIGNO de correlación son INPUTS por perfil — cero hardcode (honra ADR-001)

```
i_smtEnable  = input.bool(false, "SMT: activar (requiere par correlacionado)")
i_smtSymbol  = input.symbol("",  "SMT: símbolo correlacionado")   // p.ej. "OANDA:GBPUSD"
i_smtInverse = input.bool(false, "SMT: correlación inversa (DXY/USDCHF)")
```

- **`i_smtSymbol`** define el correlacionado. Vacío → SMT off (no penaliza performance).
- **`i_smtInverse`** indica el signo: correlación **positiva** (GBPUSD: ambos suben juntos) o **inversa** (DXY/USDCHF: se mueven al revés). El detector usa el signo para interpretar la divergencia (en inversa, "no confirma" = el correlacionado hace el extremo en el mismo sentido nominal).
- **Perfil por símbolo** (como `sessionProfile` §3.4 / pesos por símbolo de ADR-001): cada símbolo validado trae su `smtSymbol`/`smtInverse` por defecto. Validación primero en EURUSD (gate Fase 3); cada par nuevo fija su perfil SMT en Fase 5.

**Mapa de correlaciones recomendado (defaults propuestos — DECISIÓN DE FREDDY):**

| Símbolo chart | `smtSymbol` recomendado | `smtInverse` | Motivo |
|---|---|---|---|
| **EURUSD** | **GBPUSD** | false (positiva) | Par SMT clásico ICT en FX: ambos vs USD; cuando uno barre un low y el otro no, hay SMT. Disponible en todos los brokers. |
| (alterno EURUSD) | DXY | true (inversa) | Benchmark institucional del dólar; más limpio pero no siempre disponible/contínuo en el feed del broker. |
| GBPUSD | EURUSD | false | Espejo del anterior. |
| USDJPY / USDCHF | DXY | false | Pares USD-base: correlación positiva con el índice dólar. |

> **DECISIÓN (Freddy, 2026-06-21): default EURUSD↔GBPUSD (POSITIVA).** Disponibilidad universal + par SMT más enseñado + lectura intuitiva (ambos suben/bajan juntos). Preferencia general por **pares positivamente correlacionados** para los perfiles por símbolo. `i_smtInverse` permanece en el código como capacidad (coste cero), pero NO es la vía recomendada; DXY-inverso queda como opción secundaria de quien la necesite, no como default de ningún perfil.

### 2. Transporte: 2º `request.security` + buffer plano de pivotes (reusa el patrón ADR-009)

`request.security` no mueve arrays/UDT. Igual que el mapa MTF (ADR-009), se **aplana**: el consumidor llama `request.security(i_smtSymbol, timeframe.period, <tuple plano de los últimos N pivotes del correlacionado>)` con `lookahead = barmerge.lookahead_off` (regla #1, anti-repaint). El tuple lleva `[swingHighLevel, swingHighTime, swingLowLevel, swingLowTime] × N`. El consumidor reconstituye y llama al detector.

### 3. `f_detectSMT` es PURA (en el CORE byte-idéntico)

Recibe las **dos secuencias de pivotes** (la del chart + la del correlacionado ya traída) + el signo de correlación, y emite `SMC_Event KIND_SMT` cuando hay divergencia no confirmada (§5.13: equiparación por `smtTol` velas). No llama `security` (eso es del consumidor) → portable a golden tests MQL5 (ADR-002).

### 4. Performance

Hoy hay **2** `security` (D1 + H1, mapa MTF). SMT añade **1** (el correlacionado al TF del chart) → **3 totales**, solo cuando `i_smtEnable`/`i_smtSymbol` están activos. Off por defecto → **coste cero** en corridas de un símbolo. Dentro del presupuesto de Pine (límite ~40 `security`/script).

### 5. MQL5 (Fase 4)

El EA se suscribe al 2º símbolo (`SymbolSelect` + `CopyRates`) y pasa sus pivotes a la misma `f_detectSMT` portada. El mapa de correlaciones vive en el perfil del símbolo (config del EA), no en el código.

## Consecuencias

- **A favor:** respeta ADR-001 (nada hardcodeado; todo por input/perfil); reusa el patrón de transporte ya validado (ADR-009); detector puro (golden tests); coste cero si no se usa.
- **En contra / coste:** +1 `security` cuando se activa; el usuario debe configurar el par por símbolo; la calidad del SMT depende de elegir un correlacionado real (mala elección → ruido). La validación de T38 necesita **datos de 2 símbolos** (no se pudo verificar contra `eurusd_h1.csv` de un solo par; se hará en pasada TV dedicada con el par configurado).

## Alternativas descartadas

- **Hardcodear GBPUSD/DXY:** viola ADR-001 (rompe el multi-símbolo). Rechazada.
- **Solo DXY:** más "institucional" pero no siempre disponible/contínuo en el feed del broker; lo dejamos como opción inversa configurable, no como única vía.
- **No implementar SMT:** se pierde una señal de calidad fuerte (#51). Diferida no, pero **gateada** por este ADR.

## Checklist antes de codear T38

- [x] Freddy aprueba el mapa de correlaciones → **EURUSD↔GBPUSD, POSITIVA** (2026-06-21).
- [x] Estado de este ADR → **Aceptado**.
- [ ] Confirmar ticker exacto del correlacionado en el feed del broker (formato `EXCHANGE:SYMBOL`, p.ej. `OANDA:GBPUSD`) — al codear/validar T38.
- [ ] Definir el N de pivotes a transportar (arranque: reusar `MTF_K`/criterio de ADR-009).
- [ ] Verificar SMT con datos de los 2 pares (pasada TV dedicada, no posible con el CSV de un solo símbolo).

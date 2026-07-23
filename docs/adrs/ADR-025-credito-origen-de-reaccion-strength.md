# ADR-025 — Crédito de "origen de reacción/displacement" en la fuerza de zonas (W_ZREACT)

- **Estado:** Aceptado (hook latente), S142 (2026-07-23).
- **Contexto de fase:** Fase 0/1 (curación visual). El peso se calibra en **Fase 3** (IS/OOS).
- **Relacionado:** [[ADR-002]] (umbrales/pesos congelados hasta Fase 3), [[ADR-014]] (motor de fuerza), estrategia2-arquitectura-v2.

## Contexto

Durante la curación visual el usuario observó un defecto real: **un FVG del que el precio
reaccionó y del que lleva días cayendo aparece como "Secundario"** (se oculta en modo Operación).
Diagnóstico medido sobre `f_zoneStrength` (CORE): la fuerza se compone de
rango×ATR (0.30) + frescura (0.20) + **cercanía al precio (0.10)** + bias (0.10) + refinamiento (0.10).

El modelo **no acredita la reacción/movimiento que la zona GENERÓ**. Peor: cuando el precio
reacciona y **se aleja**, la zona **pierde el término de cercanía** y puede caer bajo el umbral
Primario (~0.66) → se degrada a Secundario justo por haber cumplido su función. La misma lógica
aplica a OB/Breaker/MB institucionales que producen reacciones.

## Decisión

Agregar en `f_zoneStrength` (CORE, byte-idéntico Visual/Strategy/Context) un término candidato:

```
s += W_ZREACT * (z.kind == KIND_OB or z.kind == KIND_BREAKER or z.kind == KIND_MITIGATION or z.trueFvg or z.propulsion ? 1.0 : 0.0)
```

con **`W_ZREACT = 0.0` (constante candidata, INERTE)**. Semántica: una zona institucional
(OB/Breaker/MB) o un FVG de displacement (trueFvg/propulsion) conserva fuerza aunque el precio se
aleje, compensando la pérdida de cercanía.

### Por qué constante y no input

Los pesos del motor de fuerza (0.30/0.20/…) ya son **candidatos congelados como constantes**
hasta la calibración IS/OOS (ADR-002/ADR-014). El crédito de reacción sigue el mismo patrón:
es un candidato, no un knob de usuario. Con `W=0` el término es `s += 0` → **cero cambio de
comportamiento** (verificado: SHA CORE estable, sin regresión visual).

### Por qué constante y no parámetro

`f_zoneStrength` se invoca vía `f_pushZone/f_pushZoneV` en ~20 call-sites × 3 archivos. Threadear
un parámetro rompería todos. Referenciar una constante top-level (como ya se hace con `KIND_*`)
es limpio y no viola la pureza del CORE.

## Consecuencias

- **Positivas:** el defecto queda con solución estructural lista; no altera nada hasta Fase 3;
  reversible; símbolo-agnóstico (razona sobre tipo de zona + flags de displacement).
- **Deuda / refinamiento Fase 3:** el proxy actual es por **tipo de zona + trueFvg/propulsion**.
  La versión rica (pedida por el usuario) es creditar la **secuencia SMC**:
  toque → MSS → retorno → BRK/OB + displacement → salida. Requiere un flag `reactionOrigin`
  poblado en detección; se evalúa al calibrar.
- **No cambia** ni el dibujo ni el scoring mientras `W_ZREACT=0`.

## Alternativas descartadas (S142)

- **Opción 1** (unificar nombres de etiqueta cross-familia): perdía información y el nombre del
  slot flickeaba VAC→BRK→FVG. Revertida.
- **Promoción por proximidad** (al precio / al extremo de pierna / al swing reciente): 3 anclas,
  ninguna alcanzaba el cúmulo objetivo (era mid-rango y/o mitigado). Revertida. La raíz no era
  geométrica sino de **fuerza** → de ahí W_ZREACT.

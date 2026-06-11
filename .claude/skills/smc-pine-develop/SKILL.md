---
name: smc-pine-develop
description: Desarrolla código Pine Script v6 del sistema SMC siguiendo el protocolo del proyecto - reglas SMC, naming, compilación 0 errores, validación y commit. Usar para implementar o modificar cualquier concepto en pine/.
---

# Desarrollo Pine Script SMC

## Antes de escribir código
1. Lee la definición cuantificada del concepto en docs/reglas-smc-ict.md.
   Si no existe o no tiene umbrales numéricos → DETENTE: primero se completa la
   regla (con aprobación del usuario), después se codifica.
2. Lee la sección correspondiente de docs/workplan/PINE-PLAN.md (firma de la
   función, UDT que usa, sprint al que pertenece).
3. Verifica con grep si ya existe código relacionado (no dupliques funciones).

## Reglas de código (de docs/reglas-dev.md)
- Pine v6. Un concepto = una función `f_detect<Concepto>()` — sin lógica inline.
- Prefijo SMC_ en arrays globales. Todo array acotado: tras push, shift si supera MAX.
- Eventos solo con barstate.isconfirmed. request.security siempre lookahead_off.
- Comentario por función: propósito + parámetros + retorno.
- La sección LIBRARY CORE de SMC-Visual.pine y SMC-Strategy.pine es IDÉNTICA:
  si editas el core en uno, replica el cambio exacto en el otro y corre
  scripts/check-core-sync.ps1.
- No romper las 16 alertas heredadas del base LuxAlgo.

## Ciclo por cambio
1. Implementar → 2. Compilar vía TV MCP (0 errores y 0 warnings; si no se
   resuelve al primer intento → agente pine-build-resolver) → 3. Screenshot
   EURUSD en TF relevante → 4. Validar con /smc-validator → 5. Si RECHAZADO,
   corregir y volver a 2 → 6. Commit individual:
   `feat(pine): <concepto> — <qué detecta>` o `fix(pine): ...`

## Salida esperada
Código compilando + validación APROBADA + commit. Nunca dejar un concepto a medias
entre Visual y Strategy.

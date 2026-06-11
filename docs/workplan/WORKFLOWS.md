# WORKFLOWS — Workflows Archon v2 del proyecto
> Anexo 4 del WORKPLAN-MAESTRO-V2.md | Estrategia 2.0 | 2026-06-10
> Cubre el Paso 4 del PROMPT-FABLE. El workflow custom `smc-sprint.yaml` se entrega completo; los `archon-*` default se usan tal como vienen en `.archon/workflows/defaults/`, con la adaptación SMC indicada.

**Nota de instalación:** Archon v2 se clona en Fase 0 (tarea ARCHON-01): `git clone https://github.com/coleam00/Archon .archon` y se verifica que los 18 workflows default existen. Si la estructura del repo upstream difiere de lo descrito aquí (el proyecto evoluciona), adaptar los campos del YAML al schema real del Archon instalado — la LÓGICA de los steps es lo normativo de este documento.

**Regla general:** los workflows orquestan; los agentes ejecutan; las skills definen protocolos. Cuando Archon no esté disponible o falle, cada workflow es ejecutable manualmente por Claude Code siguiendo sus steps en orden (los workflows son documentación ejecutable, no dependencia dura). `[FIX: el plan original hacía de Archon un single point of failure]`

---

## WF-01 · smc-sprint.yaml (custom) — workflow principal de Fases 1 y 2

Archivo: `.archon/workflows/smc-sprint.yaml`

```yaml
name: smc-sprint
description: >
  Ciclo completo para implementar UN concepto SMC en Pine Script:
  regla → spec → implementación → compilación → validación visual →
  aprobación humana → commit. Se ejecuta una vez por concepto del
  orden de implementación de PINE-PLAN.md §7.
version: 2.0
inputs:
  concepto: "Nombre del concepto SMC (ej: liquidity-sweep)"
  sprint: "Sprint del PINE-PLAN al que pertenece (ej: 1.3)"

steps:
  - name: check-rule
    description: Verificar que la regla del concepto existe y está cuantificada
    agent: claude-code            # supervisor
    actions:
      - leer docs/reglas-smc-ict.md sección {concepto}
      - verificar que tiene umbrales numéricos y >=3 casos de prueba con fecha
    on_fail:
      goto: write-rule
    on_pass:
      goto: spec

  - name: write-rule
    description: Completar la regla ANTES de codificar
    agent: smc-architect
    actions:
      - redactar definición cuantificada + casos de prueba
      - presentar al usuario para aprobación
    requires_human_approval: true
    output: docs/reglas-smc-ict.md (sección nueva)
    next: spec

  - name: spec
    description: Spec técnica breve de la implementación
    agent: smc-architect
    actions:
      - definir firma f_detect{Concepto}, UDT usado, arrays afectados,
        impacto en Visual (dibujo+panel) y Strategy (confluencia)
    output: spec inline (no archivo — conceptos simples no necesitan doc)
    next: implement

  - name: implement
    description: Implementación con la skill smc-pine-develop
    agent: claude-code
    skill: smc-pine-develop
    actions:
      - implementar en sección LIBRARY CORE (Visual y Strategy idénticos)
      - dibujo en Visual + fila de panel si aplica
      - compilar via TV MCP hasta 0 errores 0 warnings
        (si atasco -> agente pine-build-resolver)
    next: validate

  - name: validate
    description: Validación visual contra reglas
    agent: smc-validator-agent
    skill: smc-validator
    actions:
      - screenshots en los casos de prueba
      - score por concepto
    on_fail:                       # RECHAZADO
      max_retries: 3
      goto: implement              # loop corrección
      on_max_retries: escalate-to-human
    on_pass:
      goto: approve

  - name: approve
    description: Aprobación humana del concepto
    requires_human_approval: true
    show:
      - score de validación
      - screenshot final
      - diff del código
    on_reject:
      goto: implement
    on_pass:
      goto: commit

  - name: commit
    description: Commit individual + registro
    agent: claude-code
    actions:
      - scripts/check-core-sync.ps1 (Visual==Strategy en core)
      - git commit "feat(pine): {concepto} — validado {score}/100"
      - registrar en docs/sprint-runs/validaciones.md
    next: done
```

**Diagrama:**
```
[check-rule] ──falta──→ [write-rule (humano aprueba)] ─┐
     │ ok                                              │
     ▼                                                 ▼
  [spec] → [implement] → [validate] ──RECHAZADO×3──→ escala a humano
                ↑              │ │
                └──RECHAZADO───┘ │ APROBADO
                                 ▼
                          [approve humano] ──no──→ implement
                                 │ sí
                                 ▼
                       [check-core-sync + commit]
```

---

## WF-02 · archon-piv-loop (default) — Plan-Implement-Validate genérico
**Cuándo:** tareas que no son "un concepto SMC" (panel, alertas, refactors menores, scripts). 
**Adaptación SMC:** en el step `validate`, sustituir el test runner genérico por: compilación TV MCP (Pine) o `check-core-sync.ps1` + revisión visual. Aprobación humana siempre activada (`requires_human_approval: true` en el step final).

## WF-03 · archon-refactor-safely (default)
**Cuándo:** cambios estructurales sobre código ya validado (ej. migrar el core copiado a library formal al cerrar Fase 2 — decisión D-PINE-01; reorganizar arrays).
**Adaptación SMC:** el "test suite" que protege el refactor = re-validación de los conceptos afectados con smc-validator-agent + comparación de señales del Strategy Tester antes/después del refactor sobre el mismo periodo (deben ser **idénticas**: mismo número de trades, mismas fechas). Cualquier diferencia = el refactor cambió semántica → revertir.

## WF-04 · archon-test-loop-dag (default)
**Cuándo:** Fase 4 — loop hasta que los golden tests MQL5 pasen (el set se construye función a función durante la traducción, con casos reales extraídos de TradingView; tantos como hagan falta para cobertura).
**Adaptación SMC:** runner = script de tests MQL5 (Strategy Tester en modo matemático o script de test custom en MT5); cada test rojo genera entrada al loop con: caso fallido → mql5-translator-agent re-analiza → fix → recompilar → re-run. DAG de dependencias: Structures → Liquidity → MTF → Scoring → RiskManager (los tests de un módulo no corren hasta que su dependencia esté verde).

## WF-05 · archon-validate-pr (default)
**Cuándo:** Fase 4 — antes de cada merge a main del repo del EA.
**Adaptación SMC:** checks = compilación MetaEditor 0/0 + golden tests verdes + review de mql5-reviewer APROBADO + check-core-sync (si el cambio tocó Pine también).

## WF-06 · archon-architect (default)
**Cuándo:** inicio de Fase 4 — sweep arquitectural completo antes de traducir (verificar que el mapeo Pine→MQL5 de MQL5-PLAN §3 sigue siendo válido contra el código Pine final de Fase 3); también al inicio de Fase 2.
**Adaptación SMC:** el agente del workflow es `smc-architect`; output = MQL5-PLAN.md actualizado + ADR de arranque de fase.

## WF-07 · archon-feature-development (default)
**Cuándo:** features completos multi-archivo (ej. el panel de estado entero, el sistema de trailing del Strategy) donde smc-sprint (pensado para UN concepto) queda corto.
**Adaptación SMC:** se mantiene el flujo default (plan → branch → implement → test → PR) con: branch naming `fase-N/<feature>`, validate = compilación + smc-validator de los conceptos tocados.

---

## MATRIZ WORKFLOW ↔ FASE

| Workflow | F0 | F1 | F2 | F3 | F4 |
|---|---|---|---|---|---|
| smc-sprint | | ●●● | ●● | | |
| archon-piv-loop | ● | ● | ● | ● | ● |
| archon-refactor-safely | | ● | ● (cierre: core→library) | | ● |
| archon-test-loop-dag | | | | | ●●● |
| archon-validate-pr | | | | | ●●● |
| archon-architect | | | ● (inicio) | | ● (inicio) |
| archon-feature-development | | ● | ● | | ● |

●●● = workflow principal de la fase · ● = uso puntual

**Fallback sin Archon:** si Archon no está operativo, Claude Code ejecuta los steps del YAML manualmente en orden (este documento + el YAML son la fuente). Ningún gate de fase depende de que Archon funcione — los gates dependen de los criterios medibles del WORKPLAN §2.

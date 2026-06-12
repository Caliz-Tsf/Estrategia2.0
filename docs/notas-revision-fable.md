# Notas para revisión de Fable

> Observaciones abiertas surgidas durante el desarrollo Pine (Fases 1-3) que se
> elevan a Fable en el **gate pre-Fase 4** (revisión integral del sistema Pine
> antes de fusionar `pine/sistema-completo` → `main` y empezar el EA MQL5, ADR-003).
> No son bloqueos: son puntos donde Fable puede confirmar el enfoque o proponer
> una corrección/mejora. Cada ítem indica de qué tarea salió y por qué se dejó así.

---

## N-01 · Swings high+low en la misma vela (T02, validador 97/100)

**Tarea:** F1-S1.1-T02 — `f_detectSwings` / `f_classifySwing` (clasificación HH/HL/LH/LL).
**Fecha:** 2026-06-11 (Sesion-012).
**Estado:** dejado tal cual + comentario de invariante en el código. Pendiente visto bueno de Fable.

**Qué pasó.** El `smc-validator-agent` aprobó T02 con 97/100 y dejó una única
observación no bloqueante: en `f_classifySwing`, el caso teórico en que un swing
**high** y un swing **low** se confirman en la **misma vela `t`**.

**Por qué puede ocurrir (y por qué casi nunca).** `ta.pivothigh(5,5)` y
`ta.pivotlow(5,5)` devuelven no-`na` en la barra que confirma un pivote situado 5
velas atrás. Que ambos disparen en la misma barra implica que **la misma vela `t`
es a la vez el máximo y el mínimo estrictos de su ventana de 11 velas** (5 a cada
lado) — una vela-spike que se traga el rango de sus 10 vecinas por arriba y por
abajo. En EURUSD H1 con `swingLen=5` es prácticamente imposible.

**Por qué se dejó sin guard (análisis del supervisor).** Aunque ocurriera, el
código ya lo maneja correctamente: `f_classifySwing` **filtra por tipo**
(`sHigh == isHigh`), de modo que al clasificar el low se ignora el high recién
insertado (es de otro tipo) y se compara contra el low previo real. Los dos swings
son genuinos (esa vela realmente es techo y suelo de su ventana) y quedan anclados
en la misma `t`. Ningún concepto aguas abajo (BOS/CHoCH §1.3, MSS, EQH/EQL §Liquidez)
asume alternancia estricta high/low ni unicidad de swing por vela: todos leen por
tipo. Un guard explícito sería código muerto para un caso imposible y ya resuelto.

**Dónde quedó documentado.** Comentario `INVARIANTE [T02]` en el bloque de
`f_classifySwing` (CORE byte-idéntico en SMC-Visual / SMC-Strategy + versión
`export` en SMC-Library).

**Pregunta para Fable.** ¿Aceptás el enfoque (sin guard, con invariante
documentada) o preferís (a) un guard defensivo explícito, (b) una regla de
desempate en `docs/reglas-smc-ict.md §1.1/§1.2` para el caso spike, o (c) algo que
asegure mejor la **paridad MQL5** (Fase 4) donde el golden test debe replicar este
comportamiento función-a-función (ADR-002)?

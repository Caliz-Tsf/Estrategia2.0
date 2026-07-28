# ADRs — índice

Decisiones de arquitectura del proyecto. **Un ADR no se re-litiga**: si algo cambia, se escribe
uno nuevo que lo supersede. Los escribe `smc-architect`, nunca el doc-updater.

**Los huecos de numeración son intencionales y están explicados abajo.** Antes de dar un ADR por
perdido, mira esta tabla.

| # | Título | Estado |
|---|---|---|
| [001](ADR-001-multisimbolo-sin-filtro-horario.md) | Bot multi-símbolo, sin filtro horario duro | Aceptado |
| [002](ADR-002-cierre-gate-ver-09.md) | Cierre del gate VER-09: revisión integral de Fable pre-Pine | Aceptado |
| [003](ADR-003-estrategia-de-ramas.md) | Estrategia de ramas: dos ramas largas, una por gran etapa | Aceptado · *fichero escrito en S147, decisión de S010* |
| [004](ADR-004-escala-estructura-dominante.md) | Escala de estructura DOMINANTE (swing 50), capa aditiva | Aceptado |
| [005](ADR-005-enjambre-laboratorio-no-runtime-ea.md) | El enjambre es laboratorio + copiloto, NO runtime del EA | Aceptado |
| [006](ADR-006-pools-persistentes-ciclo-de-vida.md) | Pools de liquidez PERSISTENTES con ciclo de vida | Aceptado |
| [007](ADR-007-ea-razona-confluencias-enjambre-continuo.md) | El EA razona confluencias + enjambre continuo | Aceptado |
| [008](ADR-008-mapa-mtf-confluencias-pared-dura.md) | Mapa MTF rico + motor confluencia→entrada; pared dura EA↔laboratorio | Aceptado |
| [009](ADR-009-transporte-mtf-buffer-generico-etiquetado.md) | Transporte MTF: buffer genérico etiquetado por `kind` | Aceptado · **superseded por 010** |
| [010](ADR-010-mtf-dibujo-geometrico-anclado.md) | Mapa MTF geométrico: anclaje temporal + dibujo nativo | Aceptado |
| [011](ADR-011-smt-simbolo-correlacionado.md) | SMT Divergence: símbolo correlacionado como input por perfil | Aceptado |
| [012](ADR-012-protocolo-razonamiento-agente.md) | Protocolo de razonamiento del agente: snapshot + auto-preguntas | Aceptado |
| [013](ADR-013-confluencia-exponencial-multiplicador.md) | Confluencia exponencial de Gradient Levels = multiplicador | Aceptado · *wiring diferido a Fase 2* |
| [014](ADR-014-strength-propiedad-de-deteccion-en-core.md) | `strength` es propiedad de DETECCIÓN (vive en el CORE) | Aceptado |
| **015** | *«minRR parametrizado»* | ⬜ **RESERVADO, NO ESCRITO — no es un fichero perdido.** Ver nota abajo. |
| [016](ADR-016-retencion-zonas-por-importancia.md) | Retención de zonas por IMPORTANCIA, no por antigüedad | Aceptada |
| [017](ADR-017-consumidor-visual-auxiliar-context.md) | Tercer consumidor visual auxiliar `SMC-Context.pine` | Aceptada |
| [018](ADR-018-promocion-extremos-htf-al-core.md) | Promoción de los extremos HTF al CORE (cierra Fase B de 017) | Aceptada |
| [019](ADR-019-retencion-swings-por-importancia-rol-pegajoso.md) | Swings: capa única leg-based + jerarquía dim-to-focus | Aceptada |
| [020](ADR-020-dieta-tokens-core-funciones-un-consumidor.md) | Dieta de tokens del CORE: funciones de-un-solo-consumidor fuera | Aceptada |
| [021](ADR-021-dealing-range-segundo-extremo-estructural.md) | El dealing range es el 2.º extremo estructural por temporalidad | Aceptada |
| [022](ADR-022-extremes-core-bloque-compartido-strategy-context.md) | `EXTREMES CORE`: 2.º bloque byte-idéntico Strategy + Context | Aceptada |
| [023](ADR-023-lectura-del-panel-desde-el-tf-mas-bajo.md) | El defecto chart-TF se acota por REGLA DE OPERACIÓN, cero código | Aceptada |
| [024](ADR-024-reparto-del-dibujo-visual-context.md) | Reparto del dibujo Visual/Context por call-site | 🔴 **PREMISA REFUTADA (S139) — NO EJECUTADA** |
| [025](ADR-025-credito-origen-de-reaccion-strength.md) | Crédito de origen de reacción en la fuerza de zonas (W_ZREACT) | Aceptado (hook latente, peso 0 hasta Fase 3) |
| [026](ADR-026-dol-escalera-y-marcador-de-borde.md) | DOL: escalera de draw-on-liquidity + marcador de borde | ✅ Aceptado **e implementado** (S145) |
| [027](ADR-027-tramo-vela-a-vela-familia-liquidez.md) | El tramo vela→vela de la familia Liquidez | 🟡 **PROPUESTO** — se implementa en S148 |

## Huecos de numeración

- **ADR-015 «minRR parametrizado» — reservado a propósito, nunca escrito.** Nació *propuesto* en
  S098 al resolver la contradicción entre el pitch 1:2 de NSL y la regla dura #5 (R:R mínimo
  1:3): se fijó que **el gate `minRR` con default 3.0 es mandatorio**, y que el usuario puede
  bajarlo a 1:2 (laboratorio) o subirlo a 1:5 **solo por orden explícita**, momento en el cual
  **se redacta el ADR-015**. Mientras nadie ordene ese cambio, el ADR no debe existir: su
  ausencia *es* el estado correcto. Ver `memory/sesiones/Sesion-098.md:140-141` y
  `docs/planes/ESQUELETO-FABLE-fase4-ea-mt5.md:236`.

## Nota de mantenimiento (S147)

ADR-003 se citaba como vigente en 8 documentos sin tener fichero (verificado: ningún commit lo
añadió nunca). Se transcribió desde el texto literal que sobrevivía en `ESTADO-ACTUAL.md`, sin
inventar las alternativas descartadas, que **no quedaron registradas**. Cuando escribas un ADR
nuevo, **añade su fila aquí**: esta tabla es el único sitio donde un hueco se distingue de una
pérdida.

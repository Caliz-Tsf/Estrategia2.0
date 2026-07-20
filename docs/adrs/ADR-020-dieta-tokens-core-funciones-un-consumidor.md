# ADR-020 — Dieta de tokens del CORE: sacar funciones de-un-solo-consumidor del bloque byte-idéntico

> ## 🔴 PREMISA CUESTIONADA POR MEDICIÓN — leer antes de actuar sobre este ADR *(S135, 2026-07-18)*
>
> Este ADR afirma abajo que **"las funciones no-llamadas SÍ cuentan tokens en Pine"**. En S135 se
> midió **lo contrario**, tres veces y con el mismo número exacto (107986): quitar 101 líneas de
> funciones sin call-site → **0 tokens**; añadir 590 líneas de funciones duplicadas sin llamar →
> **0 tokens**. ⇒ **Pine hace tree-shaking completo de las funciones sin call-site.** Concuerda con
> lo que S121 ya había medido ("la dieta S120 fue no-op").
>
> **NO SE REVOCA ESTE ADR AÚN:** queda sin explicar por qué la dieta pareció funcionar en S120 y por
> qué el fix de **ADR-022** resolvió el `CE10117`. Está entregado a Fable para auditoría
> adversarial: `docs/planes/DOSSIER-FABLE-capacidad-y-codigo-muerto-S135.md` §2.1.
>
> **Mientras tanto:** no planifiques ahorro de tokens retirando código muerto — **medido, no ahorra
> nada**. La formulación provisional correcta es *"solo retirar código **que se ejecuta** ahorra"*.
> La separación de bloques que este ADR introdujo sigue siendo válida por **mantenibilidad**;
> lo que está en duda es su justificación **por tokens**.

- **Fecha:** 2026-07-13 (Sesion-120)
- **Estado:** **ACEPTADA** — ejecutada y verificada en vivo (S120). SHA del CORE re-baselined
  `d86bf37aacbd25cf` → **`752b4083a7db419d`** (CORE **1952 → 1866 líneas**).
- **Precisa (no contradice):** regla dura #2 (CORE byte-idéntico entre Visual/Strategy/Context —
  **se mantiene**; solo cambia *qué* funciones viven dentro). ADR-018 (promoción de extremos al CORE
  — intacta). No cambia ninguna definición SMC (§1–§7) ni la calibración del scoring (ADR-002).

## Contexto

Al reaplicar el Visual **committed de S119 en una instancia fresca** saltó `CE10117`:
`Compiled code contains too many tokens: 100819. The limit is 100256`. El baseline S119 estaba
**~563 tokens sobre el techo** del compilador de TradingView y **no podía aplicar** — las
"validaciones vivas" de S117–S119 se hicieron contra **instancias cacheadas viejas** (GOTCHA
recurrente: guardar el slot no refresca la instancia pinneada), que sí cabían, enmascarando que el
código base cruzó el techo.

**Causa raíz.** El CORE byte-idéntico (regla dura #2) obliga a **cada consumidor** a cargar TODAS
las funciones del CORE, aunque no las use. **Las funciones no-llamadas SÍ cuentan tokens** en Pine
(confirmado empíricamente en S120). El Visual, el consumidor más grande, cargaba funciones que solo
usa Strategy/Context → bloat que solo a él lo revienta.

## Decisión

Poner el CORE a dieta **sin borrar nada funcionando** (dos guardrails: verificar no-uso antes de
sacar, verificar sin referencias colgadas después):

1. **Borrar 5 funciones muertas en los 3 consumidores** (cero call-sites en Visual/Strategy/Context,
   verificado por grep): `f_pushPool`, `f_projStdDev`, `f_gradientZone`,
   `f_gradientConfluenceBonus`, `f_buildPools` (legacy reemplazadas: los pools usan `f_upsertPool`;
   el gradient usa otras). Removidas idénticamente del CORE en los 3 + de `SMC-Library.pine`.
2. **Mover `f_detectVolumeImbalance` FUERA del CORE** → a sección **Strategy-local** (único
   consumidor real, `SMC-Strategy.pine`; Visual/Context nunca la llaman). El CORE compartido deja de
   cargarla; Strategy la define debajo del bloque `// === LIBRARY CORE ===`.

**Regla que sienta:** una función que **un solo consumidor** usa **no pertenece al CORE compartido**;
vive local en ese consumidor. El CORE es para lógica que ≥2 consumidores comparten.

## Consecuencias

- **CORE byte-idéntico ×3 se mantiene** (regla dura #2): las 6 funciones se removieron idénticas de
  los 3; la VI re-insertada en Strategy queda **fuera** del bloque comparado → `check-core-sync` OK,
  SHA re-baselined `752b4083a7db419d` (1866 líneas).
- **Visual bajo el techo:** compila y **aplica en vivo sin CE10117**, renderiza y actualiza con el
  precio. Los 3 consumidores compilan 0/0 server-side.
- **Headroom recuperado** (~2–3k tokens; `f_buildPools` sola eran 51 líneas con doble loop + arrays)
  → **desbloquea la curación visual F1** de la familia OB+FVG, que requería espacio de tokens.
- **MQL5 (Fase 4):** las 5 borradas no tenían golden test (muertas); VI es un módulo Strategy →
  su golden test vive con el motor de scoring, no con el CORE compartido. Sin impacto en paridad.
- **Reversible:** las funciones borradas siguen en el historial git (y `f_projStdDev`/VI en
  `SMC-Library.pine` como referencia si se re-cablean en Fase 3).

## Alternativas descartadas

- **Borrar código funcionando (drawers/paneles):** viola la instrucción explícita del usuario y
  perdería concepto validado.
- **Reducir solo comentarios:** los comentarios **no cuentan tokens** en Pine → cero efecto.
- **Romper la regla dura #2** (CORE distinto por consumidor): rompería single-source-of-truth y la
  traducción MQL5. La dieta mantiene la regla; solo mueve funciones de-un-consumidor a su consumidor.

---

## ANEXO S136 — la justificación por TOKENS cae; la decisión SE MANTIENE

**Medido en S136 sobre los artefactos exactos del episodio** (`aee69a7` vs `f91a2bd`, que difieren
en exactamente las 139 líneas, verificado +139/−0), con la **regla del lastre desplazado**:

| Build | Lastre | Tokens | Timestamp |
|---|---|---|---|
| A = `aee69a7:pine/SMC-Visual.pine` (CON el muerto) | 305 | **108071** | 00:32:43 |
| B = `f91a2bd:pine/SMC-Visual.pine` (SIN el muerto) | 300 | **107929** | 00:35:43 |
| | | **ΔT = 142** | |

Predicciones **pre-registradas** (`docs/planes/RESPUESTA-FABLE-S135.md` §2.3): 130-150 si el muerto
cuesta cero; 830-850 si costaba. Salió **142** ⇒ rama 1, con la rama 2 excluida por factor ~6. Los
142 son las 5 unidades extra de lastre (~28 tokens/unidad).

⇒ **Las 139 líneas muertas costaban CERO tokens. Pine tree-shakea lo que no se llama.** El build
"100952" que motivó esta dieta fue **fantasma** (lectura de consola contaminada — mismo patrón que
S120 y S133). El "headroom recuperado ~2-3k tokens" que declara la sección de consecuencias
**no ocurrió**.

**La regla provisional queda sustituida por:** *solo retirar código que se **EJECUTA** ahorra
tokens.*

**NO se revoca la ADR.** La decisión arquitectónica (funciones de-un-consumidor viven en su
consumidor) se sostiene por **mantenibilidad y claridad de propiedad**, que nunca dependieron del
conteo de tokens.

**Matiz añadido por el usuario (S136), no medido todavía:** "cero tokens" **no es** "cero coste" —
el compilador igual **parsea** lo que luego tree-shakea, así que el muerto pesa en
compilación/carga (no en runtime). Los tiempos observados en S136 fueron planos (~70s entre 4982 y
5435 líneas) pero el rango es demasiado estrecho para concluir. Pendiente: ablación grande
cronometrada.

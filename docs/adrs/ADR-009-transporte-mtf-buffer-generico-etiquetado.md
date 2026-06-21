# ADR-009 — Transporte MTF: buffer genérico etiquetado por `kind` (en vez de slots fijos por concepto)

- **Fecha:** 2026-06-20 (Sesion-041)
- **Estado:** Aceptado
- **Precisa (no contradice):** ADR-008 §4 (mapa MTF rico) y `ESQUELETO-P3 §2.2/§2.4`. **Reemplaza** el mecanismo de transporte allí bosquejado ("N slots fijos por concepto: OB(N×2×5)+FVG(N×2×5)+pool(N×2×4)") por un **buffer genérico etiquetado**. El resto de ADR-008 (cascada, pared dura, paridad MQL5) queda intacto.
- **Tarea:** F1-S1.4-T13b (mapa MTF rico). Origen de la discusión: Freddy, S041.

## Contexto

T13a dejó el transporte de **escalares** por TF resuelto (`f_computeTFState` → tuple de 17 números vía `request.security`, estado `var` interno por-contexto, spike R-P3-1 ✅ S039). T13b debe traer además las **zonas/eventos activos** de cada HTF (OB, FVG, pools, sweep…) en cascada D1→{H1,M5}, H1→{M5}.

`ESQUELETO-P3 §2.2` proponía **reservar ranuras fijas por concepto** en el tuple (p. ej. 3 OB + 3 FVG + 3 pools por lado). Al revisar el alcance real con Freddy aparecieron dos problemas de esa vía:

1. **No escala a los ~50-60 conceptos.** La fuente de verdad `reglas-smc-ict.md` tiene hoy **24 conceptos** (§1:6 · §2:8 · §3:7 · §4:3+); con el gap ICT (T26–T40 de `ESQUELETO-P1`) + variantes se llega a ~50-60. Reservar slots fijos por **cada** concepto rompe el límite del tuple de `request.security` (~127 números en v6) muchas veces, aunque **nunca se activen todos a la vez en una misma foto**.
2. **El caso de uso real es "lo que esté pasando, sea lo que sea".** Freddy: *"si en D1 veo que sucedió un barrido, se desplazó el precio y dejó un FVG, y quiero/necesito entrar en ese FVG, necesito verlo en M5"* + *"ver el OB nativo de H1 al que el precio retrocede y las próximas 2 zonas OB que podría tocar más abajo"*. No es "siempre estos 3 conceptos": es **los pocos hechos relevantes activos del momento**, de cualquier concepto.

## Decisión

**El mapa rico de cada HTF viaja como un buffer GENÉRICO de `K` ranuras de tamaño fijo, donde cada ranura lleva una etiqueta `kind`** que identifica de qué concepto es. No se reserva cupo por concepto en el tuple.

### Contrato de la ranura (canónico — replicar en MQL5 `SMC_MTF.mqh`, Fase 4)

```
ranura_i = [ kind, top, bottom, dir ]   // 4 números
  kind   : int (KIND_OB / KIND_FVG / KIND_POOL / KIND_SWEEP / … ; 0 = ranura vacía)
  top    : float (nivel superior; para puntos top==bottom==level)
  bottom : float (nivel inferior)
  dir    : int (DIR_BULL / DIR_BEAR; en pools = BSL/SSL)
```

El tuple de `f_computeTFState` = **17 escalares (T13a) + K ranuras × 4**. Con **K=16** → `17 + 64 = 81 < ~127` (holgado; límite empírico a confirmar al compilar, R-2). **1 sola llamada `security`/TF**. Se omite `barTime`: las zonas HTF se dibujan como niveles de referencia extendidos al borde actual (no ancladas a su barra de origen), así que la marca temporal no se usa en T13b; MQL5 puede añadirla en Fase 4 si la necesita.

### Selección de qué entra en las K ranuras (productor, dentro de `f_computeTFState`)

1. Se corre la detección de cada concepto **en el contexto del HTF** con estado `var` **interno** a la función (R-P3-1, no contamina el chart).
2. Por cada concepto **habilitado para traspaso** (toggle de settings), se toman sus **N más cercanos al precio** (cap por concepto, 0-10), filtrando **no mitigados / no barridos**.
3. Se fusionan todos los candidatos, se ordenan por **cercanía al precio** y se quedan las **K globales** más cercanas. El resto de ranuras van vacías (`kind=0`).
4. **Mitigación dinámica:** una zona mitigada/barrida deja de pasar el filtro → la siguiente más cercana ocupa su lugar **automáticamente** (sin lógica de "recalcular"; es consecuencia del filtro + orden).

### Consumidor

Recibe las K ranuras, lee el `kind` de cada una y la **reconstituye + dibuja con el estilo de su concepto** (caja OB/FVG, línea pool…) con prefijo `D1:`/`H1:` y estilo tenue/punteado (cascada, ADR-008 §4). Cuota de objetos de dibujo por (concepto × TF) + Present mode (R-3).

### Extensibilidad (el porqué de todo esto)

Cuando Sprint 1.5/1.6 añadan conceptos (breaker, BPR, IDM, gaps…), **solo hacen `push` al mismo buffer** con su `kind`. **La llamada `security` y el contrato del tuple NO cambian.** Hoy se pueblan solo los conceptos detectados (**OB, FVG, pools, sweep**); el mecanismo ya es el definitivo.

### Cupo: 1 llamada ahora, 2ª preparada

Se implementa **1 llamada/TF (K=16)**. El código se estructura para activar una **2ª llamada/TF** (≈ K=32) sin refactor si en Fase 3 falta densidad HTF. No se paga el 2× de cómputo antes de que existan conceptos que llenen las ranuras (regla #8, no sobre-construir).

## Alternativas descartadas

- **Slots fijos por concepto (`ESQUELETO-P3 §2.2` original):** no escala a 50-60 conceptos; desperdicia presupuesto en conceptos inactivos. Descartada.
- **Traer todo y filtrar en el consumidor:** imposible, `security` no transporta arrays/UDTs (`PINE-PLAN §4`). El filtrado/selección **debe** ocurrir en el productor (contexto HTF) antes de aplanar.
- **Selección por recencia (tiempo) en vez de por precio:** se discutió; para un **mapa de entrada** la cercanía al precio es lo correcto ("las 2 OB que el precio podría tocar"). La recencia queda como criterio del *selector de POI* sólo si hace falta (Fase 2). Para T13b: **cercanía al precio**.
- **K=25-32 en 1 llamada:** no cabe junto a los 17 escalares bajo ~127. Para más densidad → 2 llamadas/TF (preparado, no activado).

## Consecuencias

- **`f_computeTFState` crece:** además de los escalares (T13a) corre internamente OB/FVG/pool/sweep y emite las K ranuras. Sigue en el **CORE byte-idéntico** (regla #2) + `export` en Library; SHA y nº de líneas cambian (esperado, documentado en el commit). Es el refactor que ADR-007/008 anticipaban como **adelanto de Fase 4** (`SMC_MTF.mqh`).
- **Nueva función CORE `f_nearestN`** (pura): generaliza las de presentación `f_pNearZone`/`f_pNearPool` (que devuelven 1) a devolver los N más cercanos por concepto/dirección, con filtro de calidad. Va al CORE porque la usa el transporte (paridad MQL5).
- **Settings nuevos (`GRP_MTF`):** toggle de traspaso por concepto + cap por concepto (0-10) + densidad. Agrupados por TF para no explotar el panel de ajustes (R-6).
- **Paridad MQL5:** el contrato de la ranura es el formato canónico que `SMC_MTF.mqh` replicará en Fase 4 (un array de structs `{kind,top,bottom,dir,barTime}` en MQL5).
- **`ESQUELETO-P3 §2.2/§2.4` queda superado** en el mecanismo de transporte por este ADR; el resto del documento (cascada, presupuesto de objetos, motor confluencia→entrada §3) sigue vigente.

## Documentos relacionados

- `docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md` §2 (mapa MTF) — mecanismo de transporte superado por este ADR.
- `docs/sprint-runs/spec-T13a-mtf-nucleo.md` (escalares, base de T13b).
- `docs/sprint-runs/spike-R-P3-1.md` (no-contaminación de estado por-contexto, ✅ S039).
- ADR-007 (EA razona + refactor Pine), ADR-008 (mapa MTF + pared dura).
- `docs/workplan/PINE-PLAN.md` §4 (MTF) / §5 (dibujo/presupuesto) / §7 (Sprint 1.4).

# Sesión 143 — 2026-07-23

## Objetivo con el que arrancó
Cerrar pendientes de S142 (BRK, IPR, deuda weekend-safe FVG) y — surgido en sesión — el solape
de nombres de etiquetas de zona.

## Rama
`pine/sistema-completo`

## Commits (1)
- `877d543` fix(pine-visual) — S143 escalonado X de etiquetas por kind (anti-solape cross-kind).

check-core-sync OK ×3 (LIBRARY CORE SHA `7ad95b3e612d041a`, 1783 líneas, SIN cambios vs S142.
EXTREMES CORE SHA `5f851d87e5fda720`). Sin tag (F1-GATE sigue sin firmar).

## Lo que quedó / fix aplicado

**1. BRK top-vs-high (6-ene-21):** APROBADO por el usuario como correcto (no era bug; una zona
bajista mitiga solo si la mecha llega al `top`). Pendiente cerrado.

**2. IPR — verificación visual:** confirmado que NO está roto (no apagado, no mal cableado, no
mal escrito). Evidencia: `i_showIPR` default true (:93); panel muestra modo "Todo" (IPR requiere
FAM_TODO); `f_densOK(0.0, false)` en Todo = true (densMin=0), la puerta de dibujo pasa;
`f_detectIPR` (:827-851) tiene lógica sana y capaz de devolver no-na. NO hay IPR vivo en 5
configuraciones probadas (EURUSD 1D/H1/M15/M5 + BTCUSD M5). El único bloqueante es
`currentIpr==na`: la condición de PUREZA (≥3 FVG vivos de un lado y CERO del opuesto en 10
velas) casi nunca se cumple en el borde vivo porque el detector dispara FVG en ambos sentidos.
Hallazgo: el IPR-como-calibrado (minGaps=3, window=10, pureza estricta) prácticamente nunca
enciende en vivo → candidato de revisión en Fase 3. DECISIÓN: verificación visual DIFERIDA a que
aparezca un IPR natural. Replay es de pago (no disponible).

**3. Solape de NOMBRES de etiquetas** (defecto nuevo hallado por el usuario en H1 y M5): dos
causas — (a) OB↔MB (kinds distintos, misma familia OB) por el bypass de promoción por
confluencia (`mbCfg>=2` / band-pick / ancla) que saltea `blockSeenY` en la ETIQUETA; (b)
IFVG/FVG·g ↔ OB (cross-family) por acumuladores independientes `fvgFamSeenY` vs `blockSeenY`
(decisión deliberada de S142). Requisito del usuario: arreglar SIN perder ningún nombre y sin
montarlos.

FIX implementado: helper nuevo `f_lblX(oT, f)` (:3422, Visual-only, cerca de `f_zLbl` :3415) —
X del label = fracción `f` del ancho origen->ahora, propia de cada kind, SIEMPRE en [0.5, 0.92]
(mitad derecha) => cada kind en su carril, dentro de su caja, sin eyección. Fracciones (verificadas
en el código): OB=0.50, MB=0.56, BRK=0.62, VAC=0.68, FVG=0.74, IFVG=0.80, BPR=0.86, OTE=0.92.
Conserva los 8 nombres, cero solape. El helper absorbe el `math.round` del punto medio repetido en
los 8 sitios de push de label => refactor ~token-neutral (compiló dentro del budget ~21-39
headroom, ver S136/S138). GOTCHA de método: el 1er intento usó offset en VELAS ABSOLUTAS
(`lane*barMs`) y en cajas angostas (recientes) eyectaba la etiqueta fuera de la caja por la
izquierda; corregido a fracción del ancho. Validado visualmente en H1 y M5 (EURUSD): etiquetas
legibles, dentro de caja, sin pisarse.

## Diagnósticos (sin código)
- **Aclaración de mitigación** (pregunta del usuario): los IFVG ámbar de una pierna alcista son
  BAJISTAS (invertidos de FVG alcistas que se invalidaron por cierre a través). Una zona bajista
  (supply) mitiga solo cuando el precio SUBE y la mecha alcanza su top (`high>=top`), o invalida
  si una vela cierra sobre el top. Si el precio cae y la deja por debajo (`high<bottom`), ninguna
  condición dispara → queda ACTIVA (correcto, no es bug). Excepción: una zona verde/alcista que
  cierra bajo su bottom → invalida (estado 3, renace breaker/IFVG).
- **Deuda anclaje weekend-safe FVG (CORE):** sigue PARQUEADA (cosmética de borde izquierdo; el
  fix limpio alinearía el productor nativo a `time[1]` como el transporte MTF :1727, pero es
  cambio en CORE byte-idéntico ×3, caro con el budget justo). Se resuelve la próxima vez que se
  abra el CORE de verdad, o en Fase 3.
- **W_ZREACT (ADR-025):** calibrar en Fase 3 (IS/OOS).

## Gotchas de método (S143)
- Offset por velas absolutas eyecta labels de cajas angostas; corregido a fracción del ancho
  origen->ahora, siempre en la mitad derecha [0.5, 0.92].
- TV Desktop se cayó y se relanzó con `tv_launch` (2 veces en la sesión).

## Siguiente
- Familia de zonas / curación de etiquetas: cerrada con el escalonado por kind (8 carriles fijos).
- IPR: pendiente verificación visual cuando aparezca un IPR natural en vivo; revisión de calibración
  candidata en Fase 3.
- Deuda anclaje weekend-safe FVG (CORE): pospuesta a próxima apertura real del CORE o Fase 3.
- W_ZREACT (ADR-025): calibrar en Fase 3 (IS/OOS).

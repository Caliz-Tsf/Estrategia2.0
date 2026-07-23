# Sesión 142 — 2026-07-23

## Objetivo con el que arrancó
Tarea 6 de S141: comparación FVG vs OB (¿unificar `fvgFamSeenY` con `blockSeenY`?) + revisión
en modo Operación + IPR. En paralelo, revisar los canales de los 3 mentores (Profittrading /
TJ Trading / Fedex) por videos nuevos.

## Rama
`pine/sistema-completo`

## Commits (2)
- `6726fb6` docs(mentores) — COMANDOS-profittrading Scalping 6→14 (revisión de canales).
- `5ccd7ff` feat(pine) — mitigados en blanco + W_ZREACT (crédito origen-de-reacción, off).

check-core-sync OK ×3 (LIBRARY CORE SHA `7ad95b3e612d041a`, 1783 líneas; EXTREMES CORE
`5f851d87e5fda720`). Sin tag (F1-GATE sigue sin firmar).

## Revisión de canales (mentores)
Chequeo `yt-dlp --flat-playlist` de las 14 playlists. **Única con novedad: Profittrading
"Scalping 1min" 6→14 (+8 nuevos).** Todas las MADRE (Profittrading 18, TJ 17, Fedex 50) y los
agregados SMC núcleo intactos. Actualizado COMANDOS-profittrading (re-loteo 3 tandas).

## Lo que QUEDÓ (2 cambios kept)
1. **Mitigados en blanco suave (72).** `f_mitBorder` gris→blanco; helper nuevo `f_zLblCol`
   (nombre de zona blanco si mitigada, si no color de familia atenuado por edad). Solo dibujo
   Visual. Aprobado por el usuario.
2. **W_ZREACT (=0.0, INERTE) — ADR-025.** Crédito candidato Fase 3 en `f_zoneStrength` (CORE ×3)
   que credita el ORIGEN DE REACCIÓN/DISPLACEMENT (OB/Breaker/MB o FVG trueFvg/propulsion). Off
   por default → cero regresión. Resuelve la causa raíz (abajo).

## Lo que se REVIRTIÓ (probado y descartado en vivo)
- **Opción 1** (unificar nombres de etiqueta cross-familia OB↔FVG en un solo `blockSeenY`,
  cediendo el nombre aun forzado): **pierde información** y el nombre del slot **flickea**
  VAC→BRK→FVG según qué zona gana. El usuario prefiere cada caja con su nombre.
- **Promoción por proximidad en Operación** (3 anclas probadas por ablación con censo):
  al **precio actual**, al **extremo de pierna** (`legExtHi/legExtLo` ≈ 0.95/1.51, dominante),
  y al **swing reciente** (`structSwing`). **Ninguna** alcanzaba el cúmulo objetivo — porque
  ese cúmulo era **mid-rango y/o mitigado**, no un problema geométrico.

## Diagnósticos (sin código)
- **BRK "con relleno" no es bug.** `f_updateZoneMitigation` (CORE :657): zona bajista queda
  MITIGATED (sin relleno) solo si la **mecha llega al `top`** (se llena completa); toque-y-rechazo
  abajo = PARCIAL (conserva relleno); INVALID solo por **cierre** sobre el protector. "Tocar" ≠
  "mitigar". Lever si se quiere por cierre: `i_obMitClose=true`.
- **Zonas 2021 (FVG jun / IFVG may / OB 25-may ~1.21):** no están perdidas — viven en
  **Estudio/Todo**; Operación (solo Primario) las oculta por diseño (ADR-002).
- **CAUSA RAÍZ (el hallazgo de la sesión):** `f_zoneStrength` **no acredita la reacción que la
  zona generó**; y al alejarse el precio la zona **pierde el término de cercanía** → un FVG que
  provocó una caída de días cae a Secundario. → motivó W_ZREACT (ADR-025).

## Gotchas de método (S142)
- **`in_N` de `indicator_set_inputs` se corren:** conté `i_densidad`=in_118 por grep estrecho,
  pero un `input.symbol` (línea 149) no capturado la corría a **in_119**; meter "Operación" en
  el input equivocado (i_maxShowSMT) tiró **"Internal server study error"** (rojo). Recontar con
  patrón amplio antes de setear.
- **Censo redondea a 2 decimales** y `data_get_ohlcv` solo trae barras **recientes** → verificación
  sub-pip de casos históricos (2018/2021) bloqueada por herramientas; se responde por el modelo.
- **Auto-scale vertical** imposible de acotar mientras las zonas abarcan 0.9–1.6 (extienden a
  la barra actual) → usar censo, no zoom.
- TV se cayó una vez a mitad de sesión; relanzado con `tv_launch`.

## Siguiente
- Tarea 6 cerrada como **decisión de diseño** (no unificar nombres; Operación queda lean).
- Pendiente si el usuario quiere: verificar el caso puntual del BRK con sus 2 números (top vs
  high 6-ene-21). Verificación visual de IPR cuando aparezca uno activo. Deuda anclaje
  weekend-safe FVG (CORE) sigue pospuesta.
- W_ZREACT: calibrar en Fase 3 (IS/OOS) y refinar el proxy a la secuencia SMC completa.

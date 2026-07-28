# Sesión 147 — El arranque de sesión estaba roto: ESTADO-ACTUAL rota en vez de acumular

- **Fecha:** 2026-07-28
- **Rama:** `pine/sistema-completo`
- **CORE:** INTACTO — 1809 líneas, SHA `5e21ca38b43cf0e4`. `check-core-sync` OK ×3 + EXTREMES CORE OK (ADR-022). **Cero cambios en Pine esta sesión.**
- **Tipo:** infraestructura documental / proceso. NO se tocó código del sistema.

## Objetivo con el que arrancó

Ejecutar el plan de S147 acordado al cierre de S146 (medir coste en objetos del tramo
ADR-027 → implementar por subconjuntos → verificar grab en H1/M5 → retomar curación de
Liquidez). **No se llegó a arrancar:** al leer `memory/ESTADO-ACTUAL.md`, el paso 1
BLOQUEANTE del protocolo de arranque, el tool `Read` falló. El usuario preguntó por qué,
y por qué también había fallado en la sesión anterior.

## Resultado 1 — dos defectos, y el del tamaño era el menor

**(a) TAMAÑO.** `ESTADO-ACTUAL.md` pesaba **291.219 bytes**; el tool `Read` del agente
corta en **262.144** (256 KB). Medido el crecimiento en `git log`: cruzó el límite entre el
**2026-07-18 (254.164 B)** y el **2026-07-20 (259.423 B)** — es decir, desde ~S140 **ningún
arranque de sesión pudo leer el estado**. Ritmo ~5 KB por sesión.

Causa: el archivo apilaba un párrafo por sesión desde **Sesion-017**, en **tres series
superpuestas** que coexistían sin saberlo:
- `- **Fase (SNNN) — tarea anterior:**` (18 entradas, S127→S146)
- `- **Última tarea (Sesion-NNN)**` (~45 entradas, S077→S133)
- `*Sesion-NNN (fecha):*` (~30 entradas, S017→S060)

Además había duplicados dentro de la misma serie (S100 en dos líneas, S095 en dos) y el
párrafo de la fase actual llevaba **4.685 caracteres** de historial embebido dentro de la
propia línea como `<!-- historial S145: -->` — acumulación disfrazada de reemplazo.

**(b) FRESCURA — el defecto grave.** La sección «Cómo arrancar la próxima sesión» llevaba
**congelada en S090 durante 56 sesiones**. Aunque el archivo se hubiera podido leer, decía
arrancar el Paso 9 del Eje 2 y elegir entre «Opción A / Opción B» de S058, más pendientes
muertos (enjambre S074, descarga BOXXO, reinicio de MCPs). Se apilaba en vez de
reemplazarse, igual que el resto.

## Resultado 2 — causa raíz en el agente, no en el archivo

`.claude/agents/smc-doc-updater.md`, regla de cierre:

> «Nunca borres historial; ESTADO-ACTUAL se sobreescribe, las sesiones se acumulan.»

Ambigua: mezcla dos archivos con políticas opuestas en una frase. En la práctica el agente
apiló. El histórico ya vivía completo en `memory/sesiones/` (133 ficheros), así que la
acumulación en el estado era **duplicación pura**, no respaldo.

## Resultado 3 — la poda, verificando que nada se pierde

Antes de podar se cruzaron las sesiones citadas en el estado contra `memory/sesiones/`:
**6 no tenían fichero propio** — su único registro vivía en el estado. Rescatadas
**verbatim** a `Sesion-061/067/068/070/071/115.md` antes de borrar nada. Post-poda,
re-cruzado contra el backup: solo quedan `Sesion-010` y `Sesion-049`, y ambas son menciones
en prosa sin párrafo propio. **Nada perdido.**

`ESTADO-ACTUAL.md` reescrito reutilizando las líneas vivas **verbatim vía `sed`** (no
re-tecleadas, para no introducir errores de transcripción): estado + ventana rodante de 3
sesiones + arranque real + decisiones vigentes + notas de herramientas.
**291.219 → 12.381 bytes (4,2 % del original).** Backup del original en el scratchpad de la
sesión, y en git de todas formas.

## Resultado 4 — que no vuelva a pasar

- **`smc-doc-updater` — REGLA ABSOLUTA 3 «ESTADO-ACTUAL rota, no acumula»:** reemplazo del
  párrafo de fase actual (prohibido el `<!-- historial -->` embebido), ventana rodante de
  exactamente 3, reescritura completa de la sección de arranque con el número de sesión en
  el título como comprobación, techo de 40 KB verificado con `wc -c` antes de guardar, y
  obligación de confirmar que existe el `Sesion-NNN.md` **antes** de podar un párrafo.
  Incluye la medición del daño como justificación, para que no se re-litigue como estilo.
  Corregida la regla ambigua original.
- **`smc-session-startup` — guardarraíl:** mide el archivo **antes** de leerlo (40 KB ⚠️ /
  256 KB ❌ bloqueante) y comprueba que el título del arranque nombra la sesión que empieza.
  Si se degrada otra vez, salta solo en el paso 1.
- Las reglas de mantenimiento quedan además **en la cabecera del propio ESTADO-ACTUAL**,
  para que quien lo escriba las lea sin depender de recordar el agente.

## Método — lo que hizo que esto se resolviera y no se parcheara

El usuario preguntó **«¿por qué tienes errores?»** en vez de aceptar el fallo. Medir el
archivo (`wc -c`, longitud por línea, tamaño por commit en `git log`) convirtió «el Read
falla» en «cruzó 256 KB el 20 de julio». Y **leer el archivo entero antes de podar** —no
solo la cabecera— fue lo que destapó el defecto de frescura, que era el caro y que nadie
buscaba.

## Hilos abiertos

- **El plan de S147 queda intacto y pasa a S148** — no se ejecutó nada de ADR-027.
- **Sin medir:** `WORKPLAN-MAESTRO-V2.md` (~185 KB) y `docs/reglas-smc-ict.md` se acercan
  al mismo límite. No bloquean el arranque; conviene medirlos y decidir si se trocean.
- **F1-GATE sigue sin firmar.**

## Resultado 5 — CLAUDE.md pasa a ser un MAPA (petición del usuario, tras el cierre)

CLAUDE.md tenía **59 líneas** y mezclaba mapa con doctrina. Techo nuevo: **40 líneas**, y solo
dice qué documentos madre existen, qué contiene cada uno y cuándo ir a leerlo. Quedó en **38**,
con las 10 rutas que cita verificadas como existentes.

- La doctrina salió **verbatim** a `docs/REGLAS-DURAS.md` (51 líneas). Verificado línea a
  línea: las únicas líneas del antiguo que no se trasladaron son las de índice, reescritas
  como mapa. **Cero doctrina perdida.**
- **Hallazgo:** CLAUDE.md declaraba `## Estado actual — Fase 0 (entorno y fundaciones)`,
  rancio desde ~S010. El mapa nuevo no afirma la fase: apunta a `ESTADO-ACTUAL.md`.
- **ADR-003 escrito.** Se citaba como vigente en 8 documentos y **nunca tuvo fichero**
  (`git log --all --diff-filter=A`: ningún commit lo añadió). Transcrito del texto literal de
  `ESTADO-ACTUAL`, sin inventar las alternativas descartadas — no quedaron registradas.
  Validado en vivo: `main` congelado en `3e437f2` (2026-06-11, el día de la decisión) y **429
  commits** en `pine/sistema-completo`.
- **ADR-015 NO se escribió, y es correcto.** No es un fichero perdido: está reservado desde
  S098 y solo se redacta si el usuario ordena cambiar `minRR` (default 3.0 mandatorio). Se
  creó `docs/adrs/README.md` con el índice de los 26 ADRs y **los huecos explicados**, para
  que un hueco no vuelva a confundirse con una pérdida.

## Resultado 6 — `reglas-smc-ict.md` NO se parte: la premisa del usuario era la correcta

Propuse partir el documento (231 KB, 88 % del límite de `Read`). **El usuario objetó que los
conceptos ya están todos creados.** Medido, tenía razón:

- Las **42 confluencias canónicas** están cerradas y enumeradas en `WORKPLAN-MAESTRO-V2.md`
  §4.8 (línea 353). No falta ninguna.
- Último contenido **nuevo**: 2026-07-04 (§7, 40 fichas, +488 líneas).
- Los **6 commits posteriores** (S133/S134/S135) son **un solo hilo de enmienda** al mismo
  sitio, §2.3.2 chart-TF: +36-34, +29, +17-1, +18-4, +15-1, +46-3. Correcciones, no conceptos.

Mi frase «con dos o tres conceptos más lo cruza» era **falsa**: no hay más conceptos que
añadir. Quedan **31.191 B** de margen y la única fuente de crecimiento son enmiendas.
**Recomendación retirada, documento intacto.** `WORKPLAN-MAESTRO-V2.md` mide **58 KB**, no los
~185 KB que estimé sin medir; tampoco se tocó (orden explícita del usuario).

## Resultado 7 — el vault respaldaba el estado, no las reglas

`sync-obsidian.ps1` copiaba `memory/sesiones/`, `docs/adrs/` y `ESTADO-ACTUAL.md`. Asimetría
mal puesta: un ADR se puede reconstruir desde la sesión que lo originó; **una regla
cuantificada no**. Añadidos 5 destinos (`CLAUDE.md` a la raíz del vault por ser el punto de
entrada; `WORKPLAN-MAESTRO-V2.md`, `REGLAS-DURAS.md`, `reglas-smc-ict.md`, `reglas-dev.md` a
`<vault>/docs/`). Probado con `-DryRun` y luego en real: **7 copiados, 0 fuentes ausentes.**

## Commits (4)

- `00c28f0` — `fix(memory): S147 — ESTADO-ACTUAL rota en vez de acumular (291 KB -> 12 KB)`
- `5dd5c13` — `docs(cierre): S147 — arranque reparado; el plan de ADR-027 pasa integro a S148`
- `2197e60` — `docs(estructura): CLAUDE.md pasa a ser MAPA de <=40 lineas + ADR-003 escrito + indice de ADRs`
- `7a630b1` — `tools(scr-02): S147 — sync-obsidian respalda tambien la DOCTRINA`

Ver [[Sesion-146]] · [[Sesion-145]] · [[Sesion-144]].

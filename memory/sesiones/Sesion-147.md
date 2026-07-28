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

## Commits (1)

- `00c28f0` — `fix(memory): S147 — ESTADO-ACTUAL rota en vez de acumular (291 KB -> 12 KB)`

Ver [[Sesion-146]] · [[Sesion-145]] · [[Sesion-144]].

# Historial de confluencias — SWARM (Hermes, modo laboratorio)

> Aquí el enjambre (Hermes) deja **todas las confluencias detectadas y su historial**:
> proyecciones de cada agente/perfil, el debate, la decisión (o abstención) y el
> outcome real. Es el registro darwiniano que alimenta el score de perfiles.

## Qué se registra por cada confluencia/entrada del enjambre
- Estado de mercado leído (atrás): estructura, liquidez tomada, P/D, dealing range.
- Proyección de cada perfil (a qué zona, con qué confluencias, posRole/confDegree/depthBand).
- Debate: coincidencias (confluencia, no consenso) y discrepancias.
- Decisión final + por qué / o abstención + por qué.
- Outcome verificado: ¿el precio reaccionó donde se proyectó? → exactitud de proyección.

## Regla
- El enjambre opera SOLO en modo laboratorio (ADR-005): calibra y valida;
  el EA hereda las reglas cristalizadas. Este historial es la entrega al EA.

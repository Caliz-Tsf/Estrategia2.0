# docs/laboratorio/ — Registro del enjambre (descubrimiento de confluencias)

> Diario vivo del módulo mentores como **laboratorio** (ADR-005 / ADR-007). Aquí el enjambre registra
> las confluencias que toma en tiempo real, su autoría y su resultado; y el track record de cada agente.
> **Nada de esto entra al scoring del sistema sin pasar validación IS/OOS (ADR-002).** Es insumo de
> descubrimiento, no fuente de verdad de pesos.

## Archivos
- **`DIARIO-<YYYYMM>.md`** — una entrada por confluencia/hipótesis tomada: fecha/hora, símbolo/TF, zona/nivel,
  confluencias citadas (ancladas a `reglas-smc-ict.md`), **agente que la propuso (autoría)**, sesgo,
  invalidación, confianza, y resultado posterior (positiva/negativa en TV/replay + R).
- **`track-record-<mentor-slug>.md`** — histórico por agente: aciertos/fallos, R acumulado, score.

## Convención de entrada del diario (plantilla)
```
### <YYYY-MM-DD HH:MM> · <SÍMBOLO> <TF> · <agente-autor>
- Zona/nivel: <precio/rango>  (§reglas-smc-ict.md: <ref>)
- Confluencias: <lista>
- Sesgo: long/short · Invalidación: <nivel> · Confianza: baja/media/alta
- Voto del enjambre: <resumen acuerdos/desacuerdos>
- Resultado: <pendiente | positiva R+x | negativa R-x>  (verificado en TV/replay <fecha>)
```

## Estado
Estructura creada (Sesión-031). El **runtime** que la puebla (cron/kanban + scoring de agentes) se
diseña en `docs/planes/HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md` y se pilotará tras tener fichas
de ≥2 mentores. Por ahora estos archivos son la plantilla/convención, no hay entradas automáticas aún.

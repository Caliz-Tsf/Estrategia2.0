---
name: mql5-translator
description: Protocolo del pipeline de traducción Pine→MQL5 por función - spec, escritura, revisión, compilación, golden test. Solo Fase 4.
---

# Pipeline de traducción Pine→MQL5 (por función)

GUARD: memory/ESTADO-ACTUAL.md debe marcar Fase 4. Si no → detener.

1. SPEC+CÓDIGO: invocar `mql5-translator-agent` con la función Pine + entrada del
   mapeo (docs/workplan/MQL5-PLAN.md §3) → produce código + equivalencias + tests.
2. ESCRITURA ALTERNATIVA: si Antigravity IDE está disponible y se prefiere,
   entregarle la spec del paso 1 y que escriba él; el código resultante sigue
   el mismo pipeline.
3. REVISIÓN: invocar `mql5-reviewer` con el código + spec. Loop hasta APROBADO
   (máx 3 iteraciones, luego escalar a smc-architect).
4. COMPILAR: MetaEditor vía línea de comandos
   ("metaeditor64.exe /compile:<ruta> /log") → 0 errors, 0 warnings.
5. GOLDEN TESTS: ejecutar el script de tests del módulo con los casos del
   translator → todos verdes. Un test rojo = la traducción difiere de Pine:
   volver a 1 con el caso fallido como evidencia.
6. VERIFICACIÓN VISUAL (si el cambio afecta al panel/display): Claude Desktop
   con computer use sobre MT5.
7. Commit: `feat(mql5): <módulo>::<función> traducida + N golden tests`.

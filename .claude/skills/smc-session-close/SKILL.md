---
name: smc-session-close
description: Protocolo de cierre de sesión - commits, actualización de estado vía smc-doc-updater, ADRs pendientes, sync a Obsidian. Ejecutar antes de terminar cada sesión de trabajo.
---

# Cierre de sesión

1. git status → si hay cambios sin commitear, agruparlos en commits coherentes
   (nunca un mega-commit "wip"). Verificar con git log que todo lo de hoy
   está commiteado.
2. Verificar sincronía del core: scripts/check-core-sync.ps1 → si Visual y
   Strategy divergen, ARREGLAR antes de cerrar (es la deuda más cara).
3. Redactar resumen de sesión (qué se completó con IDs del workplan, qué quedó
   a medias, bloqueos nuevos).
4. Invocar agente `smc-doc-updater` con el resumen → actualiza
   memory/ESTADO-ACTUAL.md + memory/sesiones/Sesion-NNN.md + checkboxes.
5. Si hubo decisión arquitectural sin ADR → invocar smc-architect para
   escribirla AHORA (no se acumulan).
6. Si se completó una fase/gate → tag git (`fase-N-completa`) y nota en
   ESTADO-ACTUAL.
7. scripts/sync-obsidian.ps1 → copiar sesión + ADRs nuevos al vault personal.
   ❌ → ⚠️ reportar y cerrar igualmente.

## Salida
Confirmación: commits ✅ · core sync ✅ · estado actualizado ✅ · obsidian ✅/⚠️

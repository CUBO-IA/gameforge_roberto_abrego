# Tablero de tareas — GAMEFORGE 2D

Formato por tarea: ID, objetivo, responsable, archivos permitidos, criterios de
aceptación, informe (`tasks/reports/T-XXX.md`).

Columnas: PROPUESTA → APROBADA → EN CURSO → ENTREGADA → VERIFICADA.

## ENTREGADA

### T-000 — Fase 0: cimientos
- Responsable: DIRECTOR/ARQUITECTO
- Objetivo: control de versiones, higiene de raíz, verificación estándar, propiedad y tablero.
- Archivos permitidos: `.gitignore`, `tools/verify.py`, `architecture/OWNERSHIP.md`, `tasks/`, `archive/bootstrap/`, `GAMEFORGE_2D_ARCHITECTURE_REVIEW.md` (marcas de estado).
- Criterios de aceptación:
  - [x] Repositorio git inicializado con commit base limpio (residuos archivados, no borrados).
  - [x] `tools/verify.py` verde (lint omitido: ruff no instalado; pytest 112 passed; bench p95 16.67 ms OK).
  - [x] `OWNERSHIP.md` y `tasks/BOARD.md` creados.
- Evidencia: commit `0830a27`. Pendiente: cierre VERIFICADA por el director; instalar ruff para cubrir lint.

### T-102 — Fase 1: enemigos data-driven — ENTREGADA 2026-11-06
- Responsable: IA/NPC + GAMEPLAY
- Resultado: `game/data/enemies.json` + `game/entities/enemy_catalog.py` (validado, `CatalogError`); FSM genérica con comportamientos `melee`/`ranged`/`charger` parametrizados en `game/entities/enemies.py` (eliminados `_update_slime/_update_wisp/_update_brute` por tipo). Un tipo nuevo con comportamiento existente = solo JSON + stats en config.json.
- Verificación: 10 tests nuevos en `tests/test_enemy_catalog.py`; suite 132 passed.
- Criterios: [x] sin código por tipo [x] catálogo validado [x] sin pygame en dominio.

### T-101 — Fase 1: extraer `sim/` desde `play.py` — ENTREGADA CON DESVIACIÓN 2026-11-06
- Responsable: GAMEPLAY
- Resultado: `game/sim/` creado (combat, interaction, engagement, floor); presentación del mundo extraída a `game/render/world_view.py`; `systems/combat.py` es shim de compatibilidad (contrato intacto). 12 tests nuevos en `tests/test_sim.py`.
- **Desviación**: criterio `play.py < 250 líneas` NO cumplido: 564 → 496. La orquestación de presentación (audio/efectos por resultado de sim) sigue en la escena. Propuesta: completar en F2 con `RunState` y presentación por eventos; decisión pendiente del director.
- Verificación: `tools/verify.py` OK (132 pytest + bench p95 27.7 ms dentro del umbral informativo).

## APROBADA (2026-11-06, director: "procede con los cambios")

### T-201 — Fase 2: multiplanta, misiones, A*, crafting
- Responsable: GAMEPLAY + IA/NPC + PROCEDURAL
- Bloqueo: T-101 y T-102 verificadas.

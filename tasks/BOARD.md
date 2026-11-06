# Tablero de tareas — GAMEFORGE 2D

Formato por tarea: ID, objetivo, responsable, archivos permitidos, criterios de
aceptación, informe (`tasks/reports/T-XXX.md`).

Columnas: PROPUESTA → APROBADA → EN CURSO → ENTREGADA → VERIFICADA.

## EN CURSO

### T-000 — Fase 0: cimientos
- Responsable: DIRECTOR/ARQUITECTO
- Objetivo: control de versiones, higiene de raíz, verificación estándar, propiedad y tablero.
- Archivos permitidos: `.gitignore`, `tools/verify.py`, `architecture/OWNERSHIP.md`, `tasks/`, `archive/bootstrap/`, `GAMEFORGE_2D_ARCHITECTURE_REVIEW.md` (marcas de estado).
- Criterios de aceptación:
  - [x] Repositorio git inicializado con commit base limpio (residuos archivados, no borrados).
  - [x] `tools/verify.py` verde (lint omitido: ruff no instalado; pytest 112 passed; bench p95 16.67 ms OK).
  - [x] `OWNERSHIP.md` y `tasks/BOARD.md` creados.
- Estado: EN CURSO.

## PROPUESTA (pendientes de aprobación del director)

### T-101 — Fase 1: extraer `sim/` desde `play.py`
- Responsable: GAMEPLAY
- Objetivo: combat/interact/loot/floor como sistemas puros; `play.py` < 250 líneas.
- Bloqueo: requiere aprobación del contrato `sim/` (§10 del informe).

### T-102 — Fase 1: enemigos data-driven
- Responsable: IA/NPC + GAMEPLAY (contrato compartido, coordinar con director)
- Objetivo: `game/data/enemies.json` + FSM genérica; sin `_update_<tipo>` por tipo.

### T-201 — Fase 2: multiplanta, misiones, A*, crafting
- Responsable: GAMEPLAY + IA/NPC + PROCEDURAL
- Bloqueo: T-101 y T-102 verificadas.

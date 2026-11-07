# Tablero de tareas — GAMEFORGE 2D

Formato por tarea: ID, objetivo, responsable, archivos permitidos, criterios de
aceptación, informe (`tasks/reports/T-XXX.md`).

Columnas: PROPUESTA → APROBADA → EN CURSO → ENTREGADA → VERIFICADA.

## ENTREGADA

### T-201 — Fase 2: multiplanta, misiones, A*, crafting — ENTREGADA 2026-11-06
- Responsable: GAMEPLAY + IA/NPC + PROCEDURAL
- Resultado:
  - Navegación A* con cuota de CPU y caché LRU en `game/ai/astar.py`.
  - Sistema de misiones data-driven (`game/data/quests.json`, `game/sim/quest.py`).
  - Sistema de crafting atómico con recetas en `game/data/recipes.json` y `game/sim/crafting.py`.
  - Encadenamiento multiplanta de 3 pisos con transiciones en `game/sim/floor.py` y `game/scenes/play.py`.
- Verificación: 23 tests nuevos (155 tests totales pasando), `tools/verify.py` OK (0 ruff, bench p95 1.32 ms).
- Informe completo: `tasks/reports/T-201.md`.

## VERIFICADA (por el DIRECTOR 2026-11-06)

### T-000 — Fase 0: cimientos
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: Git inicializado, residuos archivados en `archive/bootstrap/`, `tools/verify.py` operativo, matriz `OWNERSHIP.md` y 12 skills completas con 8 apartados.
- Verificación: Commit `fa25830`, ruff 0 errores, 132 tests OK. Criterios cumplidos al 100%.

### T-102 — Fase 1: enemigos data-driven
- Responsable: IA/NPC + GAMEPLAY
- Resultado: `game/data/enemies.json` + `game/entities/enemy_catalog.py` con validación estricta y FSM genérica en `game/entities/enemies.py`.
- Verificación: 10 tests de catálogo, suite 132 tests pasando. Criterios cumplidos al 100%.

### T-101 — Fase 1: extraer `sim/` desde `play.py`
- Responsable: GAMEPLAY
- Resultado: `game/sim/` creado (combat, interaction, engagement, floor) y presentación desacoplada en `render/world_view.py`.
- Verificación: 132 tests pasando y benchmarks estables. Desviación aceptada por el director al diferir eventos a Fase 2.

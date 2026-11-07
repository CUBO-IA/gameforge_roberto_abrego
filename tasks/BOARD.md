# Tablero de tareas — GAMEFORGE 2D

Formato por tarea: ID, objetivo, responsable, archivos permitidos, criterios de
aceptación, informe (`tasks/reports/T-XXX.md`).

Columnas: PROPUESTA → APROBADA → EN CURSO → ENTREGADA → VERIFICADA.

## ENTREGADA

### T-301 — Fase 3: Mundo grande y escala — ENTREGADA 2026-11-06
- Responsable: GAMEPLAY + PROCEDURAL + IA/NPC + PRESENTACIÓN
- Resultado:
  - Partición espacial `SpatialHash` en `game/world/spatial.py`.
  - Separación de enemigos y ataques optimizados con SpatialHash.
  - Frustum culling de renderizado en `game/render/world_view.py`.
  - Staggering de actualización para entidades lejanas en `game/sim/engagement.py`.
  - Cargador de mapas autorales de Tiled en `game/world/tiled_loader.py`.
- Verificación: 10 tests nuevos (165 tests totales pasando), `tools/verify.py` OK (0 ruff, bench p95 1.17 ms).
- Benchmark a gran escala: 100 entidades simultáneas con p95 = 6.58 ms (presupuesto 16.67 ms).
- Informe completo: `tasks/reports/T-301.md`.

## VERIFICADA (por el DIRECTOR 2026-11-06)

### T-201 — Fase 2: multiplanta, misiones, A*, crafting
- Responsable: GAMEPLAY + IA/NPC + PROCEDURAL
- Resultado: A* cuotado en `game/ai/astar.py`, misiones data-driven (`quests.json`), recetas (`recipes.json`) y 3 plantas encadenadas con victoria en el núcleo.
- Verificación: Commit `a12f9fd`, 155 tests verdes, bench p95 1.25 ms. Criterios cumplidos al 100%.

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

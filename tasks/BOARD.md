# Tablero de tareas — GAMEFORGE 2D

Formato por tarea: ID, objetivo, responsable, archivos permitidos, criterios de
aceptación, informe (`tasks/reports/T-XXX.md`).

Columnas: PROPUESTA → APROBADA → EN CURSO → ENTREGADA → VERIFICADA.

## EN CURSO
(Ninguna tarea en curso en este momento. Todas las fases F0 a F5 han sido completadas satisfactoriamente).

## VERIFICADA (por el DIRECTOR 2026-11-06)

### T-501 — Fase 5: Distribución y empaquetado
- Responsable: DIRECTOR/ARQUITECTO + PRESENTACIÓN
- Resultado: Especificación `gameforge.spec`, script compilador `tools/build_dist.py`, manual de usuario `documentation/GUIA_JUGADOR.md`, `README.md` actualizado y suite de pruebas `tests/test_distribution.py`.
- Verificación: 179 tests verdes, `tools/verify.py` OK, empaquetador validado con `--check-only`. Criterios cumplidos al 100%.

### T-401 — Fase 4: Presentación, Lienzo Virtual y Multi-ranura
- Responsable: PRESENTACIÓN + DIRECTOR
- Resultado: `VirtualCanvas` con letterbox/pillarbox en `game/render/canvas.py`, mapeo de ratón, guardado multi-ranura y audio.
- Verificación: Commit `5a73916`, 175 tests verdes, bench p95 1.16 ms. Criterios cumplidos al 100%.

### T-301 — Fase 3: Mundo grande y escala
- Responsable: GAMEPLAY + PROCEDURAL + IA/NPC + PRESENTACIÓN
- Resultado: SpatialHash en `game/world/spatial.py`, culling de render, staggering de IA y cargador Tiled.
- Verificación: Commit `e03d4c1`, 165 tests verdes, benchmark de 100 enemigos p95 = 6.58 ms. Criterios cumplidos al 100%.

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

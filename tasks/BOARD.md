# Tablero de tareas — GAMEFORGE 2D

Formato por tarea: ID, objetivo, responsable, archivos permitidos, criterios de
aceptación, informe (`tasks/reports/T-XXX.md`).

Columnas: PROPUESTA → APROBADA → EN CURSO → ENTREGADA → VERIFICADA.

## EN CURSO
(Ninguna tarea en curso en este momento. Todas las fases F0 a F5 han sido completadas satisfactoriamente).

## ENTREGADA (pendiente de verificación del DIRECTOR)

### T-1002 — Fase 1: Línea base de Pyright y puerta de tipado
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: `pyrightconfig.json` con el venv del proyecto (elimina 84 falsos `reportMissingImports`), corrección del único error real de `game/world` en `tiled_loader.py`, `tools/typecheck.py` con línea base y módulos obligados a cero, `pyright_baseline.json` (46 errores) y paso bloqueante en `verify.py` (`--skip-types`).
- Verificación: `game/core` y `game/world` en 0; total 112 → 46; 6 pruebas nuevas de la puerta; ruff clean.
- Informe: `tasks/reports/T-1002.md`.

### T-1001 — Misión 006: Tooling 2D y MVP del Game Test Runner
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: auditoría de herramientas corregida con mediciones reproducibles (314 tests, Pyright 112 errores de línea base, headless ~24k FPS), veredictos ajustados (Watchlight y pyfxr descartados/postergados con evidencia) e informe final consolidado en `TOOLING_AUDIT.md` §11. Implementado el MVP del GF-TR en `tools/test_runner/` (runner headless, input virtual, validación de escenarios, 8 aserciones, captura/diff y telemetría), CLI `python -m tools.test_runner`, dos escenarios piloto e integración bloqueante en `tools/verify.py`.
- Verificación: 325 tests verdes en 6.50 s, ruff clean, escenarios OK, `verify.py` OK (bench p95 1.06 ms, grafo actualizado).
- Informe: `tasks/reports/T-1001.md`.

## VERIFICADA (por el DIRECTOR 2026-11-07)

### T-902 — Misión 005: Integración Operativa de Graphify como Memoria y Grafo de Comprensión
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: 6 entregables normativos completados (`GRAPHIFY_INTEGRATION.md`, `GRAPH_UPDATE_AUTOMATION.md`, `GRAPH_MCP_CONFIGURATION.md`, `GRAPH_USAGE_DIRECTIVE.md`, `GRAPH_ACCEPTANCE_TESTS.md`, `RESOURCE_BENCHMARK.md`). Implementado el paquete desacoplado `tools/graph_memory/` y CLI `tools/graph_ops.py` en entorno aislado (`uv tool` / `graphifyy v0.9.85`). Extracción determinista AST de código Python y Markdown estructural sin coste de tokens; extractor ontológico de decisiones (ADRs, tareas, contratos, directivas, problemas y soluciones con estados epistémicos); servidor MCP (`graphify-mcp`) para Claude Code y agentes externos con soporte stdio y hot-reload; motor incremental `build_merge` con detección de drift SHA-256 (modificados, eliminados y renombrados en 235 ms); directiva formal `directives/06_GRAPH_USAGE.md`; configuración `.mcp.json`; githooks de sincronización y verificación obligatoria de frescura en `tools/verify.py`; y suite de pruebas `tests/test_graphify_integration.py`.
- Verificación: 303 tests verdes, ruff clean, `verify.py` OK (p95 = 1.23 ms). Criterios cumplidos al 100%.

### T-901 — Misión 004: Diseño del Sistema de Grafos, Memoria y Contexto Operativo (GF-Graph)
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: 7 entregables normativos completados (`KNOWLEDGE_GRAPH_ARCHITECTURE.md`, `CODE_GRAPH_INTEGRATION.md`, `AGENT_MEMORY_SYSTEM.md`, `GRAPH_UPDATE_LIFECYCLE.md`, `MANDATORY_GRAPH_USAGE.md`, `GRAPH_VALIDATION_TESTS.md`, `LOCAL_RESOURCE_BENCHMARK.md`). Análisis exhaustivo y comparativo de los 7 repositorios prioritarios (GitNexus, CodeGraph, ctx, Graphiti, Cognee, Aider RepoMap, LangGraph), detección de redundancias y poda de sobreingeniería. Especificación del sistema unificado `GF-Graph`: motor local SQLite WAL en `.gameforge/graph.db`, parser AST determinista en Python, PageRank de símbolos (Aider), esqueletos de código token-efficient (ctx), radio de explosión BFS inverso (CodeGraph), memoria episódica bi-temporal con 5 estados epistémicos (Graphiti), protocolo pre-flight de 7 pasos con recibo criptográfico de auditoría, ciclo de vida con hooks git/verify.py, diseño de prueba de coordinación real multiagente y suite de pruebas `tests/test_mission_004_deliverables.py`.
- Verificación: 295 tests verdes, ruff clean, `verify.py` OK (p95 = 1.21 ms). Criterios cumplidos al 100%.

### T-801 — Misión 003: Implementación del GameForge Asset Hub y Ecosistema de Recursos
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: Implementado el sistema local y desacoplado `tools/asset_hub/` (CLI, SQLite, dHash perceptual, scanner, validación V-01 a V-07, motor de búsqueda semántica anti-alucinaciones con `match_score`, previsualizador headless de tiras PNG, exportador hacia `gf-anim-v1`, generador automático de `CREDITS.md`), 7 entregables normativos de investigación y arquitectura, catálogo inicial indexado (LPC, Kenney e internos), y suites de pruebas `tests/test_asset_hub.py` y `tests/test_mission_003_deliverables.py`.
- Verificación: 278 tests verdes, ruff clean, `verify.py` OK (p95 = 1.24 ms). Criterios cumplidos al 100%.

### T-702 — Integración Completa de Animaciones de Enemigos, HFSM Nativa, Game Feel y LiteBehaviorTree
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: Creados atlas y manifiestos `gf-anim-v1` para `slime`, `wisp` y `brute` con `tools/generate_enemy_sprites.py`; integrado el soporte de `anim_player` en `Enemy`, `entity_renderer.py` y `play.py`; implementado el motor `game/core/fsm.py` de despacho O(1); creados `InputBuffer` y `CoyoteTimer` en `game/input/buffer.py`; e implementado `LiteBehaviorTree` en `game/ai/behavior_tree.py` con constructor JSON.
- Verificación: 267 tests verdes, ruff clean, benchmark p95 = 1.26 ms. Criterios cumplidos al 100%.

### T-701 — Implementación del Núcleo de Animación gf-anim-v1, Efectos Mejorados y Validación
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: Implementado el módulo `game/render/animation.py` con cargador `gf-anim-v1` y `AnimationPlayer` con eventos y prioridades; añadidos `HitstopManager`, `TraumaScreenShake` y `ParticlePool` contiguo en `game/render/effects.py`; creadas las herramientas `tools/validate_character.py` y `tools/preview_animation.py` para agentes; incorporado el activo canónico `knight_hero.anim.json`; y añadidas suites de pruebas `tests/test_animation_engine.py`, `tests/test_enhanced_effects.py` y `tests/test_character_validator.py`.
- Verificación: 247 tests verdes, ruff clean, benchmark p95 = 1.25 ms. Criterios cumplidos al 100%.

### T-604 — Misión 002: Investigación de Sprites, Animaciones y Lógica de Personajes
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: 7 entregables normativos (`SPRITE_PIPELINE_RESEARCH.md`, `ANIMATION_SYSTEM_PROPOSAL.md`, `CHARACTER_CONTROLLER_ARCHITECTURE.md`, `ANIMATION_FORMAT_SPEC.md`, `VISUAL_EFFECTS_ARCHITECTURE.md`, `AGENT_ANIMATION_WORKFLOW.md`, `LICENSE_AND_DEPENDENCY_AUDIT.md`), investigación de 7 repositorios (skelform, PySpine, transitions, py_trees, pygame-ce, HitBox, rsheet) y alternativas (Aseprite, TexturePacker, Spine oficial), especificación de formato `gf-anim-v1`, pipeline de 8 pasos para agentes, HFSM nativa, LiteBehaviorTree, ParticlePool preasignado, TraumaScreenShake y suite de pruebas automatizadas `tests/test_mission_002_deliverables.py`.
- Verificación: 237 tests verdes, ruff clean, benchmark p95 = 1.23 ms. Criterios cumplidos al 100%.

### T-603 — Integración del Sistema: Swarm AI, Diálogos Nemotron El Salvador, Cavernas Dinámicas y Colisión de Techos
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: Swarm AI en `sim/engagement.py` y `entities/enemies.py` con `DijkstraMap`, diálogos culturales y comercio en `sim/dialog.py` utilizando los personajes de `nvidia/Nemotron-Personas-El-Salvador` (Doña Rosa, Maestro José, Don Antonio), despacho automático de caverna orgánica en piso 2 en `sim/floor.py` y `scenes/play.py`, y colisión contra techos en salto 2.5D en `entities/player.py`.
- Verificación: 228 tests verdes, ruff clean, benchmark p95 = 1.24 ms. Criterios cumplidos al 100%.

### T-602 — Expansión Mecánicas: Salto 2.5D, Cavernas, Swarm AI y Hub Narrativo
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: Salto 2.5D con gravedad e inmunidad aérea en `player.py`, generador de cavernas orgánicas en `cavern_generation.py` (celular + radial + BFS), mapa Dijkstra O(W×H)/O(1) en `ai/dijkstra.py` para hordas, hub narrativo 20×15 en `hub_town.json` con 3 NPCs y soporte `NpcSpec` en `tiled_loader.py`.
- Verificación: Commit `762a88b`, 213 tests verdes, ruff clean, benchmark p95 = 1.29 ms. Criterios cumplidos al 100%.

### T-601 — Investigación de Repositorios, Auditoría Legal y Propuesta Arquitectónica
- Responsable: DIRECTOR/ARQUITECTO
- Resultado: 12 repositorios analizados en `REPOSITORY_RESEARCH.md`, justificación en `TECH_STACK_RECOMMENDATION.md`, capas puras y presupuestos en `ARCHITECTURE_PROPOSAL.md`, análisis de licencias y riesgos en `DEPENDENCY_AUDIT.md`, 9 algoritmos clave en `REUSABLE_ALGORITHMS.md`, tabla de referencias `OPEN_SOURCE_REFERENCES.md` y suite de pruebas `tests/test_research_deliverables.py`.
- Verificación: 185 tests verdes, `tools/verify.py` OK, benchmark p95 = 1.25 ms. Criterios cumplidos al 100%.

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

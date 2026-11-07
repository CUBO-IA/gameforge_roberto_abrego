# Graph Report - GAMEFORGE  (2026-11-07)

## Corpus Check
- 1240 files · ~150,000 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2717 nodes · 5701 edges · 201 communities (127 shown, 74 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 690 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125
- Community 126
- Community 128
- Community 129
- Community 130
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
- Community 139
- Community 140
- Community 142
- Community 143
- Community 144
- Community 147
- Community 148
- Community 149
- Community 150
- Community 151
- Community 171
- Community 172
- Community 173
- Community 174
- Community 175
- Community 176
- Community 177
- Community 178
- Community 179
- Community 180
- Community 181
- Community 182
- Community 183
- Community 184
- Community 185
- Community 186
- Community 187
- Community 188
- Community 189
- Community 190
- Community 191
- Community 192
- Community 193
- Community 194
- Community 195
- Community 196
- Community 197
- Community 198
- Community 199
- Community 200

## God Nodes (most connected - your core abstractions)
1. `Vec2` - 237 edges
2. `TileMap` - 95 edges
3. `Inventory` - 70 edges
4. `PlayScene` - 66 edges
5. `TileType` - 58 edges
6. `Camera` - 51 edges
7. `Player` - 47 edges
8. `Enemy` - 43 edges
9. `Application` - 40 edges
10. `DijkstraMap` - 34 edges

## Surprising Connections (you probably didn't know these)
- `test_cli_entrypoint_callable()` --indirect_call--> `main()`  [INFERRED]
  tests/test_distribution.py → game/__main__.py
- `Vec2` --implements_contract--> `Contract: game.core.math2d.Vec2`  [EXTRACTED]
  game/core/math2d.py → architecture/CONTRACTS.md
- `TileMap` --implements_contract--> `Contract: game.world.tilemap.TileMap`  [EXTRACTED]
  game/world/tilemap.py → architecture/CONTRACTS.md
- `main()` --uses--> `EnemyStats`  [INFERRED]
  benchmark/bench_simulation.py → game/core/config.py
- `main()` --calls--> `resolve_player_attack()`  [INFERRED]
  benchmark/bench_simulation.py → game/sim/combat.py

## Import Cycles
- None detected.

## Communities (201 total, 74 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (13): draw_anvil(), draw_title_forge(), forge_glow(), vertical_gradient(), Effects, MenuEntry, MenuList, Scene (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (14): Action, InputMapper, CoyoteTimer, InputBuffer, test_coyote_timer(), test_input_buffer_expiration(), test_input_buffer_purge_and_clear(), test_input_buffer_registration_and_consumption() (+6 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (19): AnimationClip, AnimationFormatError, AnimationPlayer, FrameData, FrameEvent, HitboxData, load_animation_manifest(), init_pygame() (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (18): draw_altar(), draw_attack_arc(), draw_campfire(), draw_chest(), draw_enemy(), draw_player(), draw_projectile(), draw_shadow() (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (16): Action, BTNode, build_tree_from_dict(), Condition, Cooldown, Inverter, NodeStatus, Parallel (+8 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (11): StateHandler, StateMachine, StateTransitionError, MockContext, MockState, test_allowed_transitions_validation(), test_basic_transition(), test_callbacks_enter_and_exit() (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (7): FontCache, Hud, draw_bar(), draw_key_hint(), draw_panel(), draw_text(), _lighten()

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (11): Campfire, Chest, ForgeAltar, RunSnapshot, PlayScene, find_nearest_interaction(), loot_message(), LootResult (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (21): CatalogError, definition_for(), EnemyDefinition, load_enemy_catalog(), _parse_catalog(), test_all_data_catalogs_load_successfully(), test_cli_entrypoint_callable(), test_packaging_prerequisites() (+13 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (19): load_tiled_json(), NpcSpec, TiledError, TiledMapData, test_hub_map_altar_and_campfire(), test_hub_map_border_is_wall(), test_hub_map_chests(), test_hub_map_file_not_found() (+11 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (20): Contract: game.sim.floor, calculate_floor_transition(), finish_score(), floor_bonus(), floor_theme_name(), floor_type_for(), FloorTransition, FloorType (+12 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (35): 10. Interfaz CLI Propuesta, 11. Métricas de Eficiencia Esperadas, 12.1. Compatibilidad, 12.2. Ubicación en el repositorio, 12. Integración con el Ecosistema Existente, 1.1. Qué extrae el parser AST, 1.2. Qué NO modela, 1. Alcance del Grafo de Código (+27 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (33): 1. Resumen Ejecutivo y Motivación, 2. Análisis Comparativo de Fuentes y Repositorios Iniciales, 3.10. Licencias y Procedencia, 3.1. Personajes y sus Animaciones, 3.2. Spritesheets y Atlas (Atlas de Texturas), 3.3. Mapas y Tilesets, 3.4. NPC y Criaturas, 3.5. Armas, Objetos y Equipamiento (+25 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (33): 10. Tabla Resumen de Ciclo de Vida, 1. Objetivo, 2. Diagrama de Estados del Ciclo de Actualización, 3. Eventos Disparadores y Sus Acciones, 4.1. Git Hooks, 4.2. Integración con `tools/verify.py`, 4.3. Watcher de `tasks/BOARD.md`, 4.4. Watcher de `architecture/CONTRACTS.md` (+25 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (10): DijkstraMap, _simple_tilemap(), test_dijkstra_best_neighbor_o1(), test_dijkstra_best_neighbor_unreachable(), test_dijkstra_determinism(), test_dijkstra_direction_toward_source(), test_dijkstra_distances_match_bfs(), test_dijkstra_multi_source() (+2 more)

### Community 15 - "Community 15"
Cohesion: 0.08
Nodes (6): HitstopManager, ParticlePool, TraumaScreenShake, test_hitstop_manager_lifecycle(), test_particle_pool_zero_allocation_lifecycle(), test_trauma_screen_shake_physics()

### Community 16 - "Community 16"
Cohesion: 0.14
Nodes (11): load_quest_catalog(), QuestDefinition, QuestError, QuestManager, QuestProgress, QuestReward, test_load_default_quest_catalog(), test_quest_definition_validation() (+3 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (18): Contract: game.core.config, AudioConfig, ConfigError, GameConfig, _int(), load_config(), _number(), _parse_enemies() (+10 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (17): EnemyStats, PlayerConfig, Player, empty_map(), player_cfg(), test_jump_avoids_ground_hazards(), test_player_cannot_double_jump(), test_player_cannot_jump_under_zero_ceiling() (+9 more)

### Community 19 - "Community 19"
Cohesion: 0.15
Nodes (11): Inventory, InventoryError, test_add_remove_and_count(), test_capacity_counts_distinct_items(), test_invalid_capacity(), test_invalid_quantities(), test_serialization_roundtrip_and_validation(), test_stack_limit() (+3 more)

### Community 20 - "Community 20"
Cohesion: 0.06
Nodes (31): 10. Flujo de Registro de una Tarea Completa, 11. Comparación con Alternativas Descartadas, 1.1. Memoria de Trabajo, 1.2. Memoria Episódica, 1.3. Memoria Semántica, 1. Modelo de Memoria del Agente, 2. Categorías de Nodos de Conocimiento, 3. Tipos de Aristas de Conocimiento (+23 more)

### Community 21 - "Community 21"
Cohesion: 0.06
Nodes (31): 1. Objetivo, 2. Perfil del Repositorio Actual, 3.1. Rendimiento temporal, 3.2. Consumo de recursos, 3.3. Eficiencia de tokens, 3. Métricas a Medir, 4.1. Herramientas, 4.2. Protocolo de medición (+23 more)

### Community 22 - "Community 22"
Cohesion: 0.13
Nodes (13): Contract: game.world.collision, Contract: game.world.tilemap.TileMap, circle_hits_solid(), CollisionResult, has_line_of_sight(), move_circle(), TileMap, make_room() (+5 more)

### Community 23 - "Community 23"
Cohesion: 0.06
Nodes (30): 10. CONTRATOS DE INTERFACES, 11. PLAN DE DESARROLLO POR FASES, 12. BENCHMARK PARA EVALUAR A LOS AGENTES, 13. MATRIZ DE RIESGOS TÉCNICOS, 14. MATRIZ DE DECISIONES DE ARQUITECTURA, 1.1 Qué contiene realmente el paquete GAMEFORGE_2D_AGENT_KIT, 1.2 Verificación técnica ejecutada en el entorno [HECHO], 1.3 Fortalezas verificadas del código existente (+22 more)

### Community 24 - "Community 24"
Cohesion: 0.14
Nodes (6): Contract: game.core.math2d.Vec2, Vec2, FloatingText, Particle, test_from_angle_and_overlap(), test_vector_arithmetic_and_length()

### Community 25 - "Community 25"
Cohesion: 0.10
Nodes (5): build_parser(), main(), AssetHubDB, AssetQueryEngine, AssetScanner

### Community 26 - "Community 26"
Cohesion: 0.17
Nodes (11): RunResult, ScoreEntry, ScoreError, ScoreRepository, _validate_result(), result(), test_invalid_limit(), test_invalid_results() (+3 more)

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (10): Application, build_parser(), main(), app(), test_application_runs_menu_frames(), test_cli_headless_smoke(), test_death_records_run(), test_play_scene_update_and_draw() (+2 more)

### Community 28 - "Community 28"
Cohesion: 0.07
Nodes (28): 1. Principio Fundamental, 2. Flujo de Consulta Pre-Tarea (7 Pasos), 3.1. Campos obligatorios, 3.2. Campos de verificación posterior, 3. Formato del Recibo de Auditoría (Pre-Flight Receipt), 4.1. Verificación de recibo, 4.2. Modos de enforcement, 4. Integración con `tools/verify.py` (+20 more)

### Community 29 - "Community 29"
Cohesion: 0.13
Nodes (8): circles_overlap(), Projectile, ProjectileSpec, EngagementEvents, move_projectiles(), projectile_hits_player(), spawn_projectile(), update_enemies()

### Community 30 - "Community 30"
Cohesion: 0.07
Nodes (27): 1. Resumen Ejecutivo, 2.1 `rsheet` (ELiijah-dev, PyPI v0.1.1, MIT), 2.2 `PySpine` (SaxonRah, GitHub, MIT), 2.3 Aseprite CLI / Formato JSON Estándar, 2.4 TexturePacker & Algoritmo MaxRects, 2. Análisis Exhaustivo de Herramientas y Repositorios, 3.1 Estructura del Sistema de Archivos, 3.2 Formato Fuente y Especificaciones Gráficas (+19 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (12): Contract: game.render.canvas, calculate_letterbox(), screen_to_logical(), VirtualCanvas, test_calculate_letterbox_exact_aspect(), test_calculate_letterbox_full_hd_scale(), test_calculate_letterbox_invalid(), test_calculate_letterbox_narrow_letterbox() (+4 more)

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (20): item_exists(), _integer(), load_run(), _number(), save_run(), SaveGameError, _string_list(), _validate_payload() (+12 more)

### Community 33 - "Community 33"
Cohesion: 0.17
Nodes (14): Contract: game.world.generation, _build(), _campfire_position(), _carve_corridor(), _carve_hazard(), _carve_horizontal(), _carve_vertical(), _distance_sq() (+6 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (3): AuditLogger, DriftReport, ManifestTracker

### Community 35 - "Community 35"
Cohesion: 0.15
Nodes (15): open_chest(), PotionResult, use_potion(), _altar(), _Campfire, _chest(), _player_config(), test_find_nearest_altar_label_counts_missing_shards() (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.13
Nodes (6): SpatialHash, test_spatial_hash_clear(), test_spatial_hash_insert_and_query_radius(), test_spatial_hash_invalid_cell_size(), test_spatial_hash_query_pairs(), test_spatial_hash_query_rect()

### Community 37 - "Community 37"
Cohesion: 0.16
Nodes (4): test_hasher_sha256_and_dhash(), compute_dhash(), compute_sha256(), hamming_distance()

### Community 38 - "Community 38"
Cohesion: 0.09
Nodes (21): 1. Resumen Ejecutivo, 2.1 Paradigma Tradicional por Fotogramas Clave (*Frame-by-Frame Spritesheets*), 2.2 Paradigma Esquelético 2D (*Skeletal Cut-Out / Mesh Deformation*), 2.3 Matriz de Decisión Multidimensional, 2. Comparativa: Animación Tradicional vs. Animación Esquelética, 3.1 `Retropaint/skelform`, 3.2 `SaxonRah/PySpine`, 3.3 Esoteric Software Spine Runtime (Referencia de la Industria) (+13 more)

### Community 39 - "Community 39"
Cohesion: 0.19
Nodes (11): can_craft(), craft(), CraftingError, CraftResult, load_recipes(), Recipe, test_can_craft_checks_ingredients(), test_craft_rollback_on_inventory_full() (+3 more)

### Community 40 - "Community 40"
Cohesion: 0.22
Nodes (9): GraphEngine, cmd_affected(), cmd_benchmark(), cmd_build(), cmd_mcp(), cmd_query(), cmd_update(), cmd_verify() (+1 more)

### Community 41 - "Community 41"
Cohesion: 0.10
Nodes (20): 1. Resumen Ejecutivo, 2.1 El Contrato `CharacterIntent`, 2. Separación Estricta de Capas (Clean Architecture), 3.1 `pytransitions/transitions` vs. HFSM Nativa de Alto Rendimiento, 3.2 `splintered-reality/py_trees` vs. Motor `LiteBehaviorTree`, 3.3 `etamowon/HitBox` y el Sistema Profesional de Cajas de Colisión, 3. Auditoría de Repositorios de Lógica: Decisiones Clave, 4.1 Prioridad de Estados y Cancelaciones (+12 more)

### Community 42 - "Community 42"
Cohesion: 0.10
Nodes (20): 1. Objetivo, 2.1. Tests del Grafo de Código, 2.2. Tests del Análisis de Impacto, 2.3. Tests de Contratos, 2.4. Tests del Grafo de Conocimiento, 2.5. Tests de Taxonomía Epistémica (Requisito 5), 2.6. Tests de Recibos de Auditoría, 2.7. Tests de Sincronización (+12 more)

### Community 43 - "Community 43"
Cohesion: 0.20
Nodes (13): Contract: game.ai.astar, _cache_result(), clear_path_cache(), find_path(), make_test_map(), test_astar_cache_works(), test_astar_completely_blocked_returns_none(), test_astar_navigates_around_wall() (+5 more)

### Community 44 - "Community 44"
Cohesion: 0.17
Nodes (13): DungeonConfig, _build_cavern(), generate_cavern(), _radial_falloff(), ChestSpec, Dungeon, EnemySpec, test_floor_generation_dispatch() (+5 more)

### Community 45 - "Community 45"
Cohesion: 0.10
Nodes (19): 1. Resumen Ejecutivo, 2.1 El Problema de las Asignaciones Dinámicas de Memoria, 2.2 Arquitectura de Reserva Preasignada (*Object Pooling*), 2.3 Modos de Dibujo y Blending, 2. Sistema de Partículas de Alto Rendimiento, 3.1 Pausa de Impacto (*Hitstop / Freeze Frames*), 3.2 Destello de Impacto (*Flash-Hit*), 3. Impactos de Combate: Hitstop, Flash-Hit y Chispas (+11 more)

### Community 46 - "Community 46"
Cohesion: 0.22
Nodes (10): save_file(), delete_save(), delete_slot(), list_save_slots(), load_slot(), save_slot(), SaveData, make_snapshot() (+2 more)

### Community 47 - "Community 47"
Cohesion: 0.11
Nodes (18): 1. Resumen y Objetivos del Pipeline, 2. Diagrama de Flujo del Pipeline de Personajes, 3. Fases del Pipeline en Detalle, 4. Algoritmo de Conversión a `gf-anim-v1`, CHARACTER_ASSET_PIPELINE.md — GAMEFORGE 2D, El Problema del Temblor de Sprites (*Sprite Jitter / Wobble*), Fase 1: Detección de Disposición e Ingestión, Fase 2 y 3: Estabilización de Pivotes y Prevención del "Sprite Wobble" (+10 more)

### Community 48 - "Community 48"
Cohesion: 0.11
Nodes (19): 1. Política de Dependencias y Principios de Cumplimiento Legal, 2. Auditoría del Stack Actual de GameForge 2D, 3.10 pygame-topdownengine, 3.11 Procedural-Maps, 3.12 opensimplex-island-generator, 3.1 pygame-ce, 3.2 pymunk, 3.3 esper (+11 more)

### Community 49 - "Community 49"
Cohesion: 0.11
Nodes (18): 1. Resumen Ejecutivo y Marco Normativo, 2.1 `pygame-community/pygame-ce`, 2.2 `rsheet` (ELiijah-dev), 2.3 `SaxonRah/PySpine`, 2.4 `Retropaint/skelform`, 2.5 `pytransitions/transitions`, 2.6 `splintered-reality/py_trees`, 2.7 `etamowon/HitBox` (+10 more)

### Community 50 - "Community 50"
Cohesion: 0.14
Nodes (19): 2.12 opensimplex-island-generator, 2.1 pygame-ce (pygame Community Edition), 2.2 pymunk, Actividad y mantenimiento, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros (+11 more)

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (18): EN CURSO, T-000 — Fase 0: cimientos, T-101 — Fase 1: extraer `sim/` desde `play.py`, T-102 — Fase 1: enemigos data-driven, T-201 — Fase 2: multiplanta, misiones, A*, crafting, T-301 — Fase 3: Mundo grande y escala, T-401 — Fase 4: Presentación, Lienzo Virtual y Multi-ranura, T-501 — Fase 5: Distribución y empaquetado (+10 more)

### Community 54 - "Community 54"
Cohesion: 0.11
Nodes (17): 1.1. Misión, 1.2. Invariantes Arquitectónicos, 1. Misión, Requisitos No Funcionales e Invariantes del Sistema, 2. Diagrama de Arquitectura de Subsistemas, 3.1. `tools/asset_hub/scanner.py` (Servicio de Escaneo e Indexación), 3.2. `tools/asset_hub/db.py` (Base de Datos Local y Caché), 3.3. `tools/asset_hub/query.py` (Motor de Búsqueda Semántica para Agentes), 3.4. `tools/asset_hub/validator.py` (Sentinela de Validación Automática) (+9 more)

### Community 55 - "Community 55"
Cohesion: 0.23
Nodes (14): generate_dungeon(), GenerationError, is_reachable(), reachable_cells(), cell_of(), test_chest_contract(), test_deeper_floor_is_generated(), test_different_seed_changes_map() (+6 more)

### Community 56 - "Community 56"
Cohesion: 0.12
Nodes (16): 10. Riesgos y evolución, 1. Objetivo y alcance, 2. Principios, 3. Módulos y dirección de dependencias, 4. Bucle y escenas, 5.1 Tiles y colisión, 5.2 Generación, 5.3 Entidades y sistemas (+8 more)

### Community 57 - "Community 57"
Cohesion: 0.12
Nodes (16): 1. Resumen y Principios del Sistema UI, 2. Diagrama de Flujo del Pipeline UI, 3.1. Fundamento Matemático, 3.2. Implementación de Alto Rendimiento en Pygame CE, 3. El Motor de Escalado 9-Slice (9-Patch), 4. Máquina de Estados para Controles Interactivos, 5.1. Fuentes TrueType Pixel Art (`.ttf`), 5.2. Fuentes Bitmap (Texture Font Atlases) (+8 more)

### Community 58 - "Community 58"
Cohesion: 0.18
Nodes (5): test_validator_detects_missing_fields_and_overflow(), test_validator_on_canonical_manifest(), generate_enemy_assets(), main(), validate_character_manifest()

### Community 59 - "Community 59"
Cohesion: 0.18
Nodes (7): init_pygame(), test_agent_query_scenario(), test_db_crud_in_memory(), test_exporter_pipeline(), test_previewer_headless(), test_validator_rules(), AssetValidator

### Community 60 - "Community 60"
Cohesion: 0.12
Nodes (15): 1. Resumen Ejecutivo, 2. Diagrama del Flujo de Trabajo del Agente, 3. Guía Paso a Paso del Pipeline, 4. Matriz de Autochequeo para el Agente (Checklist del DoD), 5. Conclusión, AGENT_ANIMATION_WORKFLOW.md — GAMEFORGE 2D, Flujo de Trabajo Automatizado para Agentes de IA: Creación, Validación e Integración de Personajes y Animaciones, Paso 1: Definición Declarativa de la Ficha del Personaje (+7 more)

### Community 61 - "Community 61"
Cohesion: 0.12
Nodes (15): Contratos de interfaces — borrador inicial, Contratos propuestos para expansión (v0.2.0), Entity, Events, `game.ai.astar`, `game.ai.behavior`, `game.data.catalog`, Game loop (+7 more)

### Community 62 - "Community 62"
Cohesion: 0.12
Nodes (15): 1. Resumen y Propósito del Pipeline, 2. Diagrama de Flujo del Pipeline de Mapas y Tilesets, 3. Fases del Pipeline en Detalle, Algoritmo 3x3 Blob Bitmasking (47 Tiles), El Problema de las Fisuras en Tilesets, Fase 1 y 2: Slicing, Normalización y Prevención de Fisuras (*Seam Bleeding*), Fase 3: Clasificación Semántica de Terrenos y Objetos, Fase 4: Autotiling Universal (Blob 47 y Wang 16) (+7 more)

### Community 63 - "Community 63"
Cohesion: 0.30
Nodes (10): AttackSpec, attack_hits_enemy(), resolve_player_attack(), make_enemy(), spec(), test_attack_can_hit_multiple_and_kill(), test_attack_hits_front_target(), test_attack_ignores_behind_and_side() (+2 more)

### Community 64 - "Community 64"
Cohesion: 0.13
Nodes (14): 1. Principios Fundamentales del Diseño, 2. Diagrama General de Componentes, 3. Desglose Detallado por Capas, 4.1 Ciclo de Vida del Fotograma (Frame Lifecycle), 4.2 Máquina de Estados de Escenas, 4. Diagramas de Flujo y Ciclo de Vida, 5. Asignación del Presupuesto de Rendimiento (Frame Budget), 6. Garantías Arquitectónicas y Directivas de Calidad (+6 more)

### Community 65 - "Community 65"
Cohesion: 0.13
Nodes (13): Directiva de eficiencia de tokens (05_TOKEN_EFFICIENCY.md), 10. Regla final, 1. Principio general, 2. Lectura selectiva, 3. Investigación externa, 4. Comunicación entre agentes, 5. Prevención de duplicación, 6. Gestión del contexto (+5 more)

### Community 66 - "Community 66"
Cohesion: 0.13
Nodes (14): 1. Resumen Ejecutivo y Misión del Sistema, 2. Evaluación Comparativa de los 7 Repositorios Prioritarios, 3.1. Redundancia 1: Superposición de Parsers Sintácticos de Código, 3.2. Redundancia 2: Motores Pesados de Grafos de Memoria, 3.3. Redundancia 3: Frameworks Pesados de Orquestación de Agentes, 3. Detección de Redundancias y Criterios de Poda, 4.1. Almacenamiento Local Único: SQLite WAL, 4. Arquitectura Mínima Unificada: GameForge Graph (`GF-Graph`) (+6 more)

### Community 67 - "Community 67"
Cohesion: 0.13
Nodes (14): 1. Visión y Principios del Stack, 2.1 Lenguaje Principal: Python 3.11+ (CPython), 2.2 Framework Multimedia y Capa de Presentación: Pygame CE (Community Edition >= 2.5), 2.3 Simulación Física y Resolución de Colisiones: Motor Propio Tile-Based ($O(1)$), 2.4 Arquitectura de Entidades: Catálogos Data-Driven vs. ECS Completo (Esper), 2.5 Autoría y Generación de Mapas: Enfoque Híbrido (Tiled Map Editor + Generador Procedural BFS), 2.6 Inteligencia Artificial y Navegación: A\* Propio con Cuota de CPU y Caché LRU, 2.7 Persistencia de Datos: Arquitectura Dual (JSON Atómico + SQLite) (+6 more)

### Community 68 - "Community 68"
Cohesion: 0.20
Nodes (3): Enemy, EnemyIntent, nearest_enemy_position()

### Community 69 - "Community 69"
Cohesion: 0.14
Nodes (13): 1. Resumen Ejecutivo y Motivación Jurídica, 2. Distinción Jurídica Esencial: Código Software vs. Activos Creativos, 3. Taxonomía de Cumplimiento de Licencias (Los 4 Niveles de Riesgo), 4. Trazabilidad Criptográfica de Procedencia: Manifiesto Sidecar `.meta.json`, 5. Prevención Automatizada de Contaminación en CI / Pre-Commit, 6. Generador Automático de Créditos y SBOM (`CREDITS.md`), Doctrina de la "Mera Agregación" (*Mere Aggregation*), Estructura Normativa del Manifiesto de Procedencia (+5 more)

### Community 70 - "Community 70"
Cohesion: 0.14
Nodes (13): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+5 more)

### Community 71 - "Community 71"
Cohesion: 0.14
Nodes (13): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+5 more)

### Community 72 - "Community 72"
Cohesion: 0.14
Nodes (13): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+5 more)

### Community 73 - "Community 73"
Cohesion: 0.23
Nodes (7): find_graphify_python(), run_graphify_script(), main(), _module_available(), _parse_p95(), run_bench(), run_step()

### Community 75 - "Community 75"
Cohesion: 0.21
Nodes (4): DialogManager, PersonaInfo, test_dialog_generation_contextual(), test_nemotron_personas_loaded_with_uuids()

### Community 76 - "Community 76"
Cohesion: 0.15
Nodes (13): Contratos concretos implementados (v0.1.0), Enemigos, Escenas, `game.core.config`, `game.core.math2d.Vec2`, `game.input`, `game.world.collision`, `game.world.generation` (+5 more)

### Community 77 - "Community 77"
Cohesion: 0.15
Nodes (11): Registro de decisiones (DECISION_LOG.md), ADR-001 — Pygame CE como framework, ADR-002 — No introducir Pymunk en este vertical slice, ADR-003 — Arte y audio procedurales, sin assets externos, ADR-004 — JSON para partida y SQLite para clasificación, ADR-005 — Vertical slice de una planta, ADR-006 — Sin bus de eventos global, ADR-007 — Determinismo y validación de mapas (+3 more)

### Community 78 - "Community 78"
Cohesion: 0.15
Nodes (12): 1. Índice de Algoritmos Optimizados, 2. Especificación Detallada de Algoritmos, ALG-01: Validación Topológica BFS y Flood Fill, ALG-02: A\* con Cuota de CPU (Budgeting) y Caché LRU, ALG-03: Partición Espacial por Spatial Hash, ALG-04: Resolución Anti-Tunneling Círculo vs. Tiles Sólidos, ALG-05: Máscara de Decaimiento Radial para Terrenos Orgánicos, ALG-06: Matriz de Biomas Whittaker (Implementación Cleanroom) (+4 more)

### Community 79 - "Community 79"
Cohesion: 0.15
Nodes (12): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+4 more)

### Community 80 - "Community 80"
Cohesion: 0.15
Nodes (12): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+4 more)

### Community 81 - "Community 81"
Cohesion: 0.15
Nodes (12): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+4 more)

### Community 82 - "Community 82"
Cohesion: 0.15
Nodes (12): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+4 more)

### Community 83 - "Community 83"
Cohesion: 0.15
Nodes (12): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+4 more)

### Community 84 - "Community 84"
Cohesion: 0.15
Nodes (12): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+4 more)

### Community 85 - "Community 85"
Cohesion: 0.37
Nodes (10): separate_enemies(), enemy(), make_map(), test_brute_charge_state_machine(), test_damage_and_death(), test_separation_pushes_enemies_apart(), test_slime_chases_player(), test_strafe_direction_is_deterministic() (+2 more)

### Community 86 - "Community 86"
Cohesion: 0.23
Nodes (3): Lighting, draw_lighting(), draw_play_overlay()

### Community 88 - "Community 88"
Cohesion: 0.17
Nodes (11): 1. Resumen y Principios de Diseño, 2. Definición Formal: JSON Schema (Draft 2020-12), 3.1. Manifiesto de Personaje Humanoide (Compatible LPC), 3.2. Manifiesto de Tileset de Mazmorra (Estilo Kenney / Roguelike 32x32), 3.3. Manifiesto de Componente UI (Panel de Diálogo 9-Slice), 3.4. Manifiesto de Icono de Objeto / Equipamiento, 3. Ejemplos Concretos de Manifiestos de Recursos, 4. Esquema de Base de Datos para Indexación Rápida (SQLite) (+3 more)

### Community 89 - "Community 89"
Cohesion: 0.17
Nodes (11): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+3 more)

### Community 90 - "Community 90"
Cohesion: 0.17
Nodes (11): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+3 more)

### Community 91 - "Community 91"
Cohesion: 0.17
Nodes (11): 1. Propósito, 2. Contexto de aplicación, 3. Instrucciones, 4. Buenas prácticas, 5. Referencias técnicas, 6. Procedimientos, 7. Criterios de aceptación, 8. Pruebas recomendadas (+3 more)

### Community 93 - "Community 93"
Cohesion: 0.36
Nodes (4): main(), percentile(), main(), percentile()

### Community 94 - "Community 94"
Cohesion: 0.18
Nodes (10): 1. Resumen y Propósito, 2. Definición Formal: JSON Schema (Draft 2020-12), 3. Ejemplo Canónico Completo: Personaje "Knight Hero", 4.1 Importación desde Aseprite JSON, 4.2 Importación desde `rsheet` (`frame_coords.txt` + `frame_norm_cache.txt`), 4.3 Importación desde `PySpine` (`sprite_project.json` + `bone_animation.json`), 4. Estrategia de Conversión desde Herramientas Externas, 5. Reglas de Validación y Consistencia para Agentes (+2 more)

### Community 95 - "Community 95"
Cohesion: 0.29
Nodes (8): angle_difference(), clamp(), lerp(), normalize_angle(), test_angles_are_normalized(), test_clamped_limits_length(), test_normalized_and_zero_vector(), test_scalar_helpers()

### Community 97 - "Community 97"
Cohesion: 0.47
Nodes (10): make_map(), player_at(), test_attack_creates_spec_and_cooldown(), test_collision_blocks_wall(), test_damage_has_invulnerability_window(), test_dash_grants_invulnerability_and_distance(), test_heal_is_capped(), test_lava_deals_continuous_damage() (+2 more)

### Community 103 - "Community 103"
Cohesion: 0.22
Nodes (8): AGENTS.md — GAMEFORGE 2D, Coordinación multiagente, Definición de terminado (DoD), Misión, Orden de autoridad, Protocolo de trabajo, Reglas obligatorias, Rendimiento

### Community 104 - "Community 104"
Cohesion: 0.25
Nodes (4): Matriz de propiedad de archivos — GAMEFORGE 2D, Procedimiento de cambio, Política de Licencias y Dependencias, Referencias de código abierto — GAMEFORGE 2D

### Community 105 - "Community 105"
Cohesion: 0.22
Nodes (8): 1. Controles Oficiales, 2. Mecánicas de Juego, ⚔️ Combate y Esquiva, ⚗️ Fabricación Alquímica (Crafting), 💾 Gestión de Partidas Guardadas, Manual del Jugador — GAMEFORGE 2D: La Fragua Olvidada, 🏰 Progresión Multiplanta (3 Niveles Subterráneos), 📜 Sistema de Misiones Secundarias

### Community 106 - "Community 106"
Cohesion: 0.22
Nodes (9): 2.10 pygame-topdownengine, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 107 - "Community 107"
Cohesion: 0.22
Nodes (9): 2.11 Procedural-Maps, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 108 - "Community 108"
Cohesion: 0.22
Nodes (9): 2.3 esper, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 109 - "Community 109"
Cohesion: 0.22
Nodes (9): 2.4 Tiled, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 110 - "Community 110"
Cohesion: 0.22
Nodes (9): 2.5 pytmx, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 111 - "Community 111"
Cohesion: 0.22
Nodes (9): 2.6 tilemap-generator, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 112 - "Community 112"
Cohesion: 0.22
Nodes (9): 2.7 python-tcod, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 113 - "Community 113"
Cohesion: 0.22
Nodes (9): 2.8 py_trees, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 114 - "Community 114"
Cohesion: 0.22
Nodes (9): 2.9 SolarWolf, Actividad y mantenimiento, Análisis arquitectónico y organización interna, Código a estudiar vs. implementar nosotros, Dependencias, licencias y compatibilidad, Ejemplos y pruebas reales, Evaluación, Rendimiento y consumo de memoria (+1 more)

### Community 115 - "Community 115"
Cohesion: 0.22
Nodes (8): 1. Resumen Ejecutivo, 2. Entregables Generados, 3. Archivos Afectados, 4. Resultados de Verificación Real, 5. Criterios de Aceptación (DoD), Creados:, Informe de Entrega — Tarea T-601 (Investigación de Repositorios y Arquitectura), Modificados:

### Community 116 - "Community 116"
Cohesion: 0.22
Nodes (9): Directive: 01_GLOBAL.md, Directive: 02_ARCHITECTURE.md, Directive: 03_QUALITY_AND_SECURITY.md, Directive: 04_INTEGRATION.md, Directive: 05_TOKEN_EFFICIENCY.md, Directive: ARCHITECTURE.md, Directive: QUALITY_AND_SECURITY.md, Directive: TOKEN_EFFICIENCY.md (+1 more)

### Community 117 - "Community 117"
Cohesion: 0.39
Nodes (4): QuestState, test_invalid_requirement(), test_quest_activation_requires_shards(), test_quest_activation_still_works_with_sim()

### Community 118 - "Community 118"
Cohesion: 0.25
Nodes (7): Cobertura funcional, Cómo ejecutar, Estrategia y resultados de pruebas, Limitaciones, Pruebas de integración, Pruebas manuales recomendadas, Resultados

### Community 119 - "Community 119"
Cohesion: 0.25
Nodes (8): Arquitectura de Capas Puras, Comandos de Utilidad y Verificación, Con el gestor de entornos `uv` (Recomendado), Con venv tradicional de Python, Controles del Juego, Cómo Ejecutar, Estado del Proyecto (Fases 0 a 5), GAMEFORGE 2D — La Fragua Olvidada

### Community 120 - "Community 120"
Cohesion: 0.25
Nodes (7): 1. Resumen Ejecutivo, 2. Archivos Afectados, 3. Resultados de Verificación Real, 4. Criterios de Aceptación (DoD), Creados:, Informe de Entrega — Tarea T-201 (Fase 2: Núcleo RPG), Modificados:

### Community 121 - "Community 121"
Cohesion: 0.25
Nodes (7): 1. Resumen Ejecutivo, 2. Archivos Afectados, 3. Resultados de Verificación Real, 4. Criterios de Aceptación (DoD), Creados:, Informe de Entrega — Tarea T-301 (Fase 3: Mundo Grande y Escala), Modificados:

### Community 122 - "Community 122"
Cohesion: 0.25
Nodes (7): 1. Resumen Ejecutivo, 2. Archivos Afectados, 3. Resultados de Verificación Real, 4. Criterios de Aceptación (DoD), Creados:, Informe de Entrega — Tarea T-401 (Fase 4: Presentación, Lienzo Virtual y Multi-ranura), Modificados:

### Community 123 - "Community 123"
Cohesion: 0.25
Nodes (7): 1. Resumen Ejecutivo, 2. Archivos Afectados, 3. Resultados de Verificación Real, 4. Criterios de Aceptación (DoD), Creados:, Informe de Entrega — Tarea T-501 (Fase 5: Distribución, Empaquetado y Cierre), Modificados:

### Community 124 - "Community 124"
Cohesion: 0.25
Nodes (7): Archivos Modificados, Criterios de Aceptación, Decisiones Técnicas, Limitaciones y Riesgos, Objetivo, T-602 — Expansión Mecánicas: Salto 2.5D, Cavernas, Swarm AI y Hub Narrativo, Verificación

### Community 125 - "Community 125"
Cohesion: 0.25
Nodes (7): 1. Resumen Ejecutivo, 2. Archivos Modificados y Creados, 3. Resultados de Verificación Real, 4. Estado de Cumplimiento (DoD), Creados:, Informe de Entrega — Tarea T-701 (Implementación del Núcleo de Animación gf-anim-v1, Efectos Mejorados y Validación), Modificados:

### Community 128 - "Community 128"
Cohesion: 0.29
Nodes (5): Capas del sistema:, Directiva de arquitectura (02_ARCHITECTURE.md), Estructura de capas y jerarquía de dependencias, Reglas obligatorias, Directiva de arquitectura (ARCHITECTURE.md)

### Community 129 - "Community 129"
Cohesion: 0.29
Nodes (5): Calidad, seguridad y rendimiento (03_QUALITY_AND_SECURITY.md), Criterios mínimos de aceptación (DoD), Seguridad y robustez, Umbrales y control de rendimiento, Directiva de calidad, seguridad y rendimiento (QUALITY_AND_SECURITY.md)

### Community 130 - "Community 130"
Cohesion: 0.29
Nodes (6): Archivos Modificados / Creados, Atribución del Dataset de Personajes, Criterios de Aceptación, Objetivo, T-603 — Integración del Sistema: Swarm AI, Diálogos Nemotron El Salvador, Cavernas Dinámicas y Colisión de Techos, Verificación

### Community 132 - "Community 132"
Cohesion: 0.33
Nodes (5): Alcance del proyecto, Calidad y disciplina, Directiva global (01_GLOBAL.md), Principios, Propósito

### Community 133 - "Community 133"
Cohesion: 0.33
Nodes (5): Assets, Dependencias y licencias, Desarrollo y pruebas, Runtime, Verificación de licencias

### Community 134 - "Community 134"
Cohesion: 0.33
Nodes (6): 2.1 Motor de renderizado 2D principal, 2.2 Física y colisiones, 2.3 Generación y autoría de mapas, 2.4 Navegación e Inteligencia Artificial de NPCs, 2.5 Persistencia y versiones de Python, 2. COMPARACIÓN TECNOLÓGICA

### Community 135 - "Community 135"
Cohesion: 0.33
Nodes (6): 1. Metodología de Evaluación y Criterios, 2. Análisis Detallado por Repositorio, 3. Matriz Comparativa Global y Clasificación, 4. Síntesis Ejecutiva y Hallazgos Críticos, Escala de Puntuación (1 a 10), GAMEFORGE 2D — INVESTIGACIÓN EXHAUSTIVA DE REPOSITORIOS

### Community 136 - "Community 136"
Cohesion: 0.33
Nodes (5): 1. Resumen Ejecutivo, 2. Entregables Generados, 3. Resultados de Verificación Real, 4. Estado de Cumplimiento (DoD), Informe de Entrega — Tarea T-604 (Investigación de Sprites, Animaciones y Lógica de Personajes)

### Community 137 - "Community 137"
Cohesion: 0.33
Nodes (5): 1. Resumen Ejecutivo, 2. Archivos Afectados, 3. Pruebas y Verificación, Informe de Tarea T-702, Metadatos

### Community 139 - "Community 139"
Cohesion: 0.40
Nodes (4): Copyleft Artístico / ShareAlike (CC-BY-SA 3.0 / 4.0, GPLv3), CRÉDITOS Y PROCEDENCIA DE RECURSOS — GAMEFORGE 2D, Dominio Público (CC0 1.0 Universal / Unlicense), Licencias Permisivas con Atribución (CC-BY 3.0 / 4.0, MIT, OGA-BY)

### Community 140 - "Community 140"
Cohesion: 0.40
Nodes (4): Directiva de integración multiagente (04_INTEGRATION.md), Estructura del informe de entrega (`tasks/reports/T-XXX.md`), Flujo de trabajo estándar, Prohibiciones estrictas

### Community 142 - "Community 142"
Cohesion: 0.50
Nodes (3): Benchmarks, Condiciones a registrar, Qué miden

## Knowledge Gaps
- **838 isolated node(s):** `ItemDef`, `TileDef`, `Misión`, `Orden de autoridad`, `Reglas obligatorias` (+833 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1428 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **74 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Application` connect `Community 27` to `Community 32`, `Community 1`, `Community 0`, `Community 101`, `Community 6`, `Community 17`, `Community 53`, `Community 26`, `Community 31`?**
  _High betweenness centrality (0.002) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TileMap` (e.g. with `Vec2` and `TileType`) actually correct?**
  _`TileMap` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ItemDef`, `TileDef`, `Misión` to the rest of the system?**
  _838 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.0819252432155658 - nodes in this community are weakly interconnected._
- **Why does `MenuScene` connect `Community 0` to `Community 32`, `Community 3`, `Community 6`, `Community 7`, `Community 24`?**
  _High betweenness centrality (0.002) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `PlayScene` (e.g. with `DijkstraMap` and `Vec2`) actually correct?**
  _`PlayScene` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06504494976203067 - nodes in this community are weakly interconnected._
# Contratos de interfaces — borrador inicial

Estos contratos son acuerdos mínimos. El director debe convertirlos en interfaces concretas al inspeccionar el repositorio.

## Game loop
- Inicializa plataforma, configuración y recursos.
- Procesa eventos de entrada.
- Actualiza simulación con delta time controlado.
- Renderiza estado.
- Libera recursos al cerrar.

## Input
La capa de entrada expone acciones abstractas como `move_left`, `move_right`, `interact`, `inventory` y `pause`. Los sistemas no deben depender de teclas físicas concretas.

## Entity
Una entidad debe tener identidad estable, estado serializable cuando corresponda y límites de colisión definidos. No todas las entidades necesitan heredar de una clase base común.

## World
El mundo expone consulta de colisión y acceso a tiles/escenas. La generación de mapa debe aceptar semilla para ser reproducible.

## Inventory
- `add(item_id, quantity) -> result`
- `remove(item_id, quantity) -> result`
- `count(item_id) -> int`
- Validar cantidades positivas y límites de capacidad.
- No permitir cantidades negativas.

## Persistence
- Guardado con versión de esquema.
- Carga validada y con errores explícitos.
- Migración documentada cuando cambie el formato.
- Guardado atómico cuando sea posible (archivo temporal + reemplazo).

## Events
Los eventos deben ser datos simples y documentados. Evitar un bus global si una llamada directa es suficiente.

## Regla
Ningún agente puede cambiar un contrato compartido sin propuesta, análisis de impacto y aprobación del director.

---

# Contratos concretos implementados (v0.1.0)

Estos contratos describen el vertical slice actual. Cualquier cambio de firma
pública requiere análisis de impacto y actualización de tests.

## `game.core.config`
- `load_config(path: str | Path | None = None) -> GameConfig`.
- Lanza `ConfigError` con mensaje accionable si falta el archivo, el JSON es
  inválido o un valor está fuera de rango.
- `GameConfig` es inmutable (`frozen`), incluye `window`, `player`, `dungeon`,
  `enemies` y `audio`.
- No importa pygame.

## `game.core.math2d.Vec2`
- Operaciones `+`, `-`, `*`, `/`, `-` unario.
- `normalized()` devuelve `(0, 0)` para el vector nulo; nunca lanza por longitud 0.
- `clamped(max_length)` nunca devuelve un vector de longitud mayor.
- División por cero lanza `ZeroDivisionError`.

## `game.input`
- `Action` enumera acciones abstractas; ninguna entidad consulta teclas.
- `InputMapper.handle_event(event)` actualiza estado; `begin_frame()` limpia
  solo lo pulsado en el frame anterior.
- `move_vector()` devuelve un `Vec2` normalizado (o cero).
- `mouse_was_pressed(button)` es de un solo frame.

## `game.world.tilemap.TileMap`
- `tile_at(col, row)` devuelve `WALL` fuera de límites.
- `is_solid_at(x, y)` consulta el tile que contiene el punto.
- `speed_multiplier_at` y `hazard_damage_at` aplican las propiedades del tile.
- `set_tile` fuera de límites lanza `IndexError`.
- La matriz debe coincidir con `width`/`height`; si no, `ValueError`.

## `game.world.collision`
- `move_circle(map, start, radius, delta, max_step=4.0) -> CollisionResult`.
- Nunca deja el círculo dentro de un tile sólido si el punto de partida era
  válido; subdivide para evitar tunneling.
- `max_step <= 0` lanza `ValueError`.
- `has_line_of_sight(map, start, end, step=6.0)` devuelve `False` si algún
  muestreo cae en tile sólido.

## `game.world.generation`
- `generate_dungeon(seed, floor=1, config=None, attempts=10) -> Dungeon`.
- Mismo `(seed, floor, config)` => mismos tiles, salas, spawn, altar, cofres y
  enemigos.
- IDs de cofres y enemigos únicos y estables.
- El spawn, altar, hoguera y todos los cofres son alcanzables por BFS.
- Si no se consigue un mapa válido, lanza `GenerationError`.

## Jugador
- `Player.update(dt, move, aim, dash, attack, tilemap)` no devuelve nada; deja
  `pending_attack` como máximo una vez por golpe y `dash_started` para eventos.
- `take_damage(amount, source=None) -> bool` respeta i-frames y devuelve si
  aplicó daño.
- `heal(amount) -> float` devuelve la curación efectiva y nunca supera el máximo.

## Enemigos
- `Enemy.update(dt, player_position, player_radius, tilemap, rng) -> EnemyIntent`.
- No crean proyectiles ni efectos: la escena materializa la intención.
- `Enemy.take_damage(amount, source=None, knockback_force=0.0) -> bool` devuelve
  `True` si aplicó el daño (la muerte se consulta con `enemy.alive`), igual que
  el jugador.
- `separate_enemies(enemies, tilemap)` mantiene a los enemigos fuera de paredes.

## Inventario
- `add(item_id, quantity) -> int` devuelve la cantidad aceptada (0 si no cabe).
- `remove(item_id, quantity) -> int` devuelve la cantidad retirada.
- Cantidades no enteras, <= 0 o booleanos lanzan `InventoryError`.
- `from_dict` valida objetos conocidos, cantidades 1..9999 y capacidad.
- `to_dict` devuelve claves ordenadas para guardados estables.

## Persistencia
- `save_run(path, RunSnapshot)` valida antes de escribir y usa reemplazo atómico.
- `load_run(path) -> SaveData` valida tamaño, JSON, esquema y todos los campos.
- `schema_version` desconocida o inferior sin migración => `SaveGameError`.
- `delete_save(path) -> bool` no falla si el archivo no existe.
- `ScoreRepository.record(RunResult) -> int` valida y devuelve el id insertado.
- `ScoreRepository.top(limit=10, victories_only=False)` ordena por score,
  duración y id.

## Escenas
- `Scene` expone `on_enter`, `on_exit`, `handle_event`, `update(dt)` y `draw`.
- `Application.replace_scene` llama a `on_exit` de la anterior y `on_enter` de la
  nueva.
- Las escenas pueden reemplazarse durante `update`; el bucle dibuja la escena
  resultante.
- El `dt` que recibe `update` está limitado a 0.05 s.

## Persistencia de progreso
- Al cargar, el mapa se regenera desde la semilla y se aplican:
  posición/salud, inventario, cofres abiertos, enemigos derrotados y estado del
  altar.
- Si la posición guardada está dentro de un tile sólido, se usa el spawn.
- Al terminar (muerte o victoria) se borra el guardado para no reanudar un
  estado terminal.


---

# Contratos propuestos para expansión (v0.2.0)

## `game.ai.astar`
- `find_path(tilemap: TileMap, start: Vec2, goal: Vec2, budget_ms: float = 1.5) -> list[Vec2] | None`
- Garantía de tiempo: Nunca excede `budget_ms`. Si se agota el tiempo, devuelve la mejor ruta parcial calculada hasta el momento o `None`.
- Determinismo: Ante idéntica terna `(tilemap, start, goal)`, devuelve la misma secuencia de nodos.
- Sin estado global mutable: Las estructuras auxiliares son locales o reutilizadas desde un contexto inyectado.
- Caché LRU de rutas parametrizada por `(floor, goal_tile)`.

## `game.ai.behavior`
- Comportamientos completamente dirigidos por datos cargados desde `game/data/enemies.json`.
- `tick(entity: Enemy, ctx: SimulationContext, dt: float) -> EnemyIntent`.
- Generación pura: Retorna intenciones de movimiento y ataque sin mutar el mundo ni invocar APIs de render.

## `game.sim.floor`
- `advance_floor(current_floor: int, seed: int, result: DungeonResult) -> FloorTransition`
- Determinista por `(seed, floor)`: Regenera el siguiente piso con dificultad y número de enemigos escalados.
- Preservación de estado: Traspasa salud del jugador, inventario acumulado y misiones activas.

## `game.data.catalog`
- Todo cargador de catálogo expone `load_xxx(path: Path) -> dict[str, ItemDefinition]` con validación estricta de tipos (`CatalogError`).
- Inmutabilidad: Devuelve objetos inmutables (`frozen dataclasses`).
- Validación al arrancar: Cero errores diferidos al momento de combate.

## `game.render.canvas`
- Desacoplamiento de resolución lógica (diseño fijo 1280x720) y física de ventana.
- `map_mouse_to_logical(pos: tuple[int, int]) -> tuple[int, int] | None`: Mapeo transparente con corrección de letterbox/pillarbox para las escenas.

---

# Contratos de Herramientas y Memoria Operativa (v0.3.0)

## `tools.graph_ops` / `tools.graph_memory`
- **Aislamiento:** Se ejecuta en un entorno aislado (`uv tool` / `graphifyy`) sin contaminar las dependencias del runtime de `game/`.
- **`GraphEngine.build_initial_graph(agent_id: str) -> dict`**:
  - Extrae AST determinista de Python (cero tokens de LLM).
  - Extrae estructura de documentos Markdown y vincula menciones de código.
  - Extrae ontología de decisiones (`documentation/DECISIONS.md`, `tasks/BOARD.md`, directivas y contratos).
  - Genera `graphify-out/graph.json` y `GRAPH_REPORT.md`.
  - Registra el evento en `graphify-out/audit.log` y actualiza `.manifest.json`.
- **`GraphEngine.update_incremental(changed_paths, deleted_paths, agent_id) -> dict`**:
  - Detecta *drift* vía hash SHA-256. Re-extrae únicamente el delta modificado en < 300 ms.
  - Poda nodos huérfanos de archivos eliminados.
- **`GraphEngine.query(question: str, agent_id: str) -> dict`**:
  - Recorrido semántico y filtrado de símbolos sin volcar archivos masivos en el contexto.
- **`GraphEngine.affected(node_id: str, depth: int = 2, agent_id: str) -> dict`**:
  - Travesía inversa para cálculo determinista de dependientes y radio de explosión (*blast radius*).
- **`ManifestTracker.check_drift() -> DriftReport`**:
  - Retorna `is_fresh: bool`, listas de archivos `modified`, `added`, `deleted` y `renamed`.
  - Criterio estricto: falla (`exit code 1`) si el sistema de archivos no coincide con el manifiesto.
- **Servidor MCP (`graphify-mcp`)**:
  - Transporte `stdio` para agentes locales y `Streamable HTTP` para orquestadores.
  - Expone herramientas estándar: `query_graph`, `get_node`, `get_neighbors`, `god_nodes`, `graph_stats`, `shortest_path`.
  - Hot-reload automático de `graph.json` ante cambios en disco.

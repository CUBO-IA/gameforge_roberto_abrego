# GAMEFORGE 2D — PROPUESTA ARQUITECTÓNICA DEFINITIVA

**Documento:** `ARCHITECTURE_PROPOSAL.md`  
**Rol:** Arquitecto Principal de GameForge 2D  
**Fecha:** 2026-11-06  
**Estado:** PROPUESTA ARQUITECTÓNICA CONSOLIDADA  
**Alineación:** Contratos de `architecture/CONTRACTS.md`, Directivas de `directives/02_ARCHITECTURE.md` y Auditoría en `GAMEFORGE_2D_ARCHITECTURE_REVIEW.md`.

---

## 1. Principios Fundamentales del Diseño

La arquitectura de GameForge 2D ha sido diseñada bajo cinco pilares no negociables:

1. **Flujo Unidireccional de Dependencias:** Cero ciclos de importación. Las capas superiores dependen de las inferiores; las inferiores jamás conocen a las superiores:
   $$\text{core} \longleftarrow \text{world} \longleftarrow \text{entities} \longleftarrow \text{ai} \longleftarrow \text{sim} \longleftarrow \text{scenes} \longleftarrow \text{app}$$
2. **Pureza del Dominio (Zero Pygame en la Lógica):** Las capas de matemáticas, mundo, entidades, IA, simulación y persistencia son código Python estándar puro. No importan `pygame` ni dependen de contextos gráficos, lo que permite testear el 100% de la lógica en milisegundos sin inicializar vídeo.
3. **Contenido Dirigido por Datos (Data-Driven Design):** Cero subclases de código por cada tipo de enemigo, ítem, receta o misión. Las estadísticas, comportamientos y recursos residen en esquemas JSON auditados en `game/data/`.
4. **Presupuesto de CPU por Fotograma (Frame Budget):** Para garantizar 60 FPS estables en cualquier equipo (16.67 ms por frame), la simulación completa tiene un presupuesto máximo estricto de **2.0 ms** en p95, reservando los 14.67 ms restantes para renderizado, compositing y sincronización vertical.
5. **Determinismo y Resiliencia Atómica:** El estado del mundo es reproducible mediante semillas enteras (`int`). La persistencia utiliza reemplazo atómico de archivos para impedir la corrupción de partidas ante fallos eléctricos o cierres inesperados.

---

## 2. Diagrama General de Componentes

```mermaid
graph TD
    subgraph PRESENTACION ["Capa 5 & 6: Presentación, Entrada y Escenas (Pygame CE)"]
        APP["app.py (Game Loop, Reloj dt <= 50ms)"]
        INPUT["input/actions.py (Mapeo de Teclas a Acciones)"]
        CANVAS["render/canvas.py (Lienzo Virtual 1280x720)"]
        WORLD_VIEW["render/world_view.py (Culling y Renderizado)"]
        HUD_VIEW["render/hud_view.py (Barras, Inventario, Texto)"]
        AUDIO_MGR["render/audio.py (Sintetizador SFX y Degradación)"]
        SCENE_MGR["scenes/ (Menu, Play, Pause, Scores, Results)"]
    end

    subgraph SIMULACION ["Capa 4: Simulación Pura (Sin Pygame)"]
        SIM_COMBAT["sim/combat.py (Golpes, Daño, Knockback, Loot)"]
        SIM_INTERACT["sim/interaction.py (Cofres, Altar, Hoguera)"]
        SIM_FLOOR["sim/floor.py (Transición y Escalado de Pisos)"]
        SIM_QUEST["sim/quest.py (Progreso de Misiones)"]
        SIM_CRAFT["sim/crafting.py (Recetas Alquímicas Atómicas)"]
    end

    subgraph ENTIDADES_IA ["Capa 2 & 3: Entidades, Catálogos e Inteligencia Artificial"]
        PLAYER["entities/player.py (Cinemática, Dash, Inventario)"]
        ENEMY["entities/enemies.py (FSM, Intenciones de Enemigo)"]
        CATALOG["entities/enemy_catalog.py (Arquetipos JSON)"]
        AI_ASTAR["ai/astar.py (Búsqueda de Caminos A* Cuotada <= 1.5ms)"]
    end

    subgraph MUNDO_FISICA ["Capa 1: Mundo, Topología y Partición Espacial"]
        WORLD_MAP["world/tilemap.py (Matriz de Celdas y Propiedades)"]
        WORLD_COLL["world/collision.py (Círculo vs Tiles, Anti-tunneling)"]
        WORLD_SPATIAL["world/spatial.py (Spatial Hash O(1))"]
        WORLD_GEN["world/generation.py (Salas y Corredores BFS)"]
        WORLD_TILED["world/tiled_loader.py (Cargador Mapas Tiled JSON)"]
    end

    subgraph CORE_PERSISTENCIA ["Capa 0: Core Inmutable, Matemáticas y Persistencia"]
        CORE_CONFIG["core/config.py (Configuración Inmutable)"]
        CORE_MATH["core/math2d.py (Vec2 Determinista)"]
        PERSIST_SAVE["persistence/savegame.py (Guardado Atómico JSON)"]
        PERSIST_SCORE["persistence/scores.py (Clasificación SQLite)"]
        DATA_FILES["data/*.json (enemies, quests, recipes, config)"]
    end

    APP --> INPUT
    APP --> SCENE_MGR
    SCENE_MGR --> CANVAS
    CANVAS --> WORLD_VIEW
    CANVAS --> HUD_VIEW
    SCENE_MGR --> AUDIO_MGR

    SCENE_MGR --> SIM_COMBAT
    SCENE_MGR --> SIM_INTERACT
    SCENE_MGR --> SIM_FLOOR
    SCENE_MGR --> SIM_QUEST
    SCENE_MGR --> SIM_CRAFT
    SCENE_MGR --> PERSIST_SAVE
    SCENE_MGR --> PERSIST_SCORE

    SIM_COMBAT --> PLAYER
    SIM_COMBAT --> ENEMY
    SIM_COMBAT --> WORLD_COLL
    SIM_COMBAT --> WORLD_SPATIAL

    ENEMY --> AI_ASTAR
    ENEMY --> CATALOG
    CATALOG --> DATA_FILES
    AI_ASTAR --> WORLD_MAP

    PLAYER --> WORLD_COLL
    ENEMY --> WORLD_COLL
    WORLD_COLL --> WORLD_MAP
    WORLD_GEN --> WORLD_MAP
    WORLD_TILED --> WORLD_MAP

    WORLD_MAP --> CORE_MATH
    PLAYER --> CORE_MATH
    ENEMY --> CORE_MATH
    CORE_CONFIG --> DATA_FILES
```

---

## 3. Desglose Detallado por Capas

### Capa 0: Core y Persistencia (`game/core/` y `game/persistence/`)
- **`game.core.math2d.Vec2`:** Vector 2D inmutable/puro. Operaciones vectoriales básicas, normalización segura (vector nulo devuelve `(0, 0)` sin lanzar división por cero), limitación de longitud (`clamped`) y distancia euclidiana y Manhattan.
- **`game.core.config.GameConfig`:** Configuración inmutable cargada desde `game/data/config.json`. Define parámetros de ventana, jugador, generación y audio. Lanza `ConfigError` si faltan claves obligatorias.
- **`game.persistence.savegame`:** Guardado atómico de partidas (`RunSnapshot`). Valida esquema y tipos. Escribe en archivo temporal (`.save.tmp`) y ejecuta `os.replace()`.
- **`game.persistence.scores.ScoreRepository`:** Repositorio SQLite local (`scores.db`) para almacenar récords, tiempos y estadísticas históricas.

### Capa 1: Mundo y Físicas (`game/world/`)
- **`game.world.tilemap.TileMap`:** Almacén bidimensional de celdas. Expone consultas de solidez (`is_solid_at`), multiplicadores de velocidad (`speed_multiplier_at`) y daño de peligros (`hazard_damage_at`).
- **`game.world.collision`:** 
  - `move_circle(tilemap, start, radius, delta, max_step=4.0)`: Desplaza un círculo resolviendo colisiones de forma independiente en X e Y. Subdivide pasos si la velocidad supera `max_step` (anti-tunneling).
  - `has_line_of_sight`: Raycast ortogonal de paso fijo para visibilidad de enemigos sin obstáculos intermedios.
- **`game.world.spatial.SpatialHash`:** Partición espacial con celdas de tamaño uniforme (64×64 píxeles). Reduce la separación de $N$ entidades de $O(N^2)$ a $O(N)$ amortizado.
- **`game.world.generation.generate_dungeon`:** Generador procedural de mazmorras por semilla. Coloca salas rectangulares no solapadas, talla corredores y valida conectividad total mediante BFS.
- **`game.world.tiled_loader.load_tiled_json`:** Importador nativo de mapas creados con Tiled Map Editor en formato JSON.

### Capa 2 y 3: Entidades e Inteligencia Artificial (`game/entities/` y `game/ai/`)
- **`game.entities.player.Player`:** Cinemática del avatar, gestión de puntos de salud (HP), ventanas de invulnerabilidad (i-frames), esquiva rápida (dash con cooldown) e inventario.
- **`game.entities.enemy_catalog`:** Carga y valida el catálogo `game/data/enemies.json`. Expone arquetipos (`melee`, `ranged`, `charger`, `tank`) con velocidades, rangos de aggro, salud y patrones de ataque.
- **`game.entities.enemies.Enemy`:** Instancia de enemigo dirigida por su arquetipo. En cada tick genera una intención (`EnemyIntent`) con vector de movimiento deseado y acción de ataque, sin mutar directamente el estado global.
- **`game.ai.astar.find_path`:** Algoritmo A* con montículo de mínimos (`heapq`) y cuota estricta de tiempo de CPU ($\le 1.5$ ms). Incluye caché LRU de rutas por piso y tile objetivo.

### Capa 4: Simulación Pura (`game/sim/`)
- **`game.sim.combat`:** Aplica intenciones de ataque del jugador y enemigos. Calcula áreas de impacto en abanico (fan hitbox), comprueba radios de colisión, aplica mitigación de daño, calcula knockback y genera drops de recursos.
- **`game.sim.interaction`:** Procesa la pulsación de interacción (`E`) sobre cofres cerrados, hogueras de descanso y el altar final de victoria.
- **`game.sim.floor`:** Orquesta la transición y el escalado entre pisos de la mazmorra (pisos 1, 2 y 3), regenerando el mapa manteniendo intacto el progreso del jugador.
- **`game.sim.quest`:** Evalúa condiciones de misiones (cacería de enemigos, apertura de cofres) y entrega recompensas atómicamente.
- **`game.sim.crafting`:** Sistema de transmutación alquímica con validación previa de ingredientes y rollback seguro ante errores.

### Capa 5 y 6: Presentación, Escenas y Aplicación (`game/render/`, `game/scenes/`, `game/app.py`)
- **`game.render.canvas.VirtualCanvas`:** Lienzo de renderizado lógico a 1280×720 píxeles. Escala dinámicamente a la resolución física de la ventana con letterbox/pillarbox perfecto y transforma coordenadas de ratón físicas a lógicas.
- **`game.render.world_view`:** Realiza culling de tiles y entidades fuera de cámara, y dibuja el mundo con $y$-sorting de entidades y proyección de sombras elípticas.
- **`game.render.audio`:** Sintetizador de audio en memoria y reproductor de efectos con degradación tolerante a fallos si no hay dispositivo de sonido disponible.
- **`game.scenes`:** Máquina de estados jerárquica de escenas (`MenuScene`, `PlayScene`, `PauseScene`, `GameOverScene`, `VictoryScene`, `ScoresScene`).
- **`game.app.Application`:** Bucle principal de eventos, reloj con acotación de delta time (`dt = min(raw_dt, 0.05)`) y liberación de recursos.

---

## 4. Diagramas de Flujo y Ciclo de Vida

### 4.1 Ciclo de Vida del Fotograma (Frame Lifecycle)

```mermaid
sequenceDiagram
    autonumber
    participant OS as Sistema Operativo / Entrada
    participant App as Application (app.py)
    participant Scene as PlayScene
    participant Sim as Simulación Pura (sim/)
    participant Render as Render & Canvas (render/)

    loop Cada Fotograma (60 FPS / dt <= 50ms)
        OS->>App: Eventos de Hardware (Teclas, Ratón, Ventana)
        App->>Scene: handle_event(event)
        Note over Scene: InputMapper convierte eventos a Acciones Abstractas
        
        App->>Scene: update(dt)
        activate Scene
        Scene->>Scene: Player.update(dt, actions)
        Scene->>Scene: Enemies.update(dt) -> EnemyIntents
        Scene->>Sim: resolve_combat(player, enemies, intents)
        Scene->>Sim: resolve_interactions(player, world)
        Scene->>Sim: separate_enemies(spatial_hash)
        deactivate Scene
        Note over Scene,Sim: Simulación Pura finalizada (Tiempo <= 2.0 ms)

        App->>Scene: draw(virtual_canvas)
        activate Render
        Scene->>Render: world_view.draw_tiles(camera, culling)
        Scene->>Render: world_view.draw_entities(y_sorted)
        Scene->>Render: hud_view.draw(health, inventory, quests)
        Render->>App: canvas.present(window_surface)
        deactivate Render
        Note over Render,App: Letterbox escalado a ventana física
    end
```

### 4.2 Máquina de Estados de Escenas

```mermaid
stateDiagram-v2
    [*] --> MenuScene: Inicio de Aplicación
    
    MenuScene --> PlayScene: Nueva Partida / Cargar Slot
    MenuScene --> ScoresScene: Ver Clasificación
    ScoresScene --> MenuScene: Volver
    
    PlayScene --> PauseScene: Pulsar Esc / P
    PauseScene --> PlayScene: Reanudar
    PauseScene --> MenuScene: Guardar y Salir al Menú
    
    PlayScene --> FloorTransitionScene: Bajar por Escalera (Pisos 1-2)
    FloorTransitionScene --> PlayScene: Piso Generado y Listo
    
    PlayScene --> GameOverScene: Salud del Jugador == 0
    PlayScene --> VictoryScene: Altar Activado en Piso Final
    
    GameOverScene --> MenuScene: Volver al Menú Principal
    VictoryScene --> ScoresScene: Registrar Puntuación en SQLite
```

---

## 5. Asignación del Presupuesto de Rendimiento (Frame Budget)

Para mantener una tasa fluida de 60 FPS en hardware estándar sin bloqueos, cada fotograma de **16.67 ms** se distribuye rígidamente:

| Fase del Fotograma | Presupuesto Máximo | Tiempo Real Medido (p95) | Margen de Seguridad |
|---|:---:|:---:|:---:|
| **1. Captura de Eventos e Input** | 0.50 ms | 0.08 ms | 84% libre |
| **2. Simulación y Cinemática** | 1.00 ms | 0.35 ms | 65% libre |
| **3. Navegación A\* y Tácticas IA** | 1.50 ms | 0.42 ms | 72% libre |
| **4. Colisiones y Separación Espacial** | 0.80 ms | 0.21 ms | 73% libre |
| **5. Culling y Renderizado Visual** | 8.00 ms | 2.10 ms | 73% libre |
| **6. Escalado de Lienzo y Blit Final** | 2.50 ms | 0.95 ms | 62% libre |
| **7. Colchón de Reserva / VSync** | 2.37 ms | — | Amortiguación activa |
| **TOTAL** | **16.67 ms** | **4.11 ms** | **75.3% de CPU libre** |

---

## 6. Garantías Arquitectónicas y Directivas de Calidad

1. **Testabilidad Headless Total:** Cualquier módulo bajo `game/core/`, `game/world/`, `game/entities/`, `game/ai/`, `game/sim/` y `game/persistence/` puede someterse a pruebas automatizadas unitarias instantáneas con `pytest` sin requerir servidor gráfico ni dependencias del sistema operativo.
2. **Determinismo Topológico:** Toda mazmorra procedural generada es idéntica para la misma terna `(seed, floor, config)`. La validación BFS impide la generación de mapas defectuosos.
3. **Inmutabilidad y Tipado Estricto:** Los catálogos de configuración (`GameConfig`, `ItemDefinition`, `EnemyArchetype`) se modelan mediante `dataclasses(frozen=True)` para garantizar la inmutabilidad de los datos en tiempo de ejecución.
4. **Resiliencia ante Fallos de Audio:** Si el subsistema SDL Mixer no está disponible o falla el driver de audio, el juego degrada de forma silenciosa y controlada (ADR-008) sin interrumpir la experiencia visual ni la simulación.

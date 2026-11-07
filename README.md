# GAMEFORGE 2D — La Fragua Olvidada

Juego RPG 2D de acción y aventura desarrollado en **Python 3.11+** con **Pygame CE**.
Diseñado y construido mediante una arquitectura limpia por capas puras y coordinación multiagente: mazmorras procedurales navegables (3 plantas), combate en tiempo real, búsqueda de rutas con A\*, misiones dirigidas por datos, fabricación alquímica, partición espacial $O(1)$, Lienzo Virtual adaptable y persistencia multi-ranura.

---

## Estado del Proyecto (Fases 0 a 5)

| Sistema / Componente | Capa | Estado |
|---|---|---|
| **Bucle principal y ciclo de vida** | `game/app.py` | Completo con delta time acotado (`<= 50 ms`) y headless mode |
| **Lienzo Virtual (Virtual Canvas)** | `game/render/canvas.py` | Resolución lógica 1280×720 con Letterbox/Pillarbox dinámico |
| **Generación procedural (BFS)** | `game/world/generation.py` | Determinista por semilla, escalado de plantas y validación Flood Fill |
| **Cargador de mapas Tiled** | `game/world/tiled_loader.py` | Importación de mapas autorales JSON de Tiled Map Editor |
| **Partición espacial ($O(1)$)** | `game/world/spatial.py` | Spatial Hash para separación de entidades y culling |
| **Navegación inteligente (A\*)** | `game/ai/astar.py` | Búsqueda con cuota de CPU (`<= 1.5 ms`) y caché LRU |
| **Enemigos data-driven** | `game/data/enemies.json` | Arquetipos configurables (melee, ranged, charger) sin código por tipo |
| **Simulación pura (Combate & Floor)** | `game/sim/` | Lógica desacoplada de Pygame: combate, looteo, transiciones de piso |
| **Misiones data-driven** | `game/data/quests.json` | Objetivos de cacería, cofres y altares con recompensas |
| **Fabricación alquímica (Crafting)** | `game/data/recipes.json` | Transmutación atómica de recursos con rollback en `game/sim/crafting.py` |
| **Persistencia multi-ranura** | `game/persistence/` | Slots 1, 2 y 3 en JSON atómico y clasificaciones en SQLite |
| **Suite de verificación integral** | `tools/verify.py` | Batería unificada de ruff, pytest (175+ tests) y benchmarks |
| **Empaquetado y distribución** | `tools/build_dist.py` | Especificación PyInstaller (`gameforge.spec`) |

---

## Cómo Ejecutar

### Con el gestor de entornos `uv` (Recomendado)
```bash
uv run python -m game
```

### Con venv tradicional de Python
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
python -m game
```

### Comandos de Utilidad y Verificación
```bash
# Verificación integral oficial (lint + tests + benchmarks)
uv run --extra dev python tools/verify.py

# Batería de pruebas automatizadas
uv run --extra dev pytest -q

# Smoke test sin ventana gráfica (Headless CI)
uv run python -m game --headless --frames 120

# Benchmarks de rendimiento
uv run python benchmark/bench_generation.py
uv run python benchmark/bench_simulation.py --enemies 100
```

---

## Controles del Juego

| Tecla / Botón | Acción |
|---|---|
| `W`, `A`, `S`, `D` / Flechas | Mover personaje |
| `Cursor del ratón` | Apuntar en 360 grados |
| `Clic izquierdo` / Espacio | Ataque en abanico (daño + knockback) |
| `Clic derecho` / Shift | Esquiva rápida / Dash (con invulnerabilidad temporal) |
| `E` | Interactuar (abrir cofres, descansar en hoguera, activar altar) |
| `Q` | Beber frasco de brasa (curación) |
| `Esc` / `P` | Pausar y menú rápido |
| `F5` | Guardar partida (durante pausa o en hoguera) |
| `F11` | Alternar pantalla completa |

---

## Arquitectura de Capas Puras

Flujo unidireccional estricto sin dependencias circulares:
$$\text{core} \leftarrow \text{world} \leftarrow \text{entities} \leftarrow \text{ai} \leftarrow \text{sim} \leftarrow \text{scenes} \leftarrow \text{app}$$

```
game/
├── core/         configuración inmutable, matemáticas Vec2 deterministas
├── world/        tilemap, colisiones, generación BFS, spatial hash, cargador Tiled
├── entities/     jugador, catálogo de enemigos data-driven, proyectiles, cofres
├── ai/           búsqueda de caminos A* cuotada y caché LRU
├── sim/          sistemas puros: combate, engagement, floor, misiones, crafting
├── persistence/  guardado atómico JSON (3 slots) y clasificaciones SQLite
├── render/       lienzo virtual (canvas), HUD, iluminación, partículas y audio
├── scenes/       menú, juego (play), pausa, clasificación y resultados
└── data/         config.json, enemies.json, quests.json, recipes.json
```

Documentación técnica detallada:
- Auditoría maestra y arquitectura: [`GAMEFORGE_2D_ARCHITECTURE_REVIEW.md`](GAMEFORGE_2D_ARCHITECTURE_REVIEW.md).
- Manual del jugador: [`documentation/GUIA_JUGADOR.md`](documentation/GUIA_JUGADOR.md).
- Contratos de interfaces: [`architecture/CONTRACTS.md`](architecture/CONTRACTS.md).
- Matriz de propiedad de archivos: [`architecture/OWNERSHIP.md`](architecture/OWNERSHIP.md).

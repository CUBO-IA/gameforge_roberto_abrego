"""Generador de cavernas orgánicas procedurales con máscara de decaimiento radial.

Inspirado en el algoritmo ALG-05 (opensimplex-island-generator).
Genera cuevas continuas con bordes externos garantizados como roca sólida (impenetrable)
y validación BFS de conectividad para spawn, altar, hoguera y cofres.
"""

from __future__ import annotations

import math
import random
from collections import deque

from game.core.config import DungeonConfig
from game.world.generation import ChestSpec, Dungeon, EnemySpec, GenerationError, Room
from game.world.tilemap import TileMap
from game.world.tiles import TileType


def generate_cavern(
    seed: int,
    floor: int = 2,
    config: DungeonConfig | None = None,
    attempts: int = 10,
) -> Dungeon:
    """Genera una caverna orgánica determinista para una semilla y piso dados."""
    cfg = config or DungeonConfig()
    if floor < 1:
        raise ValueError("floor debe ser >= 1.")
    if attempts < 1:
        raise ValueError("attempts debe ser >= 1.")

    base_seed = int(seed) & ((1 << 63) - 1)
    for attempt in range(attempts):
        derived = (
            base_seed * 4234136223846793007
            + (floor * 6571 + attempt) * 1242695040888963401
        ) & ((1 << 63) - 1)
        rng = random.Random(derived)
        dungeon = _build_cavern(rng, base_seed, floor, cfg)
        if dungeon is not None:
            return dungeon

    raise GenerationError(
        f"No se pudo generar una caverna válida (semilla={base_seed}, piso={floor})."
    )


def _radial_falloff(x: int, y: int, width: int, height: int) -> float:
    """Calcula el factor de decaimiento radial no lineal desde el centro (1.0 centro, 0.0 borde)."""
    nx = (2.0 * x - width) / max(1.0, width)
    ny = (2.0 * y - height) / max(1.0, height)
    d = math.sqrt(nx * nx + ny * ny)
    return max(0.0, 1.0 - d * d)


def _build_cavern(
    rng: random.Random, seed: int, floor: int, cfg: DungeonConfig
) -> Dungeon | None:
    width, height = cfg.width, cfg.height
    tilemap = TileMap.filled(width, height, cfg.tile_size, TileType.WALL)

    # 1. Inicialización con ruido y máscara radial
    grid = [[False for _ in range(width)] for _ in range(height)]
    for y in range(2, height - 2):
        for x in range(2, width - 2):
            falloff = _radial_falloff(x, y, width, height)
            # Probabilidad de suelo ponderada por la distancia al centro
            if rng.random() < 0.53 * falloff:
                grid[y][x] = True

    # 2. Suavizado por autómatas celulares (Cellular Automata 4 iteraciones)
    for _ in range(4):
        new_grid = [[False for _ in range(width)] for _ in range(height)]
        for y in range(2, height - 2):
            for x in range(2, width - 2):
                # Contar vecinos abiertos en vecindad Moore 3x3
                open_neighbors = sum(
                    1
                    for dy in (-1, 0, 1)
                    for dx in (-1, 0, 1)
                    if grid[y + dy][x + dx]
                )
                # Regla B5678/S45678 adaptada
                if open_neighbors >= 5:
                    new_grid[y][x] = True
                elif open_neighbors <= 3:
                    new_grid[y][x] = False
                else:
                    new_grid[y][x] = grid[y][x]
        grid = new_grid

    # 3. Identificar componentes conexos mediante BFS para aislar la cueva principal
    visited = set()
    caverns: list[list[tuple[int, int]]] = []

    for y in range(2, height - 2):
        for x in range(2, width - 2):
            if grid[y][x] and (x, y) not in visited:
                comp: list[tuple[int, int]] = []
                queue = deque([(x, y)])
                visited.add((x, y))
                while queue:
                    cx, cy = queue.popleft()
                    comp.append((cx, cy))
                    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                        nx, ny = cx + dx, cy + dy
                        if 2 <= nx < width - 2 and 2 <= ny < height - 2:
                            if grid[ny][nx] and (nx, ny) not in visited:
                                visited.add((nx, ny))
                                queue.append((nx, ny))
                caverns.append(comp)

    if not caverns:
        return None

    # Seleccionar la caverna más grande
    main_cavern = max(caverns, key=len)
    min_required_cells = (width * height) // 10
    if len(main_cavern) < min_required_cells:
        return None

    cavern_set = set(main_cavern)

    # 4. Asignar los tiles de la cueva principal en el tilemap
    for x, y in main_cavern:
        tilemap.set_tile(x, y, TileType.FLOOR)

    # Ocasionales charcos de lava subterránea (máximo 1 o 2 en zonas no centrales)
    hazard_candidates = [
        (x, y)
        for (x, y) in main_cavern
        if _radial_falloff(x, y, width, height) < 0.4
    ]
    if hazard_candidates and rng.random() < 0.7:
        sample_size = min(len(hazard_candidates), 12)
        for hx, hy in rng.sample(hazard_candidates, sample_size):
            tilemap.set_tile(hx, hy, TileType.LAVA)

    # 5. Colocar spawn y altar (en los extremos más lejanos de la caverna)
    center_x, center_y = width // 2, height // 2
    # El spawn se ubica cerca del centro de la caverna
    spawn_col, spawn_row = min(
        main_cavern,
        key=lambda pt: (pt[0] - center_x) ** 2 + (pt[1] - center_y) ** 2,
    )
    spawn = tilemap.tile_center(spawn_col, spawn_row)

    # El altar se coloca en el punto más alejado del spawn dentro de la caverna
    altar_col, altar_row = max(
        main_cavern,
        key=lambda pt: (pt[0] - spawn_col) ** 2 + (pt[1] - spawn_row) ** 2,
    )
    altar = tilemap.tile_center(altar_col, altar_row)

    # Hoguera cerca del spawn (a 2-3 tiles de distancia libre)
    campfire_pos = None
    for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (-2, -2)):
        c_cand = (spawn_col + dx, spawn_row + dy)
        if c_cand in cavern_set and tilemap.tile_at(*c_cand) == TileType.FLOOR:
            campfire_pos = tilemap.tile_center(*c_cand)
            break
    if campfire_pos is None:
        campfire_pos = spawn

    # 6. Colocar cofres (mínimo 3)
    shards_needed = 2 + floor
    chest_specs: list[ChestSpec] = []
    chest_candidates = [
        pt
        for pt in main_cavern
        if pt != (spawn_col, spawn_row)
        and pt != (altar_col, altar_row)
        and tilemap.tile_at(*pt) == TileType.FLOOR
    ]
    rng.shuffle(chest_candidates)

    for i in range(shards_needed):
        if not chest_candidates:
            break
        cx, cy = chest_candidates.pop()
        chest_specs.append(
            ChestSpec(
                id=f"cavern_chest_f{floor}_{i}",
                position=tilemap.tile_center(cx, cy),
                item_id="solar_shard",
                quantity=1,
            )
        )

    # 7. Colocar enemigos escalados
    # Derivar cantidad de enemigos del atributo existente enemies_per_room
    # con escalado por piso, consistente con el generador de mazmorras.
    enemy_count = min(cfg.enemies_per_room * 3 + (floor - 1) * 2, 20)
    enemy_kinds = ("slime", "wisp", "brute")
    enemy_specs: list[EnemySpec] = []

    enemy_candidates = [
        pt
        for pt in chest_candidates
        if (pt[0] - spawn_col) ** 2 + (pt[1] - spawn_row) ** 2 > 36  # Distancia al spawn
    ]
    rng.shuffle(enemy_candidates)

    for i in range(min(enemy_count, len(enemy_candidates))):
        ex, ey = enemy_candidates.pop()
        kind = rng.choice(enemy_kinds)
        enemy_specs.append(
            EnemySpec(
                id=f"cavern_enemy_f{floor}_{i}",
                kind=kind,
                position=tilemap.tile_center(ex, ey),
            )
        )

    # Crear pseudo-salas envolventes para compatibilidad
    rooms = (
        Room(spawn_col - 2, spawn_row - 2, 5, 5),
        Room(altar_col - 2, altar_row - 2, 5, 5),
    )

    return Dungeon(
        seed=seed,
        floor=floor,
        tilemap=tilemap,
        rooms=rooms,
        spawn=spawn,
        campfire=campfire_pos,
        altar=altar,
        chests=tuple(chest_specs),
        enemies=tuple(enemy_specs),
    )

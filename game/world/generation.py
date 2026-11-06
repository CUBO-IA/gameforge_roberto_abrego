"""Generador de mazmorras determinista.

Algoritmo: salas rectangulares dispersas + corredores en L + validación BFS de
accesibilidad. Misma semilla, piso y configuración => mismo mapa. Está inspirado
en el enfoque clásico de *rooms and corridors* descrito en el Roguelike Tutorial
(dominio público/CC0) y en la literatura de generación procedural; no se ha
copiado código de terceros.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from collections import deque

from game.core.config import DungeonConfig
from game.core.math2d import Vec2
from game.world.tilemap import TileMap
from game.world.tiles import TileType


class GenerationError(RuntimeError):
    """No se pudo generar una mazmorra válida con la semilla dada."""


@dataclass(frozen=True, slots=True)
class Room:
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> tuple[int, int]:
        return self.x + self.width // 2, self.y + self.height // 2

    def contains(self, col: int, row: int) -> bool:
        return self.x <= col < self.x + self.width and self.y <= row < self.y + self.height

    def overlaps_padded(self, other: "Room", padding: int) -> bool:
        return not (
            self.x + self.width + padding <= other.x
            or other.x + other.width + padding <= self.x
            or self.y + self.height + padding <= other.y
            or other.y + other.height + padding <= self.y
        )

    def cells(self) -> list[tuple[int, int]]:
        return [
            (col, row)
            for row in range(self.y, self.y + self.height)
            for col in range(self.x, self.x + self.width)
        ]


@dataclass(frozen=True, slots=True)
class ChestSpec:
    id: str
    position: Vec2
    item_id: str
    quantity: int


@dataclass(frozen=True, slots=True)
class EnemySpec:
    id: str
    kind: str
    position: Vec2


@dataclass(frozen=True, slots=True)
class Dungeon:
    seed: int
    floor: int
    tilemap: TileMap
    rooms: tuple[Room, ...]
    spawn: Vec2
    campfire: Vec2
    altar: Vec2
    chests: tuple[ChestSpec, ...]
    enemies: tuple[EnemySpec, ...]


def generate_dungeon(
    seed: int,
    floor: int = 1,
    config: DungeonConfig | None = None,
    attempts: int = 10,
) -> Dungeon:
    cfg = config or DungeonConfig()
    if floor < 1:
        raise ValueError("floor debe ser >= 1.")
    if attempts < 1:
        raise ValueError("attempts debe ser >= 1.")
    if cfg.min_room > cfg.max_room:
        raise GenerationError("min_room no puede ser mayor que max_room.")
    # Con padding 2 entre salas, dos salas máximas deben caber en el mapa.
    # Evita IndexError por salas fuera de límites con configuraciones directas.
    if 2 * cfg.max_room + 4 > min(cfg.width, cfg.height):
        raise GenerationError(
            "Las salas configuradas no caben en el tamaño de mapa indicado."
        )
    base_seed = int(seed) & ((1 << 63) - 1)
    for attempt in range(attempts):
        derived = (
            base_seed * 6364136223846793005
            + (floor * 7919 + attempt) * 1442695040888963407
        ) & ((1 << 63) - 1)
        rng = random.Random(derived)
        dungeon = _build(rng, base_seed, floor, cfg)
        if dungeon is not None:
            return dungeon
    raise GenerationError(
        f"No se pudo generar una mazmorra válida (semilla={base_seed}, piso={floor})."
    )


def _build(
    rng: random.Random, seed: int, floor: int, cfg: DungeonConfig
) -> Dungeon | None:
    tilemap = TileMap.filled(cfg.width, cfg.height, cfg.tile_size, TileType.WALL)
    rooms: list[Room] = []
    for _ in range(cfg.placement_attempts):
        if len(rooms) >= cfg.rooms:
            break
        width = rng.randint(cfg.min_room, cfg.max_room)
        height = rng.randint(cfg.min_room, cfg.max_room)
        x = rng.randint(1, max(1, cfg.width - width - 2))
        y = rng.randint(1, max(1, cfg.height - height - 2))
        room = Room(x, y, width, height)
        if any(room.overlaps_padded(other, padding=2) for other in rooms):
            continue
        rooms.append(room)

    minimum_rooms = max(2, min(cfg.rooms, cfg.rooms // 2 + 1))
    if len(rooms) < minimum_rooms:
        return None

    for room in rooms:
        for col, row in room.cells():
            tilemap.set_tile(col, row, TileType.FLOOR)

    # Conectar cada sala con la anterior y añadir algún bucle extra.
    for index in range(1, len(rooms)):
        _carve_corridor(tilemap, rooms[index - 1].center, rooms[index].center, rng)
    for index in range(len(rooms)):
        if rng.random() < 0.45 and len(rooms) > 3:
            target = rng.randrange(len(rooms))
            if target != index:
                _carve_corridor(tilemap, rooms[index].center, rooms[target].center, rng)

    spawn_col, spawn_row = rooms[0].center
    spawn = tilemap.tile_center(spawn_col, spawn_row)
    spawn_room = rooms[0]

    altar_room_index = max(
        range(1, len(rooms)),
        key=lambda i: _distance_sq(rooms[i].center, spawn_room.center),
    )
    altar_room = rooms[altar_room_index]
    altar = tilemap.tile_center(*altar_room.center)

    # Charcas decorativas: nunca en la sala inicial ni en la del altar.
    hazard_rooms = [
        room
        for index, room in enumerate(rooms)
        if index not in (0, altar_room_index) and room.width >= 7 and room.height >= 7
    ]
    rng.shuffle(hazard_rooms)
    for room in hazard_rooms[:2]:
        if rng.random() < 0.65:
            _carve_hazard(tilemap, room, floor, rng)

    campfire = _campfire_position(tilemap, spawn_room, spawn)
    if campfire is None:
        return None
    campfire_cell = (
        math.floor(campfire.x / tilemap.tile_size),
        math.floor(campfire.y / tilemap.tile_size),
    )

    blocked_for_chests = {altar_room.center, (spawn_col, spawn_row), campfire_cell}
    chest_cells: list[tuple[int, int]] = []
    candidate_rooms = [room for i, room in enumerate(rooms) if i != 0]
    rng.shuffle(candidate_rooms)
    for room in candidate_rooms:
        free = [
            cell
            for cell in room.cells()
            if _is_plain_floor(tilemap, cell) and cell not in blocked_for_chests
        ]
        if free:
            chest_cells.append(rng.choice(free))
        if len(chest_cells) >= cfg.chests:
            break
    if len(chest_cells) < cfg.chests:
        remaining = [
            cell
            for room in candidate_rooms
            for cell in room.cells()
            if _is_plain_floor(tilemap, cell)
            and cell not in chest_cells
            and cell not in blocked_for_chests
        ]
        rng.shuffle(remaining)
        chest_cells.extend(remaining[: cfg.chests - len(chest_cells)])
    if len(chest_cells) < cfg.chests:
        return None

    chests: list[ChestSpec] = []
    for index, cell in enumerate(chest_cells[: cfg.chests]):
        if index < cfg.shards_required:
            item_id, quantity = "shard", 1
        elif index % 2 == cfg.shards_required % 2:
            item_id, quantity = "potion", 1
        else:
            item_id, quantity = "coin", 10
        chests.append(
            ChestSpec(
                id=f"c{index}",
                position=tilemap.tile_center(*cell),
                item_id=item_id,
                quantity=quantity,
            )
        )
    chest_set = set(chest_cells)

    enemies: list[EnemySpec] = []
    enemy_index = 0
    for room in rooms[1:]:
        count = min(cfg.enemies_per_room + floor // 2, 8)
        free = [
            cell
            for cell in room.cells()
            if _is_plain_floor(tilemap, cell)
            and cell not in chest_set
            and cell not in blocked_for_chests
            and _distance_sq(cell, (spawn_col, spawn_row)) >= 49
        ]
        rng.shuffle(free)
        for cell in free[:count]:
            kind = _pick_enemy_kind(rng, floor)
            enemies.append(
                EnemySpec(
                    id=f"e{enemy_index}",
                    kind=kind,
                    position=tilemap.tile_center(*cell),
                )
            )
            enemy_index += 1

    reachable = reachable_cells(tilemap, (spawn_col, spawn_row))
    targets = [altar_room.center]
    targets.extend(chest_cells[: cfg.chests])
    targets.append(campfire_cell)
    if (spawn_col, spawn_row) not in reachable:
        return None
    if any(cell not in reachable for cell in targets):
        return None

    return Dungeon(
        seed=seed,
        floor=floor,
        tilemap=tilemap,
        rooms=tuple(rooms),
        spawn=spawn,
        campfire=campfire,
        altar=altar,
        chests=tuple(chests),
        enemies=tuple(enemies),
    )


def _campfire_position(
    tilemap: TileMap, spawn_room: Room, spawn: Vec2
) -> Vec2 | None:
    candidates = [
        (spawn_room.x + 1, spawn_room.y + 1),
        (spawn_room.x + spawn_room.width - 2, spawn_room.y + 1),
        (spawn_room.x + 1, spawn_room.y + spawn_room.height - 2),
        (spawn_room.x + spawn_room.width - 2, spawn_room.y + spawn_room.height - 2),
        (spawn_room.center[0] + 2, spawn_room.center[1] + 2),
    ]
    for col, row in candidates:
        if _is_plain_floor(tilemap, (col, row)):
            position = tilemap.tile_center(col, row)
            if position.distance_to(spawn) >= tilemap.tile_size * 1.5:
                return position
    return None


def _carve_hazard(
    tilemap: TileMap, room: Room, floor: int, rng: random.Random
) -> None:
    tile = TileType.LAVA if floor >= 2 and rng.random() < 0.55 else TileType.WATER
    max_x = room.x + room.width - 3
    max_y = room.y + room.height - 3
    if max_x < room.x + 1 or max_y < room.y + 1:
        return
    start_x = rng.randint(room.x + 1, max_x)
    start_y = rng.randint(room.y + 1, max_y)
    for row in range(start_y, start_y + 2):
        for col in range(start_x, start_x + 2):
            if room.contains(col, row) and tilemap.tile_at(col, row) == TileType.FLOOR:
                tilemap.set_tile(col, row, tile)


def _is_plain_floor(tilemap: TileMap, cell: tuple[int, int]) -> bool:
    return tilemap.tile_at(*cell) == TileType.FLOOR


def _pick_enemy_kind(rng: random.Random, floor: int) -> str:
    roll = rng.random()
    if floor <= 1:
        return "wisp" if roll > 0.68 else "slime"
    if floor == 2:
        if roll > 0.85:
            return "brute"
        return "wisp" if roll > 0.55 else "slime"
    if roll > 0.7:
        return "brute"
    return "wisp" if roll > 0.4 else "slime"


def _carve_corridor(
    tilemap: TileMap,
    start: tuple[int, int],
    end: tuple[int, int],
    rng: random.Random,
) -> None:
    start_col, start_row = start
    end_col, end_row = end
    if rng.random() < 0.5:
        _carve_horizontal(tilemap, start_col, end_col, start_row)
        _carve_vertical(tilemap, start_row, end_row, end_col)
    else:
        _carve_vertical(tilemap, start_row, end_row, start_col)
        _carve_horizontal(tilemap, start_col, end_col, end_row)


def _carve_horizontal(tilemap: TileMap, x_a: int, x_b: int, row: int) -> None:
    for col in range(min(x_a, x_b), max(x_a, x_b) + 1):
        tilemap.set_tile(col, row, TileType.FLOOR)


def _carve_vertical(tilemap: TileMap, y_a: int, y_b: int, col: int) -> None:
    for row in range(min(y_a, y_b), max(y_a, y_b) + 1):
        tilemap.set_tile(col, row, TileType.FLOOR)


def _distance_sq(a: tuple[int, int], b: tuple[int, int]) -> int:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


def reachable_cells(tilemap: TileMap, start: tuple[int, int]) -> set[tuple[int, int]]:
    """BFS por tiles no sólidos (agua y lava son transitables)."""
    if tilemap.is_solid_tile(*start):
        return set()
    seen = {start}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        col, row = queue.popleft()
        for next_col, next_row in (
            (col + 1, row),
            (col - 1, row),
            (col, row + 1),
            (col, row - 1),
        ):
            if not tilemap.in_bounds(next_col, next_row):
                continue
            cell = (next_col, next_row)
            if cell in seen or tilemap.is_solid_tile(*cell):
                continue
            seen.add(cell)
            queue.append(cell)
    return seen


def is_reachable(
    tilemap: TileMap, start: tuple[int, int], target: tuple[int, int]
) -> bool:
    return target in reachable_cells(tilemap, start)

"""Pruebas unitarias de la búsqueda de rutas A* (game.ai.astar)."""

from __future__ import annotations

import time

from game.ai.astar import clear_path_cache, find_path
from game.core.math2d import Vec2
from game.world.tilemap import TileMap
from game.world.tiles import TileType


def make_test_map(width: int = 10, height: int = 10, tile_size: int = 32) -> TileMap:
    # Mapa rodeado de paredes y suelo en el interior
    tiles = [[TileType.FLOOR for _ in range(width)] for _ in range(height)]
    for c in range(width):
        tiles[0][c] = TileType.WALL
        tiles[height - 1][c] = TileType.WALL
    for r in range(height):
        tiles[r][0] = TileType.WALL
        tiles[r][width - 1] = TileType.WALL
    return TileMap(width, height, tile_size, tiles)


def test_astar_same_tile_returns_goal() -> None:
    tmap = make_test_map()
    start = Vec2(48, 48)  # tile (1, 1)
    goal = Vec2(50, 50)  # mismo tile (1, 1)
    path = find_path(tmap, start, goal)
    assert path == [goal]


def test_astar_solid_goal_returns_none() -> None:
    tmap = make_test_map()
    start = Vec2(48, 48)  # interior
    goal = Vec2(16, 16)  # pared en (0, 0)
    path = find_path(tmap, start, goal)
    assert path is None


def test_astar_out_of_bounds_returns_none() -> None:
    tmap = make_test_map()
    start = Vec2(48, 48)
    goal = Vec2(-100, 50)
    assert find_path(tmap, start, goal) is None


def test_astar_navigates_straight_line() -> None:
    tmap = make_test_map()
    start = tmap.tile_center(1, 1)
    goal = tmap.tile_center(4, 1)
    path = find_path(tmap, start, goal)
    assert path is not None
    assert len(path) == 3  # (2,1), (3,1), (4,1)
    assert path[-1] == goal


def test_astar_navigates_around_wall() -> None:
    tmap = make_test_map(10, 10)
    # Crear un muro vertical en col=3 desde row=1 hasta row=7
    for r in range(1, 8):
        tmap.set_tile(3, r, TileType.WALL)

    # Start en (1, 3), Goal en (5, 3)
    start = tmap.tile_center(1, 3)
    goal = tmap.tile_center(5, 3)

    path = find_path(tmap, start, goal)
    assert path is not None
    # Debe rodear por el paso abierto en row=8
    for point in path:
        col = int(point.x // tmap.tile_size)
        row = int(point.y // tmap.tile_size)
        assert not tmap.is_solid_tile(col, row)
    assert path[-1] == goal


def test_astar_completely_blocked_returns_none() -> None:
    tmap = make_test_map(8, 8)
    # Muro infranqueable en col=4
    for r in range(8):
        tmap.set_tile(4, r, TileType.WALL)

    start = tmap.tile_center(1, 1)
    goal = tmap.tile_center(6, 1)
    path = find_path(tmap, start, goal)
    assert path is None


def test_astar_respects_budget_ms() -> None:
    tmap = make_test_map(50, 50)
    start = tmap.tile_center(1, 1)
    goal = tmap.tile_center(48, 48)

    t0 = time.perf_counter()
    # Con un presupuesto de 0.01 ms debe cortar rápidamente
    find_path(tmap, start, goal, budget_ms=0.01)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    # No debe colapsar y debe respetar una duración baja
    assert elapsed_ms < 50.0


def test_astar_cache_works() -> None:
    clear_path_cache()
    tmap = make_test_map()
    start = tmap.tile_center(2, 2)
    goal = tmap.tile_center(5, 5)

    path1 = find_path(tmap, start, goal)
    assert path1 is not None

    path2 = find_path(tmap, start, goal)
    assert path1 == path2

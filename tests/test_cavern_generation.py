"""Pruebas unitarias para el generador de cavernas orgánicas procedurales (Algoritmo ALG-05)."""

from __future__ import annotations

from collections import deque

import pytest

from game.world.cavern_generation import generate_cavern
from game.world.tiles import TileType


def test_cavern_generation_determinism() -> None:
    seed = 123456789
    c1 = generate_cavern(seed, floor=2)
    c2 = generate_cavern(seed, floor=2)

    assert c1.spawn == c2.spawn
    assert c1.altar == c2.altar
    assert c1.campfire == c2.campfire
    assert len(c1.chests) == len(c2.chests)
    assert len(c1.enemies) == len(c2.enemies)

    # Las matrices de tiles deben ser exactamente idénticas
    for y in range(c1.tilemap.height):
        for x in range(c1.tilemap.width):
            assert c1.tilemap.tile_at(x, y) == c2.tilemap.tile_at(x, y)


def test_cavern_outer_perimeter_is_solid_wall() -> None:
    seed = 987654321
    cavern = generate_cavern(seed, floor=2)
    tm = cavern.tilemap

    # Verificar que los 4 bordes perimetrales son impenetrables
    for x in range(tm.width):
        assert tm.tile_at(x, 0) == TileType.WALL
        assert tm.tile_at(x, tm.height - 1) == TileType.WALL
        assert tm.tile_at(x, 1) == TileType.WALL
        assert tm.tile_at(x, tm.height - 2) == TileType.WALL

    for y in range(tm.height):
        assert tm.tile_at(0, y) == TileType.WALL
        assert tm.tile_at(tm.width - 1, y) == TileType.WALL
        assert tm.tile_at(1, y) == TileType.WALL
        assert tm.tile_at(tm.width - 2, y) == TileType.WALL


def test_cavern_connectivity_bfs() -> None:
    seed = 44556677
    cavern = generate_cavern(seed, floor=2)
    tm = cavern.tilemap

    spawn_tile = (int(cavern.spawn.x // tm.tile_size), int(cavern.spawn.y // tm.tile_size))
    altar_tile = (int(cavern.altar.x // tm.tile_size), int(cavern.altar.y // tm.tile_size))

    assert not tm.is_solid_at(cavern.spawn.x, cavern.spawn.y)
    assert not tm.is_solid_at(cavern.altar.x, cavern.altar.y)

    # BFS desde el spawn
    queue = deque([spawn_tile])
    visited = {spawn_tile}

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < tm.width and 0 <= ny < tm.height:
                if not tm.is_solid_tile(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    # El altar debe ser alcanzable
    assert altar_tile in visited

    # Todos los cofres deben ser alcanzables
    for chest in cavern.chests:
        c_tile = (int(chest.position.x // tm.tile_size), int(chest.position.y // tm.tile_size))
        assert c_tile in visited


def test_cavern_invalid_params() -> None:
    with pytest.raises(ValueError):
        generate_cavern(1234, floor=0)

    with pytest.raises(ValueError):
        generate_cavern(1234, floor=2, attempts=0)

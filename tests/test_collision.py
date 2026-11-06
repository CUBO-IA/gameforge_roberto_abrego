import pytest

from game.core.math2d import Vec2
from game.world.collision import circle_hits_solid, has_line_of_sight, move_circle
from game.world.tilemap import TileMap
from game.world.tiles import TileType

TILE = 32


def make_room(width: int = 12, height: int = 10) -> TileMap:
    tilemap = TileMap.filled(width, height, TILE, TileType.FLOOR)
    for col in range(width):
        tilemap.set_tile(col, 0, TileType.WALL)
        tilemap.set_tile(col, height - 1, TileType.WALL)
    for row in range(height):
        tilemap.set_tile(0, row, TileType.WALL)
        tilemap.set_tile(width - 1, row, TileType.WALL)
    return tilemap


def test_circle_collision_against_wall() -> None:
    tilemap = make_room()
    center = Vec2(5 * TILE, 5 * TILE)
    assert not circle_hits_solid(tilemap, center, 12)
    assert circle_hits_solid(tilemap, Vec2(TILE + 5, 5 * TILE), 12)
    assert circle_hits_solid(tilemap, Vec2(-10, -10), 4)


def test_move_stops_at_wall_without_tunneling() -> None:
    tilemap = make_room()
    start = Vec2(4 * TILE, 5 * TILE)
    result = move_circle(tilemap, start, 12, Vec2(10_000, 0))
    assert result.hit_x
    assert result.position.x <= 11 * TILE - 12 + 1e-6
    assert not circle_hits_solid(tilemap, result.position, 12)


def test_move_slides_along_wall() -> None:
    tilemap = make_room()
    start = Vec2(5 * TILE, 1 * TILE + 12)
    result = move_circle(tilemap, start, 12, Vec2(TILE * 2, -TILE))
    assert result.position.x > start.x
    assert result.position.y >= TILE + 12 - 1e-6
    assert not circle_hits_solid(tilemap, result.position, 12)


def test_zero_and_negative_step() -> None:
    tilemap = make_room()
    start = Vec2(4 * TILE, 4 * TILE)
    assert move_circle(tilemap, start, 12, Vec2()).position.as_tuple() == start.as_tuple()
    with pytest.raises(ValueError):
        move_circle(tilemap, start, 12, Vec2(1, 1), max_step=0)


def test_line_of_sight() -> None:
    tilemap = make_room(12, 12)
    assert has_line_of_sight(tilemap, Vec2(3 * TILE, 3 * TILE), Vec2(7 * TILE, 3 * TILE))
    tilemap.set_tile(5, 3, TileType.WALL)
    assert not has_line_of_sight(tilemap, Vec2(3 * TILE, 3 * TILE), Vec2(7 * TILE, 3 * TILE))

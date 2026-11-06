import pytest

from game.core.config import PlayerConfig
from game.core.math2d import Vec2
from game.entities.player import Player
from game.world.collision import circle_hits_solid
from game.world.tilemap import TileMap
from game.world.tiles import TileType

TILE = 32


def make_map(width: int = 20, height: int = 20) -> TileMap:
    tilemap = TileMap.filled(width, height, TILE, TileType.FLOOR)
    for col in range(width):
        tilemap.set_tile(col, 0, TileType.WALL)
        tilemap.set_tile(col, height - 1, TileType.WALL)
    for row in range(height):
        tilemap.set_tile(0, row, TileType.WALL)
        tilemap.set_tile(width - 1, row, TileType.WALL)
    return tilemap


def player_at(tilemap: TileMap, col: int = 5, row: int = 5) -> Player:
    return Player(tilemap.tile_center(col, row), PlayerConfig())


def test_movement_and_facing() -> None:
    tilemap = make_map()
    player = player_at(tilemap)
    start_x = player.position.x
    player.update(0.5, Vec2(1, 0), Vec2(0, -1), False, False, tilemap)
    assert player.position.x > start_x
    assert player.facing.as_tuple() == pytest.approx((0.0, -1.0))


def test_water_slows_movement() -> None:
    tilemap = make_map()
    floor_player = player_at(tilemap)
    floor_player.update(0.5, Vec2(1, 0), Vec2(0, 1), False, False, tilemap)

    tilemap.set_tile(5, 5, TileType.WATER)
    water_player = player_at(tilemap)
    water_player.update(0.5, Vec2(1, 0), Vec2(0, 1), False, False, tilemap)

    floor_distance = floor_player.position.x - tilemap.tile_center(5, 5).x
    water_distance = water_player.position.x - tilemap.tile_center(5, 5).x
    assert water_distance < floor_distance


def test_collision_blocks_wall() -> None:
    tilemap = make_map()
    player = player_at(tilemap, col=2, row=5)
    for _ in range(120):
        player.update(1 / 60, Vec2(-1, 0), Vec2(-1, 0), False, False, tilemap)
    assert player.position.x >= TILE + player.radius - 1e-6
    assert not circle_hits_solid(tilemap, player.position, player.radius)


def test_dash_grants_invulnerability_and_distance() -> None:
    tilemap = make_map()
    normal = player_at(tilemap)
    dashed = player_at(tilemap)
    normal.update(0.1, Vec2(1, 0), Vec2(1, 0), False, False, tilemap)
    dashed.update(0.1, Vec2(1, 0), Vec2(1, 0), True, False, tilemap)
    assert dashed.dash_started
    assert dashed.invulnerability > 0
    assert dashed.position.x > normal.position.x
    assert dashed.take_damage(10) is False

    for _ in range(30):
        dashed.update(1 / 60, Vec2(1, 0), Vec2(1, 0), False, False, tilemap)
    assert not dashed.is_dashing
    assert dashed.dash_cooldown > 0


def test_attack_creates_spec_and_cooldown() -> None:
    tilemap = make_map()
    player = player_at(tilemap)
    player.update(1 / 60, Vec2(), Vec2(1, 0), False, True, tilemap)
    assert player.pending_attack is not None
    spec = player.pending_attack
    assert spec.damage == player.config.attack_damage
    assert spec.direction.as_tuple() == pytest.approx((1.0, 0.0))
    player.update(1 / 60, Vec2(), Vec2(1, 0), False, True, tilemap)
    assert player.pending_attack is None


def test_damage_has_invulnerability_window() -> None:
    tilemap = make_map()
    player = player_at(tilemap)
    assert player.take_damage(25, Vec2(0, 0))
    assert player.health == player.max_health - 25
    assert not player.take_damage(25)
    player.invulnerability = 0
    assert player.take_damage(10)
    assert player.knockback.length() > 0


def test_heal_is_capped() -> None:
    tilemap = make_map()
    player = player_at(tilemap)
    player.take_damage(30)
    healed = player.heal(999)
    assert healed == pytest.approx(30)
    assert player.health == player.max_health
    assert player.heal(10) == 0


def test_lava_deals_continuous_damage() -> None:
    tilemap = make_map()
    player = player_at(tilemap)
    tilemap.set_tile(5, 5, TileType.LAVA)
    player.update(1.0, Vec2(), Vec2(0, 1), False, False, tilemap)
    assert player.health == pytest.approx(player.max_health - 18.0)
    assert player.alive

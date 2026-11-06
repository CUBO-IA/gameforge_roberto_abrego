import random

import pytest

from game.core.config import EnemyStats
from game.core.math2d import Vec2
from game.entities.enemies import Enemy, separate_enemies
from game.world.collision import circle_hits_solid
from game.world.tilemap import TileMap
from game.world.tiles import TileType

TILE = 32
SLIME = EnemyStats(health=40, speed=80, radius=15, touch_damage=8, score=10)
WISP = EnemyStats(
    health=20,
    speed=80,
    radius=13,
    touch_damage=6,
    score=20,
    attack_range=300,
    shoot_cooldown=2.0,
    projectile_speed=200,
)
BRUTE = EnemyStats(
    health=100, speed=60, radius=20, touch_damage=15, score=40, attack_range=250
)


def make_map(width: int = 30, height: int = 20) -> TileMap:
    tilemap = TileMap.filled(width, height, TILE, TileType.FLOOR)
    for col in range(width):
        tilemap.set_tile(col, 0, TileType.WALL)
        tilemap.set_tile(col, height - 1, TileType.WALL)
    for row in range(height):
        tilemap.set_tile(0, row, TileType.WALL)
        tilemap.set_tile(width - 1, row, TileType.WALL)
    return tilemap


def enemy(kind: str, stats: EnemyStats, position: Vec2, enemy_id: str = "e1") -> Enemy:
    return Enemy(enemy_id, kind, position, stats)


def test_slime_chases_player() -> None:
    tilemap = make_map()
    slime = enemy("slime", SLIME, Vec2(15 * TILE, 10 * TILE))
    player = Vec2(20 * TILE, 10 * TILE)
    before = slime.position.distance_to(player)
    for _ in range(30):
        slime.update(1 / 60, player, 12, tilemap, random.Random(1))
    assert slime.position.distance_to(player) < before
    assert not circle_hits_solid(tilemap, slime.position, slime.radius)


def test_wisp_shoots_with_line_of_sight_and_cooldown() -> None:
    tilemap = make_map()
    wisp = enemy("wisp", WISP, Vec2(10 * TILE, 10 * TILE))
    player = Vec2(16 * TILE, 10 * TILE)
    intent = wisp.update(1 / 60, player, 12, tilemap, random.Random(2))
    assert intent.projectile is not None
    assert intent.projectile.speed == WISP.projectile_speed
    assert wisp.shoot_cooldown > 0
    second = wisp.update(1 / 60, player, 12, tilemap, random.Random(2))
    assert second.projectile is None


def test_wisp_does_not_shoot_through_wall() -> None:
    tilemap = make_map()
    for row in range(1, 19):
        tilemap.set_tile(13, row, TileType.WALL)
    wisp = enemy("wisp", WISP, Vec2(10 * TILE, 10 * TILE))
    player = Vec2(16 * TILE, 10 * TILE)
    intent = wisp.update(1 / 60, player, 12, tilemap, random.Random(3))
    assert intent.projectile is None


def test_brute_charge_state_machine() -> None:
    tilemap = make_map(width=40)
    brute = enemy("brute", BRUTE, Vec2(10 * TILE, 10 * TILE))
    player = Vec2(13 * TILE, 10 * TILE)
    brute.update(1 / 60, player, 12, tilemap, random.Random(4))
    assert brute.state == "windup"
    brute.update(0.6, player, 12, tilemap, random.Random(4))
    assert brute.state == "charge"
    brute.update(0.5, player, 12, tilemap, random.Random(4))
    assert brute.state == "recover"
    brute.update(0.8, player, 12, tilemap, random.Random(4))
    assert brute.state == "chase"
    assert brute.charge_cooldown > 0


def test_damage_and_death() -> None:
    slime = enemy("slime", SLIME, Vec2(100, 100))
    assert slime.take_damage(10, Vec2(90, 100), 200)
    assert slime.health == 30
    assert slime.knockback.length() == pytest.approx(200)
    assert slime.alive
    assert slime.take_damage(40, Vec2(90, 100)) is True
    assert not slime.alive
    assert not slime.take_damage(5)


def test_separation_pushes_enemies_apart() -> None:
    tilemap = make_map()
    first = enemy("slime", SLIME, Vec2(10 * TILE, 10 * TILE), "e1")
    second = enemy("slime", SLIME, Vec2(10 * TILE + 6, 10 * TILE), "e2")
    before = first.position.distance_to(second.position)
    separate_enemies([first, second], tilemap)
    assert first.position.distance_to(second.position) > before
    assert not circle_hits_solid(tilemap, first.position, first.radius)
    assert not circle_hits_solid(tilemap, second.position, second.radius)


def test_strafe_direction_is_deterministic() -> None:
    first = enemy("wisp", WISP, Vec2(0, 0), "e7")
    second = enemy("wisp", WISP, Vec2(0, 0), "e7")
    assert first._strafe_sign == second._strafe_sign

import pytest

from game.core.config import EnemyStats
from game.core.math2d import Vec2
from game.entities.enemies import Enemy
from game.entities.player import AttackSpec
from game.systems.combat import resolve_player_attack

STATS = EnemyStats(health=50, speed=0, radius=10, touch_damage=1, score=1)


def make_enemy(position: Vec2, enemy_id: str = "e") -> Enemy:
    return Enemy(enemy_id, "slime", position, STATS)


def spec(direction: Vec2 | None = None) -> AttackSpec:
    if direction is None:
        direction = Vec2(1, 0)
    return AttackSpec(
        origin=Vec2(0, 0),
        direction=direction,
        range=60,
        arc_degrees=100,
        damage=20,
        knockback=100,
    )


def test_attack_hits_front_target() -> None:
    target = make_enemy(Vec2(40, 0))
    hits = resolve_player_attack(spec(), [target])
    assert hits == [target]
    assert target.health == 30
    assert target.knockback.length() > 0


def test_attack_ignores_behind_and_side() -> None:
    behind = make_enemy(Vec2(-40, 0), "behind")
    side = make_enemy(Vec2(0, 50), "side")
    hits = resolve_player_attack(spec(), [behind, side])
    assert hits == []
    assert behind.health == 50
    assert side.health == 50


def test_attack_range_includes_radius() -> None:
    in_range = make_enemy(Vec2(68, 0), "near")
    out_of_range = make_enemy(Vec2(80, 0), "far")
    hits = resolve_player_attack(spec(), [in_range, out_of_range])
    assert hits == [in_range]


def test_attack_can_hit_multiple_and_kill() -> None:
    first = make_enemy(Vec2(30, 0), "a")
    second = make_enemy(Vec2(40, 10), "b")
    first.health = 10
    hits = resolve_player_attack(spec(), [first, second])
    assert len(hits) == 2
    assert not first.alive
    assert second.alive
    # Un segundo golpe no vuelve a dañar a un enemigo muerto.
    assert resolve_player_attack(spec(), [first]) == []


def test_zero_direction_still_hits_adjacent_target() -> None:
    target = make_enemy(Vec2(1, 0))
    result = resolve_player_attack(spec(Vec2()), [target])
    assert result == [target]
    assert target.health == pytest.approx(30)

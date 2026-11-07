"""Pruebas del sistema de progresión y transición de plantas (game.sim.floor)."""

from __future__ import annotations

from game.core.config import DungeonConfig
from game.sim.floor import (
    MAX_FLOORS,
    calculate_floor_transition,
    finish_score,
    floor_bonus,
    floor_theme_name,
    is_final_floor,
    shard_bonus,
    shards_required_for_floor,
    victory_bonus,
)
from game.world.generation import generate_dungeon


def test_floor_constants_and_theme() -> None:
    assert MAX_FLOORS == 3
    assert not is_final_floor(1)
    assert not is_final_floor(2)
    assert is_final_floor(3)
    assert is_final_floor(4)

    assert "Umbral" in floor_theme_name(1)
    assert "Cripta" in floor_theme_name(2)
    assert "Núcleo" in floor_theme_name(3)


def test_shards_scaling_per_floor() -> None:
    assert shards_required_for_floor(1) == 3
    assert shards_required_for_floor(2) == 4
    assert shards_required_for_floor(3) == 5


def test_calculate_floor_transition() -> None:
    t1 = calculate_floor_transition(1)
    assert t1 is not None
    assert t1.current_floor == 1
    assert t1.next_floor == 2
    assert t1.shards_required == 4

    t2 = calculate_floor_transition(2)
    assert t2 is not None
    assert t2.next_floor == 3

    # En la planta 3 (final), no hay siguiente piso
    t3 = calculate_floor_transition(3)
    assert t3 is None


def test_finish_score_calculation() -> None:
    assert floor_bonus(2) == 100
    assert shard_bonus(3) == 300
    assert victory_bonus() == 500

    score_defeat = finish_score(shards=2, floor=1, victory=False)
    assert score_defeat == 200 + 50  # 250

    score_victory = finish_score(shards=5, floor=3, victory=True)
    assert score_victory == 500 + 150 + 500  # 1150


def test_dungeon_generation_scales_with_floor() -> None:
    config = DungeonConfig(width=64, height=48)
    seed = 42

    d1 = generate_dungeon(seed=seed, floor=1, config=config)
    d2 = generate_dungeon(seed=seed, floor=2, config=config)
    d3 = generate_dungeon(seed=seed, floor=3, config=config)

    # Cada planta debe ser navegable y tener spawn, altar y cofres
    assert d1.spawn != d2.spawn or d1.tilemap != d2.tilemap
    assert len(d1.chests) >= 3
    assert len(d2.chests) >= 3
    assert len(d3.chests) >= 3

    # El número de enemigos escala con la planta (generation.py: enemies_per_room + floor // 2)
    assert len(d3.enemies) >= len(d1.enemies)

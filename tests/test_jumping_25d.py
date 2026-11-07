"""Pruebas unitarias de mecánicas 2.5D, salto y elevación virtual (Algoritmo ALG-08)."""

from __future__ import annotations

import pytest

from game.core.config import PlayerConfig
from game.core.math2d import Vec2
from game.entities.player import Player
from game.world.tilemap import TileMap
from game.world.tiles import TileType


@pytest.fixture
def player_cfg() -> PlayerConfig:
    return PlayerConfig(
        speed=160.0,
        radius=12.0,
        max_health=100.0,
        invulnerability=0.3,
        dash_speed=360.0,
        dash_duration=0.18,
        dash_cooldown=0.6,
        attack_range=38.0,
        attack_arc=90.0,
        attack_cooldown=0.35,
        attack_damage=25.0,
    )


@pytest.fixture
def empty_map() -> TileMap:
    return TileMap.filled(10, 10, 32, TileType.FLOOR)


def test_player_initial_elevation_is_grounded(player_cfg: PlayerConfig) -> None:
    player = Player(Vec2(64, 64), player_cfg)
    assert player.z == 0.0
    assert player.vz == 0.0
    assert not player.is_jumping


def test_player_jump_kinematics(player_cfg: PlayerConfig, empty_map: TileMap) -> None:
    player = Player(Vec2(64, 64), player_cfg)
    # Disparar salto
    player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=True)
    assert player.jump_started
    assert player.is_jumping
    assert player.z > 0.0
    assert player.vz > 0.0

    # Simular ascenso hasta el ápice
    peak_z = 0.0
    for _ in range(30):
        player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=False)
        if player.z > peak_z:
            peak_z = player.z

    assert peak_z > 20.0  # El salto alcanza una altura visible

    # Simular hasta el aterrizaje
    for _ in range(60):
        player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=False)

    assert player.z == 0.0
    assert player.vz == 0.0
    assert not player.is_jumping


def test_player_cannot_double_jump(player_cfg: PlayerConfig, empty_map: TileMap) -> None:
    player = Player(Vec2(64, 64), player_cfg)
    player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=True)
    assert player.jump_started

    # Intentar segundo salto en el aire
    player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=True)
    assert not player.jump_started  # No se permite doble salto


def test_player_cannot_jump_while_dashing(player_cfg: PlayerConfig, empty_map: TileMap) -> None:
    player = Player(Vec2(64, 64), player_cfg)
    player.update(0.016, Vec2(1, 0), Vec2(1, 0), dash=True, attack=False, tilemap=empty_map, jump=False)
    assert player.is_dashing

    # Intentar saltar mientras hace dash
    player.update(0.016, Vec2(1, 0), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=True)
    assert not player.jump_started
    assert player.z == 0.0


def test_jump_avoids_ground_hazards(player_cfg: PlayerConfig) -> None:
    # Crear un mapa donde el centro es lava (daño 18/s)
    tilemap = TileMap.filled(5, 5, 32, TileType.LAVA)
    player = Player(Vec2(64, 64), player_cfg)
    initial_health = player.health

    # Caso 1: En el suelo sobre lava recibe daño
    player.update(0.1, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=tilemap, jump=False)
    damage_taken = initial_health - player.health
    assert damage_taken > 0.0

    # Caso 2: Saltando en el aire sobre lava NO recibe daño
    player.health = 100.0
    player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=tilemap, jump=True)
    assert player.is_jumping
    assert player.z > 0.0

    # En el aire
    health_before_air = player.health
    player.update(0.05, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=tilemap, jump=False)
    assert player.is_jumping
    assert player.health == health_before_air  # Inmune a daño terrestre mientras salta


def test_player_update_backwards_compatibility(player_cfg: PlayerConfig, empty_map: TileMap) -> None:
    player = Player(Vec2(64, 64), player_cfg)
    # Llamada con 6 argumentos (sin el parámetro jump)
    player.update(0.016, Vec2(), Vec2(1, 0), False, False, empty_map)
    assert player.z == 0.0


def test_player_jump_hits_ceiling(player_cfg: PlayerConfig, empty_map: TileMap) -> None:
    player = Player(Vec2(64, 64), player_cfg)
    ceiling_height = 16.0  # Techo bajo

    # Saltar con techo bajo
    player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=True, ceiling_z=ceiling_height)
    assert player.jump_started

    # Avanzar simulación hasta chocar contra el techo
    for _ in range(10):
        player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=False, ceiling_z=ceiling_height)
        if player.ceiling_hit:
            break

    assert player.ceiling_hit
    assert player.z <= ceiling_height
    assert player.vz <= 0.0  # La velocidad vertical se invierte hacia abajo


def test_player_cannot_jump_under_zero_ceiling(player_cfg: PlayerConfig, empty_map: TileMap) -> None:
    player = Player(Vec2(64, 64), player_cfg)
    # Techo nulo o demasiado bajo
    player.update(0.016, Vec2(), Vec2(1, 0), dash=False, attack=False, tilemap=empty_map, jump=True, ceiling_z=2.0)
    assert not player.jump_started
    assert player.z == 0.0

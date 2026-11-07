"""Pruebas de integración del bucle de amenazas con DijkstraMap (Swarm AI, ALG-07)."""

from __future__ import annotations

import random

from game.ai.dijkstra import DijkstraMap
from game.core.config import EnemyStats, PlayerConfig
from game.core.math2d import Vec2
from game.entities.enemies import Enemy
from game.entities.player import Player
from game.sim.engagement import update_enemies
from game.world.tilemap import TileMap
from game.world.tiles import TileType


def _make_tilemap_with_obstacle() -> TileMap:
    """Mapa 10x8 con un muro divisor que bloquea línea de visión."""
    grid = [[TileType.FLOOR] * 10 for _ in range(8)]
    # Borde
    for r in range(8):
        grid[r][0] = TileType.WALL
        grid[r][9] = TileType.WALL
    for c in range(10):
        grid[0][c] = TileType.WALL
        grid[7][c] = TileType.WALL
    # Muro interno vertical en columna 5, filas 1..5
    for r in range(1, 6):
        grid[r][5] = TileType.WALL
    return TileMap(10, 8, 32, grid)


def test_swarm_dijkstra_triggers_when_threshold_met() -> None:
    tm = _make_tilemap_with_obstacle()
    dmap = DijkstraMap(tm)
    player = Player(Vec2(64.0, 64.0), PlayerConfig())

    # Crear 7 enemigos (por encima del umbral SWARM_THRESHOLD=6)
    stats = EnemyStats(health=30.0, speed=60.0, radius=12.0, touch_damage=10.0, score=25)
    enemies = [
        Enemy(f"swarm_e{i}", "slime", Vec2(220.0, 100.0 + i * 16.0), stats)
        for i in range(7)
    ]
    rng = random.Random(42)

    # Actualizar enemigos con dijkstra_map
    events = update_enemies(enemies, dt=0.016, player=player, tilemap=tm, rng=rng, dijkstra_map=dmap)
    assert events is not None

    # El campo de distancias de Dijkstra debe haberse calculado desde la posición del jugador
    player_col = int(player.position.x // tm.tile_size)
    player_row = int(player.position.y // tm.tile_size)
    assert dmap.distance_at(player_col, player_row) == 0


def test_dijkstra_navigation_around_obstacle() -> None:
    tm = _make_tilemap_with_obstacle()
    dmap = DijkstraMap(tm)
    player = Player(Vec2(64.0, 64.0), PlayerConfig())  # Col 2, Row 2

    # Enemigo en col 7, row 2 (al otro lado del muro en col 5)
    stats = EnemyStats(health=30.0, speed=60.0, radius=12.0, touch_damage=10.0, score=25)
    enemy = Enemy("slime_1", "slime", Vec2(7 * 32 + 16, 2 * 32 + 16), stats)
    rng = random.Random(123)

    # Precomputar Dijkstra
    p_col = int(player.position.x // tm.tile_size)
    p_row = int(player.position.y // tm.tile_size)
    dmap.compute(p_col, p_row)

    initial_pos = enemy.position.copy()
    enemy.update(dt=0.1, player_position=player.position, player_radius=player.radius, tilemap=tm, rng=rng, dijkstra_map=dmap)

    # El enemigo debe haberse movido hacia el pasaje abierto (hacia abajo, row 6)
    assert enemy.position != initial_pos


def test_backward_compatibility_without_dijkstra() -> None:
    tm = _make_tilemap_with_obstacle()
    player = Player(Vec2(64.0, 64.0), PlayerConfig())
    stats = EnemyStats(health=30.0, speed=60.0, radius=12.0, touch_damage=10.0, score=25)
    enemies = [Enemy("slime_alone", "slime", Vec2(80.0, 80.0), stats)]
    rng = random.Random(999)

    # Debe funcionar sin dijkstra_map (argumento opcional)
    events = update_enemies(enemies, dt=0.016, player=player, tilemap=tm, rng=rng)
    assert events is not None

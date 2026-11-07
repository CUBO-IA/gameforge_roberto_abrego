"""Pruebas unitarias para el mapa de distancias Dijkstra (Swarm AI, ALG-07)."""

from __future__ import annotations

import pytest

from game.ai.dijkstra import UNREACHABLE, DijkstraMap
from game.world.tilemap import TileMap
from game.world.tiles import TileType


def _simple_tilemap() -> TileMap:
    """Mapa 8×6, borde de muros, interior libre.

    Esquema (W=muro, .=piso):
        W W W W W W W W
        W . . . . . . W
        W . . . . . . W
        W . . W W . . W   <- obstáculo central
        W . . . . . . W
        W W W W W W W W
    """
    grid = [[TileType.WALL] * 8 for _ in range(6)]
    for r in range(1, 5):
        for c in range(1, 7):
            grid[r][c] = TileType.FLOOR
    # Obstáculo central
    grid[3][3] = TileType.WALL
    grid[3][4] = TileType.WALL
    return TileMap(8, 6, 32, grid)


def test_dijkstra_distances_match_bfs() -> None:
    """Las distancias deben coincidir con BFS manual."""
    tm = _simple_tilemap()
    dmap = DijkstraMap(tm)
    dmap.compute(1, 1)  # Fuente en esquina superior izquierda interior

    # Distancia a sí mismo es 0
    assert dmap.distance_at(1, 1) == 0
    # Vecino directo a la derecha
    assert dmap.distance_at(2, 1) == 1
    # Diagonal requiere 2 pasos ortogonales
    assert dmap.distance_at(2, 2) == 2
    # Muros son inalcanzables
    assert dmap.distance_at(0, 0) == UNREACHABLE
    assert dmap.distance_at(3, 3) == UNREACHABLE  # obstáculo central


def test_dijkstra_walls_block_propagation() -> None:
    """Un muro completamente aislante crea zonas inalcanzables."""
    # Mapa 5×3 con muro vertical dividiendo en dos zonas
    grid = [[TileType.WALL] * 5 for _ in range(3)]
    for r in range(3):
        grid[r][0] = TileType.FLOOR  # Columna izquierda libre
        grid[r][2] = TileType.WALL   # Muro divisor
        grid[r][4] = TileType.FLOOR  # Columna derecha libre
    # Fila superior e inferior son muro; solo r=1 es piso en columnas 0 y 4
    grid[1][0] = TileType.FLOOR
    grid[1][4] = TileType.FLOOR

    tm = TileMap(5, 3, 32, grid)
    dmap = DijkstraMap(tm)
    dmap.compute(1, 0)  # Fuente en esquina sup izq (es muro, no propaga)

    # Como (1,0) es muro, probamos desde (0,1) que sí es piso
    dmap.compute(0, 1)
    assert dmap.distance_at(0, 1) == 0
    # (4,1) está bloqueada por muro en col 2
    assert dmap.distance_at(4, 1) == UNREACHABLE


def test_dijkstra_best_neighbor_o1() -> None:
    """best_neighbor devuelve la dirección correcta hacia la fuente en O(1)."""
    tm = _simple_tilemap()
    dmap = DijkstraMap(tm)
    dmap.compute(1, 1)

    # Desde (3,1) la ruta más corta va hacia la izquierda (-1,0)
    direction = dmap.best_neighbor(3, 1)
    assert direction == (-1, 0)

    # Desde (1,2) la ruta más corta va hacia arriba (0,-1)
    direction = dmap.best_neighbor(1, 2)
    assert direction == (0, -1)

    # Desde la fuente misma no hay mejor vecino (ya está en distancia 0)
    direction = dmap.best_neighbor(1, 1)
    # Debe devolver un vecino con distancia 1 (que es > 0), o None si todos > 0
    # En realidad, best_neighbor busca d < current_d; current_d=0, ningún vecino tiene d<0
    assert direction is None


def test_dijkstra_best_neighbor_unreachable() -> None:
    """best_neighbor devuelve None para celdas inalcanzables."""
    tm = _simple_tilemap()
    dmap = DijkstraMap(tm)
    dmap.compute(1, 1)

    # Muro: inalcanzable
    assert dmap.best_neighbor(0, 0) is None
    # Fuera de límites
    assert dmap.best_neighbor(-1, -1) is None


def test_dijkstra_determinism() -> None:
    """Misma fuente produce mismas distancias."""
    tm = _simple_tilemap()
    d1 = DijkstraMap(tm)
    d1.compute(3, 2)
    d2 = DijkstraMap(tm)
    d2.compute(3, 2)

    for r in range(tm.height):
        for c in range(tm.width):
            assert d1.distance_at(c, r) == d2.distance_at(c, r)


def test_dijkstra_multi_source() -> None:
    """compute_multi con dos fuentes produce distancias mínimas a la más cercana."""
    tm = _simple_tilemap()
    dmap = DijkstraMap(tm)
    dmap.compute_multi([(1, 1), (6, 4)])

    # Cada fuente tiene distancia 0
    assert dmap.distance_at(1, 1) == 0
    assert dmap.distance_at(6, 4) == 0

    # (1,2) está a 1 de (1,1)
    assert dmap.distance_at(1, 2) == 1
    # (6,3) está a 1 de (6,4)
    assert dmap.distance_at(6, 3) == 1


def test_dijkstra_recompute_clears_previous() -> None:
    """Recomputar limpia distancias anteriores correctamente."""
    tm = _simple_tilemap()
    dmap = DijkstraMap(tm)
    dmap.compute(1, 1)
    old_dist = dmap.distance_at(6, 4)

    dmap.compute(6, 4)
    assert dmap.distance_at(6, 4) == 0
    assert dmap.distance_at(1, 1) == old_dist  # Simétrico en mapa libre


def test_dijkstra_direction_toward_source() -> None:
    """direction_toward_source devuelve un Vec2 unitario correcto."""
    tm = _simple_tilemap()
    dmap = DijkstraMap(tm)
    dmap.compute(1, 1)

    # Desde el centro del tile (3,1) → debe ir hacia izquierda
    direction = dmap.direction_toward_source(3 * 32 + 16, 1 * 32 + 16)
    assert direction is not None
    assert direction.x == pytest.approx(-1.0)
    assert direction.y == pytest.approx(0.0)

    # Desde muro → None
    direction = dmap.direction_toward_source(16, 16)  # tile (0,0) = WALL
    assert direction is None

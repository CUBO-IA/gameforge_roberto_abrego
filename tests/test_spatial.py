"""Pruebas unitarias de la partición espacial (game.world.spatial.SpatialHash)."""

from __future__ import annotations

import pytest

from game.core.math2d import Vec2
from game.world.spatial import SpatialHash


def test_spatial_hash_invalid_cell_size() -> None:
    with pytest.raises(ValueError):
        SpatialHash(cell_size=0)
    with pytest.raises(ValueError):
        SpatialHash(cell_size=-10)


def test_spatial_hash_insert_and_query_radius() -> None:
    grid: SpatialHash[str] = SpatialHash(cell_size=64.0)
    grid.insert("A", Vec2(10, 10), radius=5.0)
    grid.insert("B", Vec2(50, 50), radius=10.0)
    grid.insert("C", Vec2(200, 200), radius=5.0)

    # Consulta alrededor de (0,0) con radio 30: debe alcanzar a 'A'
    res = grid.query_radius(Vec2(0, 0), radius=30.0)
    assert "A" in res
    assert "B" not in res
    assert "C" not in res

    # Consulta con radio grande que cubra 'A' y 'B' pero no 'C'
    res_large = grid.query_radius(Vec2(20, 20), radius=60.0)
    assert "A" in res_large
    assert "B" in res_large
    assert "C" not in res_large


def test_spatial_hash_query_rect() -> None:
    grid: SpatialHash[str] = SpatialHash(cell_size=64.0)
    grid.insert("item1", Vec2(30, 30), radius=5.0)
    grid.insert("item2", Vec2(150, 150), radius=5.0)

    # Rectángulo que cubre (0, 0, 100, 100)
    res = grid.query_rect(0, 0, 100, 100)
    assert "item1" in res
    assert "item2" not in res


def test_spatial_hash_query_pairs() -> None:
    grid: SpatialHash[str] = SpatialHash(cell_size=64.0)
    # 'A' y 'B' en la misma celda
    grid.insert("A", Vec2(10, 10), radius=5.0)
    grid.insert("B", Vec2(20, 20), radius=5.0)
    # 'C' en una celda distante
    grid.insert("C", Vec2(300, 300), radius=5.0)

    pairs = grid.query_pairs()
    # Debe detectar el par (A, B) sin duplicados y sin emparejar con C
    assert len(pairs) == 1
    pair = list(pairs)[0]
    assert ("A" in pair) and ("B" in pair)


def test_spatial_hash_clear() -> None:
    grid: SpatialHash[str] = SpatialHash(cell_size=64.0)
    grid.insert("X", Vec2(10, 10), radius=5.0)
    assert len(grid.query_radius(Vec2(10, 10), 10.0)) == 1

    grid.clear()
    assert len(grid.query_radius(Vec2(10, 10), 10.0)) == 0
    assert len(grid.query_pairs()) == 0

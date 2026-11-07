"""Pruebas del cargador de mapas Tiled (game.world.tiled_loader)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from game.world.tiled_loader import TiledError, load_tiled_json
from game.world.tiles import TileType


def test_load_tiled_json_valid(tmp_path: Path) -> None:
    map_data = {
        "width": 4,
        "height": 3,
        "tilewidth": 32,
        "tileheight": 32,
        "layers": [
            {
                "name": "Ground",
                "type": "tilelayer",
                "data": [
                    1, 1, 1, 1,
                    1, 2, 2, 1,
                    1, 1, 1, 1,
                ],
            },
            {
                "name": "Entities",
                "type": "objectgroup",
                "objects": [
                    {"name": "player_spawn", "type": "spawn", "x": 48.0, "y": 48.0},
                    {"name": "altar_main", "type": "altar", "x": 80.0, "y": 48.0},
                    {"name": "chest_1", "type": "chest", "x": 48.0, "y": 80.0},
                ],
            },
        ],
    }
    file_path = tmp_path / "test_map.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(map_data, f)

    result = load_tiled_json(file_path)
    assert result.tilemap.width == 4
    assert result.tilemap.height == 3
    assert result.tilemap.tile_size == 32
    # El centro (1, 1) es FLOOR (GID 2)
    assert result.tilemap.tile_at(1, 1) == TileType.FLOOR
    # Borde es WALL (GID 1)
    assert result.tilemap.tile_at(0, 0) == TileType.WALL

    # Comprobación de objetos extraídos
    assert result.spawn.x == 48.0
    assert result.spawn.y == 48.0
    assert result.altar is not None
    assert result.altar.x == 80.0
    assert len(result.chests) == 1


def test_load_tiled_json_file_not_found() -> None:
    with pytest.raises(TiledError):
        load_tiled_json("archivo_fantasma_inexistente.json")


def test_load_tiled_json_corrupt_data(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.json"
    with open(bad_file, "w", encoding="utf-8") as f:
        f.write("esto no es json valido {[[")

    with pytest.raises(TiledError):
        load_tiled_json(bad_file)


def test_load_tiled_json_missing_dimensions(tmp_path: Path) -> None:
    bad_map = {"width": 0, "height": 10, "layers": []}
    fpath = tmp_path / "dim.json"
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(bad_map, f)

    with pytest.raises(TiledError):
        load_tiled_json(fpath)


def test_load_tiled_json_missing_tilelayer(tmp_path: Path) -> None:
    no_tilelayer = {
        "width": 5,
        "height": 5,
        "tilewidth": 32,
        "tileheight": 32,
        "layers": [{"type": "objectgroup", "objects": []}],
    }
    fpath = tmp_path / "nolayer.json"
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(no_tilelayer, f)

    with pytest.raises(TiledError):
        load_tiled_json(fpath)

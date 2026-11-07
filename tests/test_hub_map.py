"""Pruebas unitarias para la carga del mapa hub narrativo (Opción 4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from game.world.tiled_loader import TiledError, load_tiled_json
from game.world.tiles import TileType

HUB_MAP_PATH = Path(__file__).resolve().parent.parent / "game" / "data" / "maps" / "hub_town.json"


def test_hub_map_loads_successfully() -> None:
    """El mapa hub se carga sin errores."""
    result = load_tiled_json(HUB_MAP_PATH)
    assert result.tilemap is not None
    assert result.tilemap.width == 20
    assert result.tilemap.height == 15
    assert result.tilemap.tile_size == 32


def test_hub_map_spawn_position() -> None:
    """El spawn está definido y dentro del mapa."""
    result = load_tiled_json(HUB_MAP_PATH)
    assert result.spawn is not None
    # Spawn debe caer dentro del mapa en píxeles
    assert 0 <= result.spawn.x < result.tilemap.pixel_width
    assert 0 <= result.spawn.y < result.tilemap.pixel_height


def test_hub_map_altar_and_campfire() -> None:
    """El altar y la hoguera están definidos."""
    result = load_tiled_json(HUB_MAP_PATH)
    assert result.altar is not None
    assert result.campfire is not None


def test_hub_map_chests() -> None:
    """El mapa hub tiene al menos 2 cofres definidos."""
    result = load_tiled_json(HUB_MAP_PATH)
    assert len(result.chests) >= 2


def test_hub_map_npcs_extracted() -> None:
    """Se extraen los 3 NPCs con nombre, posición y propiedades."""
    result = load_tiled_json(HUB_MAP_PATH)
    assert len(result.npcs) == 3

    roles = {npc.role for npc in result.npcs}
    assert "merchant" in roles
    assert "blacksmith" in roles
    assert "quest_giver" in roles


def test_hub_map_npc_properties() -> None:
    """Cada NPC tiene diálogo no vacío."""
    result = load_tiled_json(HUB_MAP_PATH)
    for npc in result.npcs:
        assert npc.dialog, f"NPC '{npc.name}' no tiene diálogo."
        assert npc.position is not None


def test_hub_map_border_is_wall() -> None:
    """Todo el borde perimetral del mapa hub es muro sólido."""
    result = load_tiled_json(HUB_MAP_PATH)
    tm = result.tilemap

    for x in range(tm.width):
        assert tm.tile_at(x, 0) == TileType.WALL, f"Borde superior en ({x},0) no es muro"
        assert tm.tile_at(x, tm.height - 1) == TileType.WALL, f"Borde inferior en ({x},{tm.height-1}) no es muro"

    for y in range(tm.height):
        assert tm.tile_at(0, y) == TileType.WALL, f"Borde izquierdo en (0,{y}) no es muro"
        assert tm.tile_at(tm.width - 1, y) == TileType.WALL, f"Borde derecho en ({tm.width-1},{y}) no es muro"


def test_hub_map_has_water_feature() -> None:
    """El mapa hub contiene la fuente/estanque central de agua."""
    result = load_tiled_json(HUB_MAP_PATH)
    tm = result.tilemap

    has_water = any(
        tm.tile_at(c, r) == TileType.WATER
        for r in range(tm.height)
        for c in range(tm.width)
    )
    assert has_water, "El mapa hub debería contener al menos un tile de agua."


def test_hub_map_spawn_on_floor() -> None:
    """El spawn está sobre un tile de suelo transitable."""
    result = load_tiled_json(HUB_MAP_PATH)
    assert not result.tilemap.is_solid_at(result.spawn.x, result.spawn.y)


def test_hub_map_file_not_found() -> None:
    """Intentar cargar un archivo inexistente lanza TiledError."""
    with pytest.raises(TiledError, match="no encontrado"):
        load_tiled_json("nonexistent_map.json")

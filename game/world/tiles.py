"""Tipos de tile y sus propiedades de simulación."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class TileType(IntEnum):
    FLOOR = 0
    WALL = 1
    WATER = 2
    LAVA = 3


@dataclass(frozen=True, slots=True)
class TileDef:
    solid: bool
    speed_multiplier: float = 1.0
    damage_per_second: float = 0.0


TILE_DEFS: dict[TileType, TileDef] = {
    TileType.FLOOR: TileDef(solid=False),
    TileType.WALL: TileDef(solid=True),
    TileType.WATER: TileDef(solid=False, speed_multiplier=0.62, damage_per_second=0.0),
    TileType.LAVA: TileDef(solid=False, speed_multiplier=0.85, damage_per_second=18.0),
}


def is_walkable(tile: TileType) -> bool:
    return not TILE_DEFS[tile].solid

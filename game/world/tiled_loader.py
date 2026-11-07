"""Cargador de mapas autorales en formato Tiled (JSON).

Permite cargar mapas diseñados a mano con el editor Tiled Map Editor,
convirtiéndolos en instancias nativas de TileMap y extrayendo puntos clave
(spawn, altares, cofres) sin dependencias externas pesadas.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from game.core.math2d import Vec2
from game.world.tilemap import TileMap
from game.world.tiles import TileType


class TiledError(Exception):
    """Excepción para errores de esquema o contenido de mapas Tiled."""


# Mapeo por defecto de GIDs de Tiled a TileType de GAMEFORGE
DEFAULT_GID_MAP: dict[int, TileType] = {
    0: TileType.WALL,
    1: TileType.WALL,
    2: TileType.FLOOR,
    3: TileType.WATER,
    4: TileType.LAVA,
}


@dataclass(frozen=True, slots=True)
class NpcSpec:
    """Descripción de un NPC extraído de una capa de objetos de Tiled."""

    name: str
    position: Vec2
    role: str = ""
    dialog: str = ""
    properties: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TiledMapData:
    tilemap: TileMap
    spawn: Vec2
    altar: Vec2 | None = None
    campfire: Vec2 | None = None
    chests: list[Vec2] = field(default_factory=list)
    npcs: list[NpcSpec] = field(default_factory=list)


def load_tiled_json(
    path: Path | str,
    gid_map: dict[int, TileType] | None = None,
) -> TiledMapData:
    """Carga y valida un archivo de mapa exportado por Tiled en formato JSON."""
    p = Path(path)
    if not p.is_file():
        raise TiledError(f"Archivo de mapa Tiled no encontrado: {p}")

    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        raise TiledError(f"Error al leer JSON de Tiled en {p}: {exc}") from exc

    if not isinstance(data, dict):
        raise TiledError("El archivo Tiled debe ser un objeto JSON.")

    width = data.get("width")
    height = data.get("height")
    tile_width = data.get("tilewidth")
    tile_height = data.get("tileheight")

    if not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
        raise TiledError(f"Dimensiones de mapa inválidas en {p}: {width}x{height}")
    if (
        not isinstance(tile_width, int)
        or tile_width <= 0
        or not isinstance(tile_height, int)
        or tile_height <= 0
    ):
        raise TiledError(f"Tamaño de tile inválido en {p}: {tile_width}x{tile_height}")

    mapping = gid_map if gid_map is not None else DEFAULT_GID_MAP

    tile_layer_found = False
    tiles_matrix: list[list[TileType]] = [
        [TileType.WALL for _ in range(width)] for _ in range(height)
    ]

    spawn_pos: Vec2 | None = None
    altar_pos: Vec2 | None = None
    campfire_pos: Vec2 | None = None
    chests_pos: list[Vec2] = []
    npcs_list: list[NpcSpec] = []

    for layer in data.get("layers", []):
        layer_type = layer.get("type")
        if layer_type == "tilelayer":
            raw_data = layer.get("data")
            if not isinstance(raw_data, list) or len(raw_data) != width * height:
                raise TiledError(f"La capa de tiles '{layer.get('name')}' tiene datos corruptos.")
            tile_layer_found = True
            for i, gid in enumerate(raw_data):
                col = i % width
                row = i // width
                tiles_matrix[row][col] = mapping.get(int(gid), TileType.WALL)

        elif layer_type == "objectgroup":
            for obj in layer.get("objects", []):
                obj_name = str(obj.get("name", "")).lower()
                obj_type = str(obj.get("type", "")).lower()
                ox = float(obj.get("x", 0.0))
                oy = float(obj.get("y", 0.0))
                pos = Vec2(ox, oy)

                if "spawn" in obj_name or "spawn" in obj_type:
                    spawn_pos = pos
                elif "altar" in obj_name or "altar" in obj_type:
                    altar_pos = pos
                elif "campfire" in obj_name or "campfire" in obj_type:
                    campfire_pos = pos
                elif "chest" in obj_name or "chest" in obj_type:
                    chests_pos.append(pos)
                elif "npc" in obj_name or "npc" in obj_type:
                    # Extraer propiedades personalizadas del NPC
                    props: dict[str, str] = {}
                    for prop in obj.get("properties", []):
                        props[str(prop.get("name", ""))] = str(prop.get("value", ""))
                    npcs_list.append(
                        NpcSpec(
                            name=str(obj.get("name", "")),
                            position=pos,
                            role=props.get("role", ""),
                            dialog=props.get("dialog", ""),
                            properties=props,
                        )
                    )

    if not tile_layer_found:
        raise TiledError(f"El mapa {p} no contiene ninguna capa de tiles ('tilelayer').")

    if spawn_pos is None:
        # Fallback si no hay objeto spawn explícito: centro del mapa
        spawn_pos = Vec2(width * tile_width / 2.0, height * tile_height / 2.0)

    tilemap = TileMap(width, height, tile_width, tiles_matrix)
    return TiledMapData(
        tilemap=tilemap,
        spawn=spawn_pos,
        altar=altar_pos,
        campfire=campfire_pos,
        chests=chests_pos,
        npcs=npcs_list,
    )

"""Progresión por plantas y puntuación derivada.

Gestiona las transiciones entre pisos de la mazmorra, el escalado de dificultad
y las condiciones de victoria final en la última planta.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

MAX_FLOORS: int = 3


class FloorType(StrEnum):
    DUNGEON = "dungeon"
    CAVERN = "cavern"


FLOOR_THEMES: dict[int, str] = {
    1: "El Umbral Olvidado",
    2: "La Cripta de Ceniza",
    3: "El Núcleo de la Fragua",
}

FLOOR_TYPES: dict[int, FloorType] = {
    1: FloorType.DUNGEON,  # El Umbral Olvidado: arquitectura de salas y corredores
    2: FloorType.CAVERN,   # La Cripta de Ceniza: cavernas subterráneas orgánicas
    3: FloorType.DUNGEON,  # El Núcleo de la Fragua: cámara central
}


def floor_type_for(floor: int, variant: str | None = None) -> FloorType:
    """Determina si un piso utiliza generación de mazmorra clásica o caverna orgánica."""
    if variant == "cavern":
        return FloorType.CAVERN
    if variant == "dungeon":
        return FloorType.DUNGEON
    return FLOOR_TYPES.get(floor, FloorType.DUNGEON)


def floor_bonus(floor: int) -> int:
    """Puntuación por alcanzar una planta (crece linealmente)."""
    return 50 * floor


def shard_bonus(shards: int) -> int:
    """Puntuación por fragmentos recogidos al terminar."""
    return shards * 100


def victory_bonus() -> int:
    return 500


def finish_score(shards: int, floor: int, victory: bool) -> int:
    """Puntos añadidos al cerrar la partida (muerte o victoria)."""
    return shard_bonus(shards) + floor_bonus(floor) + (victory_bonus() if victory else 0)


def is_final_floor(floor: int) -> bool:
    """Indica si la planta especificada es la planta final del juego."""
    return floor >= MAX_FLOORS


def shards_required_for_floor(floor: int) -> int:
    """Fragmentos solares necesarios para activar el Altar de cada planta."""
    return 2 + floor  # Planta 1: 3, Planta 2: 4, Planta 3: 5


def floor_theme_name(floor: int) -> str:
    return FLOOR_THEMES.get(floor, f"Planta Subterránea {floor}")


@dataclass(frozen=True, slots=True)
class FloorTransition:
    """Datos de una transición a la siguiente planta."""

    current_floor: int
    next_floor: int
    theme: str
    shards_required: int
    floor_type: FloorType = FloorType.DUNGEON


def calculate_floor_transition(current_floor: int) -> FloorTransition | None:
    """Calcula la transición hacia el siguiente piso o None si ya es el final."""
    if is_final_floor(current_floor):
        return None
    next_floor = current_floor + 1
    return FloorTransition(
        current_floor=current_floor,
        next_floor=next_floor,
        theme=floor_theme_name(next_floor),
        shards_required=shards_required_for_floor(next_floor),
        floor_type=floor_type_for(next_floor),
    )

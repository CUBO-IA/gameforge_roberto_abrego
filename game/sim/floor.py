"""Progresión por plantas y puntuación derivada.

La Fase 2 extenderá este módulo con la transición real entre plantas
(``FloorTransition``) encadenando pisos del generador.
"""

from __future__ import annotations

from dataclasses import dataclass

from game.core.math2d import Vec2


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


@dataclass(frozen=True, slots=True)
class FloorTransition:
    """Datos de una transición a la siguiente planta (Fase 2)."""

    next_floor: int
    spawn: Vec2

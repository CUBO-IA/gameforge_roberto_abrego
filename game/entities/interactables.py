"""Objetos interactivos del mundo."""

from __future__ import annotations

from dataclasses import dataclass

from game.core.math2d import Vec2


@dataclass(slots=True)
class Chest:
    id: str
    position: Vec2
    item_id: str
    quantity: int
    opened: bool = False
    radius: float = 18.0

    @property
    def label(self) -> str:
        return "Cofre abierto" if self.opened else "Abrir cofre"


@dataclass(slots=True)
class Campfire:
    position: Vec2
    radius: float = 24.0

    @property
    def label(self) -> str:
        return "Descansar y guardar"


@dataclass(slots=True)
class ForgeAltar:
    position: Vec2
    activated: bool = False
    radius: float = 32.0

    @property
    def label(self) -> str:
        return "Activar la Fragua" if not self.activated else "Fragua activa"

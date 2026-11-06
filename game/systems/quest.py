"""Objetivo principal: recuperar fragmentos y activar la Fragua."""

from __future__ import annotations

from dataclasses import dataclass

from game.systems.inventory import Inventory


@dataclass(slots=True)
class QuestState:
    shards_required: int = 3
    altar_activated: bool = False

    def __post_init__(self) -> None:
        if self.shards_required < 1:
            raise ValueError("shards_required debe ser >= 1.")

    def shards_collected(self, inventory: Inventory) -> int:
        return inventory.count("shard")

    def can_activate(self, inventory: Inventory) -> bool:
        return (
            not self.altar_activated
            and self.shards_collected(inventory) >= self.shards_required
        )

    def activate(self, inventory: Inventory) -> bool:
        if not self.can_activate(inventory):
            return False
        self.altar_activated = True
        return True

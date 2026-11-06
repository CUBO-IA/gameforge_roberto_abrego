"""Pruebas de los sistemas puros de game.sim (interacción, botín, puntuación)."""

from __future__ import annotations

import pytest

from game.core.math2d import Vec2
from game.entities.interactables import Chest, ForgeAltar
from game.sim.floor import finish_score, floor_bonus
from game.sim.interaction import (
    find_nearest_interaction,
    loot_message,
    open_chest,
    use_potion,
)
from game.systems.inventory import Inventory
from game.systems.quest import QuestState


def _chest(item_id: str = "shard", quantity: int = 1, x: float = 100.0) -> Chest:
    return Chest("c0", Vec2(x, 100.0), item_id, quantity)


class _Campfire:
    """Sustituto mínimo: solo posición para find_nearest_interaction."""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.position = Vec2(x, y)
        self.opened = False


def _altar(x: float = 5000.0, activated: bool = False) -> ForgeAltar:
    altar = ForgeAltar(Vec2(x, 0.0))
    altar.activated = activated
    return altar


def test_open_chest_transfers_and_marks_opened() -> None:
    chest = _chest("shard", 2)
    inventory = Inventory()
    result = open_chest(chest, inventory)
    assert result is not None and not result.full
    assert result.quantity == 2
    assert chest.opened
    assert inventory.count("shard") == 2


def test_open_chest_twice_returns_none() -> None:
    chest = _chest()
    inventory = Inventory()
    assert open_chest(chest, inventory) is not None
    assert open_chest(chest, inventory) is None


def test_open_chest_full_inventory_does_not_open() -> None:
    chest = _chest("shard", 1)
    inventory = Inventory(capacity=1)
    inventory.add("potion", 1)
    result = open_chest(chest, inventory)
    assert result is not None and result.full
    assert not chest.opened


def test_loot_message_reports_shard_progress() -> None:
    chest = _chest("shard", 1)
    inventory = Inventory()
    result = open_chest(chest, inventory)
    assert result is not None
    message = loot_message(result, shards_required=3, shard_count=1)
    assert message == "Fragmento de ascua 1/3"


def test_find_nearest_prefers_closest_chest() -> None:
    near = _chest(x=100.0)
    far = _chest(x=150.0)
    campfire = _Campfire(3000.0, 0.0)
    found = find_nearest_interaction(
        [far, near], campfire, _altar(), Vec2(100.0, 100.0), 0, 3
    )
    assert found is not None
    assert found[0] is near


def test_find_nearest_ignores_opened_chests() -> None:
    chest = _chest(x=100.0)
    chest.opened = True
    found = find_nearest_interaction(
        [chest], _Campfire(3000.0, 0.0), _altar(), Vec2(100.0, 100.0), 0, 3
    )
    assert found is None


def test_find_nearest_altar_label_counts_missing_shards() -> None:
    altar = _altar(x=60.0)
    found = find_nearest_interaction(
        [], _Campfire(3000.0, 0.0), altar, Vec2(100.0, 0.0), 1, 3
    )
    assert found is not None
    assert "faltan 2" in found[1]


def test_use_potion_validates_state() -> None:
    from game.entities.player import Player

    player = Player(Vec2(0.0, 0.0), _player_config())
    inventory = Inventory()
    # Sin frascos.
    assert use_potion(player, inventory, 30.0).status == "empty"
    inventory.add("potion", 1)
    # Salud completa: no consume.
    assert use_potion(player, inventory, 30.0).status == "full_health"
    assert inventory.count("potion") == 1
    # Dañado: consume y cura.
    player.take_damage(40.0)
    result = use_potion(player, inventory, 30.0)
    assert result.status == "used"
    assert result.healed == 30.0
    assert inventory.count("potion") == 0


def test_finish_score_combines_bonuses() -> None:
    assert finish_score(shards=3, floor=2, victory=True) == 300 + 100 + 500
    assert finish_score(shards=1, floor=1, victory=False) == 100 + 50
    assert floor_bonus(4) == 200


def test_quest_activation_still_works_with_sim() -> None:
    """El altar sigue exigiendo fragmentos vía QuestState (contrato intacto)."""
    quest = QuestState(2)
    inventory = Inventory()
    inventory.add("shard", 1)
    assert quest.activate(inventory) is False
    inventory.add("shard", 1)
    assert quest.activate(inventory) is True


def test_items_catalog_has_core_items() -> None:
    from game.entities.items import ITEMS

    for item in ("coin", "potion", "shard"):
        assert item in ITEMS


def _player_config():
    from game.core.config import PlayerConfig

    return PlayerConfig()

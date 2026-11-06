import pytest

from game.systems.inventory import Inventory
from game.systems.quest import QuestState


def test_quest_activation_requires_shards() -> None:
    quest = QuestState(shards_required=3)
    inventory = Inventory()
    inventory.add("shard", 2)
    assert quest.shards_collected(inventory) == 2
    assert not quest.can_activate(inventory)
    assert not quest.activate(inventory)
    assert not quest.altar_activated

    inventory.add("shard", 1)
    assert quest.can_activate(inventory)
    assert quest.activate(inventory)
    assert quest.altar_activated
    assert not quest.can_activate(inventory)
    assert not quest.activate(inventory)


def test_invalid_requirement() -> None:
    with pytest.raises(ValueError):
        QuestState(shards_required=0)

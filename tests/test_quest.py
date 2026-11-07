from __future__ import annotations

import pytest

from game.sim.quest import (
    QuestDefinition,
    QuestError,
    QuestManager,
    load_quest_catalog,
)
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


def test_load_default_quest_catalog() -> None:
    catalog = load_quest_catalog()
    assert len(catalog) >= 5
    assert "quest_f1_shards" in catalog
    assert "quest_f1_slimes" in catalog


def test_quest_definition_validation() -> None:
    with pytest.raises(QuestError):
        QuestDefinition.from_dict("invalido")  # type: ignore[arg-type]

    with pytest.raises(QuestError):
        QuestDefinition.from_dict({"id": "", "count": 1})

    with pytest.raises(QuestError):
        QuestDefinition.from_dict({"id": "q1", "count": 0})


def test_quest_manager_kill_progress() -> None:
    catalog = {
        "q_slimes": QuestDefinition(
            id="q_slimes",
            title="Mata slimes",
            description="",
            floor=1,
            type="kill",
            target="slime",
            count=2,
            reward_score=100,
            reward_item="coin",
            reward_count=5,
        )
    }
    qm = QuestManager(catalog=catalog)
    qm.start_floor(1)
    inv = Inventory()

    # Matar un wisp no avanza la misión de slimes
    assert qm.on_kill("wisp", inv) == []
    assert qm.progress["q_slimes"].current_count == 0

    # Matar primer slime
    assert qm.on_kill("slime", inv) == []
    assert qm.progress["q_slimes"].current_count == 1
    assert not qm.progress["q_slimes"].completed

    # Matar segundo slime completa la misión
    rewards = qm.on_kill("slime", inv)
    assert len(rewards) == 1
    assert rewards[0].score == 100
    assert qm.progress["q_slimes"].completed
    assert inv.count("coin") == 5

    # Matar un tercer slime no vuelve a dar recompensa
    assert qm.on_kill("slime", inv) == []


def test_quest_manager_chest_and_altar() -> None:
    catalog = {
        "q_chest": QuestDefinition(
            id="q_chest",
            title="Abre cofre",
            description="",
            floor=1,
            type="chest",
            target="",
            count=1,
            reward_score=50,
            reward_item="",
            reward_count=0,
        ),
        "q_altar": QuestDefinition(
            id="q_altar",
            title="Activa altar",
            description="",
            floor=1,
            type="altar",
            target="",
            count=1,
            reward_score=200,
            reward_item="potion",
            reward_count=1,
        ),
    }
    qm = QuestManager(catalog=catalog)
    qm.start_floor(1)
    inv = Inventory()

    rewards_c = qm.on_chest_opened(inv)
    assert len(rewards_c) == 1
    assert rewards_c[0].score == 50

    rewards_a = qm.on_altar_activated(inv)
    assert len(rewards_a) == 1
    assert rewards_a[0].score == 200
    assert inv.count("potion") == 1


def test_quest_manager_serialization() -> None:
    catalog = load_quest_catalog()
    qm = QuestManager(catalog=catalog)
    qm.start_floor(1)
    qm.on_kill("slime")

    data = qm.to_dict()
    assert "progress" in data

    qm2 = QuestManager.from_dict(data, catalog=catalog)
    assert qm2.progress["quest_f1_slimes"].current_count == 1

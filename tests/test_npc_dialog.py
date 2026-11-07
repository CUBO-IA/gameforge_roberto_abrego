"""Pruebas del sistema de diálogos y comercio con personajes de Nemotron-Personas-El-Salvador."""

from __future__ import annotations

from game.core.math2d import Vec2
from game.entities.interactables import Campfire, ForgeAltar
from game.sim.dialog import (
    DATASET_LICENSE,
    DATASET_NAME,
    DATASET_URL,
    DialogManager,
)
from game.sim.interaction import find_nearest_interaction
from game.systems.inventory import Inventory
from game.world.tiled_loader import NpcSpec


def test_nemotron_dataset_attribution_constants() -> None:
    """Verifica que la atribución del dataset de Hugging Face es exacta."""
    assert DATASET_NAME == "nvidia/Nemotron-Personas-El-Salvador"
    assert DATASET_URL == "https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador"
    assert DATASET_LICENSE == "CC-BY-4.0"


def test_nemotron_personas_loaded_with_uuids() -> None:
    """Comprueba la carga de las tres personas con sus UUIDs exactos del dataset."""
    dm = DialogManager()

    # Doña Rosa - Comerciante de La Libertad
    rosa = dm.get_persona("merchant")
    assert rosa is not None
    assert rosa.uuid == "108fefeb-c9f6-4429-8ce1-a67eaad444ef"
    assert rosa.name == "Rosa"
    assert rosa.department == "La Libertad"
    assert rosa.age == 39

    # Maestro José - Herrero de Santa Ana
    jose = dm.get_persona("blacksmith")
    assert jose is not None
    assert jose.uuid == "2e2bca1d-f265-4214-beb3-858d676f2907"
    assert jose.name == "José"
    assert jose.department == "Santa Ana"
    assert jose.age == 51

    # Don Antonio - Sabio/Anciano de Santa Ana
    antonio = dm.get_persona("elder")
    assert antonio is not None
    assert antonio.uuid == "0b125a4d-c467-4cc5-8789-968ae1ba7f01"
    assert antonio.name == "Antonio"
    assert antonio.department == "Santa Ana"
    assert antonio.age == 88


def test_dialog_generation_contextual() -> None:
    """Verifica que el diálogo varía según el progreso de la misión."""
    dm = DialogManager()

    # Don Antonio aconsejando cuando faltan fragmentos
    dialog_missing = dm.get_dialog("elder", shard_count=1, shards_required=3)
    assert "faltan 2 fragmento(s)" in dialog_missing
    assert "Antonio" in dialog_missing
    assert "Santa Ana" in dialog_missing

    # Don Antonio celebrando al completar los fragmentos
    dialog_complete = dm.get_dialog("elder", shard_count=3, shards_required=3)
    assert "3 fragmentos solares completos" in dialog_complete

    # Doña Rosa ofreciendo frascos de brasa
    dialog_rosa = dm.get_dialog("merchant")
    assert "Doña Rosa" in dialog_rosa
    assert "15 monedas" in dialog_rosa


def test_trade_buy_potion_success() -> None:
    """Comprar una poción a Doña Rosa con monedas suficientes."""
    dm = DialogManager()
    inv = Inventory(capacity=4)
    inv.add("coin", 30)

    result = dm.buy_potion(inv, cost=15)
    assert result.success is True
    assert inv.count("potion") == 1
    assert inv.count("coin") == 15
    assert "¡Compraste 1 Frasco de Brasa" in result.message


def test_trade_buy_potion_insufficient_coins() -> None:
    """Intento de compra sin monedas suficientes falla limpiamente."""
    dm = DialogManager()
    inv = Inventory(capacity=4)
    inv.add("coin", 5)

    result = dm.buy_potion(inv, cost=15)
    assert result.success is False
    assert inv.count("potion") == 0
    assert inv.count("coin") == 5
    assert "No te alcanzan las monedas" in result.message


def test_npc_interaction_proximity() -> None:
    """El jugador detecta al NPC cuando entra en su radio de interacción."""
    campfire = Campfire(Vec2(500.0, 500.0))
    altar = ForgeAltar(Vec2(600.0, 600.0))
    npc = NpcSpec(
        name="Doña Rosa",
        position=Vec2(100.0, 100.0),
        role="merchant",
        dialog="¡Buenas!",
        properties={"uuid": "108fefeb-c9f6-4429-8ce1-a67eaad444ef"},
    )

    # Jugador cerca de Doña Rosa (distancia 20 px <= 56 px)
    interaction = find_nearest_interaction(
        chests=[],
        campfire=campfire,
        altar=altar,
        player_position=Vec2(100.0, 120.0),
        shard_count=0,
        shards_required=3,
        npcs=[npc],
    )
    assert interaction is not None
    obj, label = interaction
    assert obj == npc
    assert label == "Hablar con Doña Rosa"

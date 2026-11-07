"""Interacción del jugador con el mundo: cercanía, cofres y consumibles.

Sistemas puros: deciden y mutan el estado de dominio; la escena interpreta
los resultados como audio, efectos y avisos.
"""

from __future__ import annotations

from dataclasses import dataclass

from game.entities.interactables import Campfire, Chest, ForgeAltar
from game.entities.items import ITEMS
from game.entities.player import Player
from game.systems.inventory import Inventory

# Radio de interacción por tipo de objeto (en píxeles).
CHEST_RANGE = 54.0
CAMPFIRE_RANGE = 62.0
ALTAR_RANGE = 74.0
NPC_RANGE = 56.0


@dataclass(frozen=True, slots=True)
class LootResult:
    """Resultado de abrir un cofre."""

    item_id: str
    quantity: int
    full: bool


@dataclass(frozen=True, slots=True)
class PotionResult:
    """Resultado de usar un frasco de brasa."""

    status: str  # "used" | "empty" | "full_health"
    healed: float = 0.0


def find_nearest_interaction(
    chests: list[Chest],
    campfire: Campfire,
    altar: ForgeAltar,
    player_position,
    shard_count: int,
    shards_required: int,
    npcs: list | None = None,
) -> tuple[object, str] | None:
    """Objeto interactuable más cercano al jugador y su etiqueta."""
    candidates: list[tuple[float, object, str]] = []
    for chest in chests:
        if chest.opened:
            continue
        distance = chest.position.distance_to(player_position)
        if distance <= CHEST_RANGE:
            candidates.append((distance, chest, "Abrir cofre"))
    distance = campfire.position.distance_to(player_position)
    if distance <= CAMPFIRE_RANGE:
        candidates.append((distance, campfire, "Descansar y guardar"))
    distance = altar.position.distance_to(player_position)
    if distance <= ALTAR_RANGE and not altar.activated:
        remaining = shards_required - shard_count
        label = (
            "Activar la Fragua"
            if remaining <= 0
            else f"Fragua: faltan {remaining} fragmentos"
        )
        candidates.append((distance, altar, label))
    if npcs:
        for npc in npcs:
            distance = npc.position.distance_to(player_position)
            if distance <= NPC_RANGE:
                candidates.append((distance, npc, f"Hablar con {npc.name}"))
    if not candidates:
        return None
    candidates.sort(key=lambda entry: entry[0])
    return candidates[0][1], candidates[0][2]


def open_chest(chest: Chest, inventory: Inventory) -> LootResult | None:
    """Transfiere el contenido del cofre al inventario.

    Devuelve ``None`` si el cofre ya estaba abierto; ``LootResult.full``
    indica inventario sin espacio (el cofre queda sin abrir).
    """
    if chest.opened:
        return None
    accepted = inventory.add(chest.item_id, chest.quantity)
    if accepted <= 0:
        return LootResult(item_id=chest.item_id, quantity=0, full=True)
    chest.opened = True
    return LootResult(item_id=chest.item_id, quantity=accepted, full=False)


def loot_message(result: LootResult, shards_required: int, shard_count: int) -> str:
    """Mensaje de aviso asociado al botín (datos, no presentación)."""
    item = ITEMS[result.item_id]
    if result.full:
        return "Inventario lleno. Usa o descarta algo primero."
    if result.item_id == "shard":
        return f"Fragmento de ascua {shard_count}/{shards_required}"
    if result.item_id == "coin":
        return f"Monedas: +{result.quantity}"
    return f"Encontraste {item.name} x{result.quantity}"


def use_potion(player: Player, inventory: Inventory, heal_amount: float) -> PotionResult:
    """Consume un frasco y cura al jugador, con validación explícita."""
    if inventory.count("potion") <= 0:
        return PotionResult(status="empty")
    if player.health >= player.max_health:
        return PotionResult(status="full_health")
    inventory.remove("potion", 1)
    healed = player.heal(heal_amount)
    return PotionResult(status="used", healed=healed)

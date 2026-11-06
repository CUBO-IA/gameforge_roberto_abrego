import pytest

from game.systems.inventory import Inventory, InventoryError


def test_add_remove_and_count() -> None:
    inventory = Inventory(capacity=3)
    assert inventory.add("potion", 2) == 2
    assert inventory.add("potion", 3) == 3
    assert inventory.count("potion") == 5
    assert inventory.used_slots == 1
    assert inventory.total_quantity == 5
    assert inventory.has("potion", 5)
    assert not inventory.has("potion", 6)
    assert inventory.remove("potion", 2) == 2
    assert inventory.count("potion") == 3
    assert inventory.remove("potion", 99) == 3
    assert inventory.count("potion") == 0
    assert inventory.remove("potion") == 0
    assert inventory.total_quantity == 0


def test_capacity_counts_distinct_items() -> None:
    inventory = Inventory(capacity=2)
    inventory.add("potion", 50)
    inventory.add("coin", 50)
    assert inventory.is_full()
    assert inventory.add("shard", 1) == 0
    assert inventory.used_slots == 2


def test_stack_limit() -> None:
    inventory = Inventory()
    inventory.add("coin", 9999)
    assert inventory.add("coin", 10) == 0
    inventory.remove("coin", 1)
    assert inventory.add("coin", 10) == 1


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True])
def test_invalid_quantities(quantity) -> None:
    inventory = Inventory()
    with pytest.raises(InventoryError):
        inventory.add("potion", quantity)
    with pytest.raises(InventoryError):
        inventory.remove("potion", quantity)


def test_unknown_item_is_rejected() -> None:
    inventory = Inventory()
    with pytest.raises(InventoryError):
        inventory.add("sword_of_doom", 1)
    with pytest.raises(InventoryError):
        Inventory(slots={"unknown": 1})


def test_serialization_roundtrip_and_validation() -> None:
    inventory = Inventory(capacity=3, slots={"potion": 2, "coin": 5})
    assert inventory.to_dict() == {"coin": 5, "potion": 2}
    restored = Inventory.from_dict(inventory.to_dict(), capacity=3)
    assert restored.to_dict() == inventory.to_dict()

    with pytest.raises(InventoryError):
        Inventory.from_dict([])
    with pytest.raises(InventoryError):
        Inventory.from_dict({"unknown": 1})
    with pytest.raises(InventoryError):
        Inventory.from_dict({"potion": 0})
    with pytest.raises(InventoryError):
        Inventory.from_dict({"potion": True})
    with pytest.raises(InventoryError):
        Inventory.from_dict({"potion": 1, "coin": 1}, capacity=1)


def test_invalid_capacity() -> None:
    with pytest.raises(InventoryError):
        Inventory(capacity=0)

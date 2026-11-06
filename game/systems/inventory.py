"""Inventario por pilas con capacidad de ranuras."""

from __future__ import annotations

from collections.abc import Mapping

from game.entities.items import item_exists

MAX_STACK = 9999


class InventoryError(ValueError):
    """Operación de inventario inválida."""


class Inventory:
    """Capacidad medida en tipos de objeto distintos, no en unidades.

    Las cantidades deben ser enteros positivos. Las operaciones de añadir
    devuelven la cantidad realmente aceptada para que la UI pueda informar de
    un inventario lleno sin lanzar excepciones.
    """

    def __init__(self, capacity: int = 20, slots: Mapping[str, int] | None = None) -> None:
        if capacity < 1:
            raise InventoryError("La capacidad debe ser al menos 1.")
        self.capacity = capacity
        self._slots: dict[str, int] = {}
        for item_id, quantity in (slots or {}).items():
            self._validated_item(item_id)
            self._validated_quantity(quantity)
            if quantity > MAX_STACK:
                raise InventoryError(f"La pila de {item_id!r} supera {MAX_STACK}.")
            self._slots[item_id] = quantity
        if len(self._slots) > capacity:
            raise InventoryError("Los objetos iniciales superan la capacidad.")

    def add(self, item_id: str, quantity: int = 1) -> int:
        self._validated_item(item_id)
        self._validated_quantity(quantity)
        if item_id not in self._slots and len(self._slots) >= self.capacity:
            return 0
        current = self._slots.get(item_id, 0)
        accepted = min(quantity, MAX_STACK - current)
        if accepted <= 0:
            return 0
        self._slots[item_id] = current + accepted
        return accepted

    def remove(self, item_id: str, quantity: int = 1) -> int:
        self._validated_item(item_id)
        self._validated_quantity(quantity)
        current = self._slots.get(item_id, 0)
        removed = min(current, quantity)
        if removed <= 0:
            return 0
        remaining = current - removed
        if remaining:
            self._slots[item_id] = remaining
        else:
            del self._slots[item_id]
        return removed

    def count(self, item_id: str) -> int:
        return self._slots.get(item_id, 0)

    def has(self, item_id: str, quantity: int = 1) -> bool:
        if quantity <= 0:
            return True
        return self.count(item_id) >= quantity

    @property
    def used_slots(self) -> int:
        return len(self._slots)

    @property
    def total_quantity(self) -> int:
        return sum(self._slots.values())

    def items(self) -> list[tuple[str, int]]:
        return sorted(self._slots.items(), key=lambda pair: pair[0])

    def is_full(self) -> bool:
        return len(self._slots) >= self.capacity

    def clear(self) -> None:
        self._slots.clear()

    def to_dict(self) -> dict[str, int]:
        return dict(sorted(self._slots.items()))

    @classmethod
    def from_dict(cls, raw: object, capacity: int = 20) -> "Inventory":
        if not isinstance(raw, dict):
            raise InventoryError("El inventario guardado debe ser un objeto.")
        if len(raw) > capacity:
            raise InventoryError("El inventario guardado supera la capacidad.")
        slots: dict[str, int] = {}
        for item_id, quantity in raw.items():
            if not isinstance(item_id, str) or not isinstance(quantity, int):
                raise InventoryError("Entrada de inventario inválida.")
            if isinstance(quantity, bool) or not (1 <= quantity <= MAX_STACK):
                raise InventoryError(
                    f"Las cantidades del inventario deben estar entre 1 y {MAX_STACK}."
                )
            slots[item_id] = quantity
        return cls(capacity=capacity, slots=slots)

    def _validated_item(self, item_id: str) -> None:
        if not isinstance(item_id, str) or not item_exists(item_id):
            raise InventoryError(f"Objeto desconocido: {item_id!r}.")

    @staticmethod
    def _validated_quantity(quantity: int) -> None:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise InventoryError("La cantidad debe ser un entero positivo.")

"""Motor ligero de Árboles de Comportamiento (LiteBehaviorTree) para IA de enemigos y NPCs.

Implementa nodos compuestos (Sequence, Selector, Parallel), decoradores (Inverter, Cooldown),
condiciones y acciones basadas en el patrón Blackboard, con serialización data-driven.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import IntEnum


class NodeStatus(IntEnum):
    """Estado de evaluación de un nodo del árbol de comportamiento."""

    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3


class BTNode:
    """Clase base abstracta para todos los nodos del árbol de comportamiento."""

    __slots__ = ()

    def tick(self, entity: object, blackboard: dict[str, object], dt: float) -> NodeStatus:
        raise NotImplementedError


class Sequence(BTNode):
    """Compuesto que ejecuta hijos en orden secuencial.

    Falla de inmediato si un hijo falla; tiene éxito solo si todos tienen éxito.
    """

    __slots__ = ("children",)

    def __init__(self, children: list[BTNode]) -> None:
        self.children: list[BTNode] = children

    def tick(self, entity: object, blackboard: dict[str, object], dt: float) -> NodeStatus:
        for child in self.children:
            status = child.tick(entity, blackboard, dt)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS


class Selector(BTNode):
    """Compuesto que ejecuta hijos como alternativas de fallback.

    Tiene éxito en el primer hijo que no falle; falla solo si todos fallan.
    """

    __slots__ = ("children",)

    def __init__(self, children: list[BTNode]) -> None:
        self.children: list[BTNode] = children

    def tick(self, entity: object, blackboard: dict[str, object], dt: float) -> NodeStatus:
        for child in self.children:
            status = child.tick(entity, blackboard, dt)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE


class Parallel(BTNode):
    """Compuesto que ejecuta todos sus hijos concurrentemente en cada tick."""

    __slots__ = ("children",)

    def __init__(self, children: list[BTNode]) -> None:
        self.children: list[BTNode] = children

    def tick(self, entity: object, blackboard: dict[str, object], dt: float) -> NodeStatus:
        any_running = False
        any_failure = False
        for child in self.children:
            status = child.tick(entity, blackboard, dt)
            if status == NodeStatus.RUNNING:
                any_running = True
            elif status == NodeStatus.FAILURE:
                any_failure = True

        if any_failure:
            return NodeStatus.FAILURE
        if any_running:
            return NodeStatus.RUNNING
        return NodeStatus.SUCCESS


class Inverter(BTNode):
    """Decorador que invierte el resultado de su nodo hijo (SUCCESS <-> FAILURE)."""

    __slots__ = ("child",)

    def __init__(self, child: BTNode) -> None:
        self.child: BTNode = child

    def tick(self, entity: object, blackboard: dict[str, object], dt: float) -> NodeStatus:
        status = self.child.tick(entity, blackboard, dt)
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        if status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        return NodeStatus.RUNNING


class Cooldown(BTNode):
    """Decorador que limita la frecuencia de ejecución de su nodo hijo."""

    __slots__ = ("child", "cooldown_s", "_elapsed")

    def __init__(self, child: BTNode, cooldown_s: float) -> None:
        self.child: BTNode = child
        self.cooldown_s: float = cooldown_s
        self._elapsed: float = cooldown_s  # Comienza listo

    def tick(self, entity: object, blackboard: dict[str, object], dt: float) -> NodeStatus:
        self._elapsed += dt
        if self._elapsed < self.cooldown_s:
            return NodeStatus.FAILURE

        status = self.child.tick(entity, blackboard, dt)
        if status in (NodeStatus.SUCCESS, NodeStatus.RUNNING):
            self._elapsed = 0.0
        return status


class Condition(BTNode):
    """Nodo hoja evaluador de una condición sobre la entidad o el blackboard."""

    __slots__ = ("predicate", "name")

    def __init__(
        self,
        predicate: Callable[[object, dict[str, object]], bool],
        name: str = "condition",
    ) -> None:
        self.predicate: Callable[[object, dict[str, object]], bool] = predicate
        self.name: str = name

    def tick(self, entity: object, blackboard: dict[str, object], dt: float) -> NodeStatus:
        return NodeStatus.SUCCESS if self.predicate(entity, blackboard) else NodeStatus.FAILURE


class Action(BTNode):
    """Nodo hoja ejecutor de una acción de juego."""

    __slots__ = ("action_fn", "name")

    def __init__(
        self,
        action_fn: Callable[[object, dict[str, object], float], NodeStatus],
        name: str = "action",
    ) -> None:
        self.action_fn: Callable[[object, dict[str, object], float], NodeStatus] = action_fn
        self.name: str = name

    def tick(self, entity: object, blackboard: dict[str, object], dt: float) -> NodeStatus:
        return self.action_fn(entity, blackboard, dt)


def build_tree_from_dict(
    spec: dict[str, object],
    action_registry: dict[str, Callable[[object, dict[str, object], float], NodeStatus]],
    condition_registry: dict[str, Callable[[object, dict[str, object]], bool]],
) -> BTNode:
    """Construye un árbol de comportamiento a partir de una estructura declarativa de diccionario/JSON."""
    node_type = str(spec.get("type", "")).lower()

    if node_type == "sequence":
        raw_children = spec.get("children", [])
        children = [
            build_tree_from_dict(c, action_registry, condition_registry)
            for c in raw_children
            if isinstance(c, dict)
        ]
        return Sequence(children)

    if node_type == "selector":
        raw_children = spec.get("children", [])
        children = [
            build_tree_from_dict(c, action_registry, condition_registry)
            for c in raw_children
            if isinstance(c, dict)
        ]
        return Selector(children)

    if node_type == "parallel":
        raw_children = spec.get("children", [])
        children = [
            build_tree_from_dict(c, action_registry, condition_registry)
            for c in raw_children
            if isinstance(c, dict)
        ]
        return Parallel(children)

    if node_type == "inverter":
        raw_child = spec.get("child")
        if not isinstance(raw_child, dict):
            raise ValueError("Inverter requiere un objeto 'child'")
        return Inverter(build_tree_from_dict(raw_child, action_registry, condition_registry))

    if node_type == "cooldown":
        raw_child = spec.get("child")
        cooldown_s = float(spec.get("cooldown_s", 1.0))
        if not isinstance(raw_child, dict):
            raise ValueError("Cooldown requiere un objeto 'child'")
        return Cooldown(
            build_tree_from_dict(raw_child, action_registry, condition_registry),
            cooldown_s=cooldown_s,
        )

    if node_type == "condition":
        cond_id = str(spec.get("id", ""))
        predicate = condition_registry.get(cond_id)
        if predicate is None:
            raise KeyError(f"Condición '{cond_id}' no registrada en condition_registry")
        return Condition(predicate, name=cond_id)

    if node_type == "action":
        action_id = str(spec.get("id", ""))
        action_fn = action_registry.get(action_id)
        if action_fn is None:
            raise KeyError(f"Acción '{action_id}' no registrada en action_registry")
        return Action(action_fn, name=action_id)

    raise ValueError(f"Tipo de nodo de árbol de comportamiento desconocido: '{node_type}'")

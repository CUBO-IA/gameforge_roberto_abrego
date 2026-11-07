"""Pruebas unitarias para el motor LiteBehaviorTree (game.ai.behavior_tree)."""

from __future__ import annotations

from game.ai.behavior_tree import (
    Action,
    Condition,
    Cooldown,
    Inverter,
    NodeStatus,
    Parallel,
    Selector,
    Sequence,
    build_tree_from_dict,
)


def test_sequence_success_and_failure():
    bb: dict[str, object] = {"val": 10}

    # Secuencia donde todas las condiciones tienen éxito
    seq_ok = Sequence([
        Condition(lambda ent, b: b["val"] > 5),
        Condition(lambda ent, b: b["val"] < 20),
    ])
    assert seq_ok.tick(None, bb, 0.016) == NodeStatus.SUCCESS

    # Secuencia que falla en el primer nodo
    seq_fail = Sequence([
        Condition(lambda ent, b: b["val"] > 50),
        Condition(lambda ent, b: b["val"] < 20),
    ])
    assert seq_fail.tick(None, bb, 0.016) == NodeStatus.FAILURE


def test_selector_fallback():
    bb: dict[str, object] = {"target_spotted": False}

    selector = Selector([
        Condition(lambda ent, b: bool(b["target_spotted"])),
        Action(lambda ent, b, dt: NodeStatus.SUCCESS),
    ])
    assert selector.tick(None, bb, 0.016) == NodeStatus.SUCCESS

    all_fail = Selector([
        Condition(lambda ent, b: False),
        Condition(lambda ent, b: False),
    ])
    assert all_fail.tick(None, bb, 0.016) == NodeStatus.FAILURE


def test_parallel_composite():
    bb: dict[str, object] = {}

    par = Parallel([
        Action(lambda ent, b, dt: NodeStatus.SUCCESS),
        Action(lambda ent, b, dt: NodeStatus.RUNNING),
    ])
    assert par.tick(None, bb, 0.016) == NodeStatus.RUNNING

    par_fail = Parallel([
        Action(lambda ent, b, dt: NodeStatus.SUCCESS),
        Action(lambda ent, b, dt: NodeStatus.FAILURE),
    ])
    assert par_fail.tick(None, bb, 0.016) == NodeStatus.FAILURE


def test_inverter_decorator():
    bb: dict[str, object] = {}

    inv_success = Inverter(Action(lambda ent, b, dt: NodeStatus.SUCCESS))
    assert inv_success.tick(None, bb, 0.016) == NodeStatus.FAILURE

    inv_fail = Inverter(Action(lambda ent, b, dt: NodeStatus.FAILURE))
    assert inv_fail.tick(None, bb, 0.016) == NodeStatus.SUCCESS

    inv_running = Inverter(Action(lambda ent, b, dt: NodeStatus.RUNNING))
    assert inv_running.tick(None, bb, 0.016) == NodeStatus.RUNNING


def test_cooldown_decorator():
    bb: dict[str, object] = {}
    cd = Cooldown(Action(lambda ent, b, dt: NodeStatus.SUCCESS), cooldown_s=0.5)

    # Primer tick ejecuta con éxito (comienza listo)
    assert cd.tick(None, bb, 0.016) == NodeStatus.SUCCESS

    # Inmediatamente después debe fallar por estar en cooldown
    assert cd.tick(None, bb, 0.016) == NodeStatus.FAILURE

    # Avanzar el tiempo más allá del cooldown
    assert cd.tick(None, bb, 0.6) == NodeStatus.SUCCESS


def test_build_tree_from_dict():
    actions = {
        "strike": lambda ent, b, dt: NodeStatus.SUCCESS,
        "flee": lambda ent, b, dt: NodeStatus.RUNNING,
    }
    conditions = {
        "in_range": lambda ent, b: b.get("dist", 999.0) < 50.0,
    }

    tree_spec = {
        "type": "selector",
        "children": [
            {
                "type": "sequence",
                "children": [
                    {"type": "condition", "id": "in_range"},
                    {"type": "action", "id": "strike"},
                ],
            },
            {
                "type": "action",
                "id": "flee",
            },
        ],
    }

    root = build_tree_from_dict(tree_spec, actions, conditions)

    # Distancia lejana -> falla in_range, cae a flee (RUNNING)
    assert root.tick(None, {"dist": 100.0}, 0.016) == NodeStatus.RUNNING

    # Distancia cercana -> in_range tiene éxito, strike tiene éxito (SUCCESS)
    assert root.tick(None, {"dist": 20.0}, 0.016) == NodeStatus.SUCCESS

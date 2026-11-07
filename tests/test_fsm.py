"""Pruebas unitarias para el motor de máquinas de estado finitos (game.core.fsm)."""

from __future__ import annotations

from enum import IntEnum

import pytest

from game.core.fsm import StateMachine, StateTransitionError


class MockState(IntEnum):
    IDLE = 0
    WALK = 1
    ATTACK = 2
    HURT = 3
    DEAD = 4


class MockContext:
    def __init__(self) -> None:
        self.enter_log: list[tuple[MockState, MockState | None]] = []
        self.exit_log: list[tuple[MockState, MockState]] = []
        self.counter: int = 0


def test_basic_transition():
    fsm = StateMachine[MockState, MockContext](initial_state=MockState.IDLE)
    assert fsm.current_state == MockState.IDLE
    assert fsm.time_in_state == 0.0

    ctx = MockContext()
    assert fsm.transition(MockState.WALK, context=ctx)
    assert fsm.current_state == MockState.WALK
    assert fsm.history == (MockState.IDLE, MockState.WALK)

    # Misma transición devuelve False (sin cambios)
    assert not fsm.transition(MockState.WALK, context=ctx)


def test_allowed_transitions_validation():
    allowed = {
        MockState.IDLE: {MockState.WALK, MockState.ATTACK},
        MockState.WALK: {MockState.IDLE, MockState.HURT},
    }
    fsm = StateMachine[MockState, MockContext](
        initial_state=MockState.IDLE, allowed_transitions=allowed
    )
    ctx = MockContext()

    assert fsm.can_transition(MockState.WALK)
    assert not fsm.can_transition(MockState.HURT)

    with pytest.raises(StateTransitionError):
        fsm.transition(MockState.HURT, context=ctx)

    # Forzar transición ignora restricciones
    assert fsm.transition(MockState.HURT, context=ctx, force=True)
    assert fsm.current_state == MockState.HURT


def test_callbacks_enter_and_exit():
    ctx = MockContext()
    fsm = StateMachine[MockState, MockContext](initial_state=MockState.IDLE)

    def on_idle_exit(context: MockContext, target: MockState) -> None:
        context.exit_log.append((MockState.IDLE, target))

    def on_attack_enter(context: MockContext, previous: MockState | None) -> None:
        context.enter_log.append((MockState.ATTACK, previous))

    fsm.add_state(MockState.IDLE, on_exit=on_idle_exit)
    fsm.add_state(MockState.ATTACK, on_enter=on_attack_enter)

    fsm.transition(MockState.ATTACK, context=ctx)

    assert ctx.exit_log == [(MockState.IDLE, MockState.ATTACK)]
    assert ctx.enter_log == [(MockState.ATTACK, MockState.IDLE)]


def test_timed_state_auto_transition():
    ctx = MockContext()
    fsm = StateMachine[MockState, MockContext](initial_state=MockState.ATTACK)

    # Estado con duración de 0.2s que transiciona a IDLE
    fsm.add_state(
        MockState.ATTACK,
        duration=0.2,
        timeout_target=MockState.IDLE,
    )

    fsm.update(0.1, context=ctx)
    assert fsm.current_state == MockState.ATTACK
    assert fsm.time_in_state == pytest.approx(0.1)

    fsm.update(0.15, context=ctx)
    assert fsm.current_state == MockState.IDLE
    assert fsm.time_in_state == 0.0


def test_update_callback_transition():
    ctx = MockContext()
    fsm = StateMachine[MockState, MockContext](initial_state=MockState.WALK)

    def on_walk_update(context: MockContext, dt: float) -> MockState | None:
        context.counter += 1
        if context.counter >= 3:
            return MockState.IDLE
        return None

    fsm.add_state(MockState.WALK, on_update=on_walk_update)

    fsm.update(0.016, context=ctx)
    assert fsm.current_state == MockState.WALK
    fsm.update(0.016, context=ctx)
    assert fsm.current_state == MockState.WALK
    fsm.update(0.016, context=ctx)
    assert fsm.current_state == MockState.IDLE


def test_history_capacity():
    fsm = StateMachine[MockState, MockContext](initial_state=MockState.IDLE, history_capacity=3)
    ctx = MockContext()

    fsm.transition(MockState.WALK, context=ctx)
    fsm.transition(MockState.ATTACK, context=ctx)
    fsm.transition(MockState.IDLE, context=ctx)

    assert len(fsm.history) == 3
    assert fsm.history == (MockState.WALK, MockState.ATTACK, MockState.IDLE)

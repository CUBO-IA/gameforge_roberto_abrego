"""Pruebas unitarias para InputBuffer y CoyoteTimer (Game Feel)."""

from __future__ import annotations

from game.input.actions import Action
from game.input.buffer import CoyoteTimer, InputBuffer


def test_input_buffer_registration_and_consumption():
    buf = InputBuffer(buffer_window_s=0.15)
    t0 = 10.0

    buf.register(Action.ATTACK, current_time=t0)
    assert buf.has_buffered(Action.ATTACK, current_time=t0 + 0.10)
    assert not buf.has_buffered(Action.DASH, current_time=t0 + 0.10)

    # Consumir dentro de la ventana
    assert buf.consume(Action.ATTACK, current_time=t0 + 0.12)
    # Una vez consumido, ya no está disponible
    assert not buf.has_buffered(Action.ATTACK, current_time=t0 + 0.12)
    assert not buf.consume(Action.ATTACK, current_time=t0 + 0.12)


def test_input_buffer_expiration():
    buf = InputBuffer(buffer_window_s=0.10)
    t0 = 5.0

    buf.register(Action.JUMP, current_time=t0)
    # Fuera de la ventana (0.12s > 0.10s)
    assert not buf.has_buffered(Action.JUMP, current_time=t0 + 0.12)
    assert not buf.consume(Action.JUMP, current_time=t0 + 0.12)


def test_input_buffer_purge_and_clear():
    buf = InputBuffer(buffer_window_s=0.10)
    buf.register("action_a", current_time=1.0)
    buf.register("action_b", current_time=1.08)

    buf.purge_expired(current_time=1.12)
    # action_a expiró (0.12 > 0.10), action_b sigue viva (0.04 <= 0.10)
    assert not buf.has_buffered("action_a", current_time=1.12)
    assert buf.has_buffered("action_b", current_time=1.12)

    buf.clear()
    assert not buf.has_buffered("action_b", current_time=1.12)


def test_coyote_timer():
    coyote = CoyoteTimer(coyote_window_s=0.08)

    # En el suelo
    coyote.update(dt=0.016, is_grounded=True)
    assert coyote.can_jump

    # Deja el suelo (ej. cae por una cornisa)
    coyote.update(dt=0.05, is_grounded=False)
    # 0.05s <= 0.08s -> aún puede saltar
    assert coyote.can_jump

    # Consumir el salto del coyote
    assert coyote.consume_jump()
    # Ya consumido, no puede saltar de nuevo en el aire
    assert not coyote.can_jump
    assert not coyote.consume_jump()

    # Vuelve a tocar el suelo
    coyote.update(dt=0.016, is_grounded=True)
    assert coyote.can_jump

    # Cae en el aire y transcurre demasiado tiempo
    coyote.update(dt=0.10, is_grounded=False)
    assert not coyote.can_jump

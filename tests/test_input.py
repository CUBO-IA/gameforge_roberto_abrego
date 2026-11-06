import pygame
import pytest

from game.input.actions import Action, InputMapper
from game.core.math2d import Vec2


def key_event(key: int, down: bool = True, repeat: bool = False) -> pygame.event.Event:
    return pygame.event.Event(
        pygame.KEYDOWN if down else pygame.KEYUP, key=key, repeat=repeat
    )


def test_key_mapping_and_one_shot_press() -> None:
    mapper = InputMapper()
    mapper.begin_frame()
    mapper.handle_event(key_event(pygame.K_w))
    assert mapper.is_down(Action.MOVE_UP)
    assert mapper.was_pressed(Action.MOVE_UP)

    mapper.begin_frame()
    assert mapper.is_down(Action.MOVE_UP)
    assert not mapper.was_pressed(Action.MOVE_UP)

    mapper.handle_event(key_event(pygame.K_w, down=False))
    assert not mapper.is_down(Action.MOVE_UP)


def test_repeat_keydown_does_not_repeat_action() -> None:
    mapper = InputMapper()
    mapper.begin_frame()
    mapper.handle_event(key_event(pygame.K_e, repeat=True))
    assert not mapper.was_pressed(Action.INTERACT)
    mapper.handle_event(key_event(pygame.K_e, repeat=False))
    assert mapper.was_pressed(Action.INTERACT)


def test_movement_vector_is_normalized() -> None:
    mapper = InputMapper()
    mapper.handle_event(key_event(pygame.K_w))
    mapper.handle_event(key_event(pygame.K_d))
    move = mapper.move_vector()
    assert move.length() == pytest.approx(1.0)
    assert move.x > 0 and move.y < 0
    mapper.handle_event(key_event(pygame.K_w, down=False))
    mapper.handle_event(key_event(pygame.K_d, down=False))
    assert mapper.move_vector().as_tuple() == pytest.approx((0.0, 0.0))


def test_mouse_buttons() -> None:
    mapper = InputMapper()
    mapper.begin_frame()
    mapper.handle_event(
        pygame.event.Event(pygame.MOUSEMOTION, pos=(320, 240))
    )
    mapper.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(320, 240), button=1)
    )
    assert mapper.mouse_position == (320, 240)
    assert mapper.mouse_was_pressed(1)
    assert mapper.mouse_is_down(1)
    mapper.begin_frame()
    assert not mapper.mouse_was_pressed(1)
    assert mapper.mouse_is_down(1)
    mapper.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(320, 240), button=1)
    )
    assert not mapper.mouse_is_down(1)


def test_reset() -> None:
    mapper = InputMapper()
    mapper.handle_event(key_event(pygame.K_w))
    mapper.reset()
    assert not mapper.is_down(Action.MOVE_UP)
    assert mapper.move_vector().length() == 0.0

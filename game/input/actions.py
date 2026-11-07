"""Capa de entrada.

Las entidades y escenas consultan acciones (``move_up``, ``attack``…), nunca
teclas físicas. El mapeo por defecto vive aquí y puede sustituirse en tests.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum

import pygame

from game.core.math2d import Vec2


class Action(StrEnum):
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    ATTACK = "attack"
    JUMP = "jump"
    DASH = "dash"
    INTERACT = "interact"
    INVENTORY = "inventory"
    POTION = "potion"
    PAUSE = "pause"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    SAVE = "save"
    MENU = "menu"
    UP = "up"
    DOWN = "down"


DEFAULT_BINDINGS: dict[Action, tuple[int, ...]] = {
    Action.MOVE_UP: (pygame.K_w, pygame.K_UP),
    Action.MOVE_DOWN: (pygame.K_s, pygame.K_DOWN),
    Action.MOVE_LEFT: (pygame.K_a, pygame.K_LEFT),
    Action.MOVE_RIGHT: (pygame.K_d, pygame.K_RIGHT),
    Action.ATTACK: (pygame.K_f, pygame.K_j),
    Action.JUMP: (pygame.K_SPACE,),
    Action.DASH: (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_k),
    Action.INTERACT: (pygame.K_e,),
    Action.INVENTORY: (pygame.K_i,),
    Action.POTION: (pygame.K_q,),
    Action.PAUSE: (pygame.K_ESCAPE,),
    Action.CONFIRM: (pygame.K_RETURN, pygame.K_KP_ENTER),
    Action.CANCEL: (pygame.K_ESCAPE,),
    Action.SAVE: (pygame.K_F5,),
    Action.MENU: (pygame.K_m,),
    Action.UP: (pygame.K_w, pygame.K_UP),
    Action.DOWN: (pygame.K_s, pygame.K_DOWN),
}


class InputMapper:
    """Estado de entrada de un frame.

    El bucle llama a ``begin_frame`` antes de procesar eventos. ``pressed`` y
    los clics son de un solo frame; ``down`` persiste mientras se mantiene.
    """

    def __init__(self, bindings: dict[Action, Iterable[int]] | None = None) -> None:
        source = bindings if bindings is not None else DEFAULT_BINDINGS
        self._bindings: dict[Action, tuple[int, ...]] = {
            action: tuple(keys) for action, keys in source.items()
        }
        self._key_to_actions: dict[int, list[Action]] = {}
        for action, keys in self._bindings.items():
            for key in keys:
                self._key_to_actions.setdefault(key, []).append(action)
        self._down: set[Action] = set()
        self._pressed: set[Action] = set()
        self._mouse_position = (0, 0)
        self._mouse_buttons_down: set[int] = set()
        self._mouse_buttons_pressed: set[int] = set()

    def begin_frame(self) -> None:
        self._pressed.clear()
        self._mouse_buttons_pressed.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
            for action in self._key_to_actions.get(event.key, ()):
                self._down.add(action)
                self._pressed.add(action)
        elif event.type == pygame.KEYUP:
            for action in self._key_to_actions.get(event.key, ()):
                self._down.discard(action)
        elif event.type == pygame.MOUSEMOTION:
            self._mouse_position = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_position = event.pos
            self._mouse_buttons_down.add(event.button)
            self._mouse_buttons_pressed.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_buttons_down.discard(event.button)

    def is_down(self, action: Action) -> bool:
        return action in self._down

    def was_pressed(self, action: Action) -> bool:
        return action in self._pressed

    def move_vector(self) -> Vec2:
        x = float(self.is_down(Action.MOVE_RIGHT)) - float(self.is_down(Action.MOVE_LEFT))
        y = float(self.is_down(Action.MOVE_DOWN)) - float(self.is_down(Action.MOVE_UP))
        return Vec2(x, y).normalized()

    @property
    def mouse_position(self) -> tuple[int, int]:
        return self._mouse_position

    def mouse_is_down(self, button: int = 1) -> bool:
        return button in self._mouse_buttons_down

    def mouse_was_pressed(self, button: int = 1) -> bool:
        return button in self._mouse_buttons_pressed

    def reset(self) -> None:
        """Olvida el estado (útil al cambiar de escena)."""
        self._down.clear()
        self._pressed.clear()
        self._mouse_buttons_down.clear()
        self._mouse_buttons_pressed.clear()

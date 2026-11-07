"""Inyección determinista de entrada para escenarios headless.

El controlador traduce acciones declarativas (teclas, clics, vectores) a
eventos reales de Pygame publicados en la cola oficial. No conoce el motor ni
la escena: solo habla el lenguaje de eventos de Pygame.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.core.math2d import Vec2

# Teclas usadas para expresar un vector de movimiento en el mapeo por defecto.
MOVE_KEY_BY_AXIS: dict[tuple[int, int], int] = {
    (0, 1): pygame.K_w,
    (0, -1): pygame.K_s,
    (-1, 0): pygame.K_a,
    (1, 0): pygame.K_d,
}


class InputError(ValueError):
    """Nombre de tecla o acción de entrada inválida."""


@dataclass(frozen=True, slots=True)
class InputRecord:
    """Entrada aplicada, conservada para diagnosticar un fallo."""

    frame: int
    action: str
    detail: str

    def as_dict(self) -> dict[str, object]:
        return {"frame": self.frame, "action": self.action, "detail": self.detail}


def resolve_key(name: str) -> int:
    """Resuelve un nombre legible (``SPACE``, ``E``, ``K_UP``) a código Pygame."""
    candidate = name.strip().upper()
    if candidate.startswith("K_"):
        candidate = candidate[2:]
    if len(candidate) == 1:
        candidate = candidate.lower()
    try:
        return pygame.key.key_code(candidate)
    except ValueError:
        fallback = getattr(pygame, f"K_{candidate}", None)
        if isinstance(fallback, int):
            return fallback
        raise InputError(f"Tecla desconocida: {name!r}") from None


def _key_event(event_type: int, key: int) -> pygame.event.Event:
    if event_type == pygame.KEYDOWN:
        return pygame.event.Event(event_type, key=key, unicode="", mod=0, scancode=0, repeat=False)
    return pygame.event.Event(event_type, key=key, mod=0, scancode=0)


class VirtualInputController:
    """Programa entradas por número de frame y las publica en orden."""

    def __init__(self) -> None:
        self._pending: list[tuple[int, int, pygame.event.Event]] = []
        self._sequence = 0
        self._held: set[int] = set()
        self._move_held: set[int] = set()
        self.history: list[InputRecord] = []

    # -------------------------------------------------------------- programación
    def press(self, frame: int, key_name: str) -> None:
        key = resolve_key(key_name)
        if key in self._held:
            return
        self._held.add(key)
        self._schedule(frame, _key_event(pygame.KEYDOWN, key))
        self._record(frame, "press", key_name.upper())

    def release(self, frame: int, key_name: str) -> None:
        key = resolve_key(key_name)
        if key not in self._held:
            return
        self._held.discard(key)
        self._schedule(frame, _key_event(pygame.KEYUP, key))
        self._record(frame, "release", key_name.upper())

    def tap(self, frame: int, key_name: str) -> None:
        self.press(frame, key_name)
        self.release(frame + 1, key_name)

    def click(self, frame: int, button: int = 1, position: tuple[int, int] = (0, 0)) -> None:
        move = pygame.event.Event(pygame.MOUSEMOTION, pos=position, rel=(0, 0), buttons=(0, 0, 0))
        down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=position, button=button)
        up = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=position, button=button)
        self._schedule(frame, move)
        self._schedule(frame, down)
        self._schedule(frame + 1, up)
        self._record(frame, "click", f"button={button} pos={position}")

    def set_move_vector(self, frame: int, vector: Vec2) -> None:
        """Expresa un vector como estado de las teclas de movimiento."""
        desired: set[int] = set()
        if vector.x > 0:
            desired.add(MOVE_KEY_BY_AXIS[(1, 0)])
        elif vector.x < 0:
            desired.add(MOVE_KEY_BY_AXIS[(-1, 0)])
        if vector.y > 0:
            desired.add(MOVE_KEY_BY_AXIS[(0, 1)])
        elif vector.y < 0:
            desired.add(MOVE_KEY_BY_AXIS[(0, -1)])

        for key in sorted(self._move_held - desired):
            self._send_key(frame, pygame.KEYUP, key)
            self._held.discard(key)
            self._record(frame, "move_release", _key_name(key))
        for key in sorted(desired - self._move_held):
            if key not in self._held:
                self._send_key(frame, pygame.KEYDOWN, key)
                self._held.add(key)
                self._record(frame, "move_press", _key_name(key))
        self._move_held = desired

    def release_all(self, frame: int) -> None:
        for key in sorted(self._held):
            self._send_key(frame, pygame.KEYUP, key)
            self._record(frame, "release_all", _key_name(key))
        self._held.clear()
        self._move_held.clear()

    # -------------------------------------------------------------- ejecución
    def flush(self, frame: int) -> None:
        """Publica los eventos programados hasta ``frame`` (incluido)."""
        ready = sorted(
            (item for item in self._pending if item[0] <= frame),
            key=lambda item: (item[0], item[1]),
        )
        for _, _, event in ready:
            pygame.event.post(event)
        if ready:
            published = {id(item) for item in ready}
            self._pending = [item for item in self._pending if id(item) not in published]

    def recent_history(self, limit: int = 10) -> list[dict[str, object]]:
        return [record.as_dict() for record in self.history[-limit:]]

    # -------------------------------------------------------------- internos
    def _schedule(self, frame: int, event: pygame.event.Event) -> None:
        if frame < 1:
            raise InputError("Los frames de entrada empiezan en 1.")
        self._sequence += 1
        self._pending.append((frame, self._sequence, event))

    def _send_key(self, frame: int, event_type: int, key: int) -> None:
        self._schedule(frame, _key_event(event_type, key))

    def _record(self, frame: int, action: str, detail: str) -> None:
        self.history.append(InputRecord(frame=frame, action=action, detail=detail))


def _key_name(key: int) -> str:
    try:
        return pygame.key.name(key).upper()
    except pygame.error:
        return str(key)

"""Mecánicas de Game Feel para entrada del jugador: Input Buffer y Coyote Timer.

Permite amortiguar pulsaciones tempranas (buffer de acciones) y tolerar
saltos ligeramente tardíos al abandonar plataformas o salientes (coyote time).
"""

from __future__ import annotations

from game.input.actions import Action

ActionKey = Action | str


class InputBuffer:
    """Búfer de acciones con ventana temporal de expiración (Input Buffering)."""

    __slots__ = ("buffer_window_s", "_actions")

    def __init__(self, buffer_window_s: float = 0.15) -> None:
        self.buffer_window_s: float = max(0.01, buffer_window_s)
        self._actions: dict[ActionKey, float] = {}

    def register(self, action: ActionKey, current_time: float) -> None:
        """Registra la pulsación de una acción en la marca de tiempo actual."""
        self._actions[action] = current_time

    def has_buffered(self, action: ActionKey, current_time: float) -> bool:
        """Verifica si la acción está registrada y aún se encuentra dentro de la ventana de amortiguación."""
        timestamp = self._actions.get(action)
        if timestamp is None:
            return False
        return (current_time - timestamp) <= self.buffer_window_s

    def consume(self, action: ActionKey, current_time: float) -> bool:
        """Intenta consumir una acción en búfer. Devuelve True si era válida y la elimina."""
        timestamp = self._actions.get(action)
        if timestamp is None:
            return False

        elapsed = current_time - timestamp
        del self._actions[action]
        return elapsed <= self.buffer_window_s

    def purge_expired(self, current_time: float) -> None:
        """Elimina acciones viejas cuyo tiempo expiró."""
        expired = [
            action
            for action, timestamp in self._actions.items()
            if (current_time - timestamp) > self.buffer_window_s
        ]
        for action in expired:
            del self._actions[action]

    def clear(self) -> None:
        """Limpia todo el contenido del búfer."""
        self._actions.clear()


class CoyoteTimer:
    """Temporizador de tolerancia para salto tras perder contacto con el suelo (Coyote Time)."""

    __slots__ = ("coyote_window_s", "_time_since_grounded")

    def __init__(self, coyote_window_s: float = 0.08) -> None:
        self.coyote_window_s: float = max(0.01, coyote_window_s)
        self._time_since_grounded: float = 0.0

    def update(self, dt: float, is_grounded: bool) -> None:
        """Actualiza el estado de contacto con el suelo."""
        if is_grounded:
            self._time_since_grounded = 0.0
        else:
            self._time_since_grounded += dt

    @property
    def can_jump(self) -> bool:
        """Indica si el personaje aún tiene permitido saltar."""
        return self._time_since_grounded <= self.coyote_window_s

    def consume_jump(self) -> bool:
        """Consume el salto permitido; devuelve True si tuvo éxito e invalida el temporizador."""
        if self.can_jump:
            self._time_since_grounded = self.coyote_window_s + 1.0
            return True
        return False

    def reset(self) -> None:
        """Reinicia el temporizador como si estuviera en el suelo."""
        self._time_since_grounded = 0.0

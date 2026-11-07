"""Motor ligero de máquinas de estados finitos (FSM / HFSM).

Diseñado para simulación de alta tasa de refresco (60+ FPS) con despacho O(1),
cero dependencias externas y validación estricta de transiciones.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

S = TypeVar("S")  # Tipo del identificador de estado (p. ej. IntEnum o str)
C = TypeVar("C")  # Tipo del contexto pasado a handlers (p. ej. Player o Enemy)


class StateTransitionError(ValueError):
    """Error al intentar una transición no permitida o hacia un estado inexistente."""


@dataclass(slots=True)
class StateHandler(Generic[S, C]):
    """Configuración y callbacks para un estado individual."""

    state: S
    on_enter: Callable[[C, S | None], None] | None = None
    on_update: Callable[[C, float], S | None] | None = None
    on_exit: Callable[[C, S], None] | None = None
    duration: float | None = None
    timeout_target: S | None = None


class StateMachine(Generic[S, C]):
    """Máquina de estados finitos optimizada para videojuegos."""

    __slots__ = (
        "_current_state",
        "_handlers",
        "_allowed_transitions",
        "_time_in_state",
        "_history",
        "_history_capacity",
    )

    def __init__(
        self,
        initial_state: S,
        allowed_transitions: dict[S, set[S]] | None = None,
        history_capacity: int = 8,
    ) -> None:
        self._current_state: S = initial_state
        self._handlers: dict[S, StateHandler[S, C]] = {}
        self._allowed_transitions: dict[S, set[S]] = allowed_transitions or {}
        self._time_in_state: float = 0.0
        self._history_capacity: int = history_capacity
        self._history: deque[S] = deque(maxlen=history_capacity)
        self._history.append(initial_state)

    @property
    def current_state(self) -> S:
        """Estado activo actual."""
        return self._current_state

    @property
    def time_in_state(self) -> float:
        """Tiempo acumulado en segundos en el estado actual."""
        return self._time_in_state

    @property
    def history(self) -> tuple[S, ...]:
        """Historial ordenado de los últimos estados visitados."""
        return tuple(self._history)

    def add_state(
        self,
        state: S,
        on_enter: Callable[[C, S | None], None] | None = None,
        on_update: Callable[[C, float], S | None] | None = None,
        on_exit: Callable[[C, S], None] | None = None,
        duration: float | None = None,
        timeout_target: S | None = None,
    ) -> StateMachine[S, C]:
        """Registra un estado y sus manejadores."""
        self._handlers[state] = StateHandler(
            state=state,
            on_enter=on_enter,
            on_update=on_update,
            on_exit=on_exit,
            duration=duration,
            timeout_target=timeout_target,
        )
        return self

    def allow_transition(self, from_state: S, to_state: S) -> None:
        """Permite explícitamente una transición entre dos estados."""
        if from_state not in self._allowed_transitions:
            self._allowed_transitions[from_state] = set()
        self._allowed_transitions[from_state].add(to_state)

    def can_transition(self, new_state: S) -> bool:
        """Comprueba si la transición al nuevo estado está permitida."""
        if new_state == self._current_state:
            return True
        allowed = self._allowed_transitions.get(self._current_state)
        if allowed is None:
            return True
        return new_state in allowed

    def transition(self, new_state: S, context: C | None = None, force: bool = False) -> bool:
        """Ejecuta una transición de estado con llamadas a callbacks de entrada y salida."""
        if new_state == self._current_state and not force:
            return False

        if not force and not self.can_transition(new_state):
            raise StateTransitionError(
                f"Transición no permitida de {self._current_state} a {new_state}"
            )

        previous_state = self._current_state
        old_handler = self._handlers.get(previous_state)
        if old_handler and old_handler.on_exit and context is not None:
            old_handler.on_exit(context, new_state)

        self._current_state = new_state
        self._time_in_state = 0.0
        self._history.append(new_state)

        new_handler = self._handlers.get(new_state)
        if new_handler and new_handler.on_enter and context is not None:
            new_handler.on_enter(context, previous_state)

        return True

    def update(self, dt: float, context: C) -> S:
        """Avanza el temporizador del estado, procesa updates y timeouts automáticos."""
        self._time_in_state += dt
        handler = self._handlers.get(self._current_state)

        if handler:
            # Manejo de timeout automático
            if (
                handler.duration is not None
                and self._time_in_state >= handler.duration
                and handler.timeout_target is not None
            ):
                self.transition(handler.timeout_target, context=context)
                return self._current_state

            # Callback de actualización
            if handler.on_update:
                next_state = handler.on_update(context, dt)
                if next_state is not None and next_state != self._current_state:
                    self.transition(next_state, context=context)

        return self._current_state

"""GameForge Test Runner (GF-TR): escenarios headless de jugabilidad.

Uso mínimo::

    from tools.test_runner import run_scenario

    result = run_scenario("tests/scenarios/jump_and_survive.json")
    assert result.passed
"""

import os

# El modo headless y el silencio de Pygame deben fijarse antes de importarlo.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from tools.test_runner.runner import HeadlessRunner, ScenarioResult, run_scenario  # noqa: E402
from tools.test_runner.scenario import Scenario, ScenarioError, load_scenario  # noqa: E402

__all__ = [
    "HeadlessRunner",
    "Scenario",
    "ScenarioError",
    "ScenarioResult",
    "load_scenario",
    "run_scenario",
]

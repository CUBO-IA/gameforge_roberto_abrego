"""Ejecutor headless de escenarios de jugabilidad (GameForge Test Runner).

El runner arranca la aplicación con el driver dummy, sustituye la escena por
una partida determinista, inyecta entradas frame a frame y evalúa aserciones
sobre el estado del dominio. No usa ``Application.run`` para no depender del
reloj real ni de ``sleep``.
"""

from __future__ import annotations

import tempfile
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pygame

from game.app import Application
from game.core.config import GameConfig
from game.core.math2d import Vec2
from game.scenes.play import PlayScene
from tools.test_runner.capture import capture_frame, compare, save_png
from tools.test_runner.input import VirtualInputController
from tools.test_runner.inspector import AssertionOutcome, evaluate_assertion
from tools.test_runner.scenario import Scenario, TimelineEntry, load_scenario
from tools.test_runner.telemetry import Telemetry

FIXED_DT = 1.0 / 60.0


@dataclass(slots=True)
class ScenarioResult:
    """Resultado serializable de un escenario."""

    scenario_id: str
    description: str
    passed: bool
    frames_executed: int
    telemetry: dict[str, Any]
    assertions: list[AssertionOutcome] = field(default_factory=list)
    visual: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        telemetry = dict(self.telemetry)
        return {
            "scenario": self.scenario_id,
            "description": self.description,
            "status": "PASSED" if self.passed else "FAILED",
            "frames_executed": self.frames_executed,
            "elapsed_wall_ms": telemetry.get("elapsed_wall_ms", 0.0),
            "fps_achieved": telemetry.get("fps_equivalent", 0.0),
            "peak_memory_kb": telemetry.get("peak_memory_kb", 0.0),
            "telemetry": telemetry,
            "assertions": [assertion.as_dict() for assertion in self.assertions],
            "visual": self.visual,
            "errors": self.errors,
            "artifacts": self.artifacts,
        }


class HeadlessRunner:
    """Ciclo de vida de una aplicación GameForge en modo headless."""

    def __init__(
        self,
        config: GameConfig | None = None,
        data_dir: str | Path | None = None,
        artifacts_dir: str | Path | None = None,
        baseline_dir: str | Path | None = None,
        update_baselines: bool = False,
    ) -> None:
        self._temp_dir: tempfile.TemporaryDirectory[str] | None = None
        if data_dir is None:
            self._temp_dir = tempfile.TemporaryDirectory(prefix="gftr-")
            data_dir = self._temp_dir.name
        self.app = Application(config, data_dir=data_dir, headless=True)
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.baseline_dir = Path(baseline_dir) if baseline_dir is not None else None
        self.update_baselines = update_baselines
        self.input = VirtualInputController()
        self.telemetry = Telemetry()
        self.scene: PlayScene | None = None
        self.frames = 0
        self._closed = False

    def __enter__(self) -> HeadlessRunner:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.app.shutdown()
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None

    def start(self, scenario: Scenario) -> PlayScene:
        scene = PlayScene(self.app, seed=scenario.seed)
        self.app.replace_scene(scene)
        self.scene = scene
        self.frames = 0
        self._apply_initial_state(scene, scenario.initial_state)
        scene.camera.snap_to(
            scene.player.position,
            scene.tilemap.pixel_width,
            scene.tilemap.pixel_height,
        )
        return scene

    def step(self, frames: int = 1, draw: bool = False) -> None:
        scene = self.scene
        if scene is None:
            raise RuntimeError("El runner no tiene escena activa; llama antes a start().")
        for _ in range(frames):
            self.app.input.begin_frame()
            self.input.flush(self.frames + 1)
            for event in pygame.event.get():
                self.app.input.handle_event(event)
                scene.handle_event(event)
            started = time.perf_counter()
            scene.update(FIXED_DT)
            if draw:
                scene.draw(self.app.screen)
            self.telemetry.add_frame((time.perf_counter() - started) * 1000.0)
            self.frames += 1

    # ------------------------------------------------------------------ estado
    def _apply_initial_state(self, scene: PlayScene, state: dict[str, Any]) -> None:
        teleport = state.get("teleport_to")
        if isinstance(teleport, str):
            position = self._resolve_teleport(scene, teleport)
            if position is not None:
                scene.player.position = position.copy()

        spawn = state.get("player_spawn")
        if isinstance(spawn, dict):
            scene.player.position = Vec2(float(spawn.get("x", 0.0)), float(spawn.get("y", 0.0)))

        health = state.get("player_hp")
        if isinstance(health, (int, float)) and not isinstance(health, bool):
            scene.player.health = max(0.0, min(float(health), scene.player.max_health))

        inventory = state.get("inventory", [])
        if isinstance(inventory, list):
            for entry in inventory:
                if not isinstance(entry, dict):
                    continue
                item_id = entry.get("item_id")
                quantity = entry.get("quantity", 1)
                if isinstance(item_id, str) and isinstance(quantity, int):
                    scene.inventory.add(item_id, quantity)

    @staticmethod
    def _resolve_teleport(scene: PlayScene, target: str) -> Vec2 | None:
        if target == "spawn":
            return scene.dungeon.spawn
        if target == "nearest_chest":
            unopened = [chest for chest in scene.chests if not chest.opened]
            if unopened:
                return unopened[0].position
            if scene.chests:
                return scene.chests[0].position
            return scene.dungeon.spawn
        if target == "campfire":
            return scene.campfire.position
        if target == "altar":
            return scene.altar.position
        raise ValueError(f"teleport_to desconocido: {target!r}")


def _apply_timeline_entry(controller: VirtualInputController, entry: TimelineEntry) -> None:
    if entry.action == "press":
        controller.press(entry.frame, entry.key or "")
    elif entry.action == "release":
        controller.release(entry.frame, entry.key or "")
    elif entry.action == "tap":
        controller.tap(entry.frame, entry.key or "")
    elif entry.action == "move":
        controller.set_move_vector(entry.frame, Vec2(*entry.vector or (0.0, 0.0)))
    elif entry.action == "click":
        controller.click(entry.frame, entry.button, entry.position or (0, 0))


def run_scenario(
    scenario: Scenario | str | Path,
    *,
    config: GameConfig | None = None,
    data_dir: str | Path | None = None,
    artifacts_dir: str | Path | None = None,
    baseline_dir: str | Path | None = None,
    update_baselines: bool = False,
    draw_each_frame: bool = False,
) -> ScenarioResult:
    """Ejecuta un escenario y devuelve su resultado sin lanzar excepciones."""
    if not isinstance(scenario, Scenario):
        scenario = load_scenario(scenario)

    started_wall = time.perf_counter()
    assertions: list[AssertionOutcome] = []
    visual_checks: list[dict[str, Any]] = []
    artifacts: list[str] = []
    errors: list[str] = []
    frames_executed = 0
    timeline = sorted(scenario.timeline, key=lambda entry: entry.frame)
    timeline_index = 0

    with HeadlessRunner(
        config=config,
        data_dir=data_dir,
        artifacts_dir=artifacts_dir,
        baseline_dir=baseline_dir,
        update_baselines=update_baselines,
    ) as runner:
        try:
            runner.start(scenario)
            runner.telemetry.start_memory_tracking()
            capture_frames = set(scenario.visual.capture_at_frames) if scenario.visual else set()
            visual_tolerance = (
                scenario.visual.max_allowed_pixel_diff_ratio if scenario.visual else 0.0005
            )

            for frame in range(1, scenario.timeout_frames + 1):
                while timeline_index < len(timeline) and timeline[timeline_index].frame == frame:
                    _apply_timeline_entry(runner.input, timeline[timeline_index])
                    timeline_index += 1

                needs_capture = frame in capture_frames
                runner.step(1, draw=needs_capture or draw_each_frame)
                frames_executed = frame

                for spec in scenario.assertions:
                    if spec.at_frame == frame and runner.scene is not None:
                        assertions.append(evaluate_assertion(runner.scene, spec, frame))

                if needs_capture:
                    capture = capture_frame(runner.app.screen).convert_alpha()
                    name = f"{scenario.id}_f{frame:04d}.png"
                    if runner.artifacts_dir is not None:
                        path = save_png(capture, runner.artifacts_dir / name)
                        artifacts.append(str(path))
                    visual_checks.append(
                        _visual_check(runner, capture, name, visual_tolerance, artifacts)
                    )

                if runner.app.scene is not runner.scene:
                    break
        except Exception:
            errors.append(traceback.format_exc())
        finally:
            peak_kb = runner.telemetry.stop_memory_tracking()

    evaluated_frames = {assertion.at_frame for assertion in assertions}
    for spec in scenario.assertions:
        if spec.at_frame not in evaluated_frames:
            assertions.append(
                AssertionOutcome(
                    passed=False,
                    check=spec.type,
                    at_frame=spec.at_frame,
                    actual={},
                    message="No evaluada: la escena terminó o el runner falló antes del frame.",
                )
            )
    assertions.sort(key=lambda assertion: (assertion.at_frame, assertion.check))

    if timeline_index < len(timeline):
        pending = len(timeline) - timeline_index
        errors.append(
            f"{pending} entrada(s) de la línea temporal no se aplicaron "
            f"(timeout={scenario.timeout_frames} frames)."
        )

    wall_ms = (time.perf_counter() - started_wall) * 1000.0
    telemetry = runner.telemetry.summary(wall_ms, peak_kb)
    visual_passed = all(check.get("passed", False) for check in visual_checks)
    passed = (
        not errors
        and bool(assertions) == bool(scenario.assertions)
        and all(assertion.passed for assertion in assertions)
        and visual_passed
    )
    visual = None
    if visual_checks:
        visual = {
            "passed": visual_passed,
            "captures": visual_checks,
            "max_allowed_pixel_diff_ratio": visual_tolerance,
        }

    return ScenarioResult(
        scenario_id=scenario.id,
        description=scenario.description,
        passed=passed,
        frames_executed=frames_executed,
        telemetry=telemetry,
        assertions=assertions,
        visual=visual,
        errors=errors,
        artifacts=artifacts,
    )


def _visual_check(
    runner: HeadlessRunner,
    capture: pygame.Surface,
    name: str,
    tolerance: float,
    artifacts: list[str],
) -> dict[str, Any]:
    if runner.baseline_dir is None:
        return {"frame_image": name, "passed": True, "baseline_missing": True, "pixel_diff_ratio": 0.0}

    baseline_path = runner.baseline_dir / name
    if runner.update_baselines:
        save_png(capture, baseline_path)
        return {"frame_image": name, "passed": True, "baseline_written": True, "pixel_diff_ratio": 0.0}
    if not baseline_path.is_file():
        return {"frame_image": name, "passed": True, "baseline_missing": True, "pixel_diff_ratio": 0.0}

    golden = pygame.image.load(str(baseline_path)).convert_alpha()
    diff = compare(capture, golden, tolerance)
    report = dict(diff.as_dict())
    report["frame_image"] = name
    if diff.mask is not None and runner.artifacts_dir is not None:
        mask_path = save_png(diff.mask, runner.artifacts_dir / name.replace(".png", "_diff.png"))
        artifacts.append(str(mask_path))
        report["diff_image"] = mask_path.name
    return report

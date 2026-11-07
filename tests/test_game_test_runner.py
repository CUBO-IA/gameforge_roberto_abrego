"""Pruebas del GameForge Test Runner (GF-TR)."""

from __future__ import annotations

import json
from pathlib import Path

import pygame
import pytest

from tools.test_runner import run_scenario
from tools.test_runner.capture import compare, pixel_diff_ratio
from tools.test_runner.scenario import ScenarioError, load_scenario, scenario_from_dict

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "tests" / "scenarios"


def test_scenario_loader_reads_pilot_files() -> None:
    scenario = load_scenario(SCENARIOS / "jump_and_survive.json")
    assert scenario.id == "jump_and_survive"
    assert scenario.seed == 11
    assert len(scenario.timeline) == 2
    assert len(scenario.assertions) == 3


def test_pilot_scenarios_pass() -> None:
    for name in ("jump_and_survive.json", "chest_loot.json"):
        result = run_scenario(SCENARIOS / name)
        assert result.passed, f"{name}: {result.errors} {[a.message for a in result.assertions]}"
        assert result.frames_executed > 0
        assert result.telemetry["frames"] == result.frames_executed
        assert result.telemetry["fps_equivalent"] > 0


def test_jump_scenario_proves_virtual_input_works() -> None:
    result = run_scenario(SCENARIOS / "jump_and_survive.json")
    jump = next(assertion for assertion in result.assertions if assertion.check == "player_z_above")
    assert jump.passed
    assert jump.actual["z"] > 4.0


def test_failing_assertion_is_reported_without_crashing() -> None:
    data = {
        "id": "expected_failure",
        "config": {"seed": 3, "timeout_frames": 10},
        "input_timeline": [],
        "assertions": [
            {
                "at_frame": 5,
                "type": "player_position",
                "expected": {"x": 99999.0, "y": 99999.0},
                "tolerance": 1.0,
            }
        ],
    }
    result = run_scenario(scenario_from_dict(data))
    assert not result.passed
    assert result.assertions[0].passed is False
    assert "Distancia" in result.assertions[0].message


def test_unknown_assertion_type_is_rejected() -> None:
    with pytest.raises(ScenarioError):
        scenario_from_dict(
            {
                "id": "bad",
                "config": {"seed": 1},
                "assertions": [{"at_frame": 1, "type": "not_implemented"}],
            }
        )


def test_timeline_without_key_is_rejected() -> None:
    with pytest.raises(ScenarioError):
        scenario_from_dict(
            {
                "id": "bad",
                "config": {"seed": 1},
                "input_timeline": [{"frame": 2, "action": "press"}],
            }
        )


def test_report_is_json_serializable() -> None:
    result = run_scenario(SCENARIOS / "chest_loot.json")
    payload = json.dumps(result.to_dict(), ensure_ascii=False)
    assert "PASSED" in payload
    assert "assertions" in payload


def test_visual_diff_detects_a_single_changed_pixel() -> None:
    pygame.init()
    try:
        first = pygame.Surface((8, 8), pygame.SRCALPHA)
        first.fill((10, 20, 30, 255))
        second = first.copy()
        assert compare(first, second).passed
        assert pixel_diff_ratio(first, second) == 0.0

        second.set_at((0, 0), (255, 0, 0, 255))
        diff = compare(first, second, tolerance_ratio=0.0)
        assert not diff.passed
        assert diff.ratio == pytest.approx(1 / 64, rel=1e-6)
        assert diff.mask is not None
    finally:
        pygame.quit()


def test_unsupported_scenario_file_reports_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(ScenarioError):
        load_scenario(path)

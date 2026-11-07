"""Pruebas de la puerta de tipado (sin ejecutar Pyright)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.typecheck import TypecheckSummary, evaluate, load_baseline, relative_path, summarize

ROOT = Path(__file__).resolve().parents[1]


def _diag(relative: str, severity: str = "error") -> dict[str, str]:
    return {"file": str(ROOT / relative), "severity": severity}


def test_summarize_counts_only_errors_by_relative_path() -> None:
    diagnostics = [
        _diag("game/core/math2d.py"),
        _diag("game/core/math2d.py"),
        _diag("game/world/tilemap.py"),
        _diag("game/app.py", severity="warning"),
    ]
    summary = summarize(diagnostics, files_analyzed=4)
    assert summary.total_errors == 3
    assert summary.files_analyzed == 4
    assert summary.count_for("game/core/") == 2
    assert summary.count_for("game/world/") == 1


def test_evaluate_flags_zero_path_violation() -> None:
    summary = TypecheckSummary(total_errors=2, error_counts={"game/core/math2d.py": 2})
    problems = evaluate(summary, baseline_total=10)
    assert any("game/core/" in problem and "debe quedar en 0" in problem for problem in problems)
    assert not any("subió" in problem for problem in problems)


def test_evaluate_flags_baseline_regression() -> None:
    summary = TypecheckSummary(total_errors=11, error_counts={"game/render/ui.py": 11})
    problems = evaluate(summary, baseline_total=10)
    assert any("subió a 11" in problem for problem in problems)


def test_evaluate_passes_within_baseline_and_zero_paths_clean() -> None:
    summary = TypecheckSummary(total_errors=5, error_counts={"game/render/ui.py": 5})
    assert evaluate(summary, baseline_total=5) == []


def test_baseline_file_is_valid_and_declares_zero_modules() -> None:
    baseline = load_baseline()
    assert baseline["total_errors"] >= 0
    assert set(baseline["required_zero"]) == {"game/core/", "game/world/"}
    raw = json.loads((ROOT / "pyright_baseline.json").read_text(encoding="utf-8"))
    assert raw["updated_at"] == "2026-11-07"


def test_relative_path_normalizes_separators() -> None:
    path = relative_path(str(ROOT / "game" / "core" / "fsm.py"))
    assert path == "game/core/fsm.py"

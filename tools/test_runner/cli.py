"""CLI del GameForge Test Runner: ejecuta escenarios y devuelve JSON."""

from __future__ import annotations

import argparse
import json
import sys

from tools.test_runner.runner import run_scenario
from tools.test_runner.scenario import ScenarioError, load_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        action="append",
        required=True,
        help="Ruta a un escenario JSON (repetible).",
    )
    parser.add_argument("--json", action="store_true", help="Salida JSON estructurada.")
    parser.add_argument("--artifacts", help="Directorio donde guardar capturas y máscaras.")
    parser.add_argument("--baseline-dir", help="Directorio de imágenes golden.")
    parser.add_argument(
        "--update-baselines",
        action="store_true",
        help="Sobrescribe las imágenes golden con las capturas actuales.",
    )
    parser.add_argument(
        "--draw-each-frame",
        action="store_true",
        help="Dibuja todos los frames (más lento, útil para depurar).",
    )
    args = parser.parse_args(argv)

    results: list[dict[str, object]] = []
    for raw_path in args.scenario:
        try:
            scenario = load_scenario(raw_path)
        except ScenarioError as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            return 2
        result = run_scenario(
            scenario,
            artifacts_dir=args.artifacts,
            baseline_dir=args.baseline_dir,
            update_baselines=args.update_baselines,
            draw_each_frame=args.draw_each_frame,
        )
        results.append(result.to_dict())

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=True))
    else:
        for result in results:
            print(f"[{result['status']}] {result['scenario']} ({result['frames_executed']} frames)")
            for assertion in result["assertions"]:  # type: ignore[union-attr]
                mark = "ok" if assertion["passed"] else "FALLO"
                print(f"  - {mark}: {assertion['check']} @ {assertion['at_frame']} — {assertion['message']}")
            for error in result["errors"]:  # type: ignore[union-attr]
                print(f"  [ERROR] {error.strip().splitlines()[-1]}")

    return 0 if all(result["status"] == "PASSED" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

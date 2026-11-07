"""Verificación estándar de GAMEFORGE 2D: lint + pruebas + escenarios + benchmarks.

Uso:
    python tools/verify.py [--skip-bench] [--skip-scenarios]

Criterios:
- ruff check (si está instalado; si no, avisa y continúa).
- pytest completo (bloqueante: debe pasar).
- escenarios de jugabilidad del GF-TR (bloqueante).
- benchmark de simulación (informativo; avisa si p95 supera el umbral).

Umbral actual (calibrar en F2/F3 según informe de arquitectura, §14/D10):
- simulación con 24 enemigos: p95 <= 40 ms (aviso, no bloqueante hasta F3).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Umbral informativo hasta F3 (p95 en ms del bench de simulación).
BENCH_P95_WARN_MS = 40.0


def run_step(title: str, cmd: list[str]) -> tuple[int, str | None]:
    print(f"== {title} ==")
    try:
        proc = subprocess.run(cmd, cwd=ROOT, check=False)
    except FileNotFoundError:
        print(f"  [AVISO] {cmd[0]} no está disponible; paso omitido.")
        return 0, None
    return proc.returncode, None


def run_bench() -> int:
    print("== benchmark de simulación ==")
    script = ROOT / "benchmark" / "bench_simulation.py"
    proc = subprocess.run(
        [sys.executable, str(script)], cwd=ROOT, check=False, capture_output=True, text=True
    )
    output = (proc.stdout + proc.stderr).strip()
    print(output)
    if proc.returncode != 0:
        print("  [FALLO] el benchmark terminó con error.")
        return proc.returncode
    p95 = _parse_p95(output)
    if p95 is None:
        print("  [AVISO] no se pudo extraer p95 de la salida del benchmark.")
        return 0
    if p95 > BENCH_P95_WARN_MS:
        print(f"  [AVISO] p95={p95:.2f} ms supera el umbral informativo {BENCH_P95_WARN_MS} ms.")
    else:
        print(f"  [OK] p95={p95:.2f} ms dentro del umbral informativo.")
    return 0


def _parse_p95(output: str) -> float | None:
    for line in output.splitlines():
        if "p95:" in line:
            token = line.split("p95:")[1].strip().split()[0].replace(",", ".")
            try:
                return float(token)
            except ValueError:
                return None
    return None


def run_typecheck() -> int:
    print("== tipado (pyright) ==")
    script = ROOT / "tools" / "typecheck.py"
    proc = subprocess.run(
        [sys.executable, str(script)], cwd=ROOT, check=False, capture_output=True, text=True
    )
    output = (proc.stdout + proc.stderr).strip()
    if output:
        print(output)
    if proc.returncode == 2:
        print("  [AVISO] tipado no disponible; paso omitido.")
        return 0
    return proc.returncode


def run_scenarios() -> int:
    print("== escenarios de jugabilidad (GF-TR) ==")
    scenario_dir = ROOT / "tests" / "scenarios"
    paths = sorted(scenario_dir.glob("*.json"))
    if not paths:
        print("  [AVISO] no hay escenarios en tests/scenarios; paso omitido.")
        return 0
    command = [sys.executable, "-m", "tools.test_runner", "--json"]
    for path in paths:
        command.extend(["--scenario", str(path)])
    proc = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        output = (proc.stdout + proc.stderr).strip()
        print(output)
        print("  [FALLO] uno o más escenarios no pasaron.")
        return proc.returncode
    try:
        results = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print((proc.stdout + proc.stderr).strip())
        print("  [FALLO] la salida del runner no es JSON válido.")
        return 1
    for result in results:
        status = "OK" if result.get("status") == "PASSED" else "FALLO"
        print(
            f"  [{status}] {result.get('scenario')} "
            f"({result.get('frames_executed')} frames, {result.get('elapsed_wall_ms'):.1f} ms)"
        )
    return 0


def run_graph_verify() -> int:
    print("== memoria operativa (graphify) ==")
    script = ROOT / "tools" / "graph_ops.py"
    if not script.is_file():
        print("  [AVISO] tools/graph_ops.py no disponible; paso omitido.")
        return 0
    proc = subprocess.run(
        [sys.executable, str(script), "verify", "--strict"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = proc.stdout.strip()
    if output:
        print(output)
    if proc.returncode != 0:
        print("  [FALLO] el grafo presenta drift de archivos. Ejecute 'python tools/graph_ops.py update'.")
        return proc.returncode
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-bench", action="store_true", help="Omite el benchmark.")
    parser.add_argument("--skip-graph", action="store_true", help="Omite la verificación del grafo.")
    parser.add_argument(
        "--skip-scenarios", action="store_true", help="Omite los escenarios del GF-TR."
    )
    parser.add_argument("--skip-types", action="store_true", help="Omite la puerta de tipado.")
    args = parser.parse_args(argv)

    failures = 0

    if _module_available("ruff"):
        code, _ = run_step("lint (ruff)", [sys.executable, "-m", "ruff", "check", "."])
        failures += code != 0
    else:
        print("== lint (ruff) ==\n  [AVISO] ruff no está instalado; paso omitido.")

    if not args.skip_types:
        code = run_typecheck()
        failures += code != 0

    code, _ = run_step("pruebas (pytest)", [sys.executable, "-m", "pytest", "-q"])
    failures += code != 0

    if not args.skip_scenarios:
        code = run_scenarios()
        failures += code != 0

    if not args.skip_bench:
        code = run_bench()
        failures += code != 0

    if not args.skip_graph:
        code = run_graph_verify()
        failures += code != 0

    if failures:
        print(f"\nverify.py: {failures} paso(s) con fallo.")
        return 1
    print("\nverify.py: OK")
    return 0


def _module_available(name: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(name) is not None


if __name__ == "__main__":
    raise SystemExit(main())

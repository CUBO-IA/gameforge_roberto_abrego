"""Verificación estándar de GAMEFORGE 2D: lint + pruebas + benchmarks.

Uso:
    python tools/verify.py [--skip-bench]

Criterios F0:
- ruff check (si está instalado; si no, avisa y continúa).
- pytest completo (bloqueante: debe pasar).
- benchmark de simulación (informativo; avisa si p95 supera el umbral).

Umbral actual (calibrar en F2/F3 según informe de arquitectura, §14/D10):
- simulación con 24 enemigos: p95 <= 40 ms (aviso, no bloqueante hasta F3).
"""

from __future__ import annotations

import argparse
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-bench", action="store_true", help="Omite el benchmark.")
    args = parser.parse_args(argv)

    failures = 0

    if _module_available("ruff"):
        code, _ = run_step("lint (ruff)", [sys.executable, "-m", "ruff", "check", "."])
        failures += code != 0
    else:
        print("== lint (ruff) ==\n  [AVISO] ruff no está instalado; paso omitido.")

    code, _ = run_step("pruebas (pytest)", [sys.executable, "-m", "pytest", "-q"])
    failures += code != 0

    if not args.skip_bench:
        code = run_bench()
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

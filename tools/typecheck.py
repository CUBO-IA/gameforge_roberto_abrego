"""Puerta de tipado: ejecuta Pyright y aplica la línea base del proyecto.

Reglas:
- ``game/core`` y ``game/world`` deben tener **cero** errores.
- El total del repositorio no puede superar ``pyright_baseline.json``.

Si Pyright no está disponible (sin red y sin instalación local) devuelve 2 y
``verify.py`` lo trata como paso omitido, no como fallo.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "pyright_baseline.json"
DEFAULT_REQUIRED_ZERO = ("game/core/", "game/world/")


class TypecheckUnavailable(RuntimeError):
    """No se encontró un ejecutable de Pyright."""


class TypecheckError(RuntimeError):
    """Pyright se ejecutó pero su salida no es JSON válido."""


@dataclass(frozen=True, slots=True)
class TypecheckSummary:
    total_errors: int
    error_counts: dict[str, int]
    files_analyzed: int = 0

    def count_for(self, prefix: str) -> int:
        return sum(count for path, count in self.error_counts.items() if path.startswith(prefix))


def relative_path(raw: str, root: Path = ROOT) -> str:
    """Normaliza una ruta absoluta de Pyright a ruta relativa POSIX."""
    try:
        return Path(raw).resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return raw.replace("\\", "/")


def summarize(diagnostics: list[dict[str, Any]], files_analyzed: int = 0) -> TypecheckSummary:
    counts: Counter[str] = Counter(
        relative_path(str(diag.get("file", "")))
        for diag in diagnostics
        if diag.get("severity") == "error"
    )
    return TypecheckSummary(
        total_errors=sum(counts.values()),
        error_counts=dict(counts),
        files_analyzed=files_analyzed,
    )


def evaluate(
    summary: TypecheckSummary,
    baseline_total: int,
    required_zero: tuple[str, ...] = DEFAULT_REQUIRED_ZERO,
) -> list[str]:
    problems: list[str] = []
    for prefix in required_zero:
        count = summary.count_for(prefix)
        if count:
            problems.append(f"{prefix} tiene {count} error(es); debe quedar en 0.")
    if summary.total_errors > baseline_total:
        problems.append(
            f"El total de errores subió a {summary.total_errors} "
            f"(límite {baseline_total}). Corrige o justifica la nueva línea base."
        )
    return problems


def load_baseline(path: Path = BASELINE_PATH) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"total_errors": 0, "required_zero": list(DEFAULT_REQUIRED_ZERO)}
    except json.JSONDecodeError as exc:
        raise TypecheckError(f"Línea base inválida en {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise TypecheckError("pyright_baseline.json debe ser un objeto JSON.")
    required = raw.get("required_zero", list(DEFAULT_REQUIRED_ZERO))
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise TypecheckError("'required_zero' debe ser una lista de prefijos.")
    total = raw.get("total_errors", 0)
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise TypecheckError("'total_errors' debe ser un entero >= 0.")
    return {"total_errors": total, "required_zero": required}


def pyright_command() -> list[str] | None:
    """Busca Pyright local y, si no, recurre a npx (requiere red la primera vez)."""
    executable = "pyright.exe" if os.name == "nt" else "pyright"
    local = ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin") / executable
    if local.is_file():
        return [str(local)]
    npx = shutil.which("npx")
    if npx is None:
        return None
    if os.name == "nt":
        return ["cmd", "/c", npx, "--yes", "pyright"]
    return [npx, "--yes", "pyright"]


def run_pyright() -> dict[str, Any]:
    command = pyright_command()
    if command is None:
        raise TypecheckUnavailable("Pyright no está instalado ni hay npx disponible.")
    try:
        proc = subprocess.run(
            [*command, "--outputjson"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TypecheckUnavailable(f"No se pudo ejecutar Pyright: {exc}") from exc
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise TypecheckError(
            f"Salida de Pyright no es JSON (exit {proc.returncode}): {proc.stdout[:200]}"
        ) from exc
    if not isinstance(data, dict):
        raise TypecheckError("La salida de Pyright no es un objeto JSON.")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Resumen en JSON.")
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Guarda el total actual como nueva línea base (requiere revisión).",
    )
    args = parser.parse_args(argv)

    try:
        data = run_pyright()
        diagnostics = data.get("generalDiagnostics", [])
        if not isinstance(diagnostics, list):
            raise TypecheckError("'generalDiagnostics' no es una lista.")
        summary_block = data.get("summary", {})
        files = int(summary_block.get("filesAnalyzed", 0)) if isinstance(summary_block, dict) else 0
        summary = summarize(diagnostics, files_analyzed=files)
        baseline = load_baseline()
    except TypecheckUnavailable as exc:
        print(f"[AVISO] {exc} Paso de tipado omitido.")
        return 2
    except TypecheckError as exc:
        print(f"[FALLO] {exc}")
        return 2

    if args.update_baseline:
        payload = {
            "total_errors": summary.total_errors,
            "required_zero": list(DEFAULT_REQUIRED_ZERO),
            "updated_at": "2026-11-07",
        }
        BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Línea base actualizada: {summary.total_errors} errores en {BASELINE_PATH.name}.")
        return 0

    required = tuple(baseline["required_zero"])
    problems = evaluate(summary, baseline["total_errors"], required)
    if args.json:
        print(
            json.dumps(
                {
                    "files_analyzed": summary.files_analyzed,
                    "total_errors": summary.total_errors,
                    "baseline_errors": baseline["total_errors"],
                    "required_zero": {
                        prefix: summary.count_for(prefix) for prefix in required
                    },
                    "top_files": sorted(
                        summary.error_counts.items(), key=lambda item: item[1], reverse=True
                    )[:10],
                    "problems": problems,
                },
                indent=2,
                ensure_ascii=True,
            )
        )
    else:
        print(
            f"Pyright: {summary.total_errors} errores en {summary.files_analyzed} archivos "
            f"(línea base {baseline['total_errors']})."
        )
        for prefix in required:
            print(f"  {prefix}: {summary.count_for(prefix)} errores (obligatorio 0).")
        if summary.total_errors < baseline["total_errors"]:
            print(
                "  [INFO] Has bajado de la línea base; actualízala con --update-baseline "
                "para bloquear regresiones futuras."
            )
        for problem in problems:
            print(f"  [FALLO] {problem}")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

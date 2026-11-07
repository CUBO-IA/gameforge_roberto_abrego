"""Detección y ejecución en el entorno aislado de Graphify."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def find_graphify_python(root: Path | None = None) -> Path:
    """Localiza el intérprete de Python del entorno aislado de Graphify.

    Prioridad:
    1. Variable de entorno GRAPHIFY_PYTHON.
    2. Archivo marcador graphify-out/.graphify_python.
    3. Instalación de uv tool ('uv tool dir'/graphifyy).
    4. Intérprete actual si graphify está instalado localmente.
    """
    env_py = os.environ.get("GRAPHIFY_PYTHON")
    if env_py and Path(env_py).is_file():
        return Path(env_py).resolve()

    project_root = root or Path.cwd()
    marker = project_root / "graphify-out" / ".graphify_python"
    if marker.is_file():
        content = marker.read_text(encoding="utf-8-sig").strip()
        if content and Path(content).is_file():
            return Path(content).resolve()

    # Consulta a uv tool dir
    try:
        res = subprocess.run(
            ["uv", "tool", "dir"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if res.returncode == 0:
            uv_dir = Path(res.stdout.strip())
            candidate = uv_dir / "graphifyy" / "Scripts" / "python.exe"
            if not candidate.is_file():
                candidate = uv_dir / "graphifyy" / "bin" / "python"
            if candidate.is_file():
                return candidate.resolve()
    except (subprocess.SubprocessError, OSError):
        pass

    # Comprobar intérprete actual
    try:
        import graphify  # noqa: F401

        return Path(sys.executable).resolve()
    except ImportError:
        pass

    raise RuntimeError(
        "No se encontró el entorno aislado de Graphify.\n"
        "Asegúrese de instalarlo con: uv tool install --upgrade graphifyy"
    )


def run_graphify_script(
    script_content: str,
    root: Path | None = None,
    timeout: float = 60.0,
) -> subprocess.CompletedProcess[str]:
    """Ejecuta un script arbitrario dentro del entorno aislado de Graphify."""
    py_path = find_graphify_python(root)
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [str(py_path), "-"],
        input=script_content,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Fallo en ejecución de script en Graphify (código {proc.returncode}):\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
    return proc

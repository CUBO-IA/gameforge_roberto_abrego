"""Script de construcción y preparación de distribución (PyInstaller).

Uso:
    python tools/build_dist.py [--check-only]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_packaging_prerequisites() -> bool:
    """Verifica que los archivos esenciales de datos y puntos de entrada existen."""
    required = [
        ROOT / "game" / "__main__.py",
        ROOT / "game" / "data" / "config.json",
        ROOT / "game" / "data" / "enemies.json",
        ROOT / "game" / "data" / "quests.json",
        ROOT / "game" / "data" / "recipes.json",
        ROOT / "gameforge.spec",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        print(f"[ERROR] Faltan archivos requeridos para empaquetado: {missing}")
        return False
    print("[OK] Todos los archivos de datos y especificaciones están presentes.")
    return True


def build_binary() -> int:
    """Invoca PyInstaller utilizando la especificación oficial."""
    if not check_packaging_prerequisites():
        return 1

    pyinstaller_cmd = shutil.which("pyinstaller")
    if not pyinstaller_cmd:
        print("[AVISO] PyInstaller no está instalado en el entorno.")
        print("Para compilar el binario ejecutable:")
        print("    pip install pyinstaller")
        print("    pyinstaller gameforge.spec --clean --noconfirm")
        return 0

    print("== Compilando distribución binaria con PyInstaller ==")
    proc = subprocess.run(
        [pyinstaller_cmd, "gameforge.spec", "--clean", "--noconfirm"],
        cwd=ROOT,
        check=False,
    )
    if proc.returncode == 0:
        print("\n[OK] Compilación completada con éxito.")
        print(f"Binario generado en: {ROOT / 'dist' / 'gameforge'}")
    else:
        print("\n[ERROR] Falló la compilación de PyInstaller.")
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Verifica los prerrequisitos sin ejecutar PyInstaller.",
    )
    args = parser.parse_args(argv)

    if args.check_only:
        return 0 if check_packaging_prerequisites() else 1
    return build_binary()


if __name__ == "__main__":
    sys.exit(main())

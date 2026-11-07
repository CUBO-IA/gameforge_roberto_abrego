"""Punto de entrada ejecutable para python -m tools.asset_hub."""

from __future__ import annotations

import sys

from tools.asset_hub.cli import main

if __name__ == "__main__":
    sys.exit(main())

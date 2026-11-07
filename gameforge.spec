# -*- mode: python ; coding: utf-8 -*-
"""Especificación de PyInstaller para GAMEFORGE 2D."""

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
ROOT = Path.cwd()

datas = [
    (str(ROOT / "game" / "data" / "*.json"), "game/data"),
]

hiddenimports = (
    collect_submodules("game")
    + ["pygame", "sqlite3"]
)

a = Analysis(
    [str(ROOT / "game" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "numpy", "torch"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="gameforge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Permite ver logs y soporte de --headless
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="gameforge",
)

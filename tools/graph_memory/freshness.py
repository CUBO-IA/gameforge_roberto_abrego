"""Detección de obsolescencia, archivos modificados, eliminados y renombrados."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class DriftReport:
    is_fresh: bool
    modified: list[str]
    added: list[str]
    deleted: list[str]
    renamed: list[tuple[str, str]]  # (old_path, new_path)


class ManifestTracker:
    def __init__(self, root: Path, manifest_path: Path | None = None) -> None:
        self.root = root.resolve()
        self.manifest_path = manifest_path or (self.root / "graphify-out" / ".manifest.json")

    def _hash_file(self, filepath: Path) -> str:
        """Calcula el hash SHA-256 de un archivo."""
        h = hashlib.sha256()
        h.update(filepath.read_bytes())
        return h.hexdigest()

    def collect_file_hashes(self, extensions: tuple[str, ...] = (".py", ".md", ".json")) -> dict[str, str]:
        """Calcula los hashes de todos los archivos relevantes del proyecto."""
        hashes: dict[str, str] = {}
        excluded_dirs = {
            ".git",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            "graphify-out",
            "assets",
            "archive",
            ".freebuff",
        }

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in excluded_dirs for part in path.parts):
                continue
            if path.suffix.lower() in extensions:
                rel_path = str(path.relative_to(self.root)).replace("\\", "/")
                try:
                    hashes[rel_path] = self._hash_file(path)
                except OSError:
                    pass
        return hashes

    def save_manifest(self, hashes: dict[str, str] | None = None) -> dict[str, str]:
        """Guarda el estado actual de los hashes en el archivo de manifiesto."""
        current = hashes or self.collect_file_hashes()
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": "1.0",
            "file_hashes": current,
        }
        self.manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return current

    def check_drift(self) -> DriftReport:
        """Compara el estado del sistema de archivos con el manifiesto almacenado."""
        if not self.manifest_path.is_file():
            current = self.collect_file_hashes()
            return DriftReport(
                is_fresh=False,
                modified=[],
                added=list(current.keys()),
                deleted=[],
                renamed=[],
            )

        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        saved_hashes: dict[str, str] = data.get("file_hashes", {})
        current_hashes = self.collect_file_hashes()

        saved_keys = set(saved_hashes.keys())
        current_keys = set(current_hashes.keys())

        deleted_raw = list(saved_keys - current_keys)
        added_raw = list(current_keys - saved_keys)
        common_keys = saved_keys & current_keys

        modified = [k for k in common_keys if saved_hashes[k] != current_hashes[k]]

        # Detección de archivos renombrados (mismo contenido/hash)
        renamed: list[tuple[str, str]] = []
        deleted: list[str] = []
        added: list[str] = list(added_raw)

        deleted_by_hash = {saved_hashes[k]: k for k in deleted_raw}
        for a in added_raw:
            a_hash = current_hashes[a]
            if a_hash in deleted_by_hash:
                old_p = deleted_by_hash[a_hash]
                renamed.append((old_p, a))
                added.remove(a)
            else:
                pass

        renamed_old = {r[0] for r in renamed}
        deleted = [d for d in deleted_raw if d not in renamed_old]

        is_fresh = not (modified or added or deleted or renamed)
        return DriftReport(
            is_fresh=is_fresh,
            modified=sorted(modified),
            added=sorted(added),
            deleted=sorted(deleted),
            renamed=sorted(renamed),
        )

    def to_dict(self, report: DriftReport) -> dict[str, Any]:
        return asdict(report)

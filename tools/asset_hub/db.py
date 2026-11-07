"""Capa de persistencia y base de datos local SQLite para GameForge Asset Hub."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from tools.asset_hub.hasher import hamming_distance

DEFAULT_DB_PATH = Path("assets/.hub/asset_hub.db")


class AssetHubDB:
    """Gestor de base de datos relacional y catálogo local para recursos de GameForge 2D."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        if db_path is None:
            self.db_path = DEFAULT_DB_PATH
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        elif str(db_path) == ":memory:":
            self.db_path = Path(":memory:")
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Crea las tablas e índices si no existen."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    visual_style TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    frame_w INTEGER NOT NULL,
                    frame_h INTEGER NOT NULL,
                    has_alpha INTEGER NOT NULL,
                    sha256 TEXT NOT NULL UNIQUE,
                    dhash TEXT NOT NULL,
                    license_spdx TEXT NOT NULL,
                    license_tier TEXT NOT NULL,
                    author TEXT NOT NULL,
                    source_repo TEXT NOT NULL,
                    manifest_path TEXT NOT NULL,
                    manifest_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS asset_tags (
                    asset_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    PRIMARY KEY (asset_id, tag),
                    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS character_clips (
                    asset_id TEXT NOT NULL,
                    clip_name TEXT NOT NULL,
                    frame_count INTEGER NOT NULL,
                    directions_csv TEXT NOT NULL,
                    PRIMARY KEY (asset_id, clip_name),
                    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_assets_kind ON assets(kind);
                CREATE INDEX IF NOT EXISTS idx_assets_style ON assets(visual_style);
                CREATE INDEX IF NOT EXISTS idx_assets_dimensions ON assets(frame_w, frame_h);
                CREATE INDEX IF NOT EXISTS idx_tags_tag ON asset_tags(tag);
                CREATE INDEX IF NOT EXISTS idx_clips_clip ON character_clips(clip_name);
            """)

    def close(self) -> None:
        """Cierra la conexión a la base de datos."""
        self._conn.close()

    def count(self) -> int:
        """Devuelve el total de activos registrados."""
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM assets")
        row = cur.fetchone()
        return row[0] if row else 0

    def upsert_asset(self, manifest: dict[str, Any], manifest_path: str = "") -> None:
        """Registra o actualiza un activo y sus índices asociados a partir de su manifiesto."""
        asset_id = manifest["asset_id"]
        name = manifest.get("name", asset_id)
        kind = manifest["kind"]

        taxonomy = manifest.get("taxonomy", {})
        genre = taxonomy.get("genre", "top_down_rpg")
        theme = taxonomy.get("theme", "fantasy_medieval")
        visual_style = taxonomy.get("visual_style", "pixel_art_32x32")
        tags = taxonomy.get("tags", [])

        img = manifest.get("image", {})
        image_path = img.get("relative_path", "")
        width = int(img.get("width", 0))
        height = int(img.get("height", 0))
        has_alpha = 1 if img.get("has_alpha", True) else 0
        sha256 = img.get("sha256", "")
        dhash = img.get("dhash", "0000000000000000")

        geometry = manifest.get("geometry", {})
        frame_size = geometry.get("frame_size", [width, height])
        frame_w = int(frame_size[0]) if len(frame_size) > 0 else width
        frame_h = int(frame_size[1]) if len(frame_size) > 1 else height

        provenance = manifest.get("provenance", {})
        license_spdx = provenance.get("license_spdx", "UNKNOWN")
        license_tier = provenance.get("license_tier", "tier_3_prohibited")
        author = provenance.get("author", "Desconocido")
        source_repo = provenance.get("source_repo", "custom")

        manifest_json = json.dumps(manifest, ensure_ascii=False)

        with self._conn:
            self._conn.execute("""
                INSERT INTO assets (
                    asset_id, name, kind, genre, theme, visual_style,
                    image_path, width, height, frame_w, frame_h, has_alpha,
                    sha256, dhash, license_spdx, license_tier, author,
                    source_repo, manifest_path, manifest_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asset_id) DO UPDATE SET
                    name=excluded.name,
                    kind=excluded.kind,
                    genre=excluded.genre,
                    theme=excluded.theme,
                    visual_style=excluded.visual_style,
                    image_path=excluded.image_path,
                    width=excluded.width,
                    height=excluded.height,
                    frame_w=excluded.frame_w,
                    frame_h=excluded.frame_h,
                    has_alpha=excluded.has_alpha,
                    sha256=excluded.sha256,
                    dhash=excluded.dhash,
                    license_spdx=excluded.license_spdx,
                    license_tier=excluded.license_tier,
                    author=excluded.author,
                    source_repo=excluded.source_repo,
                    manifest_path=excluded.manifest_path,
                    manifest_json=excluded.manifest_json
            """, (
                asset_id, name, kind, genre, theme, visual_style,
                image_path, width, height, frame_w, frame_h, has_alpha,
                sha256, dhash, license_spdx, license_tier, author,
                source_repo, manifest_path, manifest_json
            ))

            # Actualizar tags
            self._conn.execute("DELETE FROM asset_tags WHERE asset_id = ?", (asset_id,))
            for tag in tags:
                self._conn.execute(
                    "INSERT OR IGNORE INTO asset_tags (asset_id, tag) VALUES (?, ?)",
                    (asset_id, tag.lower().strip())
                )

            # Actualizar clips
            self._conn.execute("DELETE FROM character_clips WHERE asset_id = ?", (asset_id,))
            char_data = manifest.get("character_data", {})
            available_clips = char_data.get("available_clips", [])
            for clip in available_clips:
                cname = clip.get("name", "")
                fcount = int(clip.get("frame_count", 1))
                dirs = ",".join(clip.get("directions", ["down"]))
                if cname:
                    self._conn.execute(
                        "INSERT OR REPLACE INTO character_clips (asset_id, clip_name, frame_count, directions_csv) VALUES (?, ?, ?, ?)",
                        (asset_id, cname.lower().strip(), fcount, dirs)
                    )

    def get_asset(self, asset_id: str) -> dict[str, Any] | None:
        """Recupera el manifiesto completo de un activo por su ID."""
        cur = self._conn.cursor()
        cur.execute("SELECT manifest_json FROM assets WHERE asset_id = ?", (asset_id,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row["manifest_json"])

    def find_by_sha256(self, sha256: str) -> dict[str, Any] | None:
        """Encuentra un activo por su suma de verificación SHA-256 exacta."""
        cur = self._conn.cursor()
        cur.execute("SELECT manifest_json FROM assets WHERE sha256 = ?", (sha256,))
        row = cur.fetchone()
        return json.loads(row["manifest_json"]) if row else None

    def find_duplicates(self, dhash: str, max_hamming: int = 4) -> list[tuple[dict[str, Any], int]]:
        """Busca duplicados visuales comparando la distancia de Hamming entre hashes perceptuales."""
        cur = self._conn.cursor()
        cur.execute("SELECT asset_id, dhash, manifest_json FROM assets")
        results: list[tuple[dict[str, Any], int]] = []
        for row in cur.fetchall():
            other_dhash = row["dhash"]
            if other_dhash and len(other_dhash) == len(dhash):
                dist = hamming_distance(dhash, other_dhash)
                if dist <= max_hamming:
                    results.append((json.loads(row["manifest_json"]), dist))
        return sorted(results, key=lambda x: x[1])

    def list_all(self) -> list[dict[str, Any]]:
        """Devuelve todos los activos del catálogo como lista de diccionarios."""
        cur = self._conn.cursor()
        cur.execute("SELECT manifest_json FROM assets ORDER BY asset_id ASC")
        return [json.loads(row["manifest_json"]) for row in cur.fetchall()]

    def export_catalog_json(self, output_path: Path | str) -> None:
        """Exporta el catálogo completo a un archivo JSON unificado."""
        assets = self.list_all()
        data = {
            "schema_version": "gf-asset-catalog-v1.0.0",
            "total_assets": len(assets),
            "assets": assets
        }
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

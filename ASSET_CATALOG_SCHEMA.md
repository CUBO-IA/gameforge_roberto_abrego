# ASSET_CATALOG_SCHEMA.md — GAMEFORGE 2D
## Especificación Formal del Esquema de Catálogo y Manifiestos de Recursos `gf-asset-catalog-v1`

**Estado:** ESPECIFICACIÓN TÉCNICA NORMATIVA  
**Misión:** MISIÓN 003 — Asset Ecosystem & GameForge Asset Hub  
**Versión de Esquema:** `gf-asset-catalog-v1.0.0`  
**Fecha:** 2026-11-07  
**Autor:** Director / Arquitecto de Sistemas & Especialista en Pipeline de Arte  

---

## 1. Resumen y Principios de Diseño

El esquema `gf-asset-catalog-v1` define la estructura de datos obligatoria para la indexación, clasificación taxonómica, verificación geométrica, auditoría de licencias y consulta algorítmica de activos gráficos en **GameForge 2D**.

### Principios Fundamentales
1. **Introspección Semántica para Agentes de IA:** Los agentes deben poder filtrar por propiedades funcionales exactas (ej. `kind: "character"`, `frame_size: [32, 32]`, `has_clips: ["walk", "attack_melee", "hurt"]`) sin necesidad de decodificar ni adivinar sobre los archivos binarios de imagen.
2. **Determinismo y Verificación Criptográfica:** Cada activo registrado contiene su hash SHA-256 de fichero y su hash perceptual de imagen (dHash) para prevenir duplicados y detectar modificaciones no autorizadas en el disco.
3. **Trazabilidad Legal Rigurosa:** Cada recurso incluye su identificador SPDX estándar, autor, URL original y nivel de riesgo de licencia.
4. **Desacoplamiento del Motor:** El esquema del catálogo es puro formato declarativo JSON, procesable con herramientas externas y sin dependencias de bibliotecas gráficas en tiempo de consulta.

---

## 2. Definición Formal: JSON Schema (Draft 2020-12)

A continuación se define el esquema normativo para los manifiestos de recursos individuales (`*.asset.json`) y para el índice agregado del catálogo (`catalog_index.json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://gameforge2d.org/schemas/gf-asset-catalog-v1.json",
  "title": "GameForge2DAssetManifestSpecification",
  "type": "object",
  "required": [
    "schema_version",
    "asset_id",
    "name",
    "kind",
    "taxonomy",
    "image",
    "geometry",
    "provenance",
    "engine_compatibility"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "enum": ["gf-asset-catalog-v1", "gf-asset-catalog-v1.0.0"]
    },
    "asset_id": {
      "type": "string",
      "pattern": "^[a-z0-9_]+$",
      "description": "Identificador único global en minúsculas y snake_case"
    },
    "name": {
      "type": "string",
      "description": "Nombre legible para humanos y herramientas"
    },
    "kind": {
      "type": "string",
      "enum": [
        "character",
        "creature_enemy",
        "npc",
        "tileset",
        "ui_component",
        "ui_icon",
        "item_equipment",
        "vfx",
        "audio_sfx"
      ]
    },
    "taxonomy": {
      "type": "object",
      "required": ["genre", "theme", "visual_style", "tags"],
      "properties": {
        "genre": { "type": "string", "default": "top_down_rpg" },
        "theme": { 
          "type": "string", 
          "enum": ["fantasy_medieval", "dungeon", "cavern", "gothic", "sci_fi", "steampunk", "nature"] 
        },
        "visual_style": { 
          "type": "string", 
          "enum": [
            "pixel_art_16x16",
            "pixel_art_32x32",
            "pixel_art_64x64",
            "lpc_compatible_64x64",
            "vector_flat",
            "ui_clean"
          ] 
        },
        "tags": {
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true
        }
      }
    },
    "image": {
      "type": "object",
      "required": ["relative_path", "width", "height", "has_alpha", "sha256", "dhash"],
      "properties": {
        "relative_path": { "type": "string", "description": "Ruta relativa al archivo de imagen PNG" },
        "width": { "type": "integer", "minimum": 1 },
        "height": { "type": "integer", "minimum": 1 },
        "has_alpha": { "type": "boolean" },
        "color_mode": { "type": "string", "enum": ["RGBA", "RGB", "INDEXED"], "default": "RGBA" },
        "sha256": { 
          "type": "string", 
          "pattern": "^[a-f0-9]{64}$",
          "description": "Hash SHA-256 del fichero binario para control de integridad"
        },
        "dhash": { 
          "type": "string", 
          "pattern": "^[a-f0-9]{16}$",
          "description": "Perceptual difference hash de 64 bits para detección de duplicados visuales"
        }
      }
    },
    "geometry": {
      "type": "object",
      "required": ["layout_type", "frame_size"],
      "properties": {
        "layout_type": { 
          "type": "string", 
          "enum": ["uniform_grid", "packed_atlas", "single_image", "9_slice"] 
        },
        "frame_size": {
          "type": "array",
          "description": "[ancho, alto] del fotograma o tile canónico",
          "items": { "type": "integer", "minimum": 1 },
          "minItems": 2,
          "maxItems": 2
        },
        "padding": { "type": "integer", "minimum": 0, "default": 0 },
        "spacing": { "type": "integer", "minimum": 0, "default": 0 },
        "anchor_preset": {
          "type": "string",
          "enum": ["bottom_center", "center", "top_left", "custom"],
          "default": "bottom_center"
        },
        "anchor_offset": {
          "type": "array",
          "items": { "type": "integer" },
          "minItems": 2,
          "maxItems": 2,
          "default": [0, 0]
        }
      }
    },
    "character_data": {
      "type": "object",
      "description": "Obligatorio si kind es character, creature_enemy o npc",
      "properties": {
        "directions_supported": {
          "type": "array",
          "items": { "type": "string", "enum": ["down", "left", "right", "up", "down_left", "down_right", "up_left", "up_right"] }
        },
        "available_clips": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "frame_count", "directions"],
            "properties": {
              "name": { "type": "string" },
              "frame_count": { "type": "integer", "minimum": 1 },
              "directions": { "type": "array", "items": { "type": "string" } },
              "duration_ms": { "type": "integer", "default": 100 },
              "is_looping": { "type": "boolean", "default": true }
            }
          }
        },
        "has_paperdoll_layers": { "type": "boolean", "default": false },
        "paperdoll_slot": { 
          "type": "string", 
          "enum": ["base_body", "hair", "helmet", "torso_armor", "legs_armor", "boots", "weapon", "shield", "none"],
          "default": "none"
        }
      }
    },
    "tileset_data": {
      "type": "object",
      "description": "Obligatorio si kind es tileset",
      "properties": {
        "tile_dimensions": {
          "type": "array",
          "items": { "type": "integer", "minimum": 1 },
          "minItems": 2,
          "maxItems": 2
        },
        "terrain_types": {
          "type": "array",
          "items": { "type": "string" }
        },
        "autotile_supported": {
          "type": "string",
          "enum": ["none", "wang_16", "blob_47", "corners_4"],
          "default": "none"
        },
        "solid_tile_indices": {
          "type": "array",
          "items": { "type": "integer", "minimum": 0 }
        },
        "hazard_tile_indices": {
          "type": "array",
          "items": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "ui_data": {
      "type": "object",
      "description": "Obligatorio si kind es ui_component",
      "properties": {
        "slice_margins": {
          "type": "array",
          "description": "[top, right, bottom, left] márgenes fijos de las esquinas",
          "items": { "type": "integer", "minimum": 0 },
          "minItems": 4,
          "maxItems": 4
        },
        "supported_states": {
          "type": "array",
          "items": { "type": "string", "enum": ["normal", "hover", "pressed", "disabled", "focused"] }
        },
        "recommended_min_size": {
          "type": "array",
          "items": { "type": "integer", "minimum": 1 },
          "minItems": 2,
          "maxItems": 2
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["author", "source_repo", "license_spdx", "license_tier", "attribution_required"],
      "properties": {
        "author": { "type": "string" },
        "original_url": { "type": "string", "format": "uri" },
        "source_repo": { 
          "type": "string", 
          "enum": [
            "shorepine/kenney",
            "kenney.nl",
            "OpenGameArt/LiberatedPixelCup",
            "OpenGameArt/LPC-Style-Guide",
            "Tiddybub/2d-assets",
            "eturner58/game-assets",
            "opengameart.org",
            "internal_gameforge"
          ] 
        },
        "license_spdx": { 
          "type": "string", 
          "enum": [
            "CC0-1.0",
            "CC-BY-3.0",
            "CC-BY-4.0",
            "CC-BY-SA-3.0",
            "CC-BY-SA-4.0",
            "GPL-3.0-or-later",
            "MIT",
            "OGA-BY-3.0"
          ] 
        },
        "license_tier": {
          "type": "string",
          "enum": [
            "tier_0_public_domain",
            "tier_1_permissive_attribution",
            "tier_2_copyleft_warning",
            "tier_3_prohibited"
          ]
        },
        "attribution_required": { "type": "boolean" },
        "attribution_text": { "type": "string" },
        "modifications_made": { "type": "string", "default": "none" }
      }
    },
    "engine_compatibility": {
      "type": "object",
      "required": ["gf_anim_v1_ready", "tilemap_ready", "canvas_scale_compatible"],
      "properties": {
        "gf_anim_v1_ready": { 
          "type": "boolean",
          "description": "Indica si ya cuenta con fichero anim.json compilado o es convertible de inmediato"
        },
        "tilemap_ready": { "type": "boolean" },
        "canvas_scale_compatible": { "type": "boolean" },
        "export_target_path": { "type": "string" }
      }
    }
  }
}
```

---

## 3. Ejemplos Concretos de Manifiestos de Recursos

### 3.1. Manifiesto de Personaje Humanoide (Compatible LPC)
Archivo: `hub_data/characters/lpc_skeleton_warrior.asset.json`

```json
{
  "schema_version": "gf-asset-catalog-v1",
  "asset_id": "lpc_skeleton_warrior",
  "name": "LPC Skeleton Warrior Animated",
  "kind": "creature_enemy",
  "taxonomy": {
    "genre": "top_down_rpg",
    "theme": "dungeon",
    "visual_style": "lpc_compatible_64x64",
    "tags": ["undead", "skeleton", "warrior", "melee", "sword", "enemy"]
  },
  "image": {
    "relative_path": "images/lpc_skeleton_warrior.png",
    "width": 832,
    "height": 1344,
    "has_alpha": true,
    "color_mode": "RGBA",
    "sha256": "4b5d27b9c9f688e1a6c4293f77341e459a930129bc564d6e902b45138122a611",
    "dhash": "3c3c78e0e0783c18"
  },
  "geometry": {
    "layout_type": "uniform_grid",
    "frame_size": [64, 64],
    "padding": 0,
    "spacing": 0,
    "anchor_preset": "bottom_center",
    "anchor_offset": [32, 58]
  },
  "character_data": {
    "directions_supported": ["up", "left", "down", "right"],
    "available_clips": [
      {
        "name": "walk",
        "frame_count": 9,
        "directions": ["up", "left", "down", "right"],
        "duration_ms": 100,
        "is_looping": true
      },
      {
        "name": "attack_melee",
        "frame_count": 6,
        "directions": ["up", "left", "down", "right"],
        "duration_ms": 80,
        "is_looping": false
      },
      {
        "name": "hurt",
        "frame_count": 6,
        "directions": ["down"],
        "duration_ms": 100,
        "is_looping": false
      }
    ],
    "has_paperdoll_layers": false,
    "paperdoll_slot": "none"
  },
  "provenance": {
    "author": "Stephen Challener (Redshrike), Johannes Sjölund (wulax)",
    "original_url": "https://opengameart.org/content/liberated-pixel-cup-lpc-base-assets-sprites-map-tiles",
    "source_repo": "OpenGameArt/LiberatedPixelCup",
    "license_spdx": "CC-BY-SA-3.0",
    "license_tier": "tier_2_copyleft_warning",
    "attribution_required": true,
    "attribution_text": "Skeleton Warrior by Stephen Challener (Redshrike) and Johannes Sjölund (wulax), OpenGameArt Liberated Pixel Cup, licensed under CC-BY-SA 3.0.",
    "modifications_made": "Extracted and mapped to GameForge gf-anim-v1 format."
  },
  "engine_compatibility": {
    "gf_anim_v1_ready": true,
    "tilemap_ready": false,
    "canvas_scale_compatible": true,
    "export_target_path": "assets/sprites/enemies/skeleton_warrior/"
  }
}
```

---

### 3.2. Manifiesto de Tileset de Mazmorra (Estilo Kenney / Roguelike 32x32)
Archivo: `hub_data/tilesets/kenney_dungeon_stone_32.asset.json`

```json
{
  "schema_version": "gf-asset-catalog-v1",
  "asset_id": "kenney_dungeon_stone_32",
  "name": "Kenney Dungeon Stone Tileset 32x32",
  "kind": "tileset",
  "taxonomy": {
    "genre": "top_down_rpg",
    "theme": "dungeon",
    "visual_style": "pixel_art_32x32",
    "tags": ["stone", "wall", "floor", "dungeon", "stairs", "chest", "kenney"]
  },
  "image": {
    "relative_path": "images/kenney_dungeon_stone_32.png",
    "width": 512,
    "height": 512,
    "has_alpha": true,
    "color_mode": "RGBA",
    "sha256": "89e2b109cc4a12df082736bca487198f828114092b3491cae78553d100129bc5",
    "dhash": "007e7e7e7e7e7e00"
  },
  "geometry": {
    "layout_type": "uniform_grid",
    "frame_size": [32, 32],
    "padding": 0,
    "spacing": 0,
    "anchor_preset": "top_left",
    "anchor_offset": [0, 0]
  },
  "tileset_data": {
    "tile_dimensions": [32, 32],
    "terrain_types": ["stone_floor", "mossy_floor", "stone_wall", "hazard_spikes", "water"],
    "autotile_supported": "wang_16",
    "solid_tile_indices": [16, 17, 18, 32, 34, 48, 49, 50],
    "hazard_tile_indices": [64, 65]
  },
  "provenance": {
    "author": "Kenney (Kenney.nl)",
    "original_url": "https://kenney.nl/assets/tiny-dungeon",
    "source_repo": "kenney.nl",
    "license_spdx": "CC0-1.0",
    "license_tier": "tier_0_public_domain",
    "attribution_required": false,
    "attribution_text": "Tiny Dungeon assets by Kenney (kenney.nl), dedicated to the public domain under CC0 1.0.",
    "modifications_made": "Scaled to 32x32 using nearest-neighbor filter, sliced and tagged for GameForge TileMap."
  },
  "engine_compatibility": {
    "gf_anim_v1_ready": false,
    "tilemap_ready": true,
    "canvas_scale_compatible": true,
    "export_target_path": "assets/tilesets/dungeon_stone/"
  }
}
```

---

### 3.3. Manifiesto de Componente UI (Panel de Diálogo 9-Slice)
Archivo: `hub_data/ui/fantasy_dialog_box_9slice.asset.json`

```json
{
  "schema_version": "gf-asset-catalog-v1",
  "asset_id": "fantasy_dialog_box_9slice",
  "name": "Fantasy Parchment Dialog Box 9-Slice",
  "kind": "ui_component",
  "taxonomy": {
    "genre": "top_down_rpg",
    "theme": "fantasy_medieval",
    "visual_style": "ui_clean",
    "tags": ["dialog", "window", "panel", "9slice", "parchment", "gold_border"]
  },
  "image": {
    "relative_path": "images/fantasy_dialog_box_9slice.png",
    "width": 96,
    "height": 96,
    "has_alpha": true,
    "color_mode": "RGBA",
    "sha256": "33a948ecda8421049c95b4c102a9042b3109a4d8c7b8e192a3b4c5d6e7f80192",
    "dhash": "ff818181818181ff"
  },
  "geometry": {
    "layout_type": "9_slice",
    "frame_size": [96, 96],
    "padding": 0,
    "spacing": 0,
    "anchor_preset": "top_left",
    "anchor_offset": [0, 0]
  },
  "ui_data": {
    "slice_margins": [24, 24, 24, 24],
    "supported_states": ["normal", "focused"],
    "recommended_min_size": [120, 80]
  },
  "provenance": {
    "author": "Kenney (Kenney.nl)",
    "original_url": "https://kenney.nl/assets/ui-pack-rpg-expansion",
    "source_repo": "shorepine/kenney",
    "license_spdx": "CC0-1.0",
    "license_tier": "tier_0_public_domain",
    "attribution_required": false,
    "attribution_text": "UI Pack RPG Expansion by Kenney (kenney.nl), CC0 1.0 Universal.",
    "modifications_made": "Isolated 9-slice slice margins for GameForge 2D VirtualCanvas UI."
  },
  "engine_compatibility": {
    "gf_anim_v1_ready": false,
    "tilemap_ready": false,
    "canvas_scale_compatible": true,
    "export_target_path": "assets/ui/skins/dialog_box/"
  }
}
```

---

### 3.4. Manifiesto de Icono de Objeto / Equipamiento
Archivo: `hub_data/items/iron_longsword_32.asset.json`

```json
{
  "schema_version": "gf-asset-catalog-v1",
  "asset_id": "iron_longsword_32",
  "name": "Iron Longsword Icon 32x32",
  "kind": "item_equipment",
  "taxonomy": {
    "genre": "top_down_rpg",
    "theme": "fantasy_medieval",
    "visual_style": "pixel_art_32x32",
    "tags": ["sword", "weapon", "melee", "iron", "equipment", "inventory_icon"]
  },
  "image": {
    "relative_path": "images/iron_longsword_32.png",
    "width": 32,
    "height": 32,
    "has_alpha": true,
    "color_mode": "RGBA",
    "sha256": "fe0932187654ba21cd890123ef4567890abcdef123456789abcdef0123456789",
    "dhash": "0103070f1f3f7fff"
  },
  "geometry": {
    "layout_type": "single_image",
    "frame_size": [32, 32],
    "padding": 0,
    "spacing": 0,
    "anchor_preset": "center",
    "anchor_offset": [16, 16]
  },
  "provenance": {
    "author": "OpenGameArt Community (LPC Weapons Set)",
    "original_url": "https://opengameart.org/content/lpc-weapons",
    "source_repo": "OpenGameArt/LiberatedPixelCup",
    "license_spdx": "CC-BY-SA-3.0",
    "license_tier": "tier_2_copyleft_warning",
    "attribution_required": true,
    "attribution_text": "LPC Weapons Set by OpenGameArt contributors, licensed under CC-BY-SA 3.0.",
    "modifications_made": "Framed and centered into a 32x32 inventory icon slot."
  },
  "engine_compatibility": {
    "gf_anim_v1_ready": false,
    "tilemap_ready": false,
    "canvas_scale_compatible": true,
    "export_target_path": "assets/items/icons/"
  }
}
```

---

## 4. Esquema de Base de Datos para Indexación Rápida (SQLite)

Para que el Asset Hub responda a consultas de agentes en menos de 5 milisegundos sin parsear cientos de archivos JSON en cada invocación, se define la siguiente estructura relacional en SQLite (`assets/.hub/asset_hub.db`):

```sql
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
    has_alpha BOOLEAN NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    dhash TEXT NOT NULL,
    license_spdx TEXT NOT NULL,
    license_tier TEXT NOT NULL,
    author TEXT NOT NULL,
    source_repo TEXT NOT NULL,
    manifest_path TEXT NOT NULL
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
```

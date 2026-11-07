# Diseño del GameForge Asset Hub

**Documento:** `ASSET_HUB_DESIGN.md`  
**Versión:** 1.0.0 (Aprobada tras Visual Overhaul — Misión 008)  
**Módulos Clave:** `tools/asset_hub/`, `assets/.hub/asset_hub.db`, `assets/hub_index.json`

---

## 1. Misión y Propósito

El **GameForge Asset Hub** es un subsistema offline de infraestructura y catalogación diseñado para:
1. Indexar de forma centralizada todos los recursos gráficos del proyecto.
2. Servir como fuente de verdad inmutable para que agentes de desarrollo y artistas consulten recursos antes de crear o adquirir nuevos.
3. Detectar duplicados mediante huellas perceptuales (dHash) y firmas criptográficas (SHA-256).
4. Auditar la compatibilidad técnica y la trazabilidad legal (licencias SPDX, atribución y restricciones ShareAlike).
5. Mantener un desacoplamiento estricto con el motor del juego: **el código en `game/` nunca importa el Asset Hub ni SQLite**.

---

## 2. Arquitectura y Esquema de Base de Datos

El Asset Hub utiliza una base de datos local SQLite ubicada en `assets/.hub/asset_hub.db` con soporte para exportación completa a `assets/hub_index.json`:

```sql
-- Tabla principal de activos
CREATE TABLE assets (
    asset_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,                -- 'character', 'creature_enemy', 'tileset', 'prop', 'ui'
    genre TEXT NOT NULL,
    theme TEXT NOT NULL,
    visual_style TEXT NOT NULL,        -- ej: 'pixel_art_32x32'
    image_path TEXT NOT NULL,          -- ruta relativa normalizada con '/'
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    frame_w INTEGER NOT NULL,
    frame_h INTEGER NOT NULL,
    has_alpha INTEGER NOT NULL,        -- booleano (0 o 1)
    sha256 TEXT NOT NULL UNIQUE,       -- firma SHA-256 inmutable
    dhash TEXT NOT NULL,               -- huella perceptual de 64 bits en hexadecimal
    license_spdx TEXT NOT NULL,        -- ej: 'MIT', 'CC0-1.0', 'CC-BY-SA-3.0'
    license_tier TEXT NOT NULL,        -- 'tier_0_public_domain', 'tier_1_permissive', etc.
    author TEXT NOT NULL,
    source_repo TEXT NOT NULL,
    manifest_path TEXT NOT NULL,
    manifest_json TEXT NOT NULL        -- documento JSON completo canónico
);

-- Índices de etiquetas semánticas
CREATE TABLE asset_tags (
    asset_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);

-- Catálogo de clips de animación
CREATE TABLE character_clips (
    asset_id TEXT NOT NULL,
    clip_name TEXT NOT NULL,
    frame_count INTEGER NOT NULL,
    directions_csv TEXT NOT NULL,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);
```

---

## 3. Comandos de la CLI (`python -m tools.asset_hub`)

La interfaz por línea de comandos permite la operación completa tanto por desarrolladores humanos como por agentes autónomos:

### A. Escaneo e Indexación (`scan`)
```bash
python -m tools.asset_hub scan
```
- Recorre recursivamente `assets/`.
- Procesa manifiestos formales `*.asset.json` y manifiestos canónicos de animación `*.anim.json`.
- Calcula automáticamente dimensiones, canal alfa, SHA-256 y dHash.
- Sincroniza la base de datos SQLite y exporta el catálogo universal a `assets/hub_index.json`.

### B. Búsqueda Semántica (`search`)
```bash
python -m tools.asset_hub search --kind creature_enemy --tag melee --max-size 48x48
```
Permite filtrar por categoría, estilo visual, rango de resolución, presencia de canal alfa, clips requeridos y licencia SPDX.

### C. Inspección Detallada (`inspect`)
```bash
python -m tools.asset_hub inspect knight_hero
```
Muestra toda la metadata del recurso: origen, autor, licencia, clips con número de frames, layout geométrico y firma digital.

### D. Auditoría Estricta (`validate`)
```bash
python -m tools.asset_hub validate --all
```
Ejecuta la batería de validación de reglas V-01 a V-07:
- **V-01:** Verificación de hash SHA-256 contra el binario en disco.
- **V-02:** Comprobación de existencia del archivo de imagen.
- **V-03:** Consistencia de rectángulos y límites de la textura.
- **V-04:** Verificación de clips esenciales (idle, walk, hurt, die) en personajes.
- **V-05:** Alertas de licencias restrictivas (aislamiento de paquetes ShareAlike).
- **V-06:** Detección de imágenes duplicadas o casi idénticas (distancia dHash <= 5).
- **V-07:** Verificación de transparencia obligatoria en sprites.

### E. Previsualización Headless (`preview`)
```bash
python -m tools.asset_hub preview knight_hero --clip walk --save artifacts/hero_preview.png
```
Permite generar una vista previa de la animación o del spritesheet en entornos sin display físico.

### F. Generación de Créditos (`credits`)
```bash
python -m tools.asset_hub credits
```
Reconstruye automáticamente el archivo legal de atribuciones `CREDITS.md` a partir de los metadatos verificados de cada activo.

---

## 4. Estado Actual del Catálogo

Tras el overhaul de la Misión 008, todos los 8 activos del catálogo se encuentran formalmente validados con resultado `8 aprobados, 0 con errores`:

1. `knight_hero` (MIT, GameForge ArtForge) — Atlas 624×150 px.
2. `slime` (MIT, GameForge ArtForge) — Atlas 192×128 px.
3. `wisp` (MIT, GameForge ArtForge) — Atlas 192×128 px.
4. `brute` (MIT, GameForge ArtForge) — Atlas 288×322 px.
5. `lpc_skeleton_warrior` (CC-BY-SA-3.0, Liberated Pixel Cup) — Atlas 256×64 px.
6. `kenney_dungeon_stone_32` (CC0-1.0, Kenney) — Tileset 128×128 px.
7. `kenney_roguelike_guard` (CC0-1.0, Kenney) — Spritesheet 32×16 px.
8. `fantasy_dialog_box_9slice` (CC0-1.0, Kenney) — UI 96×96 px.

---

## 5. Garantías de Seguridad y Rendimiento

- **No Ejecución de Código:** El Hub solo lee y decodifica formatos estándar seguros (`.json`, `.png`). No ejecuta scripts contenidos en paquetes de assets.
- **Determinismo y Portabilidad:** Las rutas relativas utilizan el separador canónico `/` para garantizar compatibilidad idéntica entre Windows y Linux.
- **Zero Runtime Overhead:** El motor Pygame CE en `game/` no realiza consultas SQL ni llamadas a la CLI del Hub; consume exclusivamente las texturas y datos cacheados por `ArtLibrary`.

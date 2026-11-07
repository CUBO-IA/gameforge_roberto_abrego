# Pipeline de Producción y Gestión de Assets — GameForge 2D

**Documento:** `ASSET_PIPELINE.md`  
**Versión:** 1.0.0 (Aprobada tras Visual Overhaul — Misión 008)  
**Módulos Clave:** `tools/artforge/`, `tools/asset_hub/`, `game/render/assets.py`

---

## 1. Visión General del Pipeline

El pipeline de assets de GameForge 2D sigue una arquitectura estrictamente desacoplada entre **generación/preprocesamiento offline** y **consumo en tiempo de ejecución**:

```
+-----------------------------------------------------------------------------------+
| FASE 1: PRODUCCIÓN DETERMINISTA OFFLINE (tools/artforge/)                         |
|                                                                                   |
|  palette.py ----> pixel.py (Rasterizador por software / Shading / Dithering)      |
|                       |                                                           |
|       +---------------+---------------+---------------+                           |
|       |               |               |               |                           |
|  characters.py    tiles.py       objects.py       ui.py / vfx.py                  |
|       |               |               |               |                           |
|       +---------------+---------------+---------------+                           |
|                               |                                                   |
|                        atlas.py (Empacado de atlas & manifiestos JSON)            |
+---------------------------------------+-------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| FASE 2: ALMACENAMIENTO Y CATALOGACIÓN (assets/ & tools/asset_hub/)                |
|                                                                                   |
|  assets/sprites/ (Atlas PNG + *.anim.json con rig_type="frame_by_frame")          |
|  assets/art/ (dungeon_tileset, objects, particles, ui)                            |
|  assets/.hub/asset_hub.db (Base de datos SQLite local)                            |
|  assets/hub_index.json (Catálogo universal indexado con SHA-256 y dHash)          |
|  tools/asset_hub/scanner.py / validator.py (Reglas V-01 a V-07)                   |
+---------------------------------------+-------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| FASE 3: CONSUMO EN RUNTIME (game/render/)                                         |
|                                                                                   |
|  game/render/assets.py (ArtLibrary & ArtAtlas)                                    |
|      - Caché de subsurfaces, 9-slice y tinte de partículas                        |
|      - Tolerancia total a ausencia de arte (retorna None sin lanzar error)        |
|                                                                                   |
|  Consumidores:                                                                    |
|      - TileRenderer: suelos variados, muros con sombras y agua/lava animada       |
|      - entity_renderer: spritesheets de héroe/enemigos, props con llama viva      |
|      - hud / ui: marcos y barras de salud 9-slice, retícula de puntero             |
+-----------------------------------------------------------------------------------+
```

---

## 2. Herramientas de Producción Offline (`tools/artforge`)

El paquete `tools/artforge` genera de manera determinista y reproducible todos los sprites, tilesets, props, efectos y elementos de UI sin recurrir a APIs externas de pago:

- **`palette.py`**: Define la paleta cromática canónica de fantasía oscura con rampas de luz, sombra y tonos intermedios.
- **`pixel.py`**: Implementa el motor de rasterización pixel art en memoria (`Canvas`): trazado de píxeles, líneas bresenham, círculos, elipses, patrones de dithering 2×2, sombras proyectadas y exportación de hojas de contacto (`contact_sheet`).
- **`characters.py`**: Compone las animaciones completas para el héroe y los enemigos:
  - `knight_hero`: 6 clips (idle, walk, run, attack, hurt, die), 27 frames totales.
  - `slime`: 5 clips (idle, walk, attack, hurt, die), 16 frames.
  - `wisp`: 5 clips (idle, walk, shoot, hurt, die), 18 frames.
  - `brute`: 7 clips (idle, walk, windup, charge, attack, hurt, die), 24 frames.
- **`tiles.py`**: Construye el atlas de terreno `dungeon_tileset.png` (32×32 px) con 34 tiles (suelos, muros, sombras, remates, agua, lava y adornos de calaveras, huesos y hongos).
- **`objects.py`**: Dibuja los interactivos del mundo: cofre cerrado y abierto, base de hoguera con 4 fases de llama animada y altar de la forja inactivo y activo con fuego místico.
- **`vfx.py`**: Genera 12 sprites de partículas tintables (chispas, humo, sangre, ascuas, tajos de espada, runas, estrellas).
- **`ui.py`**: Diseña 16 elementos de interfaz con configuración 9-slice (paneles, marcos de barra, ranuras de inventario, botones con estado hover y retícula).
- **`atlas.py`**: Empaca los frames en texturas compactas, calcula rectángulos y escribe manifiestos en formato estándar `gf-anim-v1`.
- **`build.py`**: CLI principal de construcción:
  ```bash
  python -m tools.artforge.build
  ```

---

## 3. Especificaciones de Manifiestos

### A. Animación de Personajes (`gf-anim-v1`)
Todos los manifiestos cumplen con la validación estricta de `tools.validate_character`:
- `version`: `"gf-anim-v1"`.
- `metadata`: Contiene `id`, `display_name`, `author`, `license`, `rig_type: "frame_by_frame"` y `tags`.
- `texture`: Ruta relativa al atlas, ancho, alto y formato RGBA.
- `frames`: Array de fotogramas con `rect: [x, y, w, h]`, `pivot: [px, py]`, `duration_ms`, `sockets`, `hurtboxes`, `hitboxes` y `events`.
- `clips`: Diccionario de animaciones con lista de frames, `loop: bool`, `playback_speed: float` y `interrupt_priority: int`.

### B. Manifiestos de Terreno (`gf-tiles-v1`), Objetos (`gf-objects-v1`) y UI (`gf-ui-v1`)
Estructuras declarativas en JSON con identificadores semánticos, coordenadas de atlas y márgenes 9-slice `[left, top, right, bottom]`.

---

## 4. Auditoría y Control de Calidad (`tools/asset_hub`)

Antes de integrar o consolidar recursos, se ejecutan las herramientas de verificación:

1. **Escaneo e Indexación:**
   ```bash
   python -m tools.asset_hub scan
   ```
   Descubre atlas e imágenes en `assets/`, calcula hashes SHA-256 criptográficos y dHash perceptuales, y actualiza `assets/hub_index.json` y la base de datos `assets/.hub/asset_hub.db`.

2. **Validación Automática de Reglas (V-01 a V-07):**
   ```bash
   python -m tools.asset_hub validate --all
   ```
   - **V-01 (Integridad de Hash):** Verifica que el contenido binario coincide con la firma SHA-256 registrada.
   - **V-02 (Existencia de Archivos):** Comprueba que no hay rutas rotas hacia imágenes de textura.
   - **V-03 (Consistencia de Manifiesto):** Asegura que los rectángulos no desbordan los límites de la textura.
   - **V-04 (Clips Obligatorios):** Comprueba presencia de idle, walk, hurt y die en personajes.
   - **V-05 (Cumplimiento de Licencias):** Valida licencias compatibles (MIT, CC0, CC-BY-SA con aislamiento).
   - **V-06 (Detección de Duplicados):** Analiza colisiones por distancia de Hamming perceptual.
   - **V-07 (Canales Alfa):** Exige canal alfa limpio en sprites y objetos recortados.

---

## 5. Carga y Caché en Runtime (`game/render/assets.py`)

La clase `ArtLibrary` proporciona un acceso limpio y unificado a todos los recursos:
- **No es Singleton:** Se instancia en `Application.__init__` y se comparte a las escenas y renderizadores.
- **Caché Inteligente:**
  - `subsurface` cacheadas para evitar recortes repetidos.
  - `nine_slice(name, (width, height))` cachea superficies escaladas por tamaño solicitado.
  - `particle_sprite(name, color)` cachea texturas teñidas mediante multiplicación RGBA de Pygame.
- **Tolerancia a Modo Headless:**
  - Si un asset no existe o el display de Pygame no está inicializado, devuelve `None` de forma segura.
  - Todos los renderizadores (`TileRenderer`, `entity_renderer`, `Hud`) contienen un camino de fallback procedural garantizado.

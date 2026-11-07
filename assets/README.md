# Assets — GameForge 2D

Catálogo oficial y estructura de recursos gráficos y de audio para GameForge 2D.

## Pipeline Gráfico (ArtForge & Asset Hub)

El proyecto cuenta con un pipeline de producción determinista y modular de arte pixel art (`tools/artforge`) y un sistema de catalogación y validación (`tools/asset_hub`):

1. **Escenarios y Tilesets (`assets/art/tiles/`)**:
   - `dungeon_tileset.png` (32×32 px): Suelos variados (4 bases, agrietado, musgoso, roto, charco, rejilla), muros con remates y sombras proyectadas, agua animada, lava animada y decoración ambiental (escombros, huesos, hongos).
   - Manifiesto: `dungeon_tileset.json` (formato `gf-tiles-v1`).

2. **Objetos y Props Interactivos (`assets/art/objects/`)**:
   - `objects.png`: Cofre cerrado y abierto, base de hoguera con 4 fotogramas de llama animados, altar de la Forja inactivo y activo con fuego místico, pebeteros.
   - Manifiesto: `objects.json` (formato `gf-objects-v1`).

3. **Efectos Visuales y Partículas (`assets/art/vfx/`)**:
   - `particles.png`: Chispas, ascuas, humo, sangre, motas de luz, anillos de impacto, polvo de pisadas, destellos, cortes de espada y runas tintables.
   - Manifiesto: `particles.json` (formato `gf-vfx-v1`).

4. **Interfaz de Usuario (`assets/art/ui/`)**:
   - `ui.png`: Paneles 9-slice con reborde de fantasía oscura, marcos y rellenos de barra de vida 9-slice, ranuras de inventario, botones interactivos y retícula de apuntado.
   - Manifiesto: `ui.json` (formato `gf-ui-v1`).

5. **Personajes y Criaturas (`assets/sprites/`)**:
   - **Jugador (`knight_hero`)**: Atlas 624×150 px RGBA con animaciones completas: idle (4 frames), walk (6 frames), run (6 frames), attack (3 frames con hitboxes/eventos), hurt (2 frames) y die (6 frames). Manifiesto `knight_hero.anim.json` (`gf-anim-v1`).
   - **Cieno (`slime`)**: Atlas 192×128 px RGBA: idle, walk, attack, hurt, die.
   - **Fuego Fatuo (`wisp`)**: Atlas 192×128 px RGBA: idle, walk, shoot, hurt, die.
   - **Bruto de Escoria (`brute`)**: Atlas 288×322 px RGBA: idle, walk, windup, charge, attack, hurt, die.
   - **Guerrero Esqueleto (`lpc_skeleton_warrior`)**: Atlas 256×64 px RGBA.

## Tolerancia a Fallos y Modo Headless

El cargador de arte `game.render.assets.ArtLibrary` es completamente tolerante a la ausencia de recursos: si los archivos no existen o no se pueden cargar, devuelve `None` y los renderizadores recurren al trazado procedural, garantizando la compatibilidad con servidores headless y pruebas automatizadas.

## Audio y Datos

- **Audio (`game/render/audio.py`)**: Sintetizado proceduralmente en memoria (golpes, pasos, disparos, daño, victoria).
- **Configuración (`game/data/config.json`)**: Parámetros de juego, ventana, mazmorra y balance de entidades.

## Registro y Licencias

Todos los recursos están indexados con firma criptográfica SHA-256 en `assets/hub_index.json` y validados con `python -m tools.asset_hub validate --all`:

| Recurso | Autor / Origen | Licencia SPDX | Tipo |
|---|---|---|---|
| `knight_hero` | GameForge ArtForge (interno) | MIT | Spritesheet héroe |
| `slime` | GameForge ArtForge (interno) | MIT | Spritesheet enemigo |
| `wisp` | GameForge ArtForge (interno) | MIT | Spritesheet enemigo |
| `brute` | GameForge ArtForge (interno) | MIT | Spritesheet enemigo |
| `dungeon_tileset` | GameForge ArtForge (interno) | MIT | Tileset 32×32 |
| `objects` | GameForge ArtForge (interno) | MIT | Props interactivos |
| `particles` | GameForge ArtForge (interno) | MIT | Partículas VFX |
| `ui` | GameForge ArtForge (interno) | MIT | Elementos 9-slice |
| `lpc_skeleton_warrior` | Stephen Challener (Redshrike), Johannes Sjölund (wulax) | CC-BY-SA-3.0 | Spritesheet catálogo |
| `kenney_dungeon_stone_32` | Kenney (Tiny Dungeon) | CC0-1.0 | Tileset muestra |
| `kenney_roguelike_guard` | Kenney (Roguelike RPG Pack) | CC0-1.0 | Sprite muestra |
| `fantasy_dialog_box_9slice` | Kenney (UI Pack RPG Expansion) | CC0-1.0 | UI muestra |

### Registro de Activos Externos
- `export_hero`: Autor: Hero Designer | Licencia: CC0-1.0 | Registro en GameForge Asset Hub

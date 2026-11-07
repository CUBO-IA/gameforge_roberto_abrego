# ANIMATION_FORMAT_SPEC.md — GAMEFORGE 2D
## Especificación Formal del Formato de Animación y Metadatos `gf-anim-v1`

**Estado:** ESPECIFICACIÓN TÉCNICA NORMATIVA  
**Misión:** MISIÓN 002 — Sprites, Animaciones y Lógica de Personajes  
**Versión de Esquema:** `gf-anim-v1.0.0`  
**Fecha:** 2026-11-07  

---

## 1. Resumen y Propósito

El formato `gf-anim-v1` es la especificación estándar, abierta y declarativa en JSON utilizada por **GameForge 2D** para definir atlas de sprites, fotogramas, puntos de anclaje (*sockets*), cajas de colisión para combate (*hitboxes* y *hurtboxes*), pistas de eventos sincronizados y clips de animación.

Ha sido diseñado específicamente para:
1. **Consumo Directo por Agentes de IA:** Estructura regular, fuertemente tipada y auto-documentada que un agente LLM puede generar o modificar sin ambigüedades.
2. **Cero Dependencias en Carga:** Un simple `json.loads()` de la biblioteca estándar de Python carga el archivo; la validación se realiza mediante esquemas JSON estándar.
3. **Interoperabilidad:** Fácilmente convertible desde y hacia los formatos de exportación de **Aseprite**, **TexturePacker**, **PySpine** y **rsheet**.

---

## 2. Definición Formal: JSON Schema (Draft 2020-12)

El siguiente esquema JSON define la estructura obligatoria de un archivo de animación `*.anim.json` en GameForge 2D:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://gameforge2d.org/schemas/gf-anim-v1.json",
  "title": "GameForge2DAnimationSpecification",
  "type": "object",
  "required": ["version", "metadata", "texture", "frames", "clips"],
  "properties": {
    "version": {
      "type": "string",
      "enum": ["gf-anim-v1", "gf-anim-v1.0.0"]
    },
    "metadata": {
      "type": "object",
      "required": ["id", "display_name", "author", "rig_type"],
      "properties": {
        "id": { "type": "string", "pattern": "^[a-z0-9_]+$" },
        "display_name": { "type": "string" },
        "author": { "type": "string" },
        "rig_type": { 
          "type": "string", 
          "enum": ["frame_by_frame", "modular_cutout", "hybrid"] 
        },
        "description": { "type": "string" },
        "tags": { 
          "type": "array", 
          "items": { "type": "string" } 
        }
      }
    },
    "texture": {
      "type": "object",
      "required": ["image_path", "width", "height", "format"],
      "properties": {
        "image_path": { "type": "string" },
        "width": { "type": "integer", "minimum": 1 },
        "height": { "type": "integer", "minimum": 1 },
        "format": { 
          "type": "string", 
          "enum": ["RGBA", "RGB_COLORKEY"] 
        },
        "colorkey": {
          "type": "array",
          "items": { "type": "integer", "minimum": 0, "maximum": 255 },
          "minItems": 3,
          "maxItems": 3
        }
      }
    },
    "frames": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "rect", "pivot"],
        "properties": {
          "id": { "type": "string" },
          "rect": {
            "type": "array",
            "description": "[x, y, width, height] en el atlas",
            "items": { "type": "integer", "minimum": 0 },
            "minItems": 4,
            "maxItems": 4
          },
          "pivot": {
            "type": "array",
            "description": "[pivot_x, pivot_y] relativo a la esquina superior izquierda del fotograma",
            "items": { "type": "integer" },
            "minItems": 2,
            "maxItems": 2
          },
          "duration_ms": {
            "type": "integer",
            "minimum": 1,
            "default": 100
          },
          "sockets": {
            "type": "object",
            "additionalProperties": {
              "type": "array",
              "items": { "type": "integer" },
              "minItems": 2,
              "maxItems": 2
            }
          },
          "hurtboxes": {
            "type": "array",
            "description": "Lista de [x, y, w, h] relativos al pivote",
            "items": {
              "type": "array",
              "items": { "type": "integer" },
              "minItems": 4,
              "maxItems": 4
            }
          },
          "hitboxes": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["rect", "damage"],
              "properties": {
                "rect": {
                  "type": "array",
                  "description": "[x, y, w, h] relativo al pivote",
                  "items": { "type": "integer" },
                  "minItems": 4,
                  "maxItems": 4
                },
                "damage": { "type": "number", "minimum": 0.0 },
                "knockback_force": { "type": "number", "default": 100.0 },
                "hitstun_duration_s": { "type": "number", "default": 0.2 },
                "hit_sound": { "type": "string" }
              }
            }
          },
          "events": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name"],
              "properties": {
                "name": { "type": "string" },
                "payload": { "type": "object" }
              }
            }
          }
        }
      }
    },
    "clips": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["frames"],
        "properties": {
          "frames": {
            "type": "array",
            "items": { "type": "string" }
          },
          "loop": { "type": "boolean", "default": true },
          "playback_speed": { "type": "number", "default": 1.0 },
          "interrupt_priority": { 
            "type": "integer", 
            "minimum": 0, 
            "maximum": 10,
            "default": 0 
          }
        }
      }
    }
  }
}
```

---

## 3. Ejemplo Canónico Completo: Personaje "Knight Hero"

El siguiente ejemplo demuestra un archivo `knight_hero.anim.json` completamente válido y funcional:

```json
{
  "version": "gf-anim-v1",
  "metadata": {
    "id": "knight_hero",
    "display_name": "Caballero Forjador",
    "author": "Agente Arquitecto",
    "rig_type": "hybrid",
    "description": "Guerrero con espada corta y armadura ligera de placas",
    "tags": ["player", "melee", "humanoid"]
  },
  "texture": {
    "image_path": "knight_hero_atlas.png",
    "width": 512,
    "height": 512,
    "format": "RGBA"
  },
  "frames": [
    {
      "id": "idle_0",
      "rect": [0, 0, 32, 36],
      "pivot": [16, 36],
      "duration_ms": 150,
      "sockets": {
        "hand_right": [20, 22],
        "head": [16, 8],
        "cast_point": [24, 18],
        "shadow": [16, 36]
      },
      "hurtboxes": [
        [-10, -34, 20, 32]
      ],
      "hitboxes": [],
      "events": []
    },
    {
      "id": "idle_1",
      "rect": [32, 0, 32, 36],
      "pivot": [16, 36],
      "duration_ms": 150,
      "sockets": {
        "hand_right": [20, 23],
        "head": [16, 9],
        "cast_point": [24, 19],
        "shadow": [16, 36]
      },
      "hurtboxes": [
        [-10, -33, 20, 31]
      ],
      "hitboxes": [],
      "events": []
    },
    {
      "id": "walk_0",
      "rect": [64, 0, 32, 36],
      "pivot": [16, 36],
      "duration_ms": 120,
      "sockets": {
        "hand_right": [22, 22],
        "head": [16, 8],
        "cast_point": [26, 18],
        "shadow": [16, 36]
      },
      "hurtboxes": [
        [-10, -34, 20, 32]
      ],
      "hitboxes": [],
      "events": [
        { "name": "play_sfx", "payload": { "sfx_id": "footstep_stone", "volume": 0.4 } },
        { "name": "spawn_particle", "payload": { "type": "dust_step", "offset": [0, 0] } }
      ]
    },
    {
      "id": "attack_slash_0",
      "rect": [96, 0, 48, 38],
      "pivot": [20, 38],
      "duration_ms": 80,
      "sockets": {
        "hand_right": [12, 18],
        "head": [20, 10],
        "cast_point": [28, 16],
        "shadow": [20, 38]
      },
      "hurtboxes": [
        [-10, -34, 22, 32]
      ],
      "hitboxes": [],
      "events": [
        { "name": "play_sfx", "payload": { "sfx_id": "sword_swing_light" } }
      ]
    },
    {
      "id": "attack_slash_1",
      "rect": [144, 0, 54, 40],
      "pivot": [20, 40],
      "duration_ms": 100,
      "sockets": {
        "hand_right": [36, 20],
        "head": [20, 10],
        "cast_point": [42, 16],
        "shadow": [20, 40]
      },
      "hurtboxes": [
        [-8, -34, 22, 32]
      ],
      "hitboxes": [
        {
          "rect": [4, -28, 36, 26],
          "damage": 15.0,
          "knockback_force": 140.0,
          "hitstun_duration_s": 0.25,
          "hit_sound": "sword_hit_flesh"
        }
      ],
      "events": [
        { "name": "spawn_particle", "payload": { "type": "slash_spark", "offset": [22, -14] } },
        { "name": "screen_shake", "payload": { "trauma": 0.15 } }
      ]
    },
    {
      "id": "attack_slash_2",
      "rect": [198, 0, 40, 36],
      "pivot": [20, 36],
      "duration_ms": 120,
      "sockets": {
        "hand_right": [30, 24],
        "head": [20, 10],
        "cast_point": [32, 20],
        "shadow": [20, 36]
      },
      "hurtboxes": [
        [-10, -34, 20, 32]
      ],
      "hitboxes": [],
      "events": []
    }
  ],
  "clips": {
    "idle": {
      "frames": ["idle_0", "idle_1"],
      "loop": true,
      "playback_speed": 1.0,
      "interrupt_priority": 0
    },
    "walk": {
      "frames": ["walk_0", "idle_0"],
      "loop": true,
      "playback_speed": 1.0,
      "interrupt_priority": 0
    },
    "attack": {
      "frames": ["attack_slash_0", "attack_slash_1", "attack_slash_2"],
      "loop": false,
      "playback_speed": 1.0,
      "interrupt_priority": 3
    }
  }
}
```

---

## 4. Estrategia de Conversión desde Herramientas Externas

### 4.1 Importación desde Aseprite JSON
Aseprite exporta habitualmente en formato `json-array` o `json-hash`:
- **Frames:** Los rectángulos `frame.x, frame.y, frame.w, frame.h` se copian directamente a `rect`.
- **Duraciones:** Aseprite almacena `duration` en milisegundos (`duration_ms = frame.duration`).
- **Tags:** Los `meta.frameTags` de Aseprite (`{ "name": "walk", "from": 0, "to": 3, "direction": "forward" }`) se transforman automáticamente en entradas de `clips` en `gf-anim-v1`.
- **Slices:** Los cortes definidos en Aseprite con nombre `hitbox` o `hurtbox` se convierten en las respectivas listas geométricas por fotograma.

### 4.2 Importación desde `rsheet` (`frame_coords.txt` + `frame_norm_cache.txt`)
- `rsheet.sprite_editor` produce una tupla por animación con rectángulos detectados automáticamente.
- El importador `tools/convert_rsheet_to_gf.py`:
  1. Lee las coordenadas detectadas de `frame_coords.txt`.
  2. Lee los desplazamientos calculados en `frame_norm_cache.txt`.
  3. Establece el pivote como centro-inferior: $[w / 2, h]$.
  4. Genera los clips correspondientes con duración por defecto de 100 ms por fotograma.

### 4.3 Importación desde `PySpine` (`sprite_project.json` + `bone_animation.json`)
- Para proyectos que utilicen el rig esquelético cut-out de PySpine:
  1. Cada imagen individual recortada se mapea como un sub-sprite.
  2. Las matrices de traslación/rotación de huesos se evalúan y hornean (*bake*) en fotogramas secuenciales rasterizados, o se exportan como piezas con sockets relativos al hueso padre.

---

## 5. Reglas de Validación y Consistencia para Agentes

Cualquier archivo de animación generado por un agente debe superar la siguiente batería de validaciones antes de ser aceptado en el repositorio (verificadas por `tools/validate_character.py`):

1. **Existencia de Textura:** La ruta indicada en `texture.image_path` debe existir en el disco relativo al archivo JSON.
2. **Dimensiones del Atlas:** Ningún fotograma (`rect`) puede exceder los límites `[0, 0, texture.width, texture.height]`.
3. **Pivote Válido:** El pivote no debe ser nulo y debe estar situado preferentemente en el contacto con el suelo.
4. **Integridad Referencial de Clips:** Todo identificador de fotograma referenciado en un clip debe existir en la lista `frames`.
5. **No Vacuidad de Clips Mandatorios:** Todo personaje jugable o enemigo debe implementar como mínimo los clips: `idle`, `walk`, `hurt`, `die`.
6. **Consistencia de Cajas:** Las `hurtboxes` y `hitboxes` deben tener anchos y altos estrictamente positivos ($w > 0, h > 0$).

# GRAPHICS_AND_ASSETS_PIPELINE.md — GAMEFORGE 2D
## Pipeline de Gráficos, Mapas, Animaciones y Recursos Multimedia

**Estado:** ESPECIFICACIÓN ARQUITECTÓNICA Y DE PIPELINE  
**Misión:** MISIÓN 006 — Investigación e Integración de Herramientas para Desarrollo 2D  
**Fecha:** 2026-11-07  
**Autor:** Director de Tecnología / Agente de Arquitectura e Integración  
**Proyecto:** GameForge 2D (RPG Modular en Python / Pygame CE)  

---

## 1. Visión y Alcance del Pipeline Multimedia 2D

El pipeline de recursos multimedia de GameForge 2D tiene como propósito transformar assets en bruto (gráficos pixel art, bocetos, archivos Tiled, audio sin procesar) en estructuras de datos optimizadas, validadas y listas para su consumo inmediato por el motor de Pygame CE a 60 FPS estables.

El sistema se rige por tres pilares inviolables:
1. **Automatización Headless para Agentes:** Los agentes de programación deben ser capaces de procesar, empaquetar, validar y convertir recursos sin necesidad de abrir interfaces gráficas.
2. **Cero Dependencias Pesadas en Runtime:** El juego final solo lee formatos estándar (PNG, JSON, OGG, WAV). Todo el procesamiento complejo se realiza en tiempo de empaquetado (*asset bake time*) mediante herramientas de desarrollo (`tools/`).
3. **Trazabilidad Absoluta de Licencias:** Ningún recurso entra al juego sin verificación estricta de procedencia, autoría y licencia permisiva conforme al sistema de `tools/asset_hub/` y `LICENSE_PROVENANCE_SYSTEM.md`.

```
┌────────────────────────────────────────────────────────────────────────┐
│               PIPELINE MULTIMEDIA Y DE ASSETS (GAMEFORGE 2D)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────┐
    ▼                                                               ▼
┌───────────────────────────────────┐               ┌───────────────────────────────────┐
│        PIPELINE GRÁFICO 2D        │               │         PIPELINE DE AUDIO         │
└─────────────────┬─────────────────┘               └─────────────────┬─────────────────┘
                  │                                                   │
  ┌───────────────┴───────────────┐                   ┌───────────────┴───────────────┐
  ▼                               ▼                   ▼                               ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Sprites/Atlas    │    │ Mapas / Niveles  │    │ SFX Procedural   │    │ Música / Pistas  │
│ Pillow + rsheet  │    │ Tiled Map Editor │    │ pyfxr / Síntesis │    │ FFmpeg Batch     │
│ (Empaquetado)    │    │ (JSON Nativo)    │    │ (WAV PCM 16-bit) │    │ (OGG Vorbis)     │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │                       │
         └───────────────┬───────┴───────────────────────┴───────────────────────┘
                         ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                    PUERTAS DE CALIDAD Y VALIDACIÓN                        │
│   - tools/validate_character.py (gf-anim-v1)                              │
│   - tools/asset_hub/validator.py (Esquemas, Hashes SHA-256)               │
│   - tools/asset_hub/hasher.py (Detección de duplicados y licencias)       │
└────────────────────────────────────┬──────────────────────────────────────┘
                                     ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     ASSETS LISTOS PARA RUNTIME (assets/)                  │
│       Texturas PNG optimizadas + Manifiestos JSON + Audio OGG/WAV         │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Roles y Separación de Responsabilidades

| Tipo de Tarea | Responsable | Herramientas Utilizadas | Entregable Producido |
|:---|:---|:---|:---|
| **Creación Artística Manual** | Artista Humano / Diseñador | LibreSprite / Tiled / Krita | Archivos fuente `.ase`, `.tmx`, `.psd` |
| **Generación Procedural** | Agente de IA | Scripts Python + Pillow | Variaciones de personajes, sprites generados |
| **Empaquetado de Atlas** | Agente de IA | Pillow (Algoritmo MaxRects) | Spritesheet `.png` + Atlas `.json` |
| **Validación de Animación**| Agente de IA | `tools/validate_character.py` | Certificado de conformidad `gf-anim-v1` |
| **Conversión de Audio** | Agente de IA | FFmpeg CLI | Archivos normalizados `.ogg` / `.wav` |
| **Registro de Licencias** | Agente de IA | `tools/asset_hub` CLI | Registro en SQLite y `assets/README.md` |

---

## 3. Pipeline de Sprites y Animaciones por Fotogramas

### 3.1. Formato de Animación Estándar: `gf-anim-v1`
GameForge 2D utiliza el formato canónico `gf-anim-v1`, auditado y verificado por la herramienta `tools/validate_character.py`.

#### Requisitos Obligatorios del Manifiesto:
- **Estructura Raíz:** Objeto JSON con campos `version` ("gf-anim-v1"), `metadata`, `texture`, `rig` y `clips`.
- **Clips Obligatorios:** Todo personaje debe contener como mínimo los cuatro clips esenciales: `"idle"`, `"walk"`, `"hurt"` y `"die"`.
- **Límites de Fotogramas:** Cada fotograma define `[x, y, w, h]`; la herramienta valida que ningún fotograma exceda las dimensiones físicas de la textura (`tex_w`, `tex_h`).
- **Puntos de Anclaje (*Origin / Anchor*):** Cada clip especifica un origen normalizado (e.g. `[0.5, 0.9]` para los pies del personaje), asegurando alineación matemática perfecta con la posición espacial 2D del cuerpo físico.

### 3.2. Evaluación de Animación Esquelética vs. Fotogramas (Frame-by-Frame)
Se investigaron alternativas de animación esquelética 2D (Spine / PySpine, DragonBones):
- **PySpine / DragonBones:** Permiten interpolación continua de huesos y reducción de memoria en sprites de alta resolución. Sin embargo, en el contexto de un RPG de estética pixel art retro (16x16 / 32x32 píxeles):
  - La rotación y escalado de píxeles produce artefactos visuales severos (*pixel distortion*, rotación no afín a la cuadrícula).
  - Las dependencias de runtime añaden complejidad masiva de matrices y shaders.
- **Conclusión Técnica:** Para GameForge 2D se adopta **animación por fotogramas clásica (*frame-by-frame*)** combinada con **diseño modular por capas (*paperdoll / dicing*)**, lo que garantiza estética pixel art pura y rendimiento instantáneo en Pygame CE sin coste de CPU en deformaciones de huesos.

### 3.3. Empaquetador Automatizado de Spritesheets (Texture Packer con Pillow)
Para optimizar el uso de memoria y minimizar el número de cambios de textura en Pygame CE, los agentes utilizan un script de empaquetado basado en Pillow y el algoritmo de empaquetado MaxRects / Shelf:
1. Toma una colección de fotogramas PNG individuales.
2. Calcula la disposición óptima reduciendo el desperdicio de espacio (*packing efficiency > 85%*).
3. Exporta una única textura compuesta en PNG con canal alfa RGBA.
4. Genera automáticamente el manifiesto JSON con las coordenadas UV de cada sub-sprite.

---

## 4. Pipeline de Mapas y Niveles (Tiled Map Editor)

### 4.1. Flujo de Autoría y Exportación
1. El diseñador edita el nivel en **Tiled Map Editor** utilizando capas estandarizadas:
   - `ground`: Capa base de suelo (hierba, tierra, baldosas).
   - `walls`: Capa de muros y obstáculos (sólidos).
   - `decorations`: Capa superficial de detalle (antorchas, grietas).
   - `objects`: Capa de objetos con spawns de jugador, cofres, altares y NPCs.
2. Se exporta directamente a formato JSON estándar (`mapa.json`), sin utilizar formatos binarios cerrados.

### 4.2. Ingesta Nativa en el Motor (`game.world.tiled_loader`)
GameForge no requiere `pytmx` ni librerías de terceros. La función `load_tiled_json()` realiza la ingesta directa:
- Mapea los GIDs de Tiled a enumeraciones nativas `TileType` (`WALL`, `FLOOR`, `WATER`, `LAVA`) mediante `DEFAULT_GID_MAP`.
- Extrae la coordenada obligatoria de `spawn` y opcionales de `altar`, `campfire` y `chests`.
- Instancia objetos estructurados inmutables `NpcSpec` para cada NPC detectado en la capa de objetos, incluyendo sus propiedades personalizadas de diálogo y rol.
- Convierte la matriz de tiles en un objeto nativo `TileMap`, el cual se acopla inmediatamente al sistema de colisiones espaciales `SpatialHash` del juego.

---

## 5. Procesamiento y Transformación Automatizada de Imágenes con Pillow

Los agentes de programación utilizan scripts headless de Pillow (`tools/`) para realizar transformaciones deterministas por lotes:

### 5.1. Reemplazo de Paletas por Código (*Color Swapping*)
Permite multiplicar la variedad visual de enemigos y equipamiento a partir de un único sprite base:
```python
def swap_palette(image: Image.Image, color_map: dict[tuple, tuple]) -> Image.Image:
    """Reemplaza colores clave en memoria preservando el canal alfa."""
    img = image.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0 and (r, g, b) in color_map:
                nr, ng, nb = color_map[(r, g, b)]
                pixels[x, y] = (nr, ng, nb, a)
    return img
```

### 5.2. Generación Procedural de Contornos (*Outlines*)
Permite añadir un borde de 1 píxel a objetos seleccionados o enemigos destacados para mejorar la legibilidad visual sin requerir dibujado a mano.

### 5.3. Escalado Estricto de Pixel Art (*Nearest-Neighbor Resampling*)
Para cambiar la escala de assets preservando la nitidez de los píxeles (sin el desenfoque bilineal común de suites estándar):
```python
scaled = img.resize((w * 2, h * 2), resample=Image.Resampling.NEAREST)
```

---

## 6. Pipeline de Audio y Efectos Sonoros

### 6.1. Síntesis Procedural de Audio para Agentes (`pyfxr`) — POSPUESTO
`pyfxr` (https://github.com/lordmauve/pyfxr) es una biblioteca de síntesis en Cython, **BSD-3-Clause**, con última versión **0.3.0 (abril 2021)**. Su API verificada en la documentación oficial es:
- `pyfxr.SFX(**params)`: efectos estilo sfxr parametrizables y serializables a JSON/dict.
- `pyfxr.tone(...)`: tonos seno/cuadrada/sierra/triángulo con envolvente ADSR.
- `pyfxr.pluck(...)`: cuerdas pulsadas (Karplus-Strong).
- Presets como `pyfxr.explosion()` y `pyfxr.jump()`; `SoundBuffer.save(path)` exporta WAV de 44,1 kHz mono.
- Requiere configurar el mezclador de Pygame a 44,1 kHz mono (`pygame.mixer.pre_init(44100, channels=1)`).

**Motivo de la postergación:** no hay evidencia de wheels para Python 3.14 ni de mantenimiento desde 2021, y el proyecto no debe compilar Cython para una capacidad accesoria. Mientras tanto, los agentes pueden generar WAV deterministas con el módulo estándar `wave` (sin dependencias) o convertir con FFmpeg.

### 6.2. Procesamiento Automatizado con FFmpeg CLI
Para archivos de audio existentes o capturas externas, se ejecuta una receta estandarizada de tres pasos mediante FFmpeg:

1. **Recorte de Silencios Iniciales y Finales:**
   Elimina la latencia de ataque del efecto sonoro para que suene instantáneamente al pulsar el botón:
   ```bash
   ffmpeg -i sfx_raw.wav -af "silenceremove=start_periods=1:start_threshold=-50dB" sfx_trimmed.wav
   ```

2. **Normalización Estándar de Sonoridad (EBU R128 / ITU-R BS.1770-4):**
   Asegura que ningún efecto de sonido ensordezca al jugador ni quede inaudible:
   ```bash
   ffmpeg -i sfx_trimmed.wav -af "loudnorm=I=-14:LRA=7:tp=-1.5" sfx_norm.wav
   ```

3. **Codificación a Formatos Óptimos de Runtime:**
   - **Efectos de Sonido Cortos (< 2 s):** Exportados a **WAV PCM sin compresión**, cargados en memoria RAM para latencia de reproducción cero.
   - **Música de Fondo y Pistas Largas (> 5 s):** Codificados en **OGG Vorbis** (`-c:a libvorbis -q:a 4`), permitiendo streaming eficiente desde disco sin saturar la memoria.

---

## 7. Puertas de Calidad, Integridad y Trazabilidad de Licencias

Todo recurso multimedia procesado debe atravesar obligatoriamente las tres puertas de control de `tools/asset_hub`:

1. **Puerta de Integridad (Hash SHA-256):**
   - El archivo se procesa mediante `tools/asset_hub/hasher.py`.
   - Si el hash coincide con un asset existente, se detecta duplicación y se cancela la ingesta para ahorrar espacio.
2. **Puerta de Validación de Metadatos:**
   - Se valida el esquema JSON del manifiesto contra la especificación correspondiente.
   - Se verifica que las dimensiones sean múltiplos de 16 (16x16, 32x32, 64x64) o coincidan con el diseño de rejilla.
3. **Puerta de Licencia y Atribución:**
   - El asset debe declarar una licencia compatible: `CC0-1.0`, `MIT`, `CC-BY-3.0`, `CC-BY-4.0` o `OGA-BY-3.0`.
   - Se registra automáticamente el autor, URL de origen y requerimiento de atribución en `assets/README.md` y `CREDITS.md`.

---

## 8. Recetas de Automatización y Comandos CLI para Agentes

```bash
# 1. Validar un manifiesto de animación de personaje:
python tools/validate_character.py assets/sprites/characters/player/metadata.json

# 2. Empaquetar y registrar un nuevo asset en el Asset Hub:
python -m tools.asset_hub scan assets/incoming/ --author "Kenney" --license "CC0"

# 3. Exportar un asset procesado listo para el juego:
python -m tools.asset_hub export --id char_warrior_01 --out assets/sprites/warrior.png

# 4. Normalizar y convertir un efecto de sonido con FFmpeg:
ffmpeg -y -i raw_sfx.wav -af "silenceremove=start_periods=1:start_threshold=-50dB,loudnorm=I=-14:LRA=7:tp=-1.5" -c:a libvorbis -q:a 4 assets/audio/sfx_normalized.ogg
```

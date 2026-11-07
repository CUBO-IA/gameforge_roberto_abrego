# SPRITE_PIPELINE_RESEARCH.md — GAMEFORGE 2D
## Investigación Integral del Pipeline de Sprites, Texturas y Atlas

**Estado:** APROBADO PARA DISEÑO ARQUITECTÓNICO  
**Misión:** MISIÓN 002 — Sprites, Animaciones y Lógica de Personajes  
**Fecha:** 2026-11-07  
**Motor de Renderizado Objetivo:** Python 3.11+ / pygame-ce (v2.5+)  

---

## 1. Resumen Ejecutivo

El pipeline de sprites de **GameForge 2D** debe resolver un dilema fundamental: permitir que agentes de IA y desarrolladores introduzcan nuevos personajes, variantes de equipamiento y animaciones sin fricción manual, manteniendo un rendimiento estricto de **60 FPS estables (presupuesto < 16.67 ms por frame)** en hardware modesto sin GPU dedicada.

Tras investigar a fondo herramientas del ecosistema como **rsheet**, **Aseprite CLI**, **TexturePacker**, **PySpine** y las capacidades nativas de **pygame-ce**, este documento define la estrategia definitiva para:
1. Ingesta y limpieza automatizada de hojas de sprites sin rejillas rígidas.
2. Empacado óptimo de atlas con eliminación de márgenes transparentes (*trimming*) y extrusión para evitar *texture bleeding*.
3. Normalización espacial de pivotes (anclaje al suelo) para erradicar el *sprite jittering*.
4. Arquitectura de capas modulares (*modular paperdoll*) para variantes y equipamiento.
5. Carga y consumo de memoria en tiempo de ejecución con **cero dependencias pesadas** en el cliente de juego.

---

## 2. Análisis Exhaustivo de Herramientas y Repositorios

### 2.1 `rsheet` (ELiijah-dev, PyPI v0.1.1, MIT)
`rsheet` es una biblioteca orientada a desacoplar el procesamiento geométrico de las hojas de sprites del bucle de juego.
- **Remoción de Fondo (`cached_removed_bg`)**:
  - *Mecanismo:* Analiza los bordes exteriores de la imagen, aplica clustering K-Means para inferir los colores dominantes del fondo y realiza un *flood-fill* conexo (utilizando `scipy.ndimage` y `numpy`) respetando la silueta del personaje.
  - *Evaluación:* Superior al simple *colorkey* de esquina cuando el sprite presenta ruido de anti-aliasing o gradientes leves. Produce una imagen PNG con canal alfa limpio y la almacena en caché junto al archivo original.
- **Detección Geométrica de Fotogramas (`sprite_editor.process_project`)**:
  - *Mecanismo:* Trata el spritesheet como una matriz de densidad de píxeles no transparentes. Detecta filas de píxeles contiguos (animaciones) y columnas dentro de cada fila (fotogramas). No asume una cuadrícula fija regular ($W \times H$).
  - *Evaluación:* Vital para agentes autónomos. Permite que un agente ingiera spritesheets con espaciados irregulares generados por artistas o herramientas generativas sin intervención humana.
- **Normalización de Puntos de Apoyo (`load_or_compute_norm_cache`)**:
  - *Mecanismo:* Calcula el centro inferior (*bottom-center*) de la masa de píxeles del personaje para cada fotograma y calcula los desfases $(\Delta w, \Delta h)$ respecto al fotograma más grande.
  - *Evaluación:* Resuelve el problema clásico de "pies flotantes" o vibración vertical cuando un personaje cambia de tamaño al levantar una espada o saltar.
- **Overhead y Dependencias**:
  - `rsheet` requiere `numpy`, `Pillow`, `scipy` y `pygame`.
  - *Dictamen para GameForge 2D:* **Excelente como herramienta offline / agent tool**. No debe importarse en el ejecutable final del juego para evitar incluir `scipy` (que añade más de 60 MB al paquete distribuible). Los cálculos de corte y normalización se exportan a metadatos JSON pre-horneados.

### 2.2 `PySpine` (SaxonRah, GitHub, MIT)
- Herramienta gráfica modular basada 100% en Python y Pygame para rigging 2D y recorte de spritesheets (`PySpine_SpriteSheetEditor.py`).
- Implementa selección rectangular interactiva de regiones, ajuste de pivotes y exportación a `sprite_project.json`.
- *Lección aprendida:* La separación entre el slicing de sprites y el acoplamiento a huesos/sockets es limpia y directamente transferible a nuestro formato de manifiesto.

### 2.3 Aseprite CLI / Formato JSON Estándar
- El exportador de línea de comandos de Aseprite (`aseprite -b sprite.aseprite --sheet atlas.png --data atlas.json --format json-array --list-tags --list-slices`) es el estándar de oro en la industria del pixel art.
- Ventajas: Exporta duración en milisegundos por fotograma individual, etiquetas de animación (*tags* con dirección forward/reverse/pingpong), y *slices* (usados como pivotes o cajas de colisión).
- *Dictamen:* GameForge 2D adoptará total compatibilidad hacia atrás con el esquema JSON de Aseprite, permitiendo importar directamente salidas de Aseprite sin pasos intermedios.

### 2.4 TexturePacker & Algoritmo MaxRects
- Algoritmo *Maximal Rectangles (MaxRects)*: Permite empacar rectángulos de diferentes proporciones en un atlas cuadrado de potencia de 2 ($2^N \times 2^N$) con un índice de ocupación de área superior al 88-94%.
- Soporta *Trimming* (recorte de píxeles transparentes redundantes) y *Extrusion* (duplicación de 1 píxel perimetral para evitar sangrado en escalado).
- *Dictamen:* Se incluirá un empacador MaxRects en Python puro dentro de `tools/` para que los agentes construyan atlas optimizados sin depender de software comercial.

---

## 3. Importación y Organización de Spritesheets

### 3.1 Estructura del Sistema de Archivos
Para mantener el desacoplamiento de datos y código, los recursos gráficos se organizan bajo `assets/sprites/`:

```
assets/
└── sprites/
    ├── characters/
    │   └── player/
    │       ├── base/
    │       │   ├── player_base_atlas.png
    │       │   └── player_base_manifest.json
    │       └── skins/
    │           └── golden_knight/
    │               ├── golden_knight_atlas.png
    │               └── golden_knight_manifest.json
    ├── equipment/
    │   ├── weapons/
    │   │   ├── iron_sword_atlas.png
    │   │   └── iron_sword_manifest.json
    │   └── armor/
    ├── enemies/
    │   ├── goblin_scout/
    │   │   ├── goblin_scout_atlas.png
    │   │   └── goblin_scout_manifest.json
    │   └── necromancer/
    └── vfx/
        ├── combat_sparks_atlas.png
        └── explosions_atlas.png
```

### 3.2 Formato Fuente y Especificaciones Gráficas
1. **Canal de Color:** Formato PNG de 32 bits (RGBA no comprimido o compresión PNG estándar sin pérdidas).
2. **Premultiplicación Alfa:** No premultiplicado en disco (Pygame-ce procesa canal alfa recto `SRCALPHA`).
3. **Márgenes de Seguridad:** Mínimo 1 píxel transparente perimetral por fotograma dentro del atlas (o 1px extrudido si se utiliza escalado bilineal en el lienzo virtual).

---

## 4. Extracción de Fotogramas y Empacado de Atlas

### 4.1 Rejilla Uniforme vs. Empacado Atléico Irregular
| Característica | Rejilla Fija ($32 \times 32$) | Atlas Empacado (MaxRects + Trimming) |
|---|---|---|
| **Consumo VRAM** | Alto (almacena grandes vacíos transparentes) | Mínimo (hasta un 40-60% menos de memoria) |
| **Complejidad del Loader** | Trivial ($O(1)$ matemática modular) | Requiere parseo de rectángulos desde JSON |
| **Flexibilidad de Animación** | Rígida (ataques largos quedan cortados) | Total (cada fotograma tiene su tamaño real) |
| **Pivotes** | Implícitos (centro o centro-inferior de la celda) | Explícitos por fotograma |
| **Elección GameForge** | Soportado para retrocompatibilidad | **Estándar Primario Recomendado** |

### 4.2 Algoritmo de Detección Automática de Islas de Píxeles
Para spritesheets importados sin archivo de metadatos (e.g. descargas de itch.io o generados por agentes):
1. **Binarización:** Convertir la imagen a una máscara booleana donde `alpha > umbral_alfa` (típicamente alfa > 10).
2. **Componentes Conexos (8-conectividad):**
   - Agrupar píxeles contiguos no vacíos.
   - Filtrar motas de ruido con área $< 4$ píxeles.
3. **Cálculo de Bounding Boxes:** Obtener $[x_{min}, y_{min}, x_{max}, y_{max}]$ de cada isla.
4. **Clasificación por Filas:**
   - Agrupar cajas cuyos centros verticales disten menos de $\Delta Y_{tol}$ (determinando una animación).
   - Ordenar las cajas de cada fila de izquierda a derecha (secuencia temporal de fotogramas).
5. **Cálculo de Pivote:** Anclaje en la base $X_{pivote} = \frac{x_{min} + x_{max}}{2}$, $Y_{pivote} = y_{max}$.

---

## 5. Gestión de Memoria y Rendimiento en pygame-ce

### 5.1 Subsurface vs. Copia Profunda
Pygame implementa `pygame.Surface.subsurface(rect)` compartiendo el búfer de píxeles original en C (`SDL_Surface*`):

```python
# Carga del atlas maestro en memoria
atlas_surface = pygame.image.load("player_atlas.png").convert_alpha()

# Subsurface: CERO asignación de memoria adicional de píxeles
frame_surf = atlas_surface.subsurface(pygame.Rect(x, y, w, h))
```

- **Ventajas de `subsurface`:**
  - Creación casi instantánea (solo asigna un wrapper Python/C de ~64 bytes).
  - Cero duplicación de memoria gráfica.
  - Excelente para caché L2/L3 de CPU al mantener la textura contigua en memoria.
- **Cuándo realizar `.copy()` obligatoriamente:**
  - Si el fotograma necesita modificaciones dinámicas por pixel (e.g., tintado destructivo, flash blanco con máscaras, o si la superficie padre debe ser liberada).
  - Si se aplica `pygame.transform.flip()` o `scale()`, la función ya devuelve una nueva superficie independiente.

### 5.2 Regla Obligatoria `.convert()` / `.convert_alpha()`
Según la directiva de rendimiento de `AGENTS.md`:
- Toda imagen cargada mediante `pygame.image.load()` debe ser convertida **inmediatamente después de inicializar la ventana de despliegue**:
  ```python
  if has_per_pixel_alpha:
      surface = surface.convert_alpha()
  else:
      surface = surface.convert()
      surface.set_colorkey(colorkey)
  ```
- Si no se ejecuta `.convert_alpha()`, cada llamada a `surface.blit()` fuerza a la CPU a realizar una conversión de formato de píxeles al vuelo en cada frame, desplomando los FPS de 60 a menos de 20 con más de 30 entidades simultáneas.

### 5.3 Presupuesto de Memoria RAM/VRAM
- Una superficie RGBA de $2048 \times 2048$ píxeles ocupa exactamente:
  $$2048 \times 2048 \times 4 \text{ bytes} = 16\,777\,216 \text{ bytes} \approx 16 \text{ MB}$$
- Para GameForge 2D, con un presupuesto total de memoria de assets de **< 128 MB**:
  - Atlas de Jugador + Equipamiento: 1 atlas de $1024 \times 1024$ (4 MB).
  - Atlas de Enemigos del piso actual: 2 atlas de $1024 \times 1024$ (8 MB).
  - Atlas de Tilesets del piso actual: 1 atlas de $1024 \times 1024$ (4 MB).
  - Atlas de Efectos e Interfaz: 1 atlas de $1024 \times 1024$ (4 MB).
  - **Total de Texturas Activas en Bucle de Juego:** $\approx 20 \text{ MB}$, muy por debajo del límite, garantizando fluidez en PCs con gráficos integrados Intel HD Graphics o Raspberry Pi 4.

---

## 6. Pivotes, Puntos de Anclaje y Normalización Espacial

### 6.1 El Problema del Sprite Jittering
Cuando un personaje ejecuta una animación donde el tamaño del dibujo cambia (e.g. un golpe donde la espada estira el ancho de 32 a 48 píxeles), posicionar el sprite usando la esquina superior izquierda `(top_left)` produce una vibración artificial (*jittering*) donde el cuerpo entero se desplaza.

### 6.2 Normalización Anclada al Suelo (*Ground Anchor*)
Para juegos 2.5D y vista cenital (*top-down*), el punto invariante físico de la entidad es el contacto de sus pies con el suelo en el plano $(x, y)$:
- Coordenadas de Pivote Normalizadas: $(\hat{u}, \hat{v}) = (0.5, 1.0)$
- Posición en pantalla para el renderizado:
  $$\text{render\_x} = \text{world\_screen\_x} - \text{pivot\_x}$$
  $$\text{render\_y} = \text{world\_screen\_y} - \text{pivot\_y} - z$$
  *(donde $z$ es la altura del salto 2.5D)*.

### 6.3 Puntos de Anclaje Secundarios (*Sockets / Mounts*)
Cada fotograma del manifiesto puede definir una colección de *sockets* para anclaje de equipamiento y emisión:
```json
"sockets": {
  "hand_right": [22, 18],
  "hand_left": [10, 18],
  "head": [16, 6],
  "cast_point": [28, 14],
  "shadow_center": [16, 30]
}
```
Esto permite que:
- El arma equipada se posicione automáticamente en `hand_right` del fotograma actual, rotándose según el ángulo de ataque.
- Los proyectiles se generen exactamente en `cast_point`.
- El sombrero o casco se posicione en `head`.

---

## 7. Variantes de Personajes y Equipamiento (Modular Paperdoll)

### 7.1 Arquitectura Multicapa
El sistema de personajes modular separa la entidad en capas ordenadas por profundidad (*Z-order* local):

```
[Capa 0: Sombra del Personaje] (draw_shadow)
[Capa 1: Capa / Espalda]
[Capa 2: Cuerpo Base / Piel]
[Capa 3: Pantalones / Botas]
[Capa 4: Pechera / Armadura]
[Capa 5: Cabeza / Rostro]
[Capa 6: Cabello / Casco]
[Capa 7: Mano Principal / Arma]
[Capa 8: Mano Secundaria / Escudo]
[Capa 9: Overlays / Estado (Fuego, Congelación, Veneno)]
```

### 7.2 Sincronización de Capas
- **Estrategia A (Spritesheets Sincronizados):** Todas las capas de equipamiento comparten la misma cantidad de fotogramas, nombres de animación y pivotes que el cuerpo base. El renderizador itera sobre las capas activas y dibuja el mismo `frame_index` correspondiente.
- **Estrategia B (Anclaje por Sockets):** El arma o accesorio es un sprite individual que se traslada y rota en función del socket `hand_right` del frame actual del cuerpo.
- **Decisión de Diseño:**
  - Armaduras y ropa usan **Estrategia A** (máxima fidelidad en pixel art sin distorsión).
  - Armas grandes y escudos usan **Estrategia B** (máxima reusabilidad entre diferentes personajes y orientaciones).

### 7.3 Palette Swapping Eficiente
Para generar variantes de color (e.g., Goblin Verde vs Goblin Rojo Élite):
- En lugar de duplicar texturas en disco, se utiliza una **paleta indexada** o sustitución de color en carga:
  ```python
  def swap_palette(surface: pygame.Surface, color_map: dict[tuple, tuple]) -> pygame.Surface:
      new_surface = surface.copy()
      # pygame.PixelArray bloquea la superficie y permite reemplazos ultrarrápidos en C
      with pygame.PixelArray(new_surface) as px:
          for old_color, new_color in color_map.items():
              px.replace(old_color, new_color)
      return new_surface
  ```
- Este proceso se ejecuta **una sola vez durante la carga del piso** o inicialización del agente, almacenando la superficie modificada en el catálogo de entidades sin coste por fotograma.

---

## 8. Conclusiones y Recomendaciones para la Arquitectura

1. **Separación Estricta:** Las herramientas de procesamiento de imágenes (`rsheet`, `scipy`, `Pillow`) permanecen exclusivamente en el entorno de desarrollo y herramientas de agentes (`tools/`). El motor de juego sólo consume atlas PNG y manifiestos JSON.
2. **Uso de Subsurfaces:** El renderizador utiliza `subsurface()` del atlas cargado con `.convert_alpha()`, maximizando el rendimiento y minimizando la memoria.
3. **Pivotes Mandatorios:** Ningún fotograma se renderiza sin coordenadas de pivote explícitas referenciadas al suelo.
4. **Formato Declarativo Estándar:** GameForge 2D implementará la especificación `gf-anim-v1`, compatible con Aseprite y rsheet, garantizando que los agentes de IA puedan generar paquetes de personajes completos y autónomos.

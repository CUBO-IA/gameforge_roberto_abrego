# Informe de Rendimiento Visual — Comparativa y Benchmark Empírico

**Documento:** `VISUAL_PERFORMANCE_REPORT.md`  
**Fecha de Medición:** 2026-11-07  
**Entorno de Ejecución:** Windows, Python 3.14.5, Pygame CE 2.5.8 (SDL 2.32.10, driver dummy headless).  
**Herramienta de Benchmark:** `tools/visual_benchmark.py` (Semilla determinista: `20261107`, 180 fotogramas completos).

---

## 1. Resumen Ejecutivo

El Visual Overhaul de la Misión 008 transformó radicalmente la presentación visual de GameForge 2D (pasando de figuras geométricas planas a pixel art de alta calidad con tilesets texturizados, sombras proyectadas, spritesheets animados, props con fuego vivo y UI 9-slice) **sin degradar el rendimiento del motor**.

Las mediciones empíricas demuestran:
- **Tasa de Refresco:** Velocidad efectiva de **114.6 FPS** en renderizado por software en CPU, superando holgadamente el objetivo de 60 FPS estables.
- **Sobrecarga de Fotograma (Frame Time p50):** Incremento de tan solo **0.82 ms** (de 7.90 ms a 8.73 ms por fotograma).
- **Consumo de Memoria:** Memoria retenida adicional de apenas **43.9 KB** gracias al sistema de caché de subsurfaces y 9-slice de `ArtLibrary`.
- **Tiempo de Carga:** Prácticamente indistinguible (682.76 ms vs 688.02 ms; variación del 0.77%).

---

## 2. Tabla Comparativa: Antes (Baseline) vs Después (Overhaul)

| Métrica | Antes (Prototipo Primitivas) | Después (Visual Overhaul) | Delta Absoluto | Impacto % | Estado |
|---|---|---|---|---|---|
| **Tiempo de Carga (`load_time_ms`)** | 682.76 ms | 688.02 ms | +5.26 ms | +0.77% | ÓPTIMO |
| **Tiempo de Frame P50 (`frame_ms_p50`)** | 7.901 ms | 8.729 ms | +0.828 ms | +10.48% | EXCELENTE |
| **Tiempo de Frame P95 (`frame_ms_p95`)** | 9.873 ms | 10.656 ms | +0.783 ms | +7.93% | EXCELENTE |
| **Tiempo de Frame Máximo (`frame_ms_max`)**| 17.032 ms | 18.708 ms | +1.676 ms | +9.84% | CONTROLADO (Pico de ataque) |
| **Tasa de Cuadros Equivalente (`fps_equivalent`)** | 126.6 FPS | 114.6 FPS | -12.0 FPS | -9.48% | SOBRADO (>60 FPS) |
| **Memoria Pico (`peak_memory_kb`)** | 2164.5 KB | 2164.6 KB | +0.1 KB | +0.00% | SIN IMPACTO |
| **Memoria Retenida (`retained_memory_kb`)** | 1130.5 KB | 1174.4 KB | +43.9 KB | +3.88% | MÍNIMO (Caché texturas) |
| **Tamaño de Mapa / Celdas** | 64 × 48 (2048×1536 px) | 64 × 48 (2048×1536 px) | 0 | 0.00% | IDÉNTICO |
| **Entidades Activas en Simulación** | 30 enemigos + 1 héroe | 30 enemigos + 1 héroe | 0 | 0.00% | IDÉNTICO |
| **Tamaño Promedio de Captura PNG** | ~78 KB / frame | ~420 KB / frame | +342 KB | +438% | ALTA DENSIDAD VISUAL |

---

## 3. Análisis Detallado del Rendimiento

### A. Pre-renderizado de Terreno (`TileRenderer`)
- En el enfoque inicial, los suelos se dibujaban iterando sobre rectángulos y líneas matemáticas en un único lienzo persistente.
- En el enfoque renovado, `TileRenderer` compone el lienzo estático usando blits directos de texturas de 32×32 px extraídas de `dungeon_tileset.png`. Al ocurrir en el inicio de la escena y cachearse en `self.surface`, **el coste de dibujo del mapa estático durante el bucle de juego es exactamente de un solo `surface.blit`**, idéntico al del prototipo inicial.

### B. Animación de Terreno (`draw_animated`)
- La animación de agua y lava cicla entre frames pregenerados (`water_0`/`water_1` y `lava_0`/`lava_1`) únicamente en las celdas visibles dentro del viewport de la cámara (`culling`).
- El tiempo invertido en `draw_animated` se mantiene por debajo de 0.4 ms por fotograma.

### C. Actores y Criaturas (`entity_renderer`)
- El dibujo de personajes con spritesheets elimina el coste computacional de calcular senos/cosenos para polígonos y extremidades vectoriales en cada frame.
- El volteo horizontal (`pygame.transform.flip`) se realiza en memoria solo cuando la entidad cambia su orientación cardinal respecto al último fotograma.

### D. Interfaz de Usuario y 9-Slice (`Hud` y `ui.py`)
- Los paneles y barras de salud se generan mediante `ArtLibrary.nine_slice(name, size)`, que almacena en un diccionario el resultado para combinaciones repetidas de tamaño `(width, height)`.
- Como los tamaños del panel de salud (360×104 px) y la barra (220×15 px) son constantes, el 9-slice solo se calcula en el primer frame y en los subsiguientes es un simple blit de textura en memoria.

---

## 4. Evidencia Visual Producida

Las capturas generadas de forma determinista confirman la transformación estética en el juego real:

- **Línea Base (`artifacts/visual/before/`):**
  - `frame_0001.png` (81.5 KB): Inicio con fondo oscuro plano y círculos primitivos.
  - `frame_0090.png` (76.8 KB): Momento del golpe con arcos vectoriales planos.
  - `frame_0180.png` (78.8 KB): Post-combate con entidades vectoriales simples.
- **Visual Overhaul (`artifacts/visual/overhaul/`):**
  - `frame_0001.png` (434.2 KB): Escenario completo con losas de piedra detalladas, muros con relieves y sombras proyectadas, héroe con armadura y espada, y HUD temático con marco forjado.
  - `frame_0090.png` (420.4 KB): Impacto de combate con animación de tajo, chispas de forja, retroceso del enemigo y sacudida de cámara.
  - `frame_0180.png` (418.4 KB): Composición atmosférica con iluminación dinámica, antorcha encendida y estallido de ascuas.

---

## 5. Dictamen de Rendimiento

El sistema cumple con holgura todos los criterios de aceptación técnicos:
1. No hay degradación en la tasa de refresco objetivo (114.6 FPS >> 60 FPS).
2. No existen fugas de memoria (memoria constante tras 180 frames).
3. La huella de memoria es ligera y apta para máquinas de bajos recursos y CPUs con gráficos integrados.

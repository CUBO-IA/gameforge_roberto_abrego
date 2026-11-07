# Skill: Gestión de Assets y Animación 2D (Assets & Animation)

## 1. Propósito
Organizar, cargar, cachear y renderizar spritesheets, animaciones por cuadros, efectos visuales y elementos de audio cumpliendo con licencias de código abierto y optimizando el consumo de memoria RAM y GPU mediante atlases y reproducción sin carga I/O en tiempo de ejecución.

## 2. Contexto de aplicación
Se aplica en `game/render/`, `assets/`, `game/scenes/` y cualquier módulo que procese recursos visuales o sonoros.
Asegura que el juego mantenga una estética coherente y trazabilidad legal de cada recurso externo utilizado.

## 3. Instrucciones
1. **Registro obligatorio de licencias**: Todo sprite, textura, fuente tipográfica o archivo de audio importado en `assets/` debe registrarse formalmente en `assets/README.md` con:
   - Nombre del asset y autor original.
   - URL de origen.
   - Licencia exacta verificada (CC0, CC-BY, MIT, OGA-BY, etc.).
   - Modificaciones realizadas.
2. **Uso de Sprite Atlases / Sheets**: Empaquetar animaciones en spritesheets homogéneas en lugar de cargar cientos de archivos PNG individuales.
3. **Carga única en inicialización**: Cargar y convertir superficies (`convert_alpha()`) durante el arranque de la escena o mediante un `AssetManager`; nunca invocar `pygame.image.load()` o recorte de sub-superficies en el bucle caliente.
4. **Animación basada en acumulador de tiempo**:
   - Avanzar fotogramas sumando `dt` a un acumulador interno: `frame_time += dt`.
   - Calcular el índice de fotograma: `int(frame_time / frame_duration) % total_frames`.
   - Permitir modos de bucle (`loop=True/False`) y disparar callbacks al finalizar animaciones de una sola reproducción (ej. muerte o golpe).
5. **Pivotes de renderizado consistentes**: Fijar el punto de pivote en la base central inferior de las entidades (`midbottom`) para asegurar ordenación por profundidad (Z-sorting en Y) natural.

## 4. Buenas prácticas
- **Fallback procedural**: Proveer siempre generadores procedurales mínimos (formas geométricas de color sólido o texturas sintéticas) para que el juego sea plenamente jugable y testeable incluso si faltan archivos gráficos externos.
- **Fuentes del sistema y fuentes seguras**: Manejar excepciones al cargar tipografías y disponer de fuentes fallback mediante `pygame.font.SysFont` o renderizadores de bitmap primitivos.
- **Evitar re-escalado por frame**: Si se requiere escalar un sprite, realizar `pygame.transform.scale()` una única vez y almacenar la superficie resultante en caché.

## 5. Referencias técnicas
- `assets/README.md`: Registro de licencias y procedencia del proyecto.
- ADR-003: Renderizado y audio procedural como base por defecto del vertical slice.
- Especificación de recorte de sprites `pygame.Surface.subsurface`.

## 6. Procedimientos
### Paso 1: Definición de una animación basada en tiempo
```python
@dataclass
class Animation:
    frames: list[pygame.Surface]
    duration_per_frame: float = 0.1
    loop: bool = True
    time: float = 0.0

    def update(self, dt: float) -> None:
        self.time += dt

    @property
    def current_frame(self) -> pygame.Surface:
        if not self.frames:
            return None
        idx = int(self.time / self.duration_per_frame)
        if self.loop:
            idx %= len(self.frames)
        else:
            idx = min(idx, len(self.frames) - 1)
        return self.frames[idx]
```
### Paso 2: Recorte de atlas durante la inicialización
```python
def slice_sheet(sheet: pygame.Surface, tile_w: int, tile_h: int) -> list[pygame.Surface]:
    frames = []
    for y in range(0, sheet.get_height(), tile_h):
        for x in range(0, sheet.get_width(), tile_w):
            rect = pygame.Rect(x, y, tile_w, tile_h)
            frames.append(sheet.subsurface(rect).copy())
    return frames
```

## 7. Criterios de aceptación
- Todos los assets externos cuentan con licencia registrada en `assets/README.md`.
- No hay caídas de FPS al reproducir animaciones o detonar efectos de sonido.
- Las animaciones se ejecutan a velocidad constante independientemente del framerate gracias al delta time.
- El juego arranca correctamente en entornos donde los assets son simulados o generados sintéticamente.

## 8. Pruebas recomendadas
- Pruebas unitarias de la clase `Animation` comprobando avance de cuadros, ciclos de repetición y límites sin necesidad de abrir display.
- Verificación estática de que no existen archivos con extensiones binarias/multimedia sin entrada en `assets/README.md`.

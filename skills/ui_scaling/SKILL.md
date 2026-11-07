# Skill: Escalado de Interfaz y Lienzo Virtual (UI Scaling & Virtual Canvas)

## 1. Propósito
Garantizar una presentación visual nítida y adaptable en múltiples resoluciones y factores de forma mediante el desacoplamiento de la resolución lógica interna de simulación/render (lienzo virtual o render target) de la resolución física de la ventana del sistema operativo, permitiendo escalado con preservación de relación de aspecto (letterboxing/pillarboxing) y mapeo automático de coordenadas de entrada del ratón.

## 2. Contexto de aplicación
Se aplica en `game/render/`, `game/scenes/`, `game/ui/` y `game/app.py`.
Esencial para cumplir el objetivo de "interfaz adaptable" sin que los subsistemas de juego o widgets de interfaz tengan que gestionar transformaciones de coordenadas físicas arbitrarias.

## 3. Instrucciones
1. **Resolución lógica fija (Lienzo virtual)**: Renderizar toda la lógica del mundo, entidades y HUD sobre una superficie `virtual_surface` con resolución lógica de diseño fija (ej. 1280x720 o 640x360).
2. **Escalado final transparente al display**: En el método de presentación final de `game/app.py`, escalar `virtual_surface` a las dimensiones reales de la ventana de Pygame, manteniendo la relación de aspecto y rellenando los bordes excedentes con barras negras (letterboxing).
3. **Mapeo inverso de coordenadas del ratón**: Transformar las coordenadas absolutas de los eventos del ratón (`pygame.MOUSEBUTTONDOWN`, `MOUSEMOTION`) restando los márgenes de letterbox y dividiendo entre el factor de escala antes de enviarlas a las escenas de la interfaz.
4. **Filtro de escalado apropiado**:
   - Para pixel-art clásico: usar `pygame.transform.scale()` (vecino más cercano / nearest neighbor) para mantener bordes nítidos.
   - Para elementos de texto o vectores: utilizar superficies de mayor resolución o filtros suaves cuando se autorice en configuración.
5. **HUD anclado**: Los elementos de interfaz (barras de vida, inventario, minimapa) deben posicionarse usando anclajes relativos a las esquinas o centros de la resolución lógica (`topleft`, `midbottom`, etc.).

## 4. Buenas prácticas
- **Sin consultas directas a `screen.get_size()` en entidades**: Las entidades y sistemas solo conocen las dimensiones de la cuadrícula o del canvas virtual.
- **Evitar recrear la superficie virtual en cada frame**: Instanciar la `virtual_surface` una sola vez y limpiarla con `.fill()` al inicio de cada fotograma.
- **Soporte de pantalla completa sin distorsión**: Permitir alternar entre modo ventana y pantalla completa (`pygame.FULLSCREEN`) sin alterar la lógica interna ni provocar estiramiento anamórfico de la imagen.

## 5. Referencias técnicas
- `architecture/CONTRACTS.md`: Contrato propuesto de `render.canvas`.
- Documentación de Pygame CE: `pygame.transform.scale`, `pygame.Rect`.
- Patrón de Lienzo Virtual para motores 2D retro y modernos.

## 6. Procedimientos
### Paso 1: Cálculo del viewport escalado con letterbox
```python
def calculate_viewport(window_size: tuple[int, int], logical_size: tuple[int, int]) -> tuple[pygame.Rect, float]:
    win_w, win_h = window_size
    log_w, log_h = logical_size
    scale = min(win_w / log_w, win_h / log_h)
    view_w = int(log_w * scale)
    view_h = int(log_h * scale)
    offset_x = (win_w - view_w) // 2
    offset_y = (win_h - view_h) // 2
    return pygame.Rect(offset_x, offset_y, view_w, view_h), scale
```
### Paso 2: Transformación de eventos del ratón a espacio lógico
```python
def map_mouse_to_logical(mouse_pos: tuple[int, int], viewport: pygame.Rect, scale: float) -> tuple[int, int] | None:
    mx, my = mouse_pos
    if not viewport.collidepoint(mx, my):
        return None
    lx = int((mx - viewport.x) / scale)
    ly = int((my - viewport.y) / scale)
    return lx, ly
```
### Paso 3: Renderizado y blit final
```python
# 1. Escena dibuja en canvas virtual
active_scene.draw(virtual_surface)
# 2. App escala canvas virtual y lo plasma en la pantalla real
scaled = pygame.transform.scale(virtual_surface, (viewport.width, viewport.height))
display_screen.fill((0, 0, 0))
display_screen.blit(scaled, viewport.topleft)
pygame.display.flip()
```

## 7. Criterios de aceptación
- La ventana se puede redimensionar o maximizar sin romper la proporción de aspecto visual del juego.
- La interacción con botones del menú e inventario mediante ratón coincide exactamente con el elemento visual bajo cualquier tamaño de ventana.
- Cero degradación del framerate debido al blit de escalado final.

## 8. Pruebas recomendadas
- Pruebas matemáticas unitarias del cálculo de letterbox y transformación de coordenadas del ratón.
- Verificación en resoluciones variadas (1280x720, 1920x1080, pantallas ultrapanorámicas 21:9).

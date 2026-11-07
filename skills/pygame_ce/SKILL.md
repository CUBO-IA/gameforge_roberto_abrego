# Skill: Pygame CE (Community Edition)

## 1. Propósito
Guiar la integración correcta, idiomática y eficiente con el motor Pygame CE (Community Edition), gestionando el ciclo de vida del display, la gestión de superficies y memoria de vídeo, el manejo de eventos y el mezclador de audio sin acoplar la lógica de dominio del juego al framework.

## 2. Contexto de aplicación
Se aplica exclusivamente en la capa de presentación y plataforma:
- `game/app.py`: ciclo principal, reloj y control de eventos globales.
- `game/render/`: dibujado de tiles, entidades, HUD, efectos y fondos.
- `game/input/`: captura y traducción de eventos de hardware a acciones abstractas.
- `game/scenes/`: orquestación de la vista de escenas y llamadas a dibujado.
**Prohibido** importar Pygame en `game/core/`, `game/entities/`, `game/sim/`, `game/world/` o `game/persistence/`.

## 3. Instrucciones
1. Utilizar siempre `pygame-ce >= 2.5` y evitar APIs obsoletas de pygame clásico.
2. Inicializar subsistemas específicos explícitamente (`pygame.display.init()`, `pygame.font.init()`, `pygame.mixer.init()`).
3. Para pruebas y CI sin entorno gráfico, respetar la inicialización con drivers ficticios (`SDL_VIDEODRIVER=dummy` y `SDL_AUDIODRIVER=dummy`).
4. Aplicar `.convert()` a superficies opacas y `.convert_alpha()` a superficies translúcidas inmediatamente después de inicializar la ventana para optimizar el blitting nativo en GPU/RAM.
5. Limitar siempre el framerate mediante `pygame.time.Clock.tick(target_fps)` y calcular `dt` en segundos, aplicando un clamp máximo (p. ej. `min(dt, 0.05)`) para evitar el "espiral de la muerte" tras cuelgues o pérdidas de foco.
6. Nunca realizar I/O bloqueante (lectura de disco no cacheada, red) dentro del bucle de eventos o del ciclo de renderizado.

## 4. Buenas prácticas
- **Carga única y reutilización**: Cargar fuentes, sprites, sonidos y texturas en un paso de inicialización o gestor de recursos; nunca invocar `pygame.image.load()` ni `pygame.font.Font()` por frame.
- **Limpieza de canales de audio**: Asignar canales dedicados a SFX recurrentes y limitar el número de sonidos simultáneos para prevenir saturación del buffer de audio.
- **Canal de eventos centralizado**: Consumir `pygame.event.get()` una sola vez por frame en el ciclo principal y distribuir eventos a la escena activa; nunca llamar a `get()` desde módulos internos o entidades.
- **Superficies temporales**: Evitar crear superficies intermedias volátiles con `pygame.Surface()` en cada fotograma; reutilizar buffers dedicados o renderizar directamente al canvas principal.

## 5. Referencias técnicas
- Documentación oficial de Pygame CE: https://pyga.me/docs/
- Diferencias de API entre Pygame clásico y CE: https://pyga.me/docs/pygame-api-diffs.html
- Arquitectura de renderizado 2D y SDL2 blitting flags.
- ADR-001: Adopción de Pygame CE frente a Pygame estándar y Arcade.

## 6. Procedimientos
### Paso 1: Configuración del modo display
```python
flags = pygame.DOUBLEBUF
screen = pygame.display.set_mode((width, height), flags)
pygame.display.set_caption("GAMEFORGE 2D")
```
### Paso 2: Conversión obligatoria de superficies
```python
surf = pygame.image.load(path).convert_alpha()
```
### Paso 3: Distribución limpia de eventos
```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        app.quit()
    else:
        active_scene.handle_event(event)
```
### Paso 4: Cierre seguro de subsistemas
```python
pygame.mixer.quit()
pygame.display.quit()
pygame.quit()
```

## 7. Criterios de aceptación
- El proyecto arranca, corre y cierra sin fugas de memoria ni errores de SDL.
- Compatible al 100% con modo headless (`python -m game --headless --frames 60` retorna exit code 0).
- 0 llamadas a `pygame` dentro de los módulos de simulación, mundo y entidades.
- Tasa de refresco limitada a 60 FPS estables con tiempo de frame medible.

## 8. Pruebas recomendadas
- `tests/test_headless_app.py`: Verificación del arranque del bucle principal en modo dummy sin colapsos de SDL.
- `tests/test_input.py`: Verificación de la traducción de eventos `pygame.KEYDOWN`/`KEYUP` a acciones de dominio `Action`.

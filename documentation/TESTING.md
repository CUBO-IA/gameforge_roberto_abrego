# Estrategia y resultados de pruebas

## Cómo ejecutar

```bash
python -m pip install -e ".[dev]"
pytest
```

Los tests fuerzan SDL en modo *dummy* desde `tests/conftest.py` antes de
inicializar Pygame. Esto permite probar escenas y renderizado sin ventana real.

## Cobertura funcional

| Área | Archivo | Qué se comprueba |
|---|---|---|
| Configuración | `tests/test_config.py` | defaults, overrides, rangos, JSON inválido |
| Matemáticas | `tests/test_math2d.py` | vectores, ángulos, clamp, solapes |
| Mapa/colisión | `tests/test_collision.py` | paredes, deslizamiento, tunneling, LOS |
| Generación | `tests/test_generation.py` | determinismo, conectividad BFS, cofres, enemigos |
| Inventario | `tests/test_inventory.py` | pilas, capacidad, validación, serialización |
| Objetivo | `tests/test_quest.py` | requisito de fragmentos y activación única |
| Jugador | `tests/test_player.py` | movimiento, agua, paredes, dash, ataque, daño, curación, lava |
| Enemigos | `tests/test_enemies.py` | persecución, disparo con LOS, carga, muerte, separación |
| Combate | `tests/test_combat.py` | arco, alcance, múltiples objetivos, muerte |
| Cámara | `tests/test_camera.py` | límites, suavizado, conversión de coordenadas |
| Entrada | `tests/test_input.py` | acciones, repeat, ratón, reset |
| Guardado | `tests/test_savegame.py` | roundtrip, atomicidad, corrupción, versiones, límites |
| SQLite | `tests/test_scores.py` | registro, orden, empates, persistencia, validación |
| Integración headless | `tests/test_headless_app.py` | app, escenas, guardado/carga, cofre, victoria, muerte, CLI |

## Pruebas de integración

- `Application` se crea con `headless=True` y un directorio temporal.
- Se ejecutan frames reales del bucle (SDL dummy).
- Se dibuja la escena de juego con HUD, inventario y pausa.
- Se guarda desde la escena, se carga y se reconstruye una partida.
- Se fuerza una victoria y una muerte, verificando la transición a resultados,
  el registro en SQLite y la eliminación del guardado.
- Se ejecuta `python -m game --headless --new-game` a través de `main()`.

## Pruebas manuales recomendadas

Las pruebas automáticas no sustituyen una partida completa:

1. Abrir el juego con `python -m game`.
2. Mover, atacar, recibir daño, usar dash y frasco.
3. Abrir un cofre, descansar en la hoguera, guardar con F5.
4. Salir al menú, continuar y comprobar salud/inventario/posición.
5. Recoger tres fragmentos, activar el altar y ver la pantalla de victoria.
6. Consultar la clasificación y reiniciar.

## Resultados

Los resultados de la última ejecución se registran al final del trabajo de
verificación (ver el informe entregado al usuario). No se deben escribir aquí
resultados de pruebas que no se hayan ejecutado realmente.

## Limitaciones

- No se prueba audio real, solo la inicialización y el modo silencioso.
- No se prueba una ventana con compositor/ventanas reales en CI.
- El rendimiento se mide con benchmarks separados, no con una cifra aislada.

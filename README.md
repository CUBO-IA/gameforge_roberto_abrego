# GAMEFORGE 2D — La Fragua Olvidada

Vertical slice jugable de acción-aventura 2D desarrollado con **Python 3.11+** y
**Pygame CE**. Explora una mazmorra generada proceduralmente, recupera tres
fragmentos de ascua, derrota a los enemigos y activa la Fragua. Guarda y carga
partidas, consulta la clasificación local y ejecuta la batería de pruebas.

## Estado

| Sistema | Estado |
|---|---|
| Bucle principal, ventana y escenas | Funcional |
| Mazmorra procedural determinista + validación BFS | Funcional |
| Movimiento, colisión tile-based y cámara | Funcional |
| Combate cuerpo a cuerpo, dash, proyectiles e IA | Funcional |
| Cofres, hoguera, altar y objetivo | Funcional |
| Inventario y consumibles | Funcional |
| Guardado/carga JSON atómico y validado | Funcional |
| Clasificación SQLite | Funcional |
| Menú, HUD, pausa, ayuda, resultados | Funcional |
| Pruebas automatizadas | Ver `documentation/TESTING.md` |
| Audio sintetizado | Funcional con degradación a silencio |

## Ejecutar

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m game
```

Comandos útiles:

```bash
python -m game --new-game --seed 123     # partida directa con semilla fija
python -m game --headless --frames 120   # smoke test sin ventana
pytest                                   # pruebas
python benchmark/bench_generation.py     # medición de generación
python benchmark/bench_simulation.py     # medición de simulación
```

## Controles

| Entrada | Acción |
|---|---|
| WASD / flechas | Mover |
| Ratón | Apuntar |
| Clic izquierdo / J / Espacio | Atacar |
| Shift / K | Dash (invulnerabilidad breve) |
| E | Interactuar |
| Q | Usar frasco de brasa |
| I | Inventario |
| F5 | Guardar |
| ESC | Pausa / volver |
| M (en pausa) | Salir al menú |

## Bucle de juego

1. Despiertas junto a una hoguera en una mazmorra de una sola planta.
2. Los cofres contienen tres fragmentos de ascua, frascos y monedas.
3. Los enemigos (cieno, fuego fatuo y bruto) patrullan y atacan.
4. Descansa en la hoguera para curarte y guardar.
5. Lleva los tres fragmentos al altar de la Fragua y actívalo para ganar.
6. La puntuación se registra en SQLite; el guardado se elimina al terminar.

## Persistencia

- **JSON**: una ranura (`slot1.json`) en el directorio de datos de usuario.
  Escritura atómica (temporal + `os.replace`) y validación estricta de tipos,
  rangos, versión de esquema, tamaño máximo y colecciones.
- **SQLite**: `scores.sqlite3` con una fila por partida terminada y consultas
  de clasificación.
- Localización por defecto:
  - Windows: `%LOCALAPPDATA%\GameForge`
  - macOS: `~/Library/Application Support/GameForge`
  - Linux: `$XDG_DATA_HOME/GameForge` o `~/.local/share/GameForge`
  - Se puede forzar con `--data-dir` o `GAMEFORGE_DATA_DIR`.

## Arquitectura (resumen)

```
game/
  core/         configuración validada y matemáticas sin pygame
  input/        acciones abstractas y mapeo de teclas/ratón
  world/        tiles, generación determinista, colisiones, cámara
  entities/     jugador, enemigos, proyectiles, objetos
  systems/      inventario, combate y objetivo
  persistence/  guardado JSON y clasificación SQLite
  render/       arte procedural, HUD, iluminación, efectos, audio
  scenes/       menú, partida, ayuda, clasificación, resultados
  data/         config.json empaquetado
```

La lógica de dominio (jugador, IA, colisiones, inventario, guardado) no importa
Pygame y se prueba sin abrir ventana. El renderizado solo lee estado.

Decisiones y contratos: `documentation/ARCHITECTURE.md`,
`documentation/DECISIONS.md` y `architecture/CONTRACTS.md`.
Dependencias y licencias: `documentation/DEPENDENCIES.md`.

## Assets

No se distribuyen sprites, mapas, música ni fuentes externas: todo el arte y
los sonidos se generan en tiempo de ejecución. Esto evita problemas de licencia
y mantiene el repositorio ligero. Ver `assets/README.md`.

## Limitaciones conocidas

- Una sola planta por partida (la semilla permite rejugabilidad).
- La clasificación es local; no hay backend online.
- El audio depende de que el dispositivo esté disponible; si falla, el juego
  continúa en silencio y lo registra en el log.
- La ventana usa resolución fija de 1280x720 (configurable por JSON).
- No se ha probado en todas las plataformas; ver informe de pruebas.

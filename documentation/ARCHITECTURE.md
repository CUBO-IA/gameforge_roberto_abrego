# Arquitectura de GAMEFORGE 2D

## 1. Objetivo y alcance

El repositorio implementa un vertical slice de acción-aventura 2D:

- una mazmorra procedural determinista por semilla;
- exploración con colisiones tile-based;
- combate cuerpo a cuerpo, dash y proyectiles enemigos;
- cofres, consumibles, hoguera (curación + guardado) y altar final;
- guardado/carga JSON y clasificación SQLite;
- menú, HUD, pausa, inventario, ayuda, derrota y victoria.

Queda fuera del alcance: multijugador, mundo abierto, editor de mapas, misiones
secundarias, árboles de diálogo y backend online.

## 2. Principios

1. **Separación dominio/presentación.** `core`, `world`, `entities`, `systems`
   y `persistence` no importan pygame (salvo `input`, que es la frontera del
   framework). Los tests de estas capas se ejecutan sin vídeo.
2. **Composición antes que jerarquías.** No hay una clase base `Entity`
   universal: jugador, enemigo, cofre y proyectil tienen estados y reglas
   propias.
3. **Dependencias explícitas.** Configuración, RNG, mapa y repositorios se
   inyectan. No hay singletons globales mutables.
4. **Errores explícitos.** `ConfigError`, `SaveGameError`, `ScoreError`,
   `InventoryError` y `GenerationError` sustituyen a excepciones genéricas.
5. **Datos fuera del código cuando aporta valor.** El balance vive en
   `game/data/config.json` con defaults tipados y validación.

## 3. Módulos y dirección de dependencias

```
core  <---- world <---- entities <---- systems
  ^                         ^
  |                         |
  +---- persistence         +---- render ---- scenes ---- app
                                      ^
                                      |
                                    input
```

- `core`: `GameConfig`, `Vec2`, utilidades numéricas.
- `input`: acciones abstractas (`Action`) y `InputMapper`.
- `world`: `TileMap`, `TILE_DEFS`, generación, colisiones, cámara.
- `entities`: jugador, enemigos, proyectiles, interactivos, catálogo de objetos.
- `systems`: inventario, combate, objetivo.
- `persistence`: rutas, guardado JSON, repositorio SQLite.
- `render`: tiles, entidades, HUD, iluminación, partículas, audio, fondos.
- `scenes`: contrato de escena y flujo de pantallas.
- `app`: ciclo de vida, escena activa, entrada, servicios y puntuación.

Ninguna capa de dominio importa `render` ni `scenes`.

## 4. Bucle y escenas

`Application.run`:

1. limita `dt` a 50 ms;
2. limpia el estado de "pulsado" (`InputMapper.begin_frame`);
3. reparte eventos a la escena activa;
4. actualiza simulación;
5. dibuja y presenta.

`Scene` define `on_enter`, `on_exit`, `handle_event`, `update` y `draw`.
La navegación usa `replace_scene` para evitar pilas ocultas con estado viejo.
El menú, la ayuda, la clasificación y los resultados usan el mismo contrato.

## 5. Simulación

### 5.1 Tiles y colisión

El mapa es una matriz de `TileType` (`FLOOR`, `WALL`, `WATER`, `LAVA`). Cada
tipo declara solidez, multiplicador de velocidad y daño por segundo.

`move_circle` subdivide el desplazamiento en pasos de como máximo 4 px y resuelve
por ejes: si el movimiento completo choca, prueba X y luego Y. Esto produce
deslizamiento, evita tunneling y es determinista. No se usa física de cuerpos
rígidos porque el diseño es top-down sin rotaciones ni impulsos continuos.

`has_line_of_sight` muestrea el segmento y comprueba tiles sólidos; lo usan los
fuegos fatuos para decidir si disparan.

### 5.2 Generación

`generate_dungeon(seed, floor, config)`:

1. coloca salas rectangulares sin solapamiento (padding 2);
2. cava salas y corredores en L, con conexiones extra;
3. elige la sala del altar como la más lejana al spawn;
4. añade charcas/charcas de lava decorativas fuera de salas críticas;
5. coloca hoguera, cofres (3 fragmentos garantizados) y enemigos;
6. valida con BFS que spawn, altar, hoguera y todos los cofres son alcanzables;
7. si falla, reintenta con una semilla derivada determinista.

La misma combinación `(seed, floor, config)` produce el mismo mapa. Los IDs de
cofres (`c0…`) y enemigos (`e0…`) son estables para persistir progreso.

### 5.3 Entidades y sistemas

- `Player`: movimiento, dash con i-frames, ataque en arco, salud, knockback,
  daño por lava. `pending_attack` es consumido por la escena.
- `Enemy`: máquinas de estado por tipo (`slime`, `wisp`, `brute`). Devuelve
  `EnemyIntent` (por ejemplo, proyectil) sin crear objetos de render.
- `Projectile`: avance, TTL y colisión con tiles.
- `Inventory`: pilas por tipo, capacidad de ranuras, validación de cantidades.
- `QuestState`: exige N fragmentos y activa el altar una sola vez.
- `resolve_player_attack`: aplica daño en arco y devuelve los alcanzados.

## 6. Persistencia

### 6.1 Guardado JSON

Esquema actual (`schema_version = 1`):

```json
{
  "schema_version": 1,
  "saved_at": "2026-01-01T00:00:00+00:00",
  "run": {
    "seed": 123, "floor": 1, "elapsed": 42.5, "score": 750, "kills": 9,
    "player": {"x": 640.0, "y": 480.0},
    "health": 87.5,
    "inventory": {"shard": 2, "potion": 1},
    "chests_opened": ["c0"], "defeated": ["e3"],
    "altar_activated": false
  }
}
```

- Escritura atómica: temporal en el mismo directorio + `os.replace`.
- Se valida antes de escribir (un snapshot inválido no sobrescribe uno bueno).
- Límites: 512 KiB, 1000 IDs por lista, 20 ranuras de inventario, cantidades
  entre 1 y 9999.
- Cargar una versión desconocida o sin migración produce error explícito.
- El guardado se elimina al terminar la partida (muerte o victoria) para evitar
  reanudar un estado terminal.

### 6.2 SQLite

Tabla `runs(id, created_at, seed, floor, score, kills, duration, victory)`.
La base se inicializa de forma idempotente. `top(limit, victories_only)` ordena
por puntuación descendente, duración ascendente e id ascendente. Si SQLite no
está disponible, la aplicación conserva el error y lo muestra en vez de
ocultarlo.

## 7. Renderizado y rendimiento

- El mapa estático se pre-renderiza una vez en un `Surface` (2048×1536 con la
  configuración por defecto).
- Solo se dibujan objetos visibles por orden Y.
- Los tiles de agua/lava añaden adornos animados solo si están en pantalla.
- Partículas con límite duro (700) y caché de halos; no se crean superficies
  grandes por partícula.
- Iluminación: máscara de oscuridad + luces radiales cacheadas + viñeta
  precalculada.
- Fuentes y sonidos se cargan una vez.
- No hay I/O en el bucle salvo guardado explícito (F5/hoguera) y registro al
  finalizar.

## 8. Configuración

`game/data/config.json` contiene ventana, jugador, mazmorra, enemigos y audio.
`GameConfig.from_dict` valida tipos y rangos. Los tests pueden construir
`GameConfig` directamente. Los valores por defecto están en dataclasses, de
modo que el juego arranca aunque falte una sección opcional (no el archivo).

## 9. Flujo de datos

```
eventos -> InputMapper -> PlayScene
PlayScene -> Player/Enemy/Inventory/Quest -> estado
PlayScene -> Render -> Surface
PlayScene -> SaveGame -> JSON
PlayScene -> ScoreRepository -> SQLite
```

El render nunca modifica el estado de simulación.

## 10. Riesgos y evolución

- Un solo piso limita la progresión; el generador acepta `floor` y la vista
  podría encadenar pisos sin cambiar el contrato.
- La IA es local y barata; para multitudes grandes habría que añadir spatial
  hashing y separación con rejilla.
- El formato de guardado necesitará migraciones si cambia el esquema; la
  versión ya se valida y existe un punto único de validación.
- La ventana fija simplifica el layout; para escalado habría que separar un
  lienzo virtual y transformar coordenadas de ratón.

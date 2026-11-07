# Directiva de arquitectura (02_ARCHITECTURE.md)

## Estructura de capas y jerarquía de dependencias
La arquitectura sigue un flujo unidireccional estricto y sin dependencias circulares:
`core` ◀ `world` ◀ `entities` ◀ `ai` ◀ `sim` ◀ `scenes` ◀ `app`
y los catálogos en `data/` alimentan tanto a `entities` como a `sim`.

### Capas del sistema:
- `game/core`: Configuración inmutable (`config.py`), matemáticas 2D (`math2d.py`), reloj y excepciones base. Cero dependencias de framework.
- `game/world`: Representación del mapa (`tilemap.py`), colisiones cinemáticas (`collision.py`), generación procedural (`generation.py`), cámara y partición espacial (`spatial.py`).
- `game/entities`: Jugador (`player.py`), enemigos genéricos (`enemies.py`), proyectiles e interactuables. Sin conocimiento de dibujado.
- `game/ai`: Búsqueda de rutas con cuota (`astar.py`), cinemática/steering y máquinas de estado dirigidas por datos.
- `game/sim`: Sistemas de simulación puros y aislados de Pygame (`combat`, `interaction`, `engagement`, `floor`, `loot`, `quest`, `crafting`).
- `game/data`: Catálogos de contenido estructurado en JSON (`enemies.json`, `items.json`, `quests.json`, `recipes.json`).
- `game/persistence`: Serialización atómica de partidas y base de datos SQLite para clasificaciones locales.
- `game/render`: Renderizado de mundo, entidades, luces, HUD y gestión de canvas virtual escalable. Única frontera de renderizado con Pygame CE.
- `game/input`: Mapeo de eventos de hardware a acciones abstractas de juego (`actions.py`).
- `game/scenes`: Orquestadores de flujo de usuario (menú, juego, pausa, resultados) que conectan entrada, simulación y renderizado.
- `tests`: Pruebas automatizadas unitarias, de integración y headless.

## Reglas obligatorias
1. **Dominio puro**: La lógica de simulación (`game/sim/`), mundo (`game/world/`), entidades (`game/entities/`) y persistencia (`game/persistence/`) jamás debe importar `pygame`.
2. **Contenido en datos, no en código**: Enemigos, ítems, recetas y misiones se definen en `game/data/*.json`. Prohibido crear métodos o clases por tipo de enemigo específico (resuelto mediante componentes y arquetipos).
3. **Escenas delgadas**: Las escenas en `game/scenes/` coordinan la vista y traducen acciones, delegando la lógica de negocio en los sistemas puros de `game/sim/`. Mantener `play.py` por debajo de 250 líneas.
4. **Persistencia versionada**: Toda estructura persistida incluye cabecera de versión y validación de esquema en la carga.
5. **Simulación determinista**: El avance del tiempo y la aleatoriedad deben ser controlables desde pruebas mediante inyección de `dt` y semillas de RNG.

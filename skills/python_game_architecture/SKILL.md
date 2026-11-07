# Skill: Arquitectura de Videojuegos en Python (Python Game Architecture)

## 1. Propósito
Establecer las directrices arquitectónicas, jerarquía de dependencias y patrones de separación de responsabilidades para garantizar un código modular, determinista, altamente testeable e inmune a acoplamientos con librerías externas o frameworks de renderizado.

## 2. Contexto de aplicación
Aplicable en todas las decisiones de diseño estructural del repositorio, especialmente al crear nuevos subsistemas (`game/sim/`), refactorizar orquestadores (`game/scenes/play.py`), modelar entidades y definir interfaces de comunicación entre componentes.

## 3. Instrucciones
1. **Flujo unidireccional y sin ciclos**: Respetar estrictamente la regla de dependencias:
   `core` ◀ `world` ◀ `entities` ◀ `ai` ◀ `sim` ◀ `scenes` ◀ `app`.
2. **Dominio puro**: Mantener `game/core/`, `game/world/`, `game/entities/`, `game/ai/`, `game/sim/` y `game/persistence/` completamente independientes de Pygame, SDL o APIs de ventana.
3. **Inyección de dependencias y determinismo**: Los sistemas no deben crear estado global oculto. Deben recibir RNGs con semilla, relojes virtuales y referencias de contexto a través de argumentos explícitos en sus métodos o constructores.
4. **Sistemas puros de simulación (`game/sim/`)**: Los cálculos de combate, interacciones, misiones, looteo y progresión se ejecutan en clases de servicio o funciones puras que reciben el estado y devuelven eventos o mutaciones estructuradas.
5. **Composición sobre herencia**: Modelar entidades mediante dataclasses y componentes agregados en lugar de árboles profundos de herencia.

## 4. Buenas prácticas
- **Evitar singletons y variables globales mutables**: El estado de la partida debe residir en contenedores de datos (`DungeonState`, `PlayerState`) manejados explícitamente.
- **Evitar "God Objects"**: Mantener las escenas del juego como orquestadoras de alto nivel (< 250 líneas) delegando el trabajo pesado en los subsistemas de `game/sim/`.
- **Inmutabilidad en configuración**: Utilizar `dataclass(frozen=True)` para configuraciones de juego (`GameConfig`) y especificaciones de ataque (`AttackSpec`).
- **Interfaces pequeñas y orientadas a datos**: Compartir estructuras planas y tipadas en lugar de exponer métodos con efectos colaterales dispersos.

## 5. Referencias técnicas
- `architecture/CONTRACTS.md`: Registro oficial de firmas públicas e invariantes del sistema.
- `documentation/ARCHITECTURE.md` y `documentation/DECISIONS.md`.
- Tutorial y arquitectura canónica de `python-tcod`: Modelo de acciones, motor y entidades.
- Principios de Clean Architecture adaptados al desarrollo de videojuegos 2D.

## 6. Procedimientos
### Paso 1: Definición de datos de entrada/salida tipados
```python
@dataclass(frozen=True)
class AttackSpec:
    origin: Vec2
    direction: Vec2
    range: float
    damage: float
```
### Paso 2: Creación de funciones de sistema puras
```python
def resolve_combat(spec: AttackSpec, targets: list[Enemy]) -> list[CombatHit]:
    hits: list[CombatHit] = []
    for target in targets:
        if is_in_hitbox(spec, target):
            hits.append(CombatHit(target=target, damage=spec.damage))
    return hits
```
### Paso 3: Orquestación en la escena sin lógica de negocio incrustada
```python
hits = resolve_combat(player_attack_spec, active_enemies)
for hit in hits:
    hit.target.take_damage(hit.damage)
    audio_system.play_hit_sfx()
```

## 7. Criterios de aceptación
- Todos los módulos de simulación y lógica se pueden probar de forma aislada sin inicializar Pygame.
- Cero dependencias circulares verificadas estáticamente con linters y analizadores.
- Escenas limitadas a coordinar entrada, llamar a `sim/` y delegar en `render/`.
- La orquestación de escenas no supera los límites de tamaño acordados.

## 8. Pruebas recomendadas
- `tests/test_sim.py`: Pruebas de integración de combate e interacción pura.
- `tests/test_project_skeleton.py`: Análisis estático de imports para certificar que la lógica no importa `pygame`.
- Pruebas unitarias directas para cada función de simulación con entradas controladas.

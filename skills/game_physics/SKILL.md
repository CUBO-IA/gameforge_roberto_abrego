# Skill: Física y Colisiones en Videojuegos (Game Physics & Collisions)

## 1. Propósito
Garantizar una simulación cinemática y de colisiones precisa, determinista y de alto rendimiento en un espacio top-down 2D mediante resolución basada en cuadrículas (tile-based) y formas primitivas (círculos y rectángulos), evitando el efecto tunneling sin sobrecargar la CPU.

## 2. Contexto de aplicación
Se aplica en:
- `game/world/collision.py`: Funciones matemáticas de intersección, resolución de contacto por ejes y raycasting (línea de visión).
- `game/world/tilemap.py`: Consultas de solidez y propiedades de fricción/ralentización del terreno.
- `game/entities/`: Actualización de posiciones de jugador, enemigos y proyectiles.
No aplica a simulaciones de cuerpos rígidos con rotaciones continuas o cuerdas (para las cuales se evaluaría Pymunk únicamente bajo justificación formal).

## 3. Instrucciones
1. **Conservar el modelo tile-based actual**: Utilizar `move_circle` y resolución separada por ejes (X e Y) contra el `TileMap`.
2. **Subdivisión de pasos (Anti-tunneling)**: Cuando el desplazamiento proyectado `velocity * dt` supere el umbral `max_step` (ej. 4.0 píxeles), subdividir el movimiento en sub-pasos iterativos para prevenir que entidades veloces atraviesen muros finos.
3. **Determinismo numérico**: Trabajar con tipos flotantes estándar sin estado aleatorio en la resolución de colisiones. Para el mismo vector inicial y mapa, la posición resultante debe ser idéntica bit a bit.
4. **Deslizamiento contra muros**: Resolver la colisión en X y en Y de forma secuencial. Si el eje X colisiona con un muro pero Y está libre, permitir el deslizamiento vertical del personaje.
5. **Criterio de adopción de Pymunk**: Solo proponer Pymunk si surgen requisitos de:
   - Apilamiento de cajas/objetos con fricción y masa dinámica.
   - Restricciones elásticas, cuerdas o resortes.
   - Colisiones poligonales rotatorias complejas.
   Si no se dan estas condiciones, rechazar Pymunk por overhead y coste de integración.

## 4. Buenas prácticas
- **Hitboxes contenidas**: Las hitboxes de colisión física deben ser círculos o rectángulos más pequeños que el sprite visual (especialmente en la base de los pies de los personajes) para dar sensación de profundidad top-down.
- **Separación de capas de colisión**: Distinguir claramente entre colisión con el terreno estático (`tilemap`), colisión física entre entidades (separación elástica leve) y cajas de daño/interacción (`hitboxes`/`hurtboxes`).
- **Límites estrictos en `dt`**: Limitar el `dt` entrante a un máximo de 50 ms antes de llamar a las funciones de colisión para evitar saltos masivos de posición ante caídas de FPS.

## 5. Referencias técnicas
- `architecture/CONTRACTS.md`: Contrato de `game.world.collision.move_circle` y `has_line_of_sight`.
- ADR-002: Elección de colisión propia tile-based frente a motores de física externos.
- Algoritmos de separación por ejes (SAT simplificado) y Circle vs AABB.

## 6. Procedimientos
### Paso 1: Verificación de solidez de punto
```python
is_solid = tilemap.is_solid_at(x, y)
```
### Paso 2: Ejecución de desplazamiento con resolución
```python
result = move_circle(
    tilemap=tilemap,
    start=entity.position,
    radius=entity.radius,
    delta=velocity * dt,
    max_step=4.0
)
entity.position = result.position
if result.collided_x:
    velocity.x = 0
if result.collided_y:
    velocity.y = 0
```
### Paso 3: Verificación de línea de visión (Raycast discreto)
```python
can_see = has_line_of_sight(tilemap, start_pos, target_pos, step=6.0)
```

## 7. Criterios de aceptación
- 0 casos de tunneling demostrados en pruebas de alta velocidad.
- Ninguna entidad queda atrapada dentro de un tile sólido tras una colisión.
- Deslizamiento suave sobre paredes diagonales y ortogonales sin atascos.
- Rendimiento medido: la resolución de colisiones de 50 entidades consume < 1 ms por frame.

## 8. Pruebas recomendadas
- `tests/test_collision.py`: Pruebas de tunneling, paso por esquinas, bloqueo frontal y deslizamiento.
- `tests/test_math2d.py`: Verificación de cálculo vectorial de distancia, normalización y límites.
- Pruebas de estrés lanzando proyectiles rápidos contra paredes delgadas de 1 tile.

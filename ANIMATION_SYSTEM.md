# Sistema de Animación y Controladores — GameForge 2D

**Documento:** `ANIMATION_SYSTEM.md`  
**Versión:** 1.0.0 (Aprobada tras Visual Overhaul — Misión 008)  
**Módulos Clave:** `game/render/animation.py`, `game/scenes/play.py`, `game/render/entity_renderer.py`

---

## 1. Arquitectura del Motor de Animación

El sistema de animación de GameForge 2D desacopla la lógica de simulación de los personajes de la reproducción temporal y el recorte de fotogramas, siguiendo un diseño basado en spritesheets y metadatos JSON declarativos (`gf-anim-v1`).

```
+-----------------------------------------------------------------------------------+
|                        ESTRUCTURA DE DATOS (animation.py)                         |
|                                                                                   |
|  FrameData:                                                                       |
|    - rect: pygame.Rect                 (Coordenadas en el atlas)                  |
|    - pivot: tuple[int, int]            (Origen del personaje en el suelo)         |
|    - duration: float                   (Tiempo de permanencia en segundos)        |
|    - sockets: dict[str, tuple[int, int]] (Puntos de anclaje: mano, cabeza, etc.)  |
|    - hurtboxes: list[pygame.Rect]      (Cajas de recepción de daño)               |
|    - hitboxes: list[HitboxData]        (Cajas de ataque con daño y empuje)        |
|    - events: list[FrameEvent]          (Eventos de sonido, partículas y sacudida) |
|                                                                                   |
|  AnimationClip:                                                                   |
|    - frames: list[FrameData]           (Secuencia ordenada de fotogramas)         |
|    - loop: bool                        (Repetición continua o parada final)       |
|    - playback_speed: float             (Modificador temporal de velocidad)        |
|    - interrupt_priority: int           (Nivel de prioridad de interrupción)       |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                     REPRODUCTOR TEMPORAL (AnimationPlayer)                        |
|                                                                                   |
|  - play(clip_name): Inicia clip si tiene igual o mayor prioridad que el actual    |
|  - interrupt_with(clip_name): Fuerza reproducción si priority(nuevo) >= priority  |
|  - update(dt): Avanza tiempo, detecta cambio de fotograma y extrae FrameEvents    |
|  - current_surface: Devuelve la subsurface recortada del frame activo             |
|  - current_pivot: Devuelve el punto de pivote para anclaje al mundo               |
+-----------------------------------------------------------------------------------+
```

---

## 2. Jerarquía de Prioridades e Interrupciones

Para evitar que una acción de menor rango interrumpa una reacción crítica, el sistema implementa una escala de prioridades estricta:

| Nivel | Prioridad | Clips Típicos | Comportamiento al Solicitar Nuevo Clip |
|---|---|---|---|
| **P-Max** | 9 | `die` | Clip terminal de una sola ejecución. Bloquea cualquier otra animación hasta el reinicio. |
| **Alta** | 5 | `hurt` | Reacción inmediata al recibir daño. Interrumpe ataques y movimiento; dura pocos frames. |
| **Combate** | 3 | `attack`, `windup`, `charge` | Animaciones de acción con cajas de golpe activas (`hitboxes`). No pueden ser canceladas por caminar. |
| **Locomoción** | 1 | `walk`, `run` | Animaciones en bucle. Se reproducen mientras la velocidad lineal supere un umbral mínimo. |
| **Base** | 0 | `idle` | Estado de reposo y respiración. Se interrumpe inmediatamente ante cualquier entrada de movimiento o acción. |

---

## 3. Sincronización de Eventos y Combate

Los fotogramas pueden contener `FrameEvents` que se disparan exactamente en el fotograma indicado, garantizando la perfecta sincronización audiovisual:

- **Pisadas (`dust_step`):** En los frames de contacto del clip `walk`, emite partículas de polvo en los pies del héroe.
- **Impacto y Chispas (`slash_spark`):** En el fotograma álgido del clip `attack`, genera un estallido de chispas en la punta de la espada.
- **Sacudida de Cámara (`screen_shake`):** Añade trauma al sistema de sacudida (`trauma: 0.35`) en golpes contundentes o embestidas del bruto.
- **Cajas de Golpe (`hitboxes`):** Activan detección de daño solo durante los frames donde el arma está extendida, con parámetros de daño, fuerza de retroceso (`knockback_force`) y duración de aturdimiento (`hitstun_duration_s`).

---

## 4. Orientación y Espejado Dinámico

El renderizador de entidades (`entity_renderer.py`) gestiona el volteo horizontal (`flip`) preservando el alineamiento espacial:

1. Si el vector de dirección o apuntado apunta hacia la izquierda (`facing.x < 0`):
   ```python
   frame_surf = pygame.transform.flip(frame_surf, True, False)
   px = frame_surf.get_width() - px  # Inversión matemática del pivote
   ```
2. La superficie se posiciona en pantalla mediante:
   ```python
   surface.blit(frame_surf, (screen_x - px, screen_y - py))
   ```
   Esto asegura que los pies del personaje nunca se deslicen ni cambien de posición al girar de dirección.

---

## 5. Implementación en Actores del Juego

### A. Jugador (`knight_hero`)
Controlado en `PlayScene.update`:
- Si `not player.alive`: reproduce `die` (prioridad 9).
- Si `player.damage_flash > 0`: reproduce `hurt` (prioridad 5).
- Si `player.pending_attack is not None or player.attack_anim > 0`: reproduce `attack` (prioridad 3).
- Si `move.length_squared() > 0.01`: reproduce `walk` (prioridad 1).
- Si no hay movimiento: reproduce `idle` (prioridad 0).

### B. Enemigos
- **Cieno (`slime`)**: Modula entre `idle`, `walk`, `attack` (salto de impacto), `hurt` y `die`.
- **Fuego Fatuo (`wisp`)**: Levita con `idle`/`walk`, dispara proyectiles arcanos mediante `shoot` y se desvanece con `die`.
- **Bruto de Escoria (`brute`)**: Fases de combate sincronizadas con su FSM: `windup` (preparación de embestida con brillo), `charge` (carrera devastadora con partículas), `attack` (mandoble circular), `hurt` y `die`.

---

## 6. Cobertura de Pruebas Automatizadas

El sistema de animación cuenta con cobertura unitaria exhaustiva:
- `tests/test_animation_engine.py`: Valida avance temporal por `dt`, bucles, prioridades de interrupción, eventos por fotograma y cálculo de pivotes.
- `tests/test_enemy_animation.py`: Comprueba que los tres tipos de enemigos cargan y reproducen sus atlas correctamente.
- `tests/test_character_validator.py`: Verifica la integridad formal de los manifiestos `gf-anim-v1`, campos obligatorios (`rig_type`, `id`, `display_name`), límites de atlas y ausencia de referencias huérfanas.

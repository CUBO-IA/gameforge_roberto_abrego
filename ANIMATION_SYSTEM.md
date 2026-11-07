# Sistema de animación

## Implementado

`game/render/animation.py` ofrece `FrameData`, `AnimationClip`, `FrameEvent`, `HitboxData`, `AnimationPlayer` y `load_animation_manifest`. Soporta avance por `dt`, loops, clips one-shot, velocidad de reproducción, prioridad de interrupción, eventos por frame, pivote, sockets, hurtboxes e hitboxes. Los tests `test_animation_engine.py` y `test_enemy_animation.py` ya cubren reproducción, prioridad, manifiestos y parte de integración.

`PlayScene` crea reproductores para el héroe y para enemigos slime/wisp/brute. Selecciona estados desde movimiento, ataque, daño y estado de combate. `draw_player`/`draw_enemy` pueden dibujar superficies del frame cuando se asigna un reproductor.

## Brechas observadas

- El render fallback sigue dibujando entidades con primitivas cuando no hay superficie animada asignada; validar en ejecución qué actores muestran atlas.
- No se asigna la animación LPC a un arquetipo de enemigo de la escena inspeccionada.
- Revisión funcional pendiente de consistencia entre estados terminales y clips disponibles. Las pruebas no se ejecutaron por falta de pygame.
- No se debe inferir animación esquelética: no hay runtime de rig conectado y el diseño actual favorece spritesheets.

## Contrato operativo

Conservar `AnimationPlayer` y gf-anim-v1. El actualizador de escena decide el estado y el reproductor avanza con `dt`; el renderer solo presenta el frame/pivote. Los eventos se consumen una sola vez por avance según el comportamiento probado. Una interrupción debe respetar la prioridad declarada. Si falta un clip, el fallback debe ser explícito y cubrirse con prueba; no ocultar errores de formato con `except: pass`.

## Extensiones a proponer antes de codificar

Transiciones con blend, sincronización de hitbox de animación frente a ataque de dominio y capas/equipamiento son extensiones, no capacidades que esta auditoría dé por implementadas. Antes de introducirlas, registrar contrato, dueño de archivos y criterio observable. No añadir rig esquelético runtime hasta que una necesidad artística y benchmark lo justifiquen.

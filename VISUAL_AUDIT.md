# GAMEFORGE — Auditoría visual (Misión 008)

**Fecha:** 2026-11-07  
**Alcance:** inspección estática de `game/render/`, `game/scenes/play.py`, `game/world/`, `assets/`, catálogo y pruebas. No se modificó el motor ni se descargaron recursos.

## Estado actual

- El juego ya cuenta con una escena de cavernas procedural de 64×48 tiles y 32 px por tile, cámara, culling básico de entidades, orden por eje Y, iluminación, sombras, partículas, sacudida, HUD y renderizado headless previsto.
- `game/render/animation.py` implementa lectura de manifiestos gf-anim-v1, reproductor temporal, clips en bucle y one-shot, prioridades de interrupción, eventos, pivotes, sockets y hitboxes.
- Hay atlas propios del héroe y de slime, wisp y brute, más un atlas de esqueleto derivado de LPC. `assets/hub_index.json` cataloga ocho entradas, incluidas muestras CC0 de Kenney y panel UI.
- `TileRenderer` pre-renderiza el mapa estático en una superficie; dibuja paredes/suelos mediante primitivas Pygame y anima agua/lava. La guía registrada en el catálogo todavía no equivale a integración en el juego.

## Hallazgos prioritarios

| Prioridad | Hallazgo comprobado | Impacto |
|---|---|---|
| P0 | `PlayScene` carga y actualiza `knight_hero`, `slime`, `wisp` y `brute`; `draw_player`/`draw_enemy` solo usan `current_surface` cuando hay reproductor asociado. Revisar los atlas: varios son generados internamente, pero su contenido visual no fue validado con una vista ejecutándose. | Riesgo de que la ruta visible siga mostrando las primitivas procedurales pese a cargar manifiestos. Confirmar las imágenes y el encuadre en ejecución. |
| P0 | `assets/README.md` declara que no hay assets binarios y que personajes/escenarios se dibujan con primitivas. Esa afirmación contradice los PNG y el catálogo actuales. | Procedencia y uso real quedan documentados de forma incoherente. |
| P1 | Los tres enemigos pequeños tienen manifiestos/atlas internos y se indexan, pero no tienen entrada individual completa en `assets/hub_index.json` como el héroe. | El Asset Hub no puede garantizar integridad/licencia ni consulta homogénea del conjunto completo. |
| P1 | El atlas esquelético LPC tiene registro CC-BY-SA-3.0 y metadatos, pero `PlayScene` solo carga animaciones de slime, wisp y brute para enemigos. | El recurso LPC no aparece integrado como enemigo en la escena normal. Hay que conservar atribución y revisar obligaciones share-alike si se distribuyen derivados. |
| P1 | `TileRenderer` no consume el tileset Kenney CC0 de 128×128; no hay decoración por capas en esa superficie estática. El mapa conserva la topología y colisiones del TileMap. | La identidad visual del terreno depende del dibujo procedural actual; integrar arte necesita respetar las colisiones existentes. |
| P2 | `draw_attack_arc` crea un overlay de tamaño de ventana por llamada activa; `Lighting` y efectos tienen superficies persistentes y partículas. | Medir el coste en ejecución antes de optimizar o añadir más luces/efectos. |
| P2 | El HUD, botones, paneles, cofres, hoguera y altar usan formas y fuentes Pygame, no el recurso UI 9-slice catalogado. | Estilo visual parcialmente desconectado entre mundo y UI. |

## Recursos y usos

| Recurso | Dimensiones / formato | Procedencia y licencia registrada | Estado de uso |
|---|---|---|---|
| `knight_hero_atlas.png` | 512×512 PNG RGBA, frames 32×36 | GameForge Team, interno, MIT, atribución indicada | Manifiesto cargado por `PlayScene`; verificar presentación visual real. |
| `slime_atlas.png` | 256×256 PNG | GameForge Team, interno, MIT | Manifiesto y reproductor integrados en enemigos slime. |
| `wisp_atlas.png` | 256×256 PNG | GameForge Team, interno, MIT | Manifiesto y reproductor integrados en enemigos wisp. |
| `brute_atlas.png` | 256×256 PNG | GameForge Team, interno, MIT | Manifiesto y reproductor integrados en enemigos brute. |
| `lpc_skeleton_warrior_atlas.png` | 256×64 PNG, frames 64×64 | Redshrike y wulax, LPC/OGA, CC-BY-SA-3.0, atribución requerida | Está en catálogo y tiene manifiesto; `PlayScene` no lo asigna a tipos de enemigo. |
| `kenney_dungeon_stone_32.png` | 128×128 PNG RGBA, celdas 32×32 | Kenney, Tiny Dungeon, CC0-1.0 | Catálogo; renderer no lo consume. |
| `kenney_roguelike_guard.png` | 32×16 PNG RGBA, celdas 16×16 | Kenney, Roguelike RPG Pack, CC0-1.0 | Catálogo; no encontrado en el flujo de juego inspeccionado. |
| `fantasy_dialog_box_9slice.png` | 96×96 PNG RGBA | Kenney, UI Pack RPG Expansion, CC0-1.0 | Catálogo; HUD actual usa primitivas y fuentes Pygame. |

Las dimensiones indicadas provienen de manifiestos/catálogo; no se pudo abrir Pygame para inspección visual o validar los píxeles decodificados. No se identificó duplicado byte a byte durante esta inspección. El catálogo incluye hashes para varios recursos, pero no se corrió una auditoría integral de duplicados.

## Código y contratos a preservar

- Simulación, colisión, entidades y persistencia son capas separadas del render. No mover lógica de combate a Pygame.
- Mantener `Scene.draw/update`, las firmas de `draw_play_world`, el TileMap y su semántica de colisión, InputMapper, guardados y configuración.
- Mantener `AnimationPlayer` y manifiesto gf-anim-v1 compatibles; no inventar un formato alternativo ni cambiar firmas públicas sin propuesta aprobada.
- Respetar el ámbito PRESENTACIÓN para `game/render/`, `game/scenes/` y `game/input/`; `assets/` también pertenece a PRESENTACIÓN. Los contratos compartidos requieren aprobación del director.

## Restricciones de la auditoría

- `python tools/graph_ops.py query ...` y `affected ...` no arrancan: falta `tools.graph_memory` (`ModuleNotFoundError`). Graphify no pudo consultarse ni actualizarse.
- `python tools/visual_benchmark.py --label mission008-baseline --frames 60` no arranca: `ModuleNotFoundError: pygame`. No hay captura real ni métricas base de FPS, memoria o carga.
- Se observó un acceso directo ajeno sin seguimiento en git (`Vídeos - Acceso directo.lnk`); se preservó sin tocar.

## Próximas prioridades

1. Corregir registro de assets y licencias, reconciliar `assets/README.md` con el estado real y completar catálogo de los atlas ya existentes.
2. Ejecutar la escena con pygame-ce disponible, inspeccionar capturas reales y medir línea base antes de juzgar calidad o rendimiento.
3. Activar explícitamente el dibujo de atlas existentes y verificar las animaciones del jugador y las tres siluetas enemigas.
4. Elaborar un único cuarto completo con tiles compatibles con la cuadrícula/colisión, decoración y capas. Probar una integración del atlas Kenney CC0 antes de buscar o adquirir recursos nuevos.
5. Conectar UI 9-slice solo tras validar márgenes, escalado y legibilidad; mantener HUD accesible.
6. Ejecutar pruebas de renderizado y regresión de mecánicas, comparar capturas y métricas con la misma semilla/configuración.

**Conclusión:** la base técnica de render, animación, Asset Hub y efectos ya existe. El vacío principal está en validar y conectar coherentemente esos recursos con la escena, además de la documentación desactualizada y la ausencia de evidencia visual/mediciones ejecutadas. Esta auditoría no afirma que la misión de overhaul esté completada.

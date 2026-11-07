# Guía de Dirección Artística — GameForge 2D

**Documento:** `ART_DIRECTION_GUIDE.md`  
**Versión:** 1.0.0 (Aprobada tras Visual Overhaul — Misión 008)  
**Público:** Desarrolladores, artistas técnicos, diseñadores y agentes de IA.

---

## 1. Identidad Visual: "Fantasía Oscura de la Forja Ancestral"

GameForge 2D se ambienta en una red de catacumbas, minas y forjas subterráneas olvidadas donde el fuego ancestral de la creación lucha contra la decadencia y la corrupción espectral.

### Pilares Estéticos:
1. **Opresión y Atmósfera:** La oscuridad y la piedra fría dominan la mayor parte del espacio, creando tensión y sensación de profundidad subterránea.
2. **Calidez Focalizada:** Los puntos de interacción vital (la hoguera, el altar de la forja, las ascuas recolectadas) irradian una luz ámbar/dorada cálida que sirve de refugio visual para el jugador.
3. **Magia Espectral Cian y Violeta:** Las amenazas arcanas y los fuegos fatuos emiten destellos fríos de alto contraste, comunicando peligro inmediato.
4. **Claridad de Siluetas:** Cada criatura y objeto posee una forma geométrica distintiva reconocible en menos de 100 ms a pantalla completa.

---

## 2. Especificaciones Técnicas y Resolución

- **Lienzo Lógico (Canvas Virtual):** 1280 × 720 píxeles a relación 16:9.
- **Cuadrícula Base de Terreno:** Módulos de 32 × 32 píxeles por tile.
- **Densidad de Píxeles (Texel Ratio):** Relación 1:1 estricta en el espacio de juego. Queda prohibido mezclar densidades de píxeles distintas (sin "pixel mixing").
- **Filtrado:** Vecino más cercano (`NEAREST_NEIGHBOR`). Se prohíbe el suavizado bilineal en texturas y fuentes retro para preservar la nitidez del pixel art.
- **Escala de Cámara:** Escala de ventana entera o escalado con letterbox nítido gestionado por `VirtualCanvas`.

---

## 3. Paleta Cromática y Tokens Oficiales

La paleta se estructura en rampas cromáticas restringidas para asegurar coherencia en todos los recursos generados por `tools/artforge`:

```
+------------------+-----------------------------------------------------+
| CATEGORÍA        | VALORES HEXADECIMALES / TOKENS                      |
+------------------+-----------------------------------------------------+
| Fondo y Vacío    | #10111A (Abismo), #1B1D2B (Sombra profunda)         |
| Piedra de Mazmorra| #232534 (Mortero), #343747 (Piedra), #565568 (Luz) |
| Suelo Musgoso    | #2D4036 (Musgo oscuro), #4A6E53 (Brote verde)       |
| Oro de la Forja  | #8A5F20 (Sombra), #D9AA58 (Oro base), #F7E49A (Luz) |
| Fuego Cálido     | #B3281E (Ascua), #E86523 (Llama), #FFA842 (Núcleo)  |
| Magia de la Forja| #1C4454 (Profundo), #348E9E (Cian), #72D9D0 (Chispa)|
| Espectro / Vacío | #36224A (Sombra), #68428A (Violeta), #A276D4 (Aura) |
| Sangre / Daño    | #4A1218 (Seca), #8A2028 (Impacto), #E54B52 (Crítico)|
| Metal y Armadura | #2C3240 (Hierro), #55627A (Acero), #9AA6B8 (Brillo) |
+------------------+-----------------------------------------------------+
```

---

## 4. Jerarquía y Proporciones de Personajes

Para garantizar la lectura instantánea en combate frenético:

### A. El Héroe Forjador (`knight_hero`)
- **Silueta:** Humanoide fornido con hombreras de hierro, tabardo teal oscuro, yelmo con hendidura de visor cian brillante y espada a dos manos.
- **Dimensiones:** Caja visual de 52 × 50 px; hurtbox física de 20 × 38 px centrada en el pivote.
- **Pivote:** (20, 48), alineado con la base de los pies en el suelo.
- **Contraste:** Es la entidad con mayor gama de valor en pantalla para no perder la vista del avatar.

### B. Enemigos
- **Cieno (`slime`)**:
  - Masa elipsoidal orgánica verde tóxica (`#4A6E53` / `#74AA7A`) con núcleo flotante y ojos saltones que siguen la dirección del jugador.
  - Dimensiones: 32 × 32 px. Animaciones con deformación elástica ("squash and stretch").
- **Fuego Fatuo (`wisp`)**:
  - Silueta circular etérea cian-violeta flotante con máscara espectral y chispas orbitales.
  - Dimensiones: 32 × 32 px. No toca el suelo (levita), sombra circular reducida debajo.
- **Bruto de Escoria (`brute`)**:
  - Masa pesada de 48 × 46 px con placas de hierro remachadas, cuernos de escoria y grietas de lava incandescente en el pecho.
  - Mayor sombra elíptica (44 px) y sacudidas de pantalla en sus embestidas.

---

## 5. Escenarios y Composición Espacial

El escenario se compone en cuatro planos de profundidad:

1. **Plano 0 — Suelo y Relieve:**
   - Suelos base de piedra fría con patrón de adoquines desgastados.
   - Variaciones orgánicas deterministas: grietas, baldosas rotas, manchas de humedad/musgo y rejillas de ventilación.
   - Decoraciones discretas (huesos, escombros, hongos) agrupadas en los laterales para mantener limpia el área central de combate.

2. **Plano 1 — Muros y Estructuras:**
   - Muros frontales de sillería rústica con 3 variaciones de tallado.
   - Remates superiores (`wall_cap`) para sugerir altura y grosor tridimensional.
   - Sombras proyectadas inferiores (`wall_shadow`) para despegar el muro del suelo de manera natural.

3. **Plano 2 — Entidades y Props:**
   - Ordenación dinámica por eje Y (`y-sorting`): cualquier objeto o entidad cuyo pivote inferior esté más abajo se dibuja sobre los que están más arriba.
   - Sombras elípticas translúcidas en el suelo para anclar visualmente cada entidad al plano.

4. **Plano 3 — Iluminación y Efectos Ambientales:**
   - Máscara de oscuridad multiplicativa con radios de luz suaves:
     - Jugador: radio 270 px (visibilidad táctica).
     - Hoguera: radio 175 px con parpadeo sinusoidal orgánico (`flicker`).
     - Altar: radio 190 px azul-cian estable.
     - Proyectiles: radio 70 px con halo brillante.

---

## 6. Principios de Animación

1. **Duración de Fotogramas:**
   - Idle: 140–180 ms por fotograma (respiración suave y expectante).
   - Movimiento (Walk/Run): 85–110 ms por fotograma (ritmo enérgico con cambio claro de apoyo en pies).
   - Ataque: 60–90 ms por fotograma (anticipación corta, golpe fulgurante y frame de recuperación).
   - Daño (Hurt): 80 ms por fotograma (reacción inmediata con hit-stop).
   - Muerte: Secuencia de colapso de 110–130 ms por fotograma sin loop.
2. **Pivote Inferior:**
   - Todo fotograma ubica su origen `(pivot_x, pivot_y)` en el centro de la base de los pies. Al voltear horizontalmente (`flip`), el pivote se recalcula automáticamente: `new_px = width - px`.
3. **Sockets y Puntos de Enlace:**
   - Cada frame expone sockets normalizados para `hand_right`, `head`, `cast_point` y `shadow`.

---

## 7. Interfaz de Usuario (UI) y 9-Slice

- **Paneles:** Construidos mediante técnica 9-slice con bordes de 14 px. Estructura de metal forjado oscuro con esquinas remachadas y fondo semitransparente oscuro (`#10111A` al 92% de opacidad).
- **Barras de Salud:** Marco ornamentado con reborde exterior metálico (`bar_frame`) y barra interior degradada roja (`bar_fill`) con brillo superior.
- **Tipografía:** Textos con sombra paralela negra a 2 px de desplazamiento para garantizar legibilidad perfecta sobre cualquier fondo de juego.
- **Iconografía:** Elementos representativos de 16×16 px limpios: corazón, espada, frasco de poción, ascua, llave y calavera.

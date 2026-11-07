# Manual del Jugador — GAMEFORGE 2D: La Fragua Olvidada

Bienvenido a **La Fragua Olvidada**, una aventura de rol y acción en 2D con combate en tiempo real, generación procedural de mazmorras y progresión por plantas subterráneas.

---

## 1. Controles Oficiales

| Acción | Control Principal | Control Alternativo |
|---|---|---|
| **Moverse** | Teclas `W`, `A`, `S`, `D` | `Flechas de dirección` |
| **Apuntar** | Movimiento del ratón | — |
| **Ataque cuerpo a cuerpo** | `Clic Izquierdo` del ratón | `Barra Espaciadora` |
| **Esquiva (Dash)** | `Clic Derecho` del ratón | `Shift Izquierdo` |
| **Interactuar** *(Cofre / Hoguera / Altar)* | Tecla `E` | — |
| **Beber Poción de Brasa** | Tecla `Q` | — |
| **Pausa / Menú** | Tecla `Escape` | Tecla `P` |
| **Guardar Partida Rápido** | Tecla `F5` *(en pausa / hoguera)* | — |
| **Pantalla Completa** | Tecla `F11` | — |

---

## 2. Mecánicas de Juego

### ⚔️ Combate y Esquiva
- **Ataque en abanico**: El ataque del personaje barre un arco frontal en la dirección donde apuntas con el ratón, infligiendo daño y empuje (knockback) a todos los enemigos en el área.
- **Dash con invulnerabilidad (i-frames)**: Al pulsar clic derecho o Shift, tu personaje realiza un deslizamiento rápido. Durante los primeros instantes del dash eres invulnerable al daño de contacto y proyectiles.
- **Curación**: Utiliza frascos de brasa (`Q`) para recuperar salud al instante. Si te quedas sin frascos, puedes sintetizarlos mediante alquimia o descansar en una hoguera.

### 🏰 Progresión Multiplanta (3 Niveles Subterráneos)
El objetivo de la expedición es descender hasta las entrañas de la montaña y reavivar la Fragua Suprema:
1. **Planta 1 — El Umbral Olvidado**: Explora las salas iniciales, derrota a los slimes y reúne **3 fragmentos solares** para abrir el portal del Altar.
2. **Planta 2 — La Cripta de Ceniza**: La densidad de enemigos aumenta y las ánimas (wisps) atacarán a distancia. Requiere **4 fragmentos solares**.
3. **Planta 3 — El Núcleo de la Fragua**: El corazón ardiente de la tierra, custodiado por brutos acorazados. Reúne **5 fragmentos solares** y activa el Altar Supremo para culminar tu partida en una victoria definitiva.

### 📜 Sistema de Misiones Secundarias
En cada planta se activan automáticamente misiones opcionales que otorgan oro y recompensas al completarse:
- **Cacería**: Eliminar un número determinado de monstruos de una especie.
- **Exploración**: Saquear los cofres protegidos en las salas de la mazmorra.
- **Objetivo Principal**: Despertar el Altar de cada piso.

### ⚗️ Fabricación Alquímica (Crafting)
En las hogueras y mediante el menú puedes transmutar los recursos recolectados:
- **Frasco de Brasa**: 1 fragmento solar + 2 monedas $\rightarrow$ 1 poción de salud.
- **Doble Frasco de Brasa**: 2 fragmentos solares + 5 monedas $\rightarrow$ 2 pociones de salud.
- **Infusión Alquímica**: 8 monedas $\rightarrow$ 1 fragmento solar (ideal si te falta un fragmento para activar el Altar).

### 💾 Gestión de Partidas Guardadas
El juego cuenta con un sistema multi-ranura que permite mantener hasta **3 expediciones independientes** sin interferir entre sí. Tu progreso de salud, inventario acumulado y misiones se guardan de forma atómica y segura cada vez que descansas en una hoguera o desciendes de planta.

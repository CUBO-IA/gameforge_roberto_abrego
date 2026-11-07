# VISUAL_EFFECTS_ARCHITECTURE.md — GAMEFORGE 2D
## Arquitectura de Efectos Visuales, Partículas, Sacudida de Cámara e Impactos de Combate

**Estado:** APROBADO PARA DISEÑO ARQUITECTÓNICO  
**Misión:** MISIÓN 002 — Sprites, Animaciones y Lógica de Personajes  
**Fecha:** 2026-11-07  
**Motor Objetivo:** Python 3.11+ / pygame-ce (v2.5+)  

---

## 1. Resumen Ejecutivo

Los efectos visuales (*VFX*) y la retroalimentación cinestésica (*Game Juice*) son los elementos determinantes que transforman un combate plano y mecánico en una experiencia visceral, gratificante y legible.

En **GameForge 2D**, la arquitectura de efectos debe satisfacer dos restricciones estrictas:
1. **Sensación de Impacto de Primer Nivel:** Pausas de impacto (*hitstop*), destellos de silueta (*flash-hit*), chispas direccionales, estelas de esquiva y sacudida de cámara no lineal basada en física de trauma.
2. **Rendimiento Estable en Hardware Modesto:** Soportar cientos de partículas simultáneas, iluminación dinámica y efectos ambientales a **60 FPS constantes** (< 1.5 ms dedicados a VFX por frame) en CPUs modestas sin saturar el Garbage Collector (GC) de Python.

---

## 2. Sistema de Partículas de Alto Rendimiento

### 2.1 El Problema de las Asignaciones Dinámicas de Memoria
En implementaciones ingenuas en Python, cada partícula creada ejecuta `Particle(...)` y cada partícula muerta se elimina de una lista `particles.remove(p)` o `[p for p in particles if p.alive]`.
- **Impacto:** Crear y destruir 200 partículas por segundo genera miles de pequeños objetos temporales, obligando al Garbage Collector de CPython a ejecutar pausas periódicas (*GC stalls*) que provocan caídas esporádicas de frames (*stuttering*).

### 2.2 Arquitectura de Reserva Preasignada (*Object Pooling*)
GameForge 2D utiliza un contenedor `ParticlePool` de tamaño fijo preasignado en memoria. Ninguna partícula es creada o destruida durante el bucle principal:

```python
class ParticlePool:
    """Pool de partículas de tamaño fijo sin asignaciones dinámicas en el bucle principal."""
    __slots__ = ("capacity", "count", "x", "y", "vx", "vy", "life", "max_life", 
                 "size", "color_r", "color_g", "color_b", "drag", "gravity", "blend_add")

    def __init__(self, capacity: int = 1000) -> None:
        self.capacity = capacity
        self.count = 0
        # Arrays contiguos o listas predimensionadas
        self.x = [0.0] * capacity
        self.y = [0.0] * capacity
        self.vx = [0.0] * capacity
        self.vy = [0.0] * capacity
        self.life = [0.0] * capacity
        self.max_life = [1.0] * capacity
        self.size = [2.0] * capacity
        self.color_r = [255] * capacity
        self.color_g = [255] * capacity
        self.color_b = [255] * capacity
        self.drag = [1.0] * capacity
        self.gravity = [0.0] * capacity
        self.blend_add = [False] * capacity

    def spawn(self, x: float, y: float, vx: float, vy: float, life: float, 
              size: float, color: tuple[int, int, int], drag: float = 1.0, 
              gravity: float = 0.0, blend_add: bool = False) -> bool:
        if self.count >= self.capacity:
            return False  # Culling natural si se satura el pool
        
        idx = self.count
        self.x[idx] = x
        self.y[idx] = y
        self.vx[idx] = vx
        self.vy[idx] = vy
        self.life[idx] = life
        self.max_life[idx] = life
        self.size[idx] = size
        self.color_r[idx], self.color_g[idx], self.color_b[idx] = color
        self.drag[idx] = drag
        self.gravity[idx] = gravity
        self.blend_add[idx] = blend_add
        self.count += 1
        return True

    def update(self, dt: float) -> None:
        """Actualización en bucle cerrado con técnica de intercambio con el último elemento (Swap-and-Pop)."""
        i = 0
        while i < self.count:
            self.life[i] -= dt
            if self.life[i] <= 0.0:
                # Partícula muerta: reemplazar con la última partícula activa en O(1)
                self.count -= 1
                if i < self.count:
                    self._swap(i, self.count)
                continue
            
            # Integración de movimiento
            d = 1.0 - (self.drag[i] * dt)
            if d < 0.0:
                d = 0.0
            self.vx[i] *= d
            self.vy[i] = (self.vy[i] + self.gravity[i] * dt) * d
            self.x[i] += self.vx[i] * dt
            self.y[i] += self.vy[i] * dt
            i += 1

    def _swap(self, a: int, b: int) -> None:
        self.x[a], self.x[b] = self.x[b], self.x[a]
        self.y[a], self.y[b] = self.y[b], self.y[a]
        self.vx[a], self.vx[b] = self.vx[b], self.vx[a]
        self.vy[a], self.vy[b] = self.vy[b], self.vy[a]
        self.life[a], self.life[b] = self.life[b], self.life[a]
        self.max_life[a], self.max_life[b] = self.max_life[b], self.max_life[a]
        self.size[a], self.size[b] = self.size[b], self.size[a]
        self.color_r[a], self.color_r[b] = self.color_r[b], self.color_r[a]
        self.color_g[a], self.color_g[b] = self.color_g[b], self.color_g[a]
        self.color_b[a], self.color_b[b] = self.color_b[b], self.color_b[a]
        self.drag[a], self.drag[b] = self.drag[b], self.drag[a]
        self.gravity[a], self.gravity[b] = self.gravity[b], self.gravity[a]
        self.blend_add[a], self.blend_add[b] = self.blend_add[b], self.blend_add[a]
```

### 2.3 Modos de Dibujo y Blending
- **Mezcla Aditiva (`pygame.BLEND_ADD`):**
  - Esencial para efectos de fuego, chispas de metal, magia y explosiones brillantes. Los colores se suman matemáticamente en el canal RGB, logrando un núcleo blanco incandescente en zonas de alta densidad sin coste de shaders.
- **Partículas Circulares vs Rectangulares:**
  - `pygame.draw.circle()` es eficiente para chispas grandes, pero dibujar cientos de círculos individuales tiene coste de CPU.
  - Para ráfagas de alta densidad (e.g. 500 motas de polvo), se utilizan partículas rectangulares de $2 \times 2$ píxeles dibujadas mediante `surface.fill(color, rect)`, que es hasta **5 veces más rápido** en pygame-ce.

---

## 3. Impactos de Combate: Hitstop, Flash-Hit y Chispas

### 3.1 Pausa de Impacto (*Hitstop / Freeze Frames*)
- **Concepto:** Tras un golpe contundente (crítico, muerte de enemigo o golpe de espadón), el avance de la simulación del atacante y defensor se congela durante un lapso muy breve (**30 a 90 milisegundos**, 2 a 5 frames).
- **Mecanismo:**
  ```python
  class HitstopManager:
      def __init__(self) -> None:
          self.duration_remaining: float = 0.0

      def trigger(self, duration_s: float) -> None:
          self.duration_remaining = max(self.duration_remaining, duration_s)

      def update(self, dt: float) -> bool:
          """Devuelve True si la simulación debe continuar normalmente, False si está congelada."""
          if self.duration_remaining > 0.0:
              self.duration_remaining = max(0.0, self.duration_remaining - dt)
              return False
          return True
  ```
- **Clave de Diseño:** Durante el hitstop, la física y los ataques se detienen, pero **la sacudida de pantalla, la música y las partículas continúan vibrando**. Esto transmite un peso cinético enorme.

### 3.2 Destello de Impacto (*Flash-Hit*)
- Cuando una entidad recibe daño, su silueta completa se tiñe de **blanco puro** durante 1-2 frames (40 ms), seguido de un parpadeo rojizo durante el periodo de invulnerabilidad.
- **Implementación Óptima en Pygame-ce sin Shaders:**
  1. Se utiliza la máscara binaria del sprite: `mask = pygame.mask.from_surface(sprite_surface)`.
  2. Se convierte la máscara a una superficie blanca: `white_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))`.
  3. Se almacena en la caché de la entidad en tiempo de carga, eliminando el coste de generar la máscara en cada frame de combate.

---

## 4. Sacudida de Cámara Basada en Física de Trauma

### 4.1 El Modelo de Trauma de Squirrel Eiserloh
Las sacudidas de cámara lineales simples (donde la amplitud decrece linealmente) producen una vibración robótica y desagradable. GameForge 2D implementa el modelo estándar de la industria basado en **Trauma no lineal**:

$$Trauma \in [0.0, 1.0]$$
$$Shake = Trauma^2 \quad \text{o} \quad Shake = Trauma^3$$

- **Ventajas:**
  - Si el trauma es leve (ej. 0.2 por un paso pesado), $Shake = 0.2^2 = 0.04$ (una sacudida sutil, casi imperceptible pero inmersiva).
  - Si el trauma es masivo (ej. 0.9 por una explosión), $Shake = 0.9^2 = 0.81$ (sacudida contundente y dramática).

### 4.2 Desplazamiento Traslacional y Rotacional
El offset resultante aplica dos componentes:
1. **Traslación $(X, Y)$:** Desplazamiento de los ejes de la cámara.
2. **Rotación $(\theta)$:** Ligera inclinación angular de la superficie de visualización ($< 2.5^\circ$), crucial para explosiones e impactos sísmicos.

```python
class TraumaScreenShake:
    def __init__(self, max_offset_px: float = 14.0, max_angle_deg: float = 2.5, decay_rate: float = 1.8) -> None:
        self.trauma: float = 0.0
        self.max_offset_px = max_offset_px
        self.max_angle_deg = max_angle_deg
        self.decay_rate = decay_rate
        self.time_accumulator: float = 0.0

    def add_trauma(self, amount: float) -> None:
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt: float) -> None:
        self.time_accumulator += dt * 35.0  # Frecuencia de oscilación armónica
        self.trauma = max(0.0, self.trauma - self.decay_rate * dt)

    def get_transform(self) -> tuple[Vec2, float]:
        if self.trauma <= 0.001:
            return Vec2(0.0, 0.0), 0.0
        
        shake = self.trauma * self.trauma  # Exponente cuadrático
        # Ruido armónico compuesto para evitar regularidad
        offset_x = self.max_offset_px * shake * (math.sin(self.time_accumulator) + 0.5 * math.sin(self.time_accumulator * 2.3))
        offset_y = self.max_offset_px * shake * (math.cos(self.time_accumulator * 1.4) + 0.5 * math.cos(self.time_accumulator * 3.1))
        angle = self.max_angle_deg * shake * math.sin(self.time_accumulator * 0.9)
        return Vec2(offset_x, offset_y), angle
```

---

## 5. Efectos Ambientales y Atmosféricos

Para dotar a las mazmorras y cavernas de atmósfera sin coste desmedido:
1. **Motas de Polvo y Cenizas Flotantes:**
   - Un emisor ambiental global de 50 a 100 partículas con movimiento browniano sinusoidal suave:
     $$v_x(t) = v_{base\_x} + A \sin(\omega t), \quad v_y(t) = v_{base\_y} + B \cos(\omega t)$$
2. **Parpadeo de Antorchas y Hogueras (*Torch Flicker*):**
   - Modulación del radio y opacidad de la luz en `game.render.lighting` mediante una onda de ruido fractal de baja frecuencia:
     $$Radius(t) = R_0 \cdot \left(1.0 + 0.06 \sin(8t) + 0.03 \sin(22t)\right)$$
3. **Culling Espacial de Efectos:**
   - Toda partícula o efecto situada a más de 120 píxeles de los bordes del visor visible (`Camera.in_view`) omite completamente su rutina de renderizado.

---

## 6. Animaciones de Interfaz y Retroalimentación (UI Juice)

### 6.1 Motor Ligero de Interpolación Paramétrica (*Tweens*)
Para barras de vida que vibran al recibir daño o números de combate flotantes:

```python
def ease_out_quad(t: float) -> float:
    return 1.0 - (1.0 - t) * (1.0 - t)

def ease_out_elastic(t: float) -> float:
    p = 0.3
    return math.pow(2.0, -10.0 * t) * math.sin((t - p / 4.0) * (2.0 * math.pi) / p) + 1.0

def ease_out_bounce(t: float) -> float:
    if t < (1 / 2.75):
        return 7.5625 * t * t
    elif t < (2 / 2.75):
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    else:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
```

### 6.2 Texto Flotante de Combate (*Floating Damage Numbers*)
- Generación con arco de movimiento: Se expulsa hacia arriba con un ángulo aleatorio $\pm 25^\circ$.
- Escalado inicial con `ease_out_elastic` (el texto "explota" al aparecer y luego flota desacelerando mientras reduce su opacidad alfa).
- Números críticos con mayor tamaño de fuente y color dorado/amarillo brillante.

---

## 7. Presupuesto y Métricas de Rendimiento en Hardware Modesto

Para asegurar que GameForge 2D cumpla el compromiso de hardware modesto:

| Sistema | Presupuesto Máximo de CPU | Capacidad Máxima Activa | Optimización Principal |
|---|---|---|---|
| **Partículas de Combate** | 0.60 ms | 600 partículas | Object pool contiguo + `swap-and-pop` |
| **Partículas Ambientales** | 0.20 ms | 150 partículas | Viewport culling estricto |
| **Screen Shake (Trauma)** | 0.05 ms | 1 instancia global | Cálculo trigonométrico $O(1)$ |
| **Hitstop Manager** | 0.01 ms | 1 instancia global | Comprobación de timer $O(1)$ |
| **Texto de Daño Flotante** | 0.25 ms | 40 textos activos | FontCache pre-renderizado |
| **Total Subsistema VFX** | **1.11 ms** | — | **< 7% del frame budget total de 16.67 ms** |

---

## 8. Conclusiones y Recomendaciones

1. **Pool Mandatorio:** Queda prohibida la instanciación dinámica de objetos de partículas dentro del ciclo de juego. Todo emisor debe solicitar índices al `ParticlePool`.
2. **Integración con Eventos de Animación:** Los eventos `spawn_particle` y `screen_shake` definidos en `ANIMATION_FORMAT_SPEC.md` se conectan directamente con este subsistema mediante el despachador de simulación.
3. **Cero Dependencias Externas:** El sistema se implementa exclusivamente sobre la biblioteca estándar y `pygame-ce`, garantizando portabilidad universal sin requerir librerías pesadas adicionales.

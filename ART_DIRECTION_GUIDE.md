# Guía de dirección artística — GameForge

**Estado:** propuesta para el primer vertical slice; se debe validar en captura de juego antes de ampliarla.

## Identidad

Fantasía oscura legible y cálida en los puntos de interés: piedra fría azul petróleo, carbón y violeta en sombras; hierro y hueso neutros; oro viejo en la interfaz y la Forja; cian espectral para magia. El jugador debe leerse como la silueta de mayor contraste. Cada enemigo conserva una masa y un color de acento propios: slime verde, wisp cian, brute óxido/ámbar y skeleton hueso.

## Reglas de producción propuestas

- **Lienzo lógico actual:** 1280×720; conservarlo. La cuadrícula del mundo ya usa tiles de 32×32. No escalar assets con filtrado bilineal: usar vecino más cercano y escala entera cuando el canvas lo permita.
- **Escala:** priorizar tiles 32×32 y personajes en múltiplos compatibles. Los recursos de 16×16 pueden aparecer como detalle o duplicar resolución con nearest-neighbor, tras revisar legibilidad. No mezclar sin prueba estilos LPC de 64×64 y sprites internos más compactos en una misma capa.
- **Paleta de trabajo:** base `#10111A`, sombra `#1B1D2B`, piedra `#343747`, piedra iluminada `#565568`, hueso `#D8D0B8`, hierro `#9AA6B8`, oro `#D9AA58`, magia `#72D9D0`, daño `#E56C69`. Colores del código existente deben auditarse frente a estas muestras antes de fijar tokens de paleta.
- **Contraste:** entidades y objetos interactivos deben separarse del suelo por valor y contorno de forma selectiva. No colocar destellos persistentes detrás de información del HUD.
- **Iluminación:** luz cálida local en hoguera/forja y acento frío en altar/proyectiles. Usar máscaras existentes, radios limitados y superficies reutilizadas. No añadir luz por tile.
- **Composición:** suelo como plano de lectura; muros y columnas en silueta; decoración agrupada en bordes/zonas seguras, dejando rutas de combate despejadas. Orden de profundidad por Y para objetos y criaturas, con foreground opcional solo si el culling y la lectura lo permiten.
- **Animación:** pivote inferior centrado; idle sutil, walk con cambio claro de apoyo, anticipación/impacto/recuperación para ataques, hurt breve y death one-shot. Prioridades y eventos del formato gf-anim-v1 existentes son la base.
- **UI:** panel oscuro translúcido, borde de oro viejo, tipografía con alto contraste y tamaños actuales legibles. El 9-slice Kenney es una referencia CC0 disponible; validar sus márgenes de 24 px con tamaños reales antes de adoptarlo.

## Criterio de aceptación visual

Validar en una captura headless del juego: siluetas distinguibles a tamaño de ventana, tiles sin costuras, objetivo/interacción legibles, animación del protagonista perceptible y UI contrastada. La guía sigue siendo propuesta hasta contar con una captura real; no es prueba de calidad final.

# Skill: Python Game Architecture

## Cuándo usar
Al diseñar módulos, ciclo de vida, estados, eventos y límites entre lógica y framework.

## Procedimiento
1. Inspeccionar estructura y dependencias actuales.
2. Identificar responsabilidades y dependencias circulares.
3. Separar dominio de infraestructura cuando aporte testabilidad.
4. Proponer interfaces pequeñas y explícitas.
5. Crear pruebas para reglas del dominio.
6. Documentar decisiones relevantes.

## Buenas prácticas
- Composición antes que jerarquías profundas.
- Evitar managers omniscientes.
- Evitar estado global mutable.
- Inyectar reloj, RNG o repositorios cuando se necesite determinismo.
- No abstraer una única implementación sin necesidad demostrada.

## Entrega
Diagrama textual de módulos, interfaces públicas, dependencias y pruebas.

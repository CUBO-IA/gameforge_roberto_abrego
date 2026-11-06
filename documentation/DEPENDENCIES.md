# Dependencias y licencias

## Runtime

| Dependencia | Versión mínima | Licencia | Uso |
|---|---|---|---|
| Python | 3.11 | PSF License | Lenguaje y biblioteca estándar |
| pygame-ce | 2.5 | LGPL-2.1-or-later | Ventana, entrada, superficies, fuentes, audio |

No se usa Pymunk: ver ADR-002. No se usan Tiled/LDtk/PyTMX porque la mazmorra se
genera en código y no hay mapas editados externamente.

## Desarrollo y pruebas

| Dependencia | Versión mínima | Licencia | Uso |
|---|---|---|---|
| pytest | 8 | MIT | Pruebas automatizadas |
| ruff | 0.6 (opcional) | MIT | Lint |

SQLite y `json` forman parte de la biblioteca estándar de Python.

## Assets

No hay assets de terceros. Todo el arte es procedural y los sonidos se
sintetizan en memoria. La fuente es la incluida por Pygame CE.

## Verificación de licencias

- Pygame CE: https://github.com/pygame-community/pygame-ce (LGPL-2.1-or-later).
- pytest: https://github.com/pytest-dev/pytest (MIT).
- Python: https://www.python.org/ (PSF).
- SQLite: dominio público.

Las licencias se citan a título informativo; antes de redistribuir el juego hay
que revisar los textos completos de las versiones efectivamente instaladas.

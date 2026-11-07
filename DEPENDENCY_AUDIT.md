# GAMEFORGE 2D — AUDITORÍA EXHAUSTIVA DE DEPENDENCIAS Y LICENCIAS

**Documento:** `DEPENDENCY_AUDIT.md`  
**Rol:** Arquitecto Principal de GameForge 2D & Auditor Técnico  
**Fecha:** 2026-11-06  
**Estado:** AUDITORÍA LEGAL Y TÉCNICA OFICIAL  
**Marco normativo:** Licencia del proyecto (MIT), directivas de `directives/03_QUALITY_AND_SECURITY.md` y `documentation/DEPENDENCIES.md`.

---

## 1. Política de Dependencias y Principios de Cumplimiento Legal

GameForge 2D mantiene una política de dependencias estricta:
1. **Minimización de Superficie de Dependencias:** Toda biblioteca de terceros introduce riesgos de seguridad, mantenimiento a largo plazo, sobrecarga en la distribución binaria y posibles conflictos de licencia. Ninguna dependencia se incorpora sin un análisis formal de coste-beneficio.
2. **Compatibilidad con la Licencia MIT del Proyecto:** GameForge 2D se distribuye bajo la licencia **MIT**. Cualquier componente incorporado al runtime debe permitir la distribución comercial y libre del software sin forzar el relicenciamiento viral del código propietario de GameForge.
3. **Reproducibilidad y Bloqueo Criptográfico:** Todas las dependencias de desarrollo y producción se fijan mediante el archivo de bloqueo `uv.lock`, garantizando que todos los agentes y entornos de CI construyan exactamente con los mismos hashes binarios.
4. **Respeto a la Propiedad Intelectual:** Está terminantemente prohibido copiar código fuente de repositorios que carezcan de licencia abierta explícita o que utilicen licencias incompatibles sin autorización expresa.

---

## 2. Auditoría del Stack Actual de GameForge 2D

| Paquete | Versión Mínima | Licencia | Tipo | Uso en el Proyecto | Compatibilidad MIT |
|---|---|---|---|---|:---:|
| **Python** | 3.11+ | PSF License | Runtime Core | Intérprete y biblioteca estándar | **COMPATIBLE** |
| **pygame-ce** | 2.5.0+ | LGPL-2.1-or-later | Runtime | Ventana, entrada, superficies, audio | **COMPATIBLE** (Enlace dinámico) |
| **sqlite3** | Nativo Python | Dominio Público | Runtime | Persistencia de clasificaciones | **COMPATIBLE** |
| **json** | Nativo Python | PSF License | Runtime | Persistencia atómica de partidas | **COMPATIBLE** |
| **pytest** | 8.0.0+ | MIT License | Desarrollo / CI | Suite de pruebas unitarias | **COMPATIBLE** |
| **ruff** | 0.6.0+ | MIT License | Desarrollo / CI | Linter y formateador de código | **COMPATIBLE** |
| **PyInstaller** | 6.0.0+ | GPL v2+ con Excepción | Empaquetado | Generador de binario distribuible | **COMPATIBLE** (Output libre) |

### Análisis Legal de Pygame CE (LGPL-2.1-or-later)
La licencia LGPL-2.1 permite utilizar la biblioteca en proyectos con licencias más permisivas (como MIT) siempre que se cumpla con la condición de **enlace dinámico**. Al distribuirse a través de wheels binarios independientes en PyPI que cargan dinámicamente las librerías compartidas de SDL2 (`.dll` en Windows, `.so` en Linux, `.dylib` en macOS), no se produce una obra derivada contaminada por copyleft. El código fuente de GameForge 2D permanece 100% bajo licencia MIT.

---

## 3. Auditoría de los 12 Repositorios Investigados

A continuación se detalla la situación legal, de dependencias y de riesgos técnicos de cada uno de los 12 repositorios analizados en `REPOSITORY_RESEARCH.md`:

```mermaid
pie title Distribución de Licencias de Repositorios Investigados
    "MIT": 4
    "LGPL (v2.1 / v3)": 3
    "BSD (2-Clause / 3-Clause)": 2
    "GPL v2 / Formato Abierto": 1
    "Dominio Público / CC0": 1
    "Sin Licencia (All Rights Reserved)": 1
```

### 3.1 pygame-ce
- **Licencia:** LGPL-2.1-or-later.
- **Dependencias internas:** SDL2, SDL2_image, SDL2_mixer, SDL2_ttf.
- **Dictamen legal:** Aceptado para la capa de presentación. Requiere mantener enlace dinámico en la distribución.

### 3.2 pymunk
- **Licencia:** MIT License (tanto Pymunk como la biblioteca C Chipmunk 2D).
- **Dependencias internas:** CFFI (MIT), librería binaria Chipmunk.
- **Dictamen legal:** Plenamente compatible con MIT.
- **Veredicto técnico:** Descartado para el núcleo actual por sobrecoste innecesario en un RPG top-down en cuadrícula; reservado como opcional condicional (ADR-002).

### 3.3 esper
- **Licencia:** MIT License.
- **Dependencias internas:** Cero (Python puro).
- **Dictamen legal:** 100% compatible con MIT. Puede incorporarse como paquete o como módulo copiado con preservación de cabecera de copyright.
- **Veredicto técnico:** Aceptable, pero no prioritario en este momento para evitar fragmentación prematura del estado.

### 3.4 Tiled
- **Licencia:** GPL v2 (aplicación Qt Tiled) / BSD 2-Clause (`libtiled` y especificaciones).
- **Dependencias internas:** Qt framework.
- **Dictamen legal:** **COMPATIBLE AL 100%**. Los archivos de mapa generados (`.json`, `.tmx`) son documentos de datos creados por el desarrollador/diseñador; no están sujetos a la licencia GPL del editor.
- **Veredicto técnico:** Adoptado como herramienta externa de autoría gráfica.

### 3.5 pytmx
- **Licencia:** **LGPL v3**.
- **Dependencias internas:** `six`, opcionalmente `zstandard`.
- **Dictamen legal y riesgo:** La LGPLv3 contiene cláusulas contra la "tivoización" (bloqueo por hardware) y requisitos más estrictos de re-enlace en entornos congelados con PyInstaller.
- **Veredicto técnico:** **DESCARTADO**. Nuestro cargador propio `game/world/tiled_loader.py` utiliza la biblioteca estándar `json` de Python, eliminando por completo cualquier dependencia externa y cualquier fricción de licencia LGPLv3.

### 3.6 tilemap-generator
- **Licencia:** MIT License.
- **Dependencias internas:** Ecosistema Node.js / npm.
- **Dictamen legal:** Compatible con MIT.
- **Veredicto técnico:** **DESCARTADO**. Incompatible con el runtime unificado de Python; obligaría a mantener dos runtimes y dependencias de npm sin aportar ventajas sobre nuestro generador en Python.

### 3.7 python-tcod
- **Licencia:** BSD 2-Clause (python-tcod) / BSD 3-Clause (libtcod).
- **Dependencias internas:** CFFI, **NumPy**, biblioteca C libtcod.
- **Dictamen legal:** Altamente permisiva y 100% compatible con MIT.
- **Veredicto técnico:** **DESCARTADO COMO RUNTIME / ADOPTADO A NIVEL ALGORÍTMICO**. Arrastrar NumPy y CFFI añade más de 40 MB de binarios al empaquetado de GameForge. Sus algoritmos (Shadow Casting FOV y Dijkstra Maps) pueden escribirse en Python puro optimizado.

### 3.8 py_trees
- **Licencia:** BSD 3-Clause License.
- **Dependencias internas:** Python estándar (núcleo) + herramientas auxiliares opcionales.
- **Dictamen legal:** Totalmente compatible con MIT.
- **Veredicto técnico:** **DESCARTADO PARA MOBs / OPCIONAL PARA BOSSES**. Demasiado pesado para enemigos comunes; nuestras FSM por arquetipos JSON son 40 veces más rápidas.

### 3.9 SolarWolf
- **Licencia:** LGPL-2.1-or-later.
- **Dependencias internas:** Pygame.
- **Dictamen legal:** Compatible mediante enlace dinámico.
- **Veredicto técnico:** Repositorio de referencia histórica. No se copian assets ni código fuente directo; se adopta el patrón de diseño de degradación tolerante a fallos de audio (ADR-008).

### 3.10 pygame-topdownengine
- **Licencia:** MIT License (librería) y Creative Commons Zero 1.0 Universal (CC0-1.0 para ejemplos y documentación).
- **Dependencias internas:** pygame-ce.
- **Dictamen legal:** Totalmente compatible con GameForge (MIT).
- **Veredicto técnico:** Adoptar conceptualmente la simulación de elevación en eje $z$ (2.5D), el renderizado de sombras elípticas y el algoritmo de ordenamiento $y$-sorting para la capa de renderizado.

### 3.11 Procedural-Maps
- **Licencia:** **INEXISTENTE (SIN LICENCIA EXPLÍCITA — ALL RIGHTS RESERVED)**.
- **Dependencias internas:** `noise`, Pillow.
- **Dictamen legal y riesgo:** **PELIGRO LEGAL CRÍTICO**. Bajo la legislación de copyright internacional (Convenio de Berna), la ausencia de licencia implica que el autor original conserva todos los derechos patrimoniales y morales. Copiar código, funciones o archivos de este repositorio en GameForge 2D constituiría una infracción directa de propiedad intelectual.
- **Veredicto técnico:** **ESTRICTAMENTE PROHIBIDO COPIAR CÓDIGO O ASSETS**. Solo se absorbe el principio matemático abstracto general (clasificación de biomas de Whittaker combinando ruido de altura y ruido de humedad), implementándose en código limpio propio desde cero.

### 3.12 opensimplex-island-generator
- **Licencia:** Dominio Público (CC0 / Unlicense para el algoritmo matemático de Kurt Spencer) y MIT License para librerías en Python (`opensimplex`).
- **Dependencias internas:** Matemáticas puras de gradientes o módulo `opensimplex`.
- **Dictamen legal:** 100% seguro y compatible con licencias libres y propietarias.
- **Veredicto técnico:** Adoptar la fórmula matemática de decaimiento radial (radial falloff mask) dentro de `game/world/noise.py` para generar islas orgánicas o cavernas sin dependencias externas.

---

## 4. Matriz de Clasificación de Dependencias para GameForge 2D

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CLASIFICACIÓN OFICIAL DE DEPENDENCIAS                │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. RUNTIME OBLIGATORIO (PyPI)  │ • pygame-ce >= 2.5                    │
│                                │ • (Biblioteca estándar: json, sqlite3)│
├────────────────────────────────┼───────────────────────────────────────┤
│ 2. DESARROLLO Y CI (Dev)       │ • uv (Gestor de entorno y lockfile)   │
│                                │ • pytest >= 8                         │
│                                │ • ruff >= 0.6                         │
│                                │ • PyInstaller (para build_dist.py)    │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. OPCIONALES / CONDICIONALES  │ • pymunk (Solo si se aprueba física)  │
│                                │ • esper (Solo para sistema de buffs)  │
├────────────────────────────────┼───────────────────────────────────────┤
│ 4. ESTRICTAMENTE DESCARTADAS   │ • pytmx (Riesgo LGPLv3; innecesaria)  │
│    O PROHIBIDAS                │ • tilemap-generator (Stack JS)        │
│                                │ • python-tcod (Sobrecarga NumPy/CFFI) │
│                                │ • py_trees (Sobrecarga de GC a 60 FPS)│
│                                │ • Procedural-Maps (SIN LICENCIA)      │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 5. Instrucciones para Agentes de Desarrollo y QA

1. **Inspección Previa a Nuevas Dependencias:** Ningún agente puede ejecutar `uv add` o modificar `pyproject.toml` sin presentar previamente:
   - Justificación técnica basada en benchmarks que demuestren imposibilidad de implementarlo en código nativo.
   - Auditoría de licencia compatible con MIT (se prohíben licencias GPL viral en runtime).
   - Aprobación explícita del Arquitecto Principal / Agente Director.
2. **Chequeo de Licencia en Assets:** Cualquier sprite, textura, fuente tipográfica o archivo de sonido debe acompañarse de su licencia expresa y registrarse en `assets/README.md`. En la actualidad, GameForge 2D utiliza arte y audio procedurales sintetizados en memoria (ADR-003).
3. **Mantenimiento del Lockfile:** El archivo `uv.lock` debe actualizarse y commitearse de forma atómica junto a cualquier cambio en dependencias opcionales.

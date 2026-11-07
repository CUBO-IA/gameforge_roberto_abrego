# LICENSE_PROVENANCE_SYSTEM.md — GAMEFORGE 2D
## Marco Legal, Gobernanza de Licencias SPDX, Trazabilidad Criptográfica de Procedencia y Prevención de Contaminación Copyleft

**Estado:** ESPECIFICACIÓN NORMATIVA Y PROTOCOLO LEGAL  
**Misión:** MISIÓN 003 — Asset Ecosystem & GameForge Asset Hub  
**Fecha:** 2026-11-07  
**Autor:** Director / Arquitecto de Sistemas & Especialista Legal Open Source  
**Alcance:** Todos los activos gráficos, auditados, importados o creados para GameForge 2D  

---

## 1. Resumen Ejecutivo y Motivación Jurídica

En la industria del videojuego independiente y en el desarrollo de software impulsado por agentes de IA, los litigios e infracciones por uso no autorizado de activos protegidos por derechos de autor (*copyright*) o por incumplimiento involuntario de licencias de código abierto representan un riesgo operativo y financiero crítico.

Tres riesgos fundamentales amenazan a proyectos que integran arte externo:
1. **Contaminación Copyleft (*Viral License Contamination*):** La adopción descuidada de activos bajo licencias `GPLv3` o `CC-BY-SA 3.0/4.0` (como parte de los recursos de *Liberated Pixel Cup*) puede comprometer la licencia del resto del código o de otros activos si no se establece una frontera de separación clara entre el software y los datos creativos.
2. **Infracción de Cláusulas Restrictivas:** Uso inadvertido de material marcado como "No Comercial" (`CC-BY-NC`) o "Sin Derivadas" (`CC-BY-ND`), que imposibilita la venta comercial o cualquier adaptación gráfica (recorte, rotación, escalado).
3. **Pérdida de la Cadena de Custodia (*Provenance Loss*):** Archivos renombrados como `player_final.png` que pierden todo registro de quién fue el autor original, de qué repositorio o URL se descargó y qué modificaciones se le aplicaron.

Este documento establece el marco normativo obligatorio para GameForge 2D: una taxonomía de 4 niveles de riesgo (*Licensing Tiers*), un sistema de metadatos criptográficos (*Sidecar Metadata*) y un generador automático de avisos de atribución (*Credits & SBOM Generator*).

---

## 2. Distinción Jurídica Esencial: Código Software vs. Activos Creativos

En el derecho de propiedad intelectual internacional (Convenio de Berna, DMCA, Directivas Europeas de Derechos de Autor):
- **Código Software:** Protegido como obra literaria. Racionalizado mediante licencias como MIT, Apache 2.0, BSD o GNU GPL.
- **Activos Creativos (Arte 2D, Música, Modelos, Fuentes):** Protegidos como obras visuales y plásticas. Racionalizados típicamente mediante el ecosistema Creative Commons (CC) o licencias de dominio público (CC0).

### Doctrina de la "Mera Agregación" (*Mere Aggregation*)
Para evitar que un activo artístico licenciado bajo `CC-BY-SA` o `GPL` contamine el código fuente de GameForge 2D (licenciado bajo MIT):
1. **Aislamiento Físico y de Formato:** Los activos visuales se distribuyen en carpetas de datos independientes (`assets/` o paquetes de datos `.zip`/`.pak`) y se cargan dinámicamente mediante archivos estándar JSON y PNG.
2. **Sin Vinculación de Compilación (*No Binary Linking*):** Ningún gráfico se incrusta como código fuente en Python (evitar arrays hexadecimales de bytes en archivos `.py`).
3. **Comunicación por Interfaces Estándar:** El motor de juego lee los activos como flujos de datos externos, constituyendo una "mera agregación" legalmente válida y no una obra derivada integral.

---

## 3. Taxonomía de Cumplimiento de Licencias (Los 4 Niveles de Riesgo)

GameForge 2D clasifica cada recurso gráfico en uno de 4 niveles estandarizados basados en identificadores SPDX:

```
+-------------------------------------------------------------------------+
| NIVEL 0: Dominio Público / Cero Restricciones (CC0-1.0, Unlicense)     |
| Permite: Uso comercial, modificación, redistribución, sin atribución    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| NIVEL 1: Permisivo con Atribución (CC-BY-4.0, MIT, OGA-BY-3.0)         |
| Permite: Uso comercial y modificación. Exige: Atribución en CREDITS.md |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| NIVEL 2: Copyleft Artístico / ShareAlike (CC-BY-SA-3.0/4.0, GPLv3)      |
| Permite: Uso y modificación. Exige: Derivadas idénticas y aislamiento  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| NIVEL 3: RESTRINGIDO / PROHIBIDO (CC-NC, CC-ND, All Rights Reserved)   |
| ESTRICTAMENTE RECHAZADO: El Asset Hub bloquea su importación           |
+-------------------------------------------------------------------------+
```

### Tabla Comparativa de Licencias SPDX Soportadas

| Identificador SPDX | Nombre Formal | Nivel de Riesgo | ¿Uso Comercial? | ¿Modificación? | ¿Atribución Obligatoria? | ¿ShareAlike (Viral)? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`CC0-1.0`** | Creative Commons Zero 1.0 Universal | **Nivel 0** | Sí | Sí | No (Recomendada) | No |
| **`MIT`** | MIT License (aplicada a recursos) | **Nivel 1** | Sí | Sí | Sí | No |
| **`CC-BY-3.0`** | Creative Commons Attribution 3.0 | **Nivel 1** | Sí | Sí | Sí | No |
| **`CC-BY-4.0`** | Creative Commons Attribution 4.0 | **Nivel 1** | Sí | Sí | Sí | No |
| **`OGA-BY-3.0`** | OpenGameArt Attribution License 3.0 | **Nivel 1** | Sí | Sí | Sí | No |
| **`CC-BY-SA-3.0`** | Creative Commons Attribution-ShareAlike 3.0 | **Nivel 2** | Sí | Sí | Sí | **Sí (Solo obra derivada)** |
| **`CC-BY-SA-4.0`** | Creative Commons Attribution-ShareAlike 4.0 | **Nivel 2** | Sí | Sí | Sí | **Sí (Solo obra derivada)** |
| **`GPL-3.0-or-later`**| GNU General Public License v3 | **Nivel 2** | Sí | Sí | Sí | **Sí (Solo software/datos)** |
| **`CC-BY-NC-4.0`** | CC Attribution-NonCommercial | **Nivel 3** | **NO** | Sí | Sí | No |
| **`CC-BY-ND-4.0`** | CC Attribution-NoDerivatives | **Nivel 3** | Sí | **NO** | Sí | No |

---

## 4. Trazabilidad Criptográfica de Procedencia: Manifiesto Sidecar `.meta.json`

Cada archivo de activo binario importado en GameForge 2D (ej. `assets/sprites/enemies/skeleton.png`) debe contar de manera obligatoria e inseparable con su archivo homónimo de metadatos:  
`assets/sprites/enemies/skeleton.png.meta.json`.

### Estructura Normativa del Manifiesto de Procedencia

```json
{
  "$schema": "https://gameforge2d.org/schemas/gf-provenance-v1.json",
  "asset_file": "skeleton.png",
  "checksums": {
    "sha256": "4b5d27b9c9f688e1a6c4293f77341e459a930129bc564d6e902b45138122a611",
    "md5": "e2fc714c4727ee9395f324cd2e7f331f"
  },
  "provenance": {
    "source_repository": "OpenGameArt/LiberatedPixelCup",
    "original_filename": "skeleton_walk_slash.png",
    "upstream_url": "https://opengameart.org/content/liberated-pixel-cup-lpc-base-assets-sprites-map-tiles",
    "pinned_commit_or_version": "v1.2.0-lpc",
    "retrieved_date": "2026-11-07T00:45:00Z",
    "author": "Stephen Challener (Redshrike), Johannes Sjölund (wulax)"
  },
  "license": {
    "spdx_id": "CC-BY-SA-3.0",
    "tier": "tier_2_copyleft_warning",
    "full_license_url": "https://creativecommons.org/licenses/by-sa/3.0/legalcode",
    "attribution_notice": "Skeleton Warrior graphics by Stephen Challener (Redshrike) and Johannes Sjölund (wulax), created for the OpenGameArt Liberated Pixel Cup, licensed under CC-BY-SA 3.0.",
    "derivative_notice": "Modified by GameForge AI Agent: frames trimmed, ground pivot stabilized at [32, 58], packed into 512x512 atlas."
  },
  "governance": {
    "audited_by": "GameForge License Sentinel v1.0",
    "audit_status": "APPROVED_ISOLATED_DATA_PACK",
    "allow_commercial_bundle": true
  }
}
```

---

## 5. Prevención Automatizada de Contaminación en CI / Pre-Commit

Para cumplir con la directiva de calidad y disciplina (`01_GLOBAL.md` y `03_QUALITY_AND_SECURITY.md`), se establece un script de auditoría que se integra en `tools/verify.py`:

### Reglas de Validación de Integridad
1. **Regla L-01 (Sin Huérfanos):** Todo archivo `.png`, `.wav` u `.ogg` dentro de `assets/` sin su respectivo `.meta.json` bloquea de inmediato la verificación con un error explícito:
   `LicenseError: Archivo sin procedencia registrada: assets/sprites/foo.png`.
2. **Regla L-02 (Integridad Criptográfica):** Si el contenido de la imagen se altera sin actualizar su hash `sha256` en el metadato, la auditoría falla por manipulación no declarada.
3. **Regla L-03 (Bloqueo de Nivel 3):** Cualquier archivo marcado con `CC-BY-NC`, `CC-BY-ND` o `UNKNOWN` es rechazado y no puede añadirse al repositorio de control de versiones.
4. **Regla L-04 (Advertencia de Nivel 2):** Los activos bajo `CC-BY-SA` o `GPL` deben residir exclusivamente en directorios de datos desacoplados y nunca compilarse en binarios monolíticos.

---

## 6. Generador Automático de Créditos y SBOM (`CREDITS.md`)

El GameForge Asset Hub incluye un comando de exportación y un hook de compilación que recorre todos los archivos `.meta.json` de los activos utilizados efectivamente en el juego y genera automáticamente:

1. **`assets/README.md`:** Resumen técnico y legal para desarrolladores del repositorio.
2. **`CREDITS.md`:** Documento formal visible para el usuario final en el menú de pausa y créditos del juego, garantizando el cumplimiento al 100% de la cláusula de atribución de las licencias `CC-BY` y `CC-BY-SA`.
3. **`DISTRIBUTION_LICENSES.md`:** Lista exhaustiva de licencias de terceros para el instalador y la distribución ejecutable (`gameforge.spec`).

### Formato de Salida Generado para `CREDITS.md`

```markdown
# CRÉDITOS Y RECONOCIMIENTO DE ACTIVOS DE TERCEROS

GameForge 2D utiliza con gratitud recursos artísticos y sonoros creados por talentosos artistas de la comunidad de código abierto y dominio público. A continuación se detalla la atribución legal de cada activo utilizado en esta versión:

## Activos bajo Licencia Creative Commons Atribución-CompartirIgual 3.0 (CC-BY-SA 3.0)
- **LPC Base Sprites & Skeleton:** Creado por Stephen Challener (Redshrike) y Johannes Sjölund (wulax) para el concurso Liberated Pixel Cup de OpenGameArt.org. Licenciado bajo CC-BY-SA 3.0 / GPLv3. Modificado para estabilización de pivotes y formato gf-anim-v1.

## Activos bajo Licencia Creative Commons Zero 1.0 (CC0 - Dominio Público)
- **Kenney Tiny Dungeon & UI Pack RPG Expansion:** Creado por Kenney (https://kenney.nl). Dedicado al Dominio Público bajo CC0 1.0 Universal.
- **2D Asset Collection:** Curado por Tiddybub (https://github.com/Tiddybub/2d-assets). Licencia CC0 1.0.

*Nota de Cumplimiento Legal:* Los activos bajo licencia ShareAlike se distribuyen como paquetes de datos externos independientes. La inclusión de dichos recursos en el juego no altera la licencia MIT del motor de software de GameForge 2D, conforme a la doctrina de mera agregación de obras independientes.
```

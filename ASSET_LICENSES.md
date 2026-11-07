# Registro de Licencias y Procedencia de Assets — GameForge 2D

**Documento:** `ASSET_LICENSES.md`  
**Versión:** 1.0.0 (Aprobada tras Visual Overhaul — Misión 008)  
**Herramienta de Verificación:** `python -m tools.asset_hub validate --all`

---

## 1. Política de Licenciamiento y Trazabilidad

GameForge 2D mantiene una política estricta de propiedad intelectual y cumplimiento de licencias:
1. **Sin Dependencias de Servicios de Pago:** No se utiliza ningún servicio o API de generación de imágenes que imponga costes recurrentes o restricciones de uso comercial.
2. **Prioridad a Creación Interna y Recursos Libres Permisivos:** Todo el conjunto principal de arte del juego se genera internamente mediante el pipeline determinista `tools/artforge` bajo licencia permisiva MIT.
3. **Aislamiento de Recursos ShareAlike (Copyleft):** Cualquier recurso bajo licencias virales tipo ShareAlike (e.g. `CC-BY-SA-3.0` de Liberated Pixel Cup) se almacena de forma aislada en paquetes de datos específicos, documentando de forma transparente a los autores originales y asegurando que las modificaciones conserven la misma licencia sin afectar el código base del motor.
4. **Verificación Criptográfica:** Cada binario gráfico cuenta con una firma SHA-256 inmutable registrada en el catálogo `assets/hub_index.json`.

---

## 2. Inventario Completo de Activos y Licencias

| Identificador (ID) | Descripción y Dimensiones | Autor / Procedencia | Licencia SPDX | Categoría / Tier | Firma Digital SHA-256 | Requisitos de Atribución |
|---|---|---|---|---|---|---|
| `knight_hero` | Atlas jugador (624×150 px RGBA) | GameForge ArtForge | `MIT` | Permisivo (Tier 1) | `e9ce0c3a6beecef53abde6752fec9824d8ce4786c46a7ebd54cdc40052a466da` | Aviso de copyright de GameForge. |
| `slime` | Atlas cieno (192×128 px RGBA) | GameForge ArtForge | `MIT` | Permisivo (Tier 1) | `c63d546d75d917c2f2db64183f976e022049d2347871a2277b42ea375c2cb4f5` | Aviso de copyright de GameForge. |
| `wisp` | Atlas fuego fatuo (192×128 px RGBA) | GameForge ArtForge | `MIT` | Permisivo (Tier 1) | `0ca00dbb49455841b057e204d35a45471aa27e447d9ce1a3ef4da3cb4fa70bf8` | Aviso de copyright de GameForge. |
| `brute` | Atlas bruto escoria (288×322 px RGBA) | GameForge ArtForge | `MIT` | Permisivo (Tier 1) | `6333128b1cc1dc04f09f39e0da5ed37969c1d50c54ca4c7a64341669c766915a` | Aviso de copyright de GameForge. |
| `dungeon_tileset` | Tileset mazmorra (256×160 px RGBA) | GameForge ArtForge | `MIT` | Permisivo (Tier 1) | `6110fec6034346aa86ec70cb0750ca213d2948bb6fa076d5069fecf4460c44bb` | Aviso de copyright de GameForge. |
| `objects` | Props interactivos (252×102 px RGBA)| GameForge ArtForge | `MIT` | Permisivo (Tier 1) | `b680517fa977fb0317e1e6955a828691f1a5ba826b52c03c51323ca5530ecbb8` | Aviso de copyright de GameForge. |
| `particles` | Partículas VFX (96×32 px RGBA) | GameForge ArtForge | `MIT` | Permisivo (Tier 1) | `844aee8faec5668e1c6670aaef9ee8dfec5c731e84a56972e0b5711b7dfb8fb3` | Aviso de copyright de GameForge. |
| `ui` | Elementos 9-slice (236×88 px RGBA) | GameForge ArtForge | `MIT` | Permisivo (Tier 1) | `f0fa5a40bbfb7da5dcfa35029e0dc15a0c3bb20e3fb8f381014e7aebaa2226a2` | Aviso de copyright de GameForge. |
| `lpc_skeleton_warrior` | Atlas esqueleto (256×64 px RGBA) | Stephen Challener (Redshrike), Johannes Sjölund (wulax); LPC / OpenGameArt | `CC-BY-SA-3.0` | Copyleft (Tier 2) | `a84ba713ff48721c5fdfb2d69f706596395b05786ca1b2c45330a845fca683fe` | Atribución explícita a Redshrike y wulax; cualquier redistribución derivada del atlas mantiene CC-BY-SA-3.0. |
| `kenney_dungeon_stone_32`| Tileset muestra (128×128 px RGBA) | Kenney (Tiny Dungeon) | `CC0-1.0` | Dominio Público (Tier 0) | `32f1ea38ba1b700ef58a2e1d7cf9d1a34dbeab299e504be6620ca94b7f8f9e61` | Sin obligación de atribución (atribución conservada por buena fe). |
| `kenney_roguelike_guard` | Sprite muestra (32×16 px RGBA) | Kenney (Roguelike RPG Pack) | `CC0-1.0` | Dominio Público (Tier 0) | `5f6d7e21a2245c38676dc4c5be7be26ca3d9e29f86be2e4aa366cb4b5b7cb851` | Sin obligación de atribución. |
| `fantasy_dialog_box_9slice` | Marco diálogo (96×96 px RGBA) | Kenney (UI Pack RPG Expansion) | `CC0-1.0` | Dominio Público (Tier 0) | `cfebfba4bbbe4910cf3c88e79b9487c6742512f43cf0bf2404e1834927cb7801` | Sin obligación de atribución. |

---

## 3. Protocolo de Acreditación Automática

El subsistema Asset Hub cuenta con un generador automático de créditos (`tools/asset_hub/credits.py`):
```bash
python -m tools.asset_hub credits
```
Este comando examina todos los activos catalogados y sincroniza el archivo `CREDITS.md` en la raíz del repositorio, garantizando que ninguna versión distribuida carezca de las menciones legales correspondientes.

---

## 4. Estado de Validación

El último análisis de auditoría legal y técnica ejecutado con:
```bash
python -m tools.asset_hub validate --all
```
produjo el siguiente resultado verificado:
- **Total de activos evaluados:** 8
- **Activos aprobados:** 8 (100%)
- **Errores de licencia o integridad:** 0
- **Avisos controlados:** 1 (Aviso de cláusula ShareAlike en `lpc_skeleton_warrior`, debidamente aislado en datos y con atribución en `CREDITS.md`).

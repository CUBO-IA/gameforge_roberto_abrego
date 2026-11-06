"""Escena principal: partida, interacción, combate y guardado."""

from __future__ import annotations

import math
import random

import pygame

from game.core.math2d import Vec2, circles_overlap
from game.entities.enemies import Enemy, separate_enemies
from game.entities.interactables import Campfire, Chest, ForgeAltar
from game.entities.items import ITEMS
from game.entities.player import Player
from game.entities.projectiles import Projectile
from game.input.actions import Action
from game.persistence.savegame import RunSnapshot, SaveGameError, save_run
from game.persistence.scores import RunResult
from game.render import entity_renderer, palette
from game.render.effects import Effects
from game.render.entity_renderer import draw_attack_arc
from game.render.hud import Hud
from game.render.lighting import Lighting
from game.render.tile_renderer import TileRenderer
from game.scenes.base import Scene
from game.systems.combat import resolve_player_attack
from game.systems.inventory import Inventory, InventoryError
from game.systems.quest import QuestState
from game.world.camera import Camera
from game.world.collision import circle_hits_solid
from game.world.generation import generate_dungeon
from game.world.tilemap import TileMap


class PlayScene(Scene):
    def __init__(self, app, snapshot: RunSnapshot | None = None, seed: int | None = None) -> None:
        super().__init__(app)
        self.time = 0.0
        self.elapsed = 0.0
        self.score = 0
        self.kills = 0
        self.floor = snapshot.floor if snapshot else 1
        if snapshot is None:
            run_seed = seed if seed is not None else random.SystemRandom().randrange(1, 2**31)
        else:
            run_seed = snapshot.seed
        self.dungeon = generate_dungeon(run_seed, self.floor, app.config.dungeon)
        self.tilemap: TileMap = self.dungeon.tilemap
        self.player = Player(self.dungeon.spawn, app.config.player)
        self.inventory = Inventory()
        self.quest = QuestState(app.config.dungeon.shards_required)
        self.chests = [
            Chest(spec.id, spec.position, spec.item_id, spec.quantity)
            for spec in self.dungeon.chests
        ]
        self.enemies = [
            Enemy(spec.id, spec.kind, spec.position, app.config.enemies[spec.kind])
            for spec in self.dungeon.enemies
        ]
        self.campfire = Campfire(self.dungeon.campfire)
        self.altar = ForgeAltar(self.dungeon.altar)
        self.projectiles: list[Projectile] = []
        self.chests_opened: set[str] = set()
        self.defeated_ids: set[str] = set()

        if snapshot is not None:
            self._restore(snapshot)

        self.effects = Effects((app.config.window.width, app.config.window.height))
        self.camera = Camera(app.config.window.width, app.config.window.height)
        self.camera.snap_to(self.player.position, self.tilemap.pixel_width, self.tilemap.pixel_height)
        self.tile_renderer = TileRenderer(self.tilemap)
        self.lighting = Lighting((app.config.window.width, app.config.window.height))
        self.hud = Hud(
            app.fonts,
            self.tilemap,
            self.quest,
            (app.config.window.width, app.config.window.height),
        )
        self.rng = random.Random(run_seed ^ 0x5F3759DF)
        self.paused = False
        self.show_inventory = False
        self.toast = ""
        self.toast_timer = 0.0
        self.save_hint = ""
        self.nearby: tuple[object, str] | None = None
        self.victory_timer = -1.0
        self.finished = False
        self._hurt_overlay = pygame.Surface(
            (app.config.window.width, app.config.window.height), pygame.SRCALPHA
        )
        self._fade = pygame.Surface(
            (app.config.window.width, app.config.window.height), pygame.SRCALPHA
        )

    # ------------------------------------------------------------------ setup

    def _restore(self, snapshot: RunSnapshot) -> None:
        self.elapsed = snapshot.elapsed
        self.score = snapshot.score
        self.kills = snapshot.kills
        try:
            self.inventory = Inventory.from_dict(snapshot.inventory)
        except InventoryError as exc:
            raise SaveGameError(f"Inventario guardado inválido: {exc}") from exc
        self.chests_opened = set(snapshot.chests_opened)
        for chest in self.chests:
            chest.opened = chest.id in self.chests_opened
        self.defeated_ids = set(snapshot.defeated)
        self.enemies = [enemy for enemy in self.enemies if enemy.id not in self.defeated_ids]
        self.quest.altar_activated = snapshot.altar_activated
        self.altar.activated = snapshot.altar_activated
        position = Vec2(snapshot.player_x, snapshot.player_y)
        if circle_hits_solid(self.tilemap, position, self.player.radius):
            position = self.dungeon.spawn
        self.player.position = position
        self.player.health = max(0.5, min(snapshot.health, self.player.max_health))

    def on_enter(self) -> None:
        self.app.input.reset()

    # ------------------------------------------------------------------ events

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.finished or self.victory_timer >= 0:
            return
        if event.type != pygame.KEYDOWN:
            return
        input_map = self.app.input
        if self.paused:
            if input_map.was_pressed(Action.PAUSE):
                self.paused = False
                self.app.audio.play("ui")
            elif input_map.was_pressed(Action.SAVE):
                self._save()
            elif input_map.was_pressed(Action.MENU):
                self._to_menu()
            return
        if self.show_inventory:
            if input_map.was_pressed(Action.INVENTORY) or input_map.was_pressed(Action.PAUSE):
                self.show_inventory = False
                self.app.audio.play("ui")
            elif input_map.was_pressed(Action.POTION):
                self._use_potion()
            return
        if input_map.was_pressed(Action.PAUSE):
            self.paused = True
            self.save_hint = ""
            self.app.audio.play("ui")
        elif input_map.was_pressed(Action.INVENTORY):
            self.show_inventory = True
            self.app.audio.play("ui")
        elif input_map.was_pressed(Action.SAVE):
            self._save()

    # ------------------------------------------------------------------ update

    def update(self, dt: float) -> None:
        self.time += dt
        self.effects.update(dt, self.player.position)
        if self.paused or self.show_inventory:
            return
        if self.toast_timer > 0:
            self.toast_timer = max(0.0, self.toast_timer - dt)
        if self.victory_timer >= 0:
            self.victory_timer -= dt
            if self.victory_timer <= 0:
                self._finish(victory=True)
            return
        if self.finished:
            return

        input_map = self.app.input
        move = input_map.move_vector()
        mouse_world = self.camera.screen_to_world(Vec2(*input_map.mouse_position))
        aim = mouse_world - self.player.position
        attack = input_map.mouse_was_pressed(1) or input_map.was_pressed(Action.ATTACK)
        dash = input_map.was_pressed(Action.DASH)

        self.player.update(dt, move, aim, dash, attack, self.tilemap)
        if self.player.dash_started:
            self.app.audio.play("dash")
            self.effects.burst(self.player.position, palette.ACCENT, 10, 90)
            self.effects.shake.add(2.0)

        if self.player.pending_attack is not None:
            hits = resolve_player_attack(self.player.pending_attack, self.enemies)
            if hits:
                self.app.audio.play("hit")
                self.effects.shake.add(3.0)
                for enemy in hits:
                    self.effects.burst(
                        enemy.position,
                        palette.ENEMY_COLORS.get(enemy.kind, palette.TEXT),
                        10,
                        170,
                        add=True,
                    )
                    if not enemy.alive:
                        self._kill(enemy)
                self.enemies = [enemy for enemy in self.enemies if enemy.alive]

        for enemy in list(self.enemies):
            if not enemy.alive:
                continue
            intent = enemy.update(
                dt, self.player.position, self.player.radius, self.tilemap, self.rng
            )
            if intent.projectile is not None:
                spec = intent.projectile
                self.projectiles.append(
                    Projectile(
                        position=spec.origin,
                        velocity=spec.direction * spec.speed,
                        radius=spec.radius,
                        damage=spec.damage,
                        color=palette.VIOLET,
                    )
                )
                self.app.audio.play("shoot")
            if circles_overlap(
                enemy.position, enemy.radius, self.player.position, self.player.radius
            ) and enemy.touch_cooldown <= 0.0:
                enemy.touch_cooldown = 0.8
                if self.player.take_damage(enemy.stats.touch_damage, enemy.position):
                    self._hurt(enemy.stats.touch_damage)

        separate_enemies(self.enemies, self.tilemap)

        for projectile in list(self.projectiles):
            projectile.update(dt, self.tilemap)
            if not projectile.alive:
                self.projectiles.remove(projectile)
                continue
            if circles_overlap(
                projectile.position,
                projectile.radius,
                self.player.position,
                self.player.radius,
            ):
                projectile.alive = False
                self.projectiles.remove(projectile)
                self.effects.burst(projectile.position, palette.VIOLET, 10, 120, add=True)
                if self.player.take_damage(projectile.damage, projectile.position):
                    self._hurt(projectile.damage)

        self.elapsed += dt
        self.camera.update(
            self.player.position,
            dt,
            self.tilemap.pixel_width,
            self.tilemap.pixel_height,
        )
        self.nearby = self._nearest_interaction()
        if input_map.was_pressed(Action.INTERACT):
            self._interact()
        elif input_map.was_pressed(Action.POTION):
            self._use_potion()

        if not self.player.alive:
            self._finish(victory=False)

    def _hurt(self, amount: float) -> None:
        self.effects.add_text(f"-{int(amount)}", self.player.position, (255, 120, 110), 22)
        self.effects.burst(self.player.position, (220, 80, 90), 12, 140)
        self.effects.shake.add(5.0)
        self.app.audio.play("hit")

    def _kill(self, enemy: Enemy) -> None:
        if enemy.id in self.defeated_ids:
            return
        self.defeated_ids.add(enemy.id)
        self.kills += 1
        self.score += enemy.stats.score
        self.effects.add_text(
            f"+{enemy.stats.score}", enemy.position + Vec2(0, -12), palette.GOLD, 20
        )
        self.effects.burst(
            enemy.position, palette.ENEMY_COLORS.get(enemy.kind, palette.TEXT), 22, 220, add=True
        )
        self.effects.shake.add(3.0)

    def _nearest_interaction(self) -> tuple[object, str] | None:
        candidates: list[tuple[float, object, str]] = []
        for chest in self.chests:
            if chest.opened:
                continue
            distance = chest.position.distance_to(self.player.position)
            if distance <= 54.0:
                candidates.append((distance, chest, "Abrir cofre"))
        distance = self.campfire.position.distance_to(self.player.position)
        if distance <= 62.0:
            candidates.append((distance, self.campfire, "Descansar y guardar"))
        distance = self.altar.position.distance_to(self.player.position)
        if distance <= 74.0 and not self.altar.activated:
            remaining = self.quest.shards_required - self.inventory.count("shard")
            label = (
                "Activar la Fragua"
                if remaining <= 0
                else f"Fragua: faltan {remaining} fragmentos"
            )
            candidates.append((distance, self.altar, label))
        if not candidates:
            return None
        candidates.sort(key=lambda entry: entry[0])
        return candidates[0][1], candidates[0][2]

    def _interact(self) -> None:
        if self.nearby is None:
            return
        obj = self.nearby[0]
        if isinstance(obj, Chest):
            self._open_chest(obj)
        elif isinstance(obj, Campfire):
            self._rest()
        elif isinstance(obj, ForgeAltar):
            self._activate_altar()
        self.nearby = self._nearest_interaction()

    def _open_chest(self, chest: Chest) -> None:
        if chest.opened:
            return
        accepted = self.inventory.add(chest.item_id, chest.quantity)
        if accepted <= 0:
            self._toast("Inventario lleno. Usa o descarta algo primero.")
            self.app.audio.play("denied")
            return
        chest.opened = True
        self.chests_opened.add(chest.id)
        item = ITEMS[chest.item_id]
        self.app.audio.play("pickup")
        self.effects.burst(chest.position, item.color, 16, 120, add=True)
        self.effects.add_text(f"+{accepted} {item.name}", chest.position + Vec2(0, -20), item.color, 20)
        if chest.item_id == "coin":
            self.score += accepted
        elif chest.item_id == "shard":
            collected = self.inventory.count("shard")
            self._toast(f"Fragmento de ascua {collected}/{self.quest.shards_required}")
        else:
            self._toast(f"Encontraste {item.name} x{accepted}")

    def _rest(self) -> None:
        healed = self.player.heal(self.player.max_health)
        save_error = self._save(show_toast=False)
        if save_error:
            self._toast(f"Descanso: +{int(healed)} salud. Error al guardar: {save_error}", 4.0)
        else:
            self._toast(f"Descanso: +{int(healed)} salud. Partida guardada.")
        self.app.audio.play("heal")
        self.effects.burst(self.player.position, palette.GREEN, 20, 90, add=True)

    def _activate_altar(self) -> None:
        if self.quest.altar_activated:
            return
        if self.quest.activate(self.inventory):
            self.altar.activated = True
            self.score += 500
            self.victory_timer = 2.2
            self.app.audio.play("victory")
            self.effects.burst(self.altar.position, palette.ACCENT, 60, 280, add=True)
            self.effects.shake.add(10.0)
            self._toast("La Fragua despierta. La ascua vuelve a arder.")
        else:
            remaining = self.quest.shards_required - self.inventory.count("shard")
            self._toast(f"La Fragua exige {remaining} fragmento(s) más.")
            self.app.audio.play("denied")

    def _use_potion(self) -> None:
        if self.inventory.count("potion") <= 0:
            self._toast("No tienes frascos de brasa.")
            self.app.audio.play("denied")
            return
        if self.player.health >= self.player.max_health:
            self._toast("Tu salud ya está completa.")
            self.app.audio.play("denied")
            return
        self.inventory.remove("potion", 1)
        healed = self.player.heal(self.app.config.player.potion_heal)
        self.app.audio.play("heal")
        self.effects.add_text(f"+{int(healed)}", self.player.position, palette.GREEN, 24)
        self.effects.burst(self.player.position, palette.GREEN, 18, 110, add=True)
        self._toast(f"Frasco de brasa: +{int(healed)} salud.")

    def _toast(self, text: str, duration: float = 2.8) -> None:
        self.toast = text
        self.toast_timer = duration

    def _save(self, show_toast: bool = True) -> str | None:
        snapshot = RunSnapshot(
            seed=self.dungeon.seed,
            floor=self.floor,
            elapsed=self.elapsed,
            score=self.score,
            kills=self.kills,
            player_x=self.player.position.x,
            player_y=self.player.position.y,
            health=self.player.health,
            inventory=self.inventory.to_dict(),
            chests_opened=tuple(sorted(self.chests_opened)),
            defeated=tuple(sorted(self.defeated_ids)),
            altar_activated=self.quest.altar_activated,
        )
        try:
            save_run(self.app.save_path, snapshot)
        except SaveGameError as exc:
            self.save_hint = "Error al guardar"
            self._toast(f"No se pudo guardar: {exc}", 4.0)
            self.app.audio.play("denied")
            return str(exc)
        self.save_hint = "Partida guardada"
        if show_toast:
            self._toast("Partida guardada.")
            self.app.audio.play("interact")
        return None

    def _to_menu(self) -> None:
        from game.scenes.menu import MenuScene

        self.app.audio.play("ui")
        self.app.replace_scene(MenuScene(self.app))

    def _finish(self, victory: bool) -> None:
        if self.finished:
            return
        self.finished = True
        shards = self.inventory.count("shard")
        self.score += shards * 100 + self.floor * 50 + (500 if victory else 0)
        result = RunResult(
            seed=self.dungeon.seed,
            floor=self.floor,
            score=self.score,
            kills=self.kills,
            duration=self.elapsed,
            victory=victory,
        )
        record_error = self.app.record_result(result)
        delete_error = self.app.discard_save()
        if delete_error:
            record_error = (
                f"{record_error} {delete_error}" if record_error else delete_error
            )
        from game.scenes.results import ResultsScene, RunSummary

        summary = RunSummary(
            victory=victory,
            score=self.score,
            kills=self.kills,
            duration=self.elapsed,
            floor=self.floor,
            shards=shards,
            seed=self.dungeon.seed,
            record_error=record_error,
        )
        self.app.replace_scene(ResultsScene(self.app, summary))

    # ------------------------------------------------------------------ draw

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(palette.BACKGROUND_DEEP)
        shake = self.effects.current_shake()
        top_left = self.camera.top_left + shake
        surface.blit(self.tile_renderer.surface, (-int(top_left.x), -int(top_left.y)))
        self.tile_renderer.draw_animated(surface, self.camera, self.time, shake)

        drawables: list[tuple[float, str, object]] = []
        for chest in self.chests:
            drawables.append((chest.position.y, "chest", chest))
        drawables.append((self.campfire.position.y, "campfire", self.campfire))
        drawables.append((self.altar.position.y, "altar", self.altar))
        for enemy in self.enemies:
            drawables.append((enemy.position.y, "enemy", enemy))
        for projectile in self.projectiles:
            drawables.append((projectile.position.y, "projectile", projectile))
        drawables.append((self.player.position.y, "player", self.player))
        drawables.sort(key=lambda item: item[0])

        for _, kind, obj in drawables:
            if kind == "chest":
                entity_renderer.draw_chest(
                    surface,
                    obj,
                    self.camera,
                    shake,
                    self.time,
                    self.nearby is not None and self.nearby[0] is obj,
                )
            elif kind == "campfire":
                entity_renderer.draw_campfire(
                    surface,
                    obj,
                    self.camera,
                    shake,
                    self.time,
                    self.nearby is not None and self.nearby[0] is obj,
                )
            elif kind == "altar":
                entity_renderer.draw_altar(
                    surface,
                    obj,
                    self.camera,
                    shake,
                    self.time,
                    self.inventory.count("shard"),
                    self.quest.shards_required,
                    self.nearby is not None and self.nearby[0] is obj,
                )
            elif kind == "enemy":
                entity_renderer.draw_enemy(
                    surface, obj, self.player.position, self.camera, shake, self.time
                )
            elif kind == "projectile":
                entity_renderer.draw_projectile(surface, obj, self.camera, shake)
            else:
                entity_renderer.draw_player(surface, obj, self.camera, shake, self.time)

        draw_attack_arc(
            surface,
            self.player,
            self.camera,
            shake,
            (surface.get_width(), surface.get_height()),
        )
        self.effects.draw(surface, self.camera, self.app.fonts, shake=shake)

        flicker = 1.0 + 0.08 * math.sin(self.time * 9.0)
        lights = [
            (self.player.position, 270, 1.0),
            (self.campfire.position, int(175 * flicker), 1.0),
            (self.altar.position, 190, 1.0),
        ]
        for projectile in self.projectiles:
            lights.append((projectile.position, 70, 0.8))
        self.lighting.render(surface, lights, self.camera, shake)

        if self.player.damage_flash > 0:
            alpha = int(110 * min(1.0, self.player.damage_flash * 5))
            self._hurt_overlay.fill((160, 20, 30, alpha))
            surface.blit(self._hurt_overlay, (0, 0))

        self.hud.draw(
            surface,
            self.player,
            self.inventory,
            self.altar.position,
            self.campfire.position,
            self.floor,
            self.elapsed,
            self.score,
            self.nearby[1] if self.nearby else None,
            self.toast,
            self.toast_timer,
            self.app.input.mouse_position,
            self.app.fps,
        )

        if self.show_inventory:
            self.hud.draw_inventory(surface, self.inventory)
        elif self.paused:
            self.hud.draw_pause(surface, self.save_hint)

        if self.victory_timer >= 0:
            progress = 1.0 - max(0.0, self.victory_timer) / 2.2
            self._fade.fill((255, 200, 130, int(200 * min(1.0, progress))))
            surface.blit(self._fade, (0, 0))

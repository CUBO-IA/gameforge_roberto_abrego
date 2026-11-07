"""Escena principal: orquesta input, sistemas de simulación y presentación.

Las reglas de dominio viven en ``game.sim`` (combate, interacción, botín,
engagement, progresión) y el dibujo del mundo en ``game.render.world_view``;
esta escena traduce entrada a intenciones y resultados a presentación.
"""

from __future__ import annotations

import random

import pygame

from game.ai.astar import clear_path_cache
from game.ai.dijkstra import DijkstraMap
from game.core.math2d import Vec2
from game.entities.enemies import Enemy
from game.entities.interactables import Campfire, Chest, ForgeAltar
from game.entities.items import ITEMS
from game.entities.player import Player
from game.entities.projectiles import Projectile
from game.input.actions import Action
from game.persistence.savegame import RunSnapshot, SaveGameError, save_run
from game.persistence.scores import RunResult
from game.render import palette
from game.render.effects import Effects
from game.render.hud import Hud
from game.render.lighting import Lighting
from game.render.tile_renderer import TileRenderer
from game.render.world_view import draw_lighting, draw_play_overlay, draw_play_world
from game.scenes.base import Scene
from game.sim.combat import resolve_player_attack
from game.sim.crafting import craft, load_recipes
from game.sim.engagement import (
    move_projectiles,
    projectile_hits_player,
    spawn_projectile,
    update_enemies,
)
from game.sim.floor import (
    FloorType,
    finish_score,
    floor_theme_name,
    floor_type_for,
    is_final_floor,
    shards_required_for_floor,
)
from game.sim.interaction import (
    find_nearest_interaction,
    loot_message,
    open_chest,
    use_potion,
)
from game.sim.quest import QuestManager
from game.systems.inventory import Inventory, InventoryError
from game.systems.quest import QuestState
from game.world.camera import Camera
from game.world.cavern_generation import generate_cavern
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
        if floor_type_for(self.floor) == FloorType.CAVERN:
            self.dungeon = generate_cavern(run_seed, self.floor, app.config.dungeon)
        else:
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
        self.quest_manager = QuestManager()
        self.quest_manager.start_floor(self.floor)
        try:
            self.recipes = {r.id: r for r in load_recipes()}
        except Exception:
            self.recipes = {}

        if snapshot is not None:
            self._restore(snapshot)

        self.effects = Effects((app.config.window.width, app.config.window.height))
        self.camera = Camera(app.config.window.width, app.config.window.height)
        self.camera.snap_to(self.player.position, self.tilemap.pixel_width, self.tilemap.pixel_height)
        self.tile_renderer = TileRenderer(self.tilemap)
        self.dijkstra_map = DijkstraMap(self.tilemap)
        self.lighting = Lighting((app.config.window.width, app.config.window.height))
        self.hud = Hud(
            app.fonts,
            self.tilemap,
            self.quest,
            (app.config.window.width, app.config.window.height),
        )
        self.rng = random.Random(run_seed ^ 0x5F3759DF)
        self.frame_counter = 0
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
        jump = input_map.was_pressed(Action.JUMP)

        self.player.update(dt, move, aim, dash, attack, self.tilemap, jump=jump)
        if self.player.jump_started:
            self.effects.burst(self.player.position, palette.TEXT_MUTED, 6, 40)
        if self.player.ceiling_hit:
            self.effects.burst(self.player.position - Vec2(0, self.player.z), palette.TEXT_MUTED, 4, 30)
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

        self.frame_counter += 1
        events = update_enemies(
            self.enemies,
            dt,
            self.player,
            self.tilemap,
            self.rng,
            self.frame_counter,
            dijkstra_map=self.dijkstra_map,
        )
        for spec in events.projectiles:
            self.projectiles.append(spawn_projectile(spec))
            self.app.audio.play("shoot")
        for damage in events.touch_damage:
            self._hurt(damage)

        self.projectiles = move_projectiles(self.projectiles, dt, self.tilemap)
        for projectile in list(self.projectiles):
            if projectile_hits_player(projectile, self.player):
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
        self.nearby = find_nearest_interaction(
            self.chests,
            self.campfire,
            self.altar,
            self.player.position,
            self.inventory.count("shard"),
            self.quest.shards_required,
        )
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
        for reward in self.quest_manager.on_kill(enemy.kind, self.inventory):
            self.score += reward.score
            self._toast(f"Misión: {reward.title} (+{reward.score} pts)")

    # ------------------------------------------------------------------ interact

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
        self.nearby = find_nearest_interaction(
            self.chests,
            self.campfire,
            self.altar,
            self.player.position,
            self.inventory.count("shard"),
            self.quest.shards_required,
        )

    def _open_chest(self, chest: Chest) -> None:
        result = open_chest(chest, self.inventory)
        if result is None:
            return
        item = ITEMS[result.item_id]
        if result.full:
            self._toast(loot_message(result, self.quest.shards_required, 0))
            self.app.audio.play("denied")
            return
        chest.opened = True
        self.chests_opened.add(chest.id)
        self.app.audio.play("pickup")
        self.effects.burst(chest.position, item.color, 16, 120, add=True)
        self.effects.add_text(
            f"+{result.quantity} {item.name}", chest.position + Vec2(0, -20), item.color, 20
        )
        for reward in self.quest_manager.on_chest_opened(self.inventory):
            self.score += reward.score
            self._toast(f"Misión: {reward.title} (+{reward.score} pts)")
        if result.item_id == "coin":
            self.score += result.quantity
        else:
            self._toast(
                loot_message(
                    result, self.quest.shards_required, self.inventory.count("shard")
                )
            )

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
            for reward in self.quest_manager.on_altar_activated(self.inventory):
                self.score += reward.score
                self._toast(f"Misión: {reward.title} (+{reward.score} pts)")

            if is_final_floor(self.floor):
                self.victory_timer = 2.2
                self.app.audio.play("victory")
                self.effects.burst(self.altar.position, palette.ACCENT, 60, 280, add=True)
                self.effects.shake.add(10.0)
                self._toast("¡La Fragua Suprema despierta! Has conquistado el Núcleo.")
            else:
                self.app.audio.play("victory")
                self.effects.burst(self.altar.position, palette.ACCENT, 50, 240, add=True)
                self.effects.shake.add(8.0)
                self._descend_floor()
        else:
            remaining = self.quest.shards_required - self.inventory.count("shard")
            self._toast(f"El Altar exige {remaining} fragmento(s) más.")
            self.app.audio.play("denied")

    def _descend_floor(self) -> None:
        self.floor += 1
        clear_path_cache()
        if floor_type_for(self.floor) == FloorType.CAVERN:
            self.dungeon = generate_cavern(self.dungeon.seed, self.floor, self.app.config.dungeon)
        else:
            self.dungeon = generate_dungeon(self.dungeon.seed, self.floor, self.app.config.dungeon)
        self.tilemap = self.dungeon.tilemap
        self.dijkstra_map = DijkstraMap(self.tilemap)
        self.tile_renderer = TileRenderer(self.tilemap)
        self.camera.snap_to(
            self.dungeon.spawn, self.tilemap.pixel_width, self.tilemap.pixel_height
        )
        self.player.position = self.dungeon.spawn
        self.chests = [
            Chest(spec.id, spec.position, spec.item_id, spec.quantity)
            for spec in self.dungeon.chests
        ]
        self.enemies = [
            Enemy(spec.id, spec.kind, spec.position, self.app.config.enemies[spec.kind])
            for spec in self.dungeon.enemies
        ]
        self.campfire = Campfire(self.dungeon.campfire)
        self.altar = ForgeAltar(self.dungeon.altar)
        self.projectiles.clear()
        self.chests_opened.clear()
        self.defeated_ids.clear()

        new_shards = shards_required_for_floor(self.floor)
        self.quest = QuestState(new_shards)
        self.quest_manager.start_floor(self.floor)
        self.hud = Hud(
            self.app.fonts,
            self.tilemap,
            self.quest,
            (self.app.config.window.width, self.app.config.window.height),
        )

        theme = floor_theme_name(self.floor)
        self._toast(f"Has descendido a {theme} (Planta {self.floor}).")
        self._save(show_toast=False)

    def craft_recipe(self, recipe_id: str) -> bool:
        recipe = self.recipes.get(recipe_id)
        if recipe is None:
            return False
        result = craft(recipe, self.inventory)
        if result.success:
            self.app.audio.play("pickup")
            self._toast(result.message)
            return True
        self.app.audio.play("denied")
        self._toast(result.message)
        return False

    def _use_potion(self) -> None:
        result = use_potion(self.player, self.inventory, self.app.config.player.potion_heal)
        if result.status == "empty":
            self._toast("No tienes frascos de brasa.")
            self.app.audio.play("denied")
            return
        if result.status == "full_health":
            self._toast("Tu salud ya está completa.")
            self.app.audio.play("denied")
            return
        healed = result.healed
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
        self.score += finish_score(shards, self.floor, victory)
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
        draw_play_world(
            surface,
            tile_renderer=self.tile_renderer,
            camera=self.camera,
            effects=self.effects,
            lighting=self.lighting,
            time=self.time,
            player=self.player,
            enemies=self.enemies,
            projectiles=self.projectiles,
            chests=self.chests,
            campfire=self.campfire,
            altar=self.altar,
            nearby=self.nearby,
            shard_count=self.inventory.count("shard"),
            shards_required=self.quest.shards_required,
        )
        shake = self.effects.current_shake()
        draw_lighting(
            surface,
            self.lighting,
            self.camera,
            shake,
            self.time,
            self.player,
            self.campfire,
            self.altar,
            self.projectiles,
        )
        draw_play_overlay(
            surface,
            effects=self.effects,
            hud=self.hud,
            fonts=self.app.fonts,
            camera=self.camera,
            shake=shake,
            player=self.player,
            inventory=self.inventory,
            altar=self.altar,
            campfire=self.campfire,
            floor=self.floor,
            elapsed=self.elapsed,
            score=self.score,
            nearby=self.nearby,
            toast=self.toast,
            toast_timer=self.toast_timer,
            mouse_position=self.app.input.mouse_position,
            fps=self.app.fps,
            show_inventory=self.show_inventory,
            paused=self.paused,
            save_hint=self.save_hint,
            victory_timer=self.victory_timer,
            hurt_overlay=self._hurt_overlay,
            fade=self._fade,
        )

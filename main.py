import arcade
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from pyglet.graphics import Batch
import math
import random

tower_types = {"apple": 50}


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.GRAY)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

    def setup_widgets(self):
        label = UILabel(text="Текст",
                        font_size=20,
                        text_color=arcade.color.WHITE,
                        width=300,
                        multiline=True,
                        align="center")
        self.box_layout.add(label)
        flat_button = UIFlatButton(text="Играть", width=200, height=50, color=arcade.color.BLUE)
        flat_button.on_click = self.play_game
        self.box_layout.add(flat_button)
        flat_button2 = UIFlatButton(text="Выход", width=200, height=50, color=arcade.color.RED)
        flat_button2.on_click = self.exit_game
        self.box_layout.add(flat_button2)

    def on_draw(self):
        self.clear()
        self.manager.draw()  # Рисуй GUI поверх всего

    def play_game(self, event):
        level_selecton = LevelSelectionView()
        self.window.show_view(level_selecton)

    def exit_game(self, event):
        arcade.exit()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()


class LevelSelectionView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.LIGHT_GRAY)
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

    def setup_widgets(self):
        label = UILabel(text="Выберите уровень",
                        font_size=20,
                        text_color=arcade.color.BLUE,
                        width=300,
                        multiline=True,
                        align="center")
        label.center_x = 400
        label.center_y = 300
        button_level_1 = UIFlatButton(text='Первый уровень', width=200, height=50, color=arcade.color.BLUE)
        button_level_1.on_click = self.play_level_1

        self.manager.add(label)
        self.manager.add(button_level_1)

    def on_draw(self):
        self.clear()
        self.manager.draw()  # Рисуй GUI поверх всего

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Для кликов, но manager сам обрабатывает

    def play_level_1(self, event):
        game_view = Level1View()
        self.window.show_view(game_view)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.LIGHT_GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()


class Enemy(arcade.Sprite):
    def __init__(self, path_points, speed=100, hp=100, scale=0.05,
                 img='imgs/ooze-monster-clip-art-slime-814deb4f1a447995e26ae0b10b344fe6.png'):

        super().__init__(img, scale=scale)

        self.hp = hp
        self.path = path_points
        self.speed = speed
        self.path_index = 0

        self.center_x, self.center_y = self.path[0]

    def update(self, delta_time):
        if self.path_index >= len(self.path) - 1:
            return

        dest_x, dest_y = self.path[self.path_index + 1]
        dx = dest_x - self.center_x
        dy = dest_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            self.path_index += 1
            return

        step = self.speed * delta_time

        if dist <= step:
            self.center_x, self.center_y = dest_x, dest_y
            self.path_index += 1
        else:
            self.center_x += dx / dist * step
            self.center_y += dy / dist * step

    def reached_end(self):
        return self.path_index >= len(self.path) - 1


class GameBase(arcade.View):
    background_path = None
    path = None
    build_place = list()
    wave_lists = list()

    def __init__(self):
        super().__init__()
        self.background_texture = arcade.load_texture(self.background_path)
        self.enemies = arcade.SpriteList()
        self.build_slots = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.money = 200
        self.spawn_timer = 0.0
        self.base_hp = 20
        self.ui = UIManager()

        self.popup_anchor = None
        self.selected_spot = None
        self.open = False
        self.wave = 0
        self.pack = 0
        self.spawned = 0

    def on_show_view(self):
        self.enemies = arcade.SpriteList()
        self.spawn_timer = 0.0
        self.base_hp = 20

        self.enemies = arcade.SpriteList()
        self.build_slots = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.projectiles.draw()

        for x, y in self.build_place:
            self.build_slots.append(BuildTowerPlace(x, y))

        self.money = 200
        self.ui.enable()

    def hide_ui(self):
        self.ui.disable()

    def spawn_enemy(self, enemy):
        self.enemies.append(enemy(self.path))

    def on_mouse_press(self, x, y, button, modifiers):
        if self.open:
            return
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        hits = arcade.get_sprites_at_point((x, y), self.build_slots)

        if not hits:
            return
        spot = hits[0]
        if spot.taken:
            return
        self.open_tower_menu(spot)

    def open_tower_menu(self, spot):
        self.open = True
        self.selected_spot = spot
        spot.color = arcade.color.GREEN

        self.button1 = UIFlatButton(text=f'Яблоня {tower_types["apple"]}', width=220, height=40)
        self.button1.center_x = spot.center_x
        self.button1.center_y = spot.center_y + 50
        self.button1.on_click = lambda build_apple: self.build_tower("apple")

        self.leave_menu_button = UIFlatButton(text=f'Выйти', width=220, height=40)
        self.leave_menu_button.center_x = spot.center_x
        self.leave_menu_button.center_y = spot.center_y - 50
        self.leave_menu_button.on_click = lambda leave: self.close_tower_menu(spot)

        self.ui.add(self.button1)
        self.ui.add(self.leave_menu_button)

    def close_tower_menu(self, spot):
        self.ui.remove(self.button1)
        self.ui.remove(self.leave_menu_button)
        spot.color = arcade.color.GRAY
        self.open = False
        self.selected_spot = None

    def build_tower(self, tower_type):
        cost = tower_types[tower_type]
        if self.money < cost:
            return
        if tower_type == "apple":
            spot = self.selected_spot
            tower = AppleTower(spot.center_x, spot.center_y + 45)
            self.towers.append(tower)

            self.build_slots.remove(spot)
            spot.taken = True
            spot.color = arcade.color.DARK_GRAY
            self.money -= cost
            self.close_tower_menu(spot)

    def on_update(self, delta_time):
        self.spawn_timer += delta_time
        start = 0
        start = 1

        if self.wave <= len(self.wave_lists) - 1:
            if self.pack <= len(self.wave_lists[self.wave]) - 1:
                if self.spawned < self.wave_lists[self.wave][self.pack][0]:
                    if self.spawn_timer >= 1:
                        self.spawn_enemy(self.wave_lists[self.wave][self.pack][1])
                        self.spawned += 1
                        self.spawn_timer = 0.0
                else:
                    if self.spawn_timer >= 0.5:
                        self.pack += 1
                        self.spawned = 0
                        self.spawn_timer = 0.0
            else:
                if self.spawn_timer >= 1.0:
                    self.wave += 1
                    self.pack = 0
                    self.spawn_timer = 0.0

        self.enemies.update(delta_time)
        self.towers.update(delta_time)
        self.projectiles.update(delta_time)

        for i in list(self.enemies):
            if i.reached_end():
                self.base_hp -= 1
                i.remove_from_sprite_lists()

        if self.base_hp <= 0:
            self.window.show_view(MenuView())

        for tower in self.towers:
            tower.update_tower(delta_time, self.enemies, self.projectiles)

        for projectile in self.projectiles:
            hit = arcade.check_for_collision_with_list(projectile, self.enemies)
            if hit:
                enemy = hit[0]
                enemy.hp -= projectile.damage
                if enemy.hp <= 0:
                    enemy.remove_from_sprite_lists()
                projectile.remove_from_sprite_lists()

    def on_draw(self):
        self.clear()
        texture_rectangle = arcade.XYWH(self.window.width // 2, self.window.height // 2, self.window.width,
                                        self.window.height)
        arcade.draw_texture_rect(self.background_texture, texture_rectangle)
        arcade.draw_line_strip(self.path, arcade.color.GREEN, 10)
        arcade.draw_text(f"Money: {self.money}", 10, 50, arcade.color.WHITE, 24)

        self.build_slots.draw()
        self.towers.draw()
        self.enemies.draw()
        self.projectiles.draw()

        for x, y in self.path:
            arcade.draw_circle_filled(x, y, 2, arcade.color.ORANGE)

        self.enemies.draw()
        arcade.draw_text(f"HP: {self.base_hp}", 10, 10, arcade.color.BLACK, 24)
        self.ui.draw()


class Level1View(GameBase):
    path = [(64 * 2.5, 500 * 1.8), (736 * 2.5, 500 * 1.8), (64 * 2.5, 128 * 1.8), (736 * 2.5, 128 * 1.8)]
    build_place = [(200 * 2.5, 450 * 1.8), (350 * 2.5, 450 * 1.8), (500 * 2.5, 450 * 1.8), (700 * 2.5, 200 * 1.8)]
    background_path = "imgs/травазаготовка.png"
    # каждый список внутри списка - мобы волны
    wave_lists = [[(1, Enemy)], [(4, Enemy), (2, Enemy)], [(3, Enemy)]]


class BuildTowerPlace(arcade.Sprite):
    def __init__(self, x, y, scale=2.0, texture_path="imgs/горшок.png"):
        super().__init__(texture_path, scale)
        self.center_x = x
        self.center_y = y
        self.taken = False


class AppleTower(arcade.Sprite):
    def __init__(self, x, y, scale=2.0, img='imgs/яблонявгоршке.png'):
        super().__init__(img, scale=scale)
        self.center_x = x
        self.center_y = y

        self.range = 300
        self.fire_rate = 0.6
        self.cooldown = 0.0
        self.damage = 100
        self.projectile_speed = 600

    def update_tower(self, delta_time, enemies, projectiles):
        self.cooldown -= delta_time
        if self.cooldown > 0:
            return
        target = self.find_target(enemies)
        if not target:
            return

        projectile = Projectile(self.center_x, self.center_y, target, speed=300, damage=self.damage)
        projectiles.append(projectile)
        self.cooldown = 1.0 / self.fire_rate

    def find_target(self, enemies):
        ans = None
        distant = self.range

        for i in enemies:
            d = math.hypot(i.center_x - self.center_x, i.center_y - self.center_y)
            if d <= distant:
                distant = d
                ans = i
        return ans


class Projectile(arcade.Sprite):
    def __init__(self, start_x, start_y, enemy, speed=800, damage=10):
        super().__init__()
        self.texture = arcade.load_texture(":resources:/images/space_shooter/laserBlue01.png")
        self.center_x = start_x
        self.center_y = start_y
        self.speed = speed
        self.damage = damage
        self.enemy = enemy
        self.target_x = self.enemy.center_x
        self.target_y = self.enemy.center_y


        x_diff = self.target_x - start_x
        y_diff = self.target_y - start_y
        angle = math.atan2(y_diff, x_diff)
        # И скорость
        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed
        # Если текстура ориентирована по умолчанию вправо, то поворачиваем пулю в сторону цели
        # Для другой ориентации нужно будет подправить угол
        self.angle = math.degrees(-angle)  # Поворачиваем пулю

    def update(self, delta_time):
        # Удаляем пулю, если она ушла за экран
        if (self.center_x < 0 or self.center_x > primary_screen.width or
                self.center_y < 0 or self.center_y > primary_screen.height):
            self.remove_from_sprite_lists()
        self.target_x = self.enemy.center_x
        self.target_y = self.enemy.center_y

        x_diff = self.target_x - self.center_x
        y_diff = self.target_y - self.center_y
        angle = math.atan2(y_diff, x_diff)
        # И скорость
        self.change_x = math.cos(angle) * self.speed
        self.change_y = math.sin(angle) * self.speed
        # Если текстура ориентирована по умолчанию вправо, то поворачиваем пулю в сторону цели
        # Для другой ориентации нужно будет подправить угол
        self.angle = math.degrees(-angle)

        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time






screen_info = arcade.get_screens()
primary_screen = screen_info[0]

window = arcade.Window(
    width=primary_screen.width,
    height=primary_screen.height,
    title="Tower Defense",
    fullscreen=False,
    resizable=False,
    style=arcade.Window.WINDOW_STYLE_BORDERLESS
)
menu_view = MenuView()
window.show_view(menu_view)
arcade.run()

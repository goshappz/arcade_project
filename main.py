import arcade
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from pyglet.graphics import Batch
import math

width = 800
height = 600

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

class Enemy(arcade.SpriteSolidColor):
    def __init__(self, path_points, speed = 120):
        super().__init__(width=24, height=24, color=arcade.color.RED)

        self.path = path_points
        self.speed = speed
        self.path_index = 0

        self.center_x, self.center_y = self.path[0]

    def update(self, delta_time: float = 1/60):
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

    def reached_end(self) -> bool:
        return self.path_index >= len(self.path) - 1

class GameBase(arcade.View):
    path = None
    def __init__(self):
        super().__init__()
        self.enemies = arcade.SpriteList()
        self.spawn_timer = 0.0
        self.base_hp = 20

    def on_show_view(self):
        self.enemies = arcade.SpriteList()
        self.spawn_timer = 0.0
        self.base_hp = 20

    def spawn_enemy(self):
        self.enemies.append(Enemy(self.path, speed=100))

    def on_update(self, delta_time):
        self.spawn_timer += delta_time
        if self.spawn_timer >= 1.0:
            self.spawn_timer = 0.0
            self.spawn_enemy()

        self.enemies.update(delta_time)

        for i in list(self.enemies):
            if i.reached_end():
                self.base_hp -= 1
                i.remove_from_sprite_lists()

        if self.base_hp <= 0:
            self.window.show_view(MenuView())

    def on_draw(self):
        self.clear()

        arcade.draw_line_strip(self.path, arcade.color.GRAY, 3)
        for x, y in self.path:
            arcade.draw_circle_filled(x, y, 5, arcade.color.ORANGE)

        self.enemies.draw()
        arcade.draw_text(f"HP: {self.base_hp}", 10, 10, arcade.color.WHITE, 16)
class Level1View(GameBase):
    path = [(64, 320), (256, 320), (256, 128), (640, 128)]


window = arcade.Window(width, height, "Tower Defense")
menu_view = MenuView()
window.show_view(menu_view)
arcade.run()

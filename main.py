import arcade
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from pyglet.graphics import Batch

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

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Для кликов, но manager сам обрабатывает

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
        game_view = GameView()
        self.window.show_view(game_view)

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK_BEAN)

    def on_draw(self):
        self.clear()
        # Рисуем спрайты, сцену...

    def on_update(self, delta_time):
        # Обновляем физику
        ...

    def on_key_press(self, key, modifiers):
        ...


window = arcade.Window(800, 600, "Учимся ставить на паузу")
menu_view = MenuView()
window.show_view(menu_view)
arcade.run()


import arcade
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from pyglet.graphics import Batch
from arcade.particles import FadeParticle, Emitter, EmitBurst, EmitInterval, EmitMaintainCount
from arcade.camera import Camera2D
import math
import random

arcade.load_font("font/Pharmakon.otf")
tower_types = {"apple": 50, 'nut': 60, 'cherry': 70}
screen_info = arcade.get_screens()
primary_screen = screen_info[0]
WIDHT = primary_screen.width
HEIGHT = primary_screen.height

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.GRAY)

        self.button_sound = arcade.Sound('sounds/button_sound.wav')
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
        label = UILabel(text="Slime defence",
                        font_size=40,
                        text_color=arcade.color.WHITE,
                        width=300,
                        multiline=True,
                        align="center",
                        font_name="Pharmakon",)
        self.box_layout.add(label)
        play_button = UIFlatButton(text="Играть", width=200, height=50, color=arcade.color.BLUE, font_name="Pharmakon")
        play_button.on_click = self.play_game
        self.box_layout.add(play_button)
        sts_button = UIFlatButton(text="Статистика", width=200, height=50, color=arcade.color.BLUE, font_name="Pharmakon")
        sts_button.on_click = self.sts_screen
        self.box_layout.add(sts_button)
        ext_button2 = UIFlatButton(text="Выход", width=200, height=50, color=arcade.color.RED, font_name="Pharmakon")
        ext_button2.on_click = self.exit_game
        self.box_layout.add(ext_button2)

    def on_draw(self):
        self.clear()
        self.manager.draw()  # Рисуй GUI поверх всего

    def play_game(self, event):
        self.button_sound.play()
        level_selecton = LevelSelectionView()
        self.window.show_view(level_selecton)

    def sts_screen(self, event):
        self.button_sound.play()
        sts_screen = StsView()
        self.window.show_view(sts_screen)

    def exit_game(self, event):
        self.button_sound.play()
        arcade.exit()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

class StsView(arcade.View):
    def __init__(self):
        super().__init__()
        f = open("sts.txt", "r", encoding="utf-8")
        self.vr = []
        for i in f:
            if '\n' in i:
                self.vr.append(i)
            else:
                self.vr.append(i + '\n')
        f.close()
        self.vr = ''.join(self.vr)
        arcade.set_background_color((64, 224, 208))
        self.manager = UIManager()
        self.manager.enable()
        self.setup_widgets()


    def setup_widgets(self):
        label_ttl = UILabel(text='Статистика',
                            font_size=90,
                            text_color=(123, 104, 238),
                            width=300,
                            multiline=True,
                            align="center",
                            font_name="Pharmakon")
        label_ttl.center_x = WIDHT // 2 - 130
        label_ttl.center_y = round(((1080 - 350) / 1080) * HEIGHT + 150)

        label_res = UILabel(text=self.vr,
                            font_size=38,
                            text_color=(255, 215, 0),
                            width=400,
                            multiline=True,
                            align="center",
                            font_name="Pharmakon")
        label_res.center_x = WIDHT // 2
        label_res.center_y = round(((1080 - 350) / 1080) * HEIGHT - 225)

        button_ext = UIFlatButton(text='В меню', width=200, height=50, color=arcade.color.BLUE, font_name="Pharmakon")
        button_ext.on_click = self.ext
        button_ext.center_x = WIDHT // 2
        button_ext.center_y = round(((1080 - 900) / 1080) * HEIGHT)

        self.manager.add(button_ext)
        self.manager.add(label_res)
        self.manager.add(label_ttl)

    def ext(self, event):
        main_screen = MenuView()
        self.window.show_view(main_screen)

    def on_draw(self):
        self.clear()
        arcade.draw_lbwh_rectangle_filled(610,
                                          300,
                                          700,
                                          450,
                                          (13, 33, 79))
        self.manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_show_view(self):
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

class EndView(arcade.View):
    def __init__(self, name, stats, res):
        super().__init__()
        self.res = res
        self.stats = stats
        self.name = name
        if res == 'Lose':
            backcol = (205, 92, 92)
            self.rescol = (255, 69, 0)
            self.namecol = (255, 165, 0)
        elif res == 'Win':
            backcol = (60, 179, 113)
            self.rescol = (0, 128, 0)
            self.namecol = (107, 142, 35)
        arcade.set_background_color(backcol)
        self.manager = UIManager()
        self.manager.enable()
        self.setup_widgets()
        self.sts_chng()

    def sts_chng(self):
        f = open("sts.txt", "r", encoding="utf-8")
        vr = []
        for i in f:
            if '\n' in i:
                vr.append(i[:-1])
            else:
                vr.append(i)
        f.close()
        f = open("sts.txt", "w", encoding="utf-8")
        f.write(vr[0][:vr[0].find('- ') + 2] + str(int(vr[0][vr[0].find('- ') + 2:]) + self.stats[0]) + '\n')
        if self.res == 'Win':
            f.write(vr[1][:vr[1].find('- ') + 2] + str(int(vr[1][vr[1].find('- ') + 2:]) + 1) + '\n')
            f.write(vr[2][:vr[2].find('- ') + 2] + str(int(vr[2][vr[2].find('- ') + 2:]) + 0) + '\n')
        else:
            f.write(vr[1][:vr[1].find('- ') + 2] + str(int(vr[1][vr[1].find('- ') + 2:]) + 0) + '\n')
            f.write(vr[2][:vr[2].find('- ') + 2] + str(int(vr[2][vr[2].find('- ') + 2:]) + 1) + '\n')
        f.close()

    def setup_widgets(self):
        label_res = UILabel(text=self.res,
                            font_size=100,
                            text_color=self.rescol,
                            width=300,
                            multiline=True,
                            align="center",
                            font_name="Pharmakon")
        label_res.center_x = WIDHT // 2
        label_res.center_y = round(((1080 - 350) / 1080) * HEIGHT)

        label_sts = UILabel(text=f'Slimes killed: {self.stats[0]}/{self.stats[1]}',
                            font_size=50,
                            text_color=(255, 215, 0),
                            width=400,
                            multiline=True,
                            align="center",
                            font_name="Pharmakon")
        label_sts.center_x = WIDHT // 2
        label_sts.center_y = round(((1080 - 700) / 1080) * HEIGHT)

        label_name = UILabel(text=f'{self.name}:',
                             font_size=50,
                             text_color=self.namecol,
                             width=300,
                             multiline=True,
                             align="center",
                             font_name="Pharmakon")
        label_name.center_x = WIDHT // 2
        label_name.center_y = round(((1080 - 250) / 1080) * HEIGHT)

        button_ext = UIFlatButton(text='В меню', width=200, height=50, color=arcade.color.BLUE, font_name="Pharmakon")
        button_ext.on_click = self.ext
        button_ext.center_x = WIDHT // 2
        button_ext.center_y = round(((1080 - 900) / 1080) * HEIGHT)

        self.manager.add(label_res)
        self.manager.add(label_sts)
        self.manager.add(label_name)
        self.manager.add(button_ext)

    def ext(self, event):
        main_screen = MenuView()
        self.window.show_view(main_screen)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_show_view(self):
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()


class LevelSelectionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.button_sound = arcade.Sound('sounds/button_sound.wav')
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
                        align="center",
                        font_name="Pharmakon")
        label.center_x = 400
        label.center_y = 300

        button_level_1 = UIFlatButton(text='Первый уровень', width=200, height=50, color=arcade.color.BLUE, font_name="Pharmakon")
        button_level_1.on_click = self.play_level_1
        button_level_1.center_x = 100
        button_level_1.center_y = 100

        self.manager.add(label)
        self.manager.add(button_level_1)

        button_level_2 = UIFlatButton(text='Второй уровень', width=200, height=50, color=arcade.color.BLUE, font_name="Pharmakon")
        button_level_2.on_click = self.play_level_2

        self.manager.add(label)
        self.manager.add(button_level_2)

    def on_draw(self):
        self.clear()
        self.manager.draw()  # Рисуй GUI поверх всего

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Для кликов, но manager сам обрабатывает

    def play_level_1(self, event):
        self.button_sound.play()
        game_view = Level1View()
        self.window.show_view(game_view)

    def play_level_2(self, event):
        self.button_sound.play()
        game_view = Level2View()
        self.window.show_view(game_view)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.LIGHT_GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()


class Enemy(arcade.Sprite):
    def __init__(self, path_points, speed=100, hp=100, scale=2,
                 img='imgs/слизень_обычный.png', money=4, SPARK_TEX=[
                arcade.make_soft_circle_texture(6, (60, 179, 113)),
                arcade.make_soft_circle_texture(6, (0, 100, 0)),
                arcade.make_soft_circle_texture(6, (128, 128, 0)),
                arcade.make_soft_circle_texture(6, (0, 128, 0)),
                arcade.make_soft_circle_texture(6, (173, 255, 47))
            ]):

        super().__init__(img, scale=scale)
        self.SPARK_TEX = SPARK_TEX
        self.hp = hp
        self.path = path_points
        self.speed = round(speed * random.randint(100, 125) / 100)
        self.path_index = 0
        self.way = 0
        self.money = round(money * random.randint(10, 20) / 10)

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
        self.way += step

        if dist <= step:
            self.center_x, self.center_y = dest_x, dest_y
            self.path_index += 1
        else:
            self.center_x += dx / dist * step
            self.center_y += dy / dist * step

    def reached_end(self):
        return self.path_index >= len(self.path) - 1


class Blue_Enemy(Enemy):
    def __init__(self, path_points, speed=100, hp=150, scale=2,
                 img='imgs/слизень_синий.png', money=8, SPARK_TEX=[
                arcade.make_soft_circle_texture(6, (0, 0, 139)),
                arcade.make_soft_circle_texture(6, (70, 130, 180)),
                arcade.make_soft_circle_texture(6, (0, 191, 255)),
                arcade.make_soft_circle_texture(6, (65, 105, 225)),
            ]):
        super().__init__(path_points, speed, hp, scale,
                         img, money, SPARK_TEX)


class Red_Enemy(Enemy):
    def __init__(self, path_points, speed=125, hp=100, scale=2,
                 img='imgs/слизень_красный.png', money=8, SPARK_TEX=[
                arcade.make_soft_circle_texture(6, (139, 0, 0)),
                arcade.make_soft_circle_texture(6, (220, 20, 60)),
                arcade.make_soft_circle_texture(6, (205, 92, 92)),
                arcade.make_soft_circle_texture(6, (255, 140, 0)),
            ]):
        super().__init__(path_points, speed, hp, scale,
                         img, money, SPARK_TEX)


class GameBase(arcade.View):
    background_path = None
    background_path1 = None
    path = None
    build_place = list()
    money_log = {}
    wave_lists = list()
    building_towers = {}
    name = str()
    apple_tree_textures = [
        arcade.load_texture("imgs/яблонявгоршке.png"),
        arcade.load_texture("imgs/яблоня_средняя.png"),
        arcade.load_texture("imgs/яблонявзрослая.png"),
    ]

    def __init__(self):
        super().__init__()
        self.background_texture = arcade.load_texture(self.background_path)
        self.background_texture1 = arcade.load_texture(self.background_path1)
        self.enemies = arcade.SpriteList()
        self.build_slots = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.road_sprites = arcade.SpriteList()

        self.world_camera = None
        self.ui_camera = None
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        self.cam_speed = 900
        self.zoom = 1.0
        self.zoom_min = 0.5
        self.zoom_max = 1.0
        self.world_width = 3840
        self.world_height = 1080

        self.money = 90
        self.spawn_timer = 0.0
        self.base_hp = 3
        self.start = 0
        self.kills = 0
        self.mobs = 0

        self.horn_sound = arcade.Sound('sounds/horn.wav')
        self.button_sound = arcade.Sound('sounds/button_sound.wav')
        self.cash = arcade.Sound('sounds/Cash.wav')
        self.horn_sound.play(volume=0.3)
        for i in self.wave_lists:
            for x in i:
                self.mobs += x[0]
        self.waves = len(self.wave_lists)

        self.emitters = []

        self.popup_anchor = None
        self.selected_spot = None
        self.open = False
        self.wave = 0
        self.pack = 0
        self.spawned = 0
        self.ui = UIManager()
        # self.ui.enable()  # Включить, чтоб виджеты работали

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()
    def setup_widgets(self):
        self.wave_label = UILabel(text=f"Wave {self.wave}/{len(self.wave_lists)}",
                                  font_size=55,
                                  text_color=(0, 100, 0),
                                  width=300,
                                  multiline=True,
                                  align="center",
                                  font_name="Pharmakon")
        self.wave_label.center_x = 1920 / 2
        self.wave_label.center_y = 1080 - 100

        button_ext = UIFlatButton(text='Выйти', width=150, height=50, color=arcade.color.BLUE, font_name="Pharmakon")
        button_ext.on_click = self.close_game
        button_ext.center_x = 100
        button_ext.center_y = HEIGHT - 50

        self.ui.add(self.wave_label)
        self.ui.add(button_ext)
        self.ui.enable()

    def on_show_view(self):
        self.enemies = arcade.SpriteList()
        self.spawn_timer = 0.0

        self.world_camera = Camera2D()
        self.ui_camera = Camera2D()

        self.enemies = arcade.SpriteList()
        self.build_slots = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.projectiles.draw()
        self.road_sprites = arcade.SpriteList()
        self.build_road(self.path, "imgs/дорога1.png", scale=1.0, step_px=48)

        for x, y in self.build_place:
            self.build_slots.append(BuildTowerPlace(x, y))

        # self.ui.enable()

    def hide_ui(self):
        self.ui.disable()

    def close_game(self, event):
        self.button_sound.play()
        main_screen = MenuView()
        self.window.show_view(main_screen)

    def spawn_enemy(self, enemy):
        self.enemies.append(enemy(self.path))

    def build_road(self, path, texture_path, scale=1.0, step_px=48):
        road_texture = arcade.load_texture(texture_path)
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            distance = math.dist((x1, y1), (x2, y2))
            if distance <= 0:
                continue
            steps = int(distance // step_px)
            angle_deg = math.degrees(math.atan2((x2 - x1), (y2 - y1)))
            for s in range(steps + 1):
                t = (s * step_px) / distance

                spr = arcade.Sprite(scale=scale)
                spr.texture = road_texture
                spr.center_x = x1 + (x2 - x1) * t
                spr.center_y = y1 + (y2 - y1) * t
                spr.angle = angle_deg
                self.road_sprites.append(spr)

    def on_mouse_press(self, x, y, button, modifiers):
        world_x, world_y, world_z = self.world_camera.unproject((x, y))
        if self.open:
            return
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        hits_spot = arcade.get_sprites_at_point((world_x,world_y), self.build_slots)
        hits_towers = arcade.get_sprites_at_point((world_x, world_y), self.towers)

        if not hits_spot and not hits_towers:
            return
        elif hits_spot and not hits_towers:
            spot = hits_spot[0]
            if spot.taken:
                return
            else:
                self.open_tower_menu(spot)
        elif hits_towers and not hits_spot:
            tower = hits_towers[0]
            self.tower_upg_menu(tower)

    def tower_upg_menu(self, tower):
        world_x, world_y = self.world_camera.project((tower.center_x, tower.center_y))
        self.open = True

        self.button2 = UIFlatButton(text=f'Улучшение {tower.upg_cost}', width=220, height=40, font_name="Pharmakon")
        self.button2.center_x = world_x
        self.button2.center_y = world_y + 40
        self.button2.on_click = lambda upg: self.upg_tower(tower)

        self.leave_menu_button = UIFlatButton(text=f'Выйти', width=220, height=40, font_name="Pharmakon")
        self.leave_menu_button.center_x = world_x
        self.leave_menu_button.center_y = world_y - 100
        self.leave_menu_button.on_click = lambda leave: self.close_tower_menu(tower)

        self.ui.add(self.button2)
        self.ui.add(self.leave_menu_button)

    def upg_tower(self, tower):
        cost = tower.upg_cost
        if self.money < cost:
            return
        tower.lvl += 1
        tower.upg_cost += 10
        tower.fire_rate += 0.1
        self.money -= cost
        self.close_tower_menu(tower)

    def close_tower_menu(self, tower):
        self.button_sound.play()
        self.ui.remove(self.button2)
        self.ui.remove(self.leave_menu_button)
        self.open = False

    def open_tower_menu(self, spot):
        self.button_sound.play()
        self.open = True
        self.selected_spot = spot
        spot.color = arcade.color.GREEN
        world_x, world_y = self.world_camera.project((spot.center_x, spot.center_y))
        self.button1 = UIFlatButton(text=f'Яблоня {tower_types["apple"]}', width=220, height=40, font_name="Pharmakon")
        self.button1.center_x = world_x
        self.button1.center_y = world_y + 50
        self.button1.on_click = lambda build_apple: self.build_tower("apple")

        self.button2 = UIFlatButton(text=f'Орех {tower_types["nut"]}', width=220, height=40, font_name="Pharmakon")
        self.button2.center_x = world_x
        self.button2.center_y = world_y + 100
        self.button2.on_click = lambda build_apple: self.build_tower("nut")

        self.button3 = UIFlatButton(text=f'Вишня {tower_types["cherry"]}', width=220, height=40, font_name="Pharmakon")
        self.button3.center_x = world_x
        self.button3.center_y = world_y + 150
        self.button3.on_click = lambda build_apple: self.build_tower("cherry")

        self.leave_menu_button = UIFlatButton(text=f'Выйти', width=220, height=40, font_name="Pharmakon")
        self.leave_menu_button.center_x = world_x
        self.leave_menu_button.center_y = world_y - 50
        self.leave_menu_button.on_click = lambda leave: self.close_spot_menu(spot)

        self.ui.add(self.button3)
        self.ui.add(self.button2)
        self.ui.add(self.button1)
        self.ui.add(self.leave_menu_button)

    def close_spot_menu(self, spot):
        self.ui.remove(self.button3)
        self.ui.remove(self.button2)
        self.ui.remove(self.button1)
        self.ui.remove(self.leave_menu_button)
        spot.color = arcade.color.GRAY
        self.open = False
        self.selected_spot = None

    def build_tower(self, tower_type):
        self.button_sound.play()
        cost = tower_types[tower_type]
        if self.money < cost:
            return
        if tower_type == "apple":
            spot = self.selected_spot
            tower = AppleTower(spot.center_x, spot.center_y + 45)
            tower.texture = self.apple_tree_textures[0]
            self.towers.append(tower)
            self.building_towers[tower] = {
                "textures": self.apple_tree_textures,
                "elapsed": 0.0,
                "frame_time": 0.15,  # сек на кадр
            }
            self.build_slots.remove(spot)
            spot.taken = tower_type
            spot.color = arcade.color.DARK_GRAY
            self.money -= cost
            self.close_spot_menu(spot)
        elif tower_type == "nut":
            spot = self.selected_spot
            tower = NutsTower(spot.center_x, spot.center_y + 45)
            self.towers.append(tower)

            self.build_slots.remove(spot)
            spot.taken = tower_type
            spot.color = arcade.color.DARK_GRAY
            self.money -= cost
            self.close_spot_menu(spot)

        elif tower_type == "cherry":
            spot = self.selected_spot
            tower = CherryTower(spot.center_x, spot.center_y + 45)
            self.towers.append(tower)

            self.build_slots.remove(spot)
            spot.taken = tower_type
            spot.color = arcade.color.DARK_GRAY
            self.money -= cost
            self.close_spot_menu(spot)

    def gravity_drag(self, p):  # Для искр: чуть вниз и затухание скорости
        p.change_y += -0.03
        p.change_x *= 0.92
        p.change_y *= 0.9

    def make_explosion(self, x, y, SPARK_TEX, count=100):
        # Разовый взрыв с искрами во все стороны
        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(count),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(SPARK_TEX),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 0.9),
                start_alpha=255, end_alpha=0,
                scale=random.uniform(0.35, 0.9),
                mutation_callback=self.gravity_drag,
            ),
        )
    def camera_limit(self):
        view_x = self.window.width / self.zoom
        view_y = self.window.height / self.zoom

        min_x = view_x / 2
        max_x = self.world_width - view_x / 2
        min_y = view_y / 2
        max_y = self.world_height - view_y / 2

        cx, cy = self.world_camera.position

        if max_x < min_x:
            cx = self.world_width / 2
        else:
            cx = max(min_x, min(cx, max_x))

        if max_y < min_y:
            cy = self.world_height / 2
        else:
            cy = max(min_y, min(cy, max_y))

        self.world_camera.position = (cx, cy)




    def on_update(self, delta_time):
        dx = dy = 0.0
        speed = self.cam_speed * delta_time / self.zoom

        if self.move_left:
            dx -= speed
            self.camera_limit()
        if self.move_right:
            dx += speed
            self.camera_limit()
        if self.move_up:
            dy += speed
            self.camera_limit()
        if self.move_down:
            dy -= speed
            self.camera_limit()

        if dx or dy:
            x, y = self.world_camera.position
            self.world_camera.position = (x + dx, y + dy)
            self.camera_limit()
        self.camera_limit()
        self.spawn_timer += delta_time

        if self.spawn_timer >= 3 or self.start:
            if not self.start:
                self.spawn_timer = 0
            self.start = 1
            if self.wave <= self.waves - 1:
                if self.pack <= len(self.wave_lists[self.wave]) - 1:
                    if self.spawned < self.wave_lists[self.wave][self.pack][0]:
                        if self.spawn_timer >= 0.4:
                            self.spawn_enemy(self.wave_lists[self.wave][self.pack][1])
                            self.spawned += 1
                            self.spawn_timer = 0.0
                    else:
                        if self.spawn_timer >= 0.7:
                            self.pack += 1
                            self.spawned = 0
                            self.spawn_timer = 0.0
                else:
                    if self.spawn_timer >= 2.5:
                        self.wave += 1
                        self.pack = 0
                        self.spawn_timer = 0.0

        if self.wave >= len(self.wave_lists):
            self.waves = - 1
            self.wave = len(self.wave_lists) - 1
        self.wave_label.text = f"Wave {self.wave + 1}/{len(self.wave_lists)}"

        self.enemies.update(delta_time)
        self.towers.update(delta_time)
        self.projectiles.update(delta_time)

        for i in list(self.enemies):
            if i.reached_end():
                self.base_hp -= 1
                i.remove_from_sprite_lists()

        if self.base_hp <= 0:
            self.window.show_view(EndView(self.name, (self.kills, self.mobs), 'Lose'))

        if len(self.enemies) == 0 and self.waves == -1:
            self.window.show_view(EndView(self.name, (self.kills, self.mobs), 'Win'))

        for tower in self.towers:
            tower.update_tower(delta_time, self.enemies, self.projectiles)

        for projectile in self.projectiles:
            projectile.shot(self)

        emitters_copy = self.emitters.copy()  # Защищаемся от мутаций списка
        for e in emitters_copy:
            e.update(delta_time)
        for e in emitters_copy:
            if e.can_reap():  # Готов к уборке?
                self.emitters.remove(e)
        finished = []
        for tower, anim in self.building_towers.items():
            anim["elapsed"] += delta_time
            frame = int(anim["elapsed"] / anim["frame_time"])

            if frame >= len(anim["textures"]):
                tower.texture = anim["textures"][-1]
                finished.append(tower)
            else:
                tower.texture = anim["textures"][frame]

        for tower in finished:
            del self.building_towers[tower]
    def on_draw(self):
        self.clear()
        self.world_camera.use()
        texture_rectangle = arcade.LBWH(0, 0, self.window.width,
                                        self.window.height)
        arcade.draw_texture_rect(self.background_texture, texture_rectangle)
        arcade.draw_line_strip(self.path, arcade.color.GREEN, 10)
        texture_rectangle1 = arcade.LBWH(1920, 0, self.window.width, self.window.height)
        arcade.draw_texture_rect(self.background_texture1, texture_rectangle1)
        self.road_sprites.draw()
        self.build_slots.draw()
        self.enemies.draw()
        self.towers.draw()
        self.projectiles.draw()

        for e in self.emitters:
            e.draw()

        for x, y in self.path:
            arcade.draw_circle_filled(x, y, 2, arcade.color.ORANGE)

        self.ui_camera.use()
        arcade.draw_text(f"Money: {self.money}", 10, 50, arcade.color.BLACK, 24, font_name="Pharmakon")
        arcade.draw_text(f"HP: {self.base_hp}", 10, 10, arcade.color.BLACK, 24, font_name="Pharmakon")
        self.ui.draw()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = True
        elif key in (arcade.key.W, arcade.key.UP):
            self.move_up = True
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.move_down = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = False
        elif key in (arcade.key.W, arcade.key.UP):
            self.move_up = False
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.move_down = False

class Level1View(GameBase):
    path = [(64 * 2.5, 500 * 1.8 - 50), (736 * 2.5, 500 * 1.8 - 50), (64 * 2.5, 128 * 1.8 - 50),
            (736 * 2.5, 128 * 1.8 - 50)]
    build_place = [(200 * 2.5 + 50, 450 * 1.8 - 75), (350 * 2.5 + 50, 450 * 1.8 - 75),
                   (500 * 2.5 + 50, 450 * 1.8 - 75), (200 * 2.5 + 50, 450 * 1.8 - 550),
                   (350 * 2.5 + 50, 450 * 1.8 - 550), (500 * 2.5 + 50, 450 * 1.8 - 550)]
    background_path = "imgs/задний фон.png"
    background_path1 = "imgs/так_называемая_роща.png"
    # каждый список внутри списка - мобы волны
    wave_lists = [[(1, Enemy)], [(3, Enemy), (2, Enemy)], [(2, Blue_Enemy), (2, Red_Enemy), (3, Enemy)],
                  [(2, Blue_Enemy), (2, Red_Enemy), (3, Enemy), (3, Blue_Enemy)],
                  [(4, Blue_Enemy), (4, Red_Enemy), (1, Enemy)]]
    name = 'Level1'


class Level2View(GameBase):
    path = [(200, 200), (200, 850), (900, 850), (900, 200), (1450, 200), (1450, 500), (1800, 500)]
    build_place = [(300, 500), (550, 750), (800, 500), (1175, 300), (1625, 400)]
    background_path = "imgs/задний фон.png"
    background_path1 = "imgs/так_называемая_роща.png"
    # каждый список внутри списка - мобы волны
    wave_lists = [[(1 * 2, Enemy)], [(3 * 2, Enemy), (2 * 2, Enemy)],
                  [(2 * 2, Blue_Enemy), (2 * 2, Red_Enemy), (3 * 2, Enemy)],
                  [(2 * 2, Blue_Enemy), (2 * 2, Red_Enemy), (3 * 2, Enemy), (3 * 2, Blue_Enemy)],
                  [(4 * 2, Blue_Enemy), (4 * 2, Red_Enemy), (1 * 2, Enemy)],
                  [(2 * 3, Blue_Enemy), (2 * 3, Red_Enemy), (3 * 3, Enemy), (3 * 3, Blue_Enemy)],
                  [(4 * 3, Blue_Enemy), (4 * 3, Red_Enemy), (1 * 3, Enemy)]
                  ]
    name = 'Level2'


class BuildTowerPlace(arcade.Sprite):
    def __init__(self, x, y, scale=2.0, texture_path="imgs/горшок.png"):
        super().__init__(texture_path, scale)
        self.center_x = x
        self.center_y = y
        self.taken = False


class AppleTower(arcade.Sprite):
    def __init__(self, x, y, scale=2.0, img='imgs/яблонявзрослая.png', dmg=100):
        super().__init__(img, scale=scale)
        self.center_x = x
        self.center_y = y

        self.lvl = 0
        self.upg_cost = 60
        self.range = 350
        self.fire_rate = 0.3
        self.cooldown = 0.0
        self.damage = dmg
        self.projectile_speed = 450

    def update_tower(self, delta_time, enemies, projectiles):
        self.cooldown -= delta_time
        if self.cooldown > 0:
            return
        target = self.find_target(enemies)
        if not target:
            return

        projectile = Projectile(self.center_x, self.center_y, target, speed=self.projectile_speed, damage=self.damage)
        projectiles.append(projectile)
        self.cooldown = 1.0 / self.fire_rate

    def find_target(self, enemies):
        ans = None
        steps = -1

        for i in enemies:
            d = math.hypot(i.center_x - self.center_x, i.center_y - self.center_y)
            if d <= self.range and steps <= i.way:
                steps = i.way
                ans = i
        return ans


class Projectile(arcade.Sprite):
    def __init__(self, start_x, start_y, enemy, speed, damage):
        super().__init__()
        self.texture = arcade.load_texture("imgs/яблоко_снаряд.png")
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
        self.angle += 1440 * delta_time
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

    def shot(self, gb):
        hit = arcade.check_for_collision(self, self.enemy)
        if hit:
            enemy = self.enemy
            enemy.hp -= self.damage
            if enemy.hp <= 0:
                gb.money += enemy.money
                if enemy in gb.enemies:
                    gb.emitters.append(gb.make_explosion(enemy.center_x, enemy.center_y, enemy.SPARK_TEX))
                    gb.kills += 1
                enemy.remove_from_sprite_lists()
            self.remove_from_sprite_lists()



class Projectile_Nut(Projectile):
    def __init__(self, start_x, start_y, enemy, speed, damage):
        super().__init__(start_x, start_y, enemy, speed, damage)
        self.texture = arcade.load_texture("imgs/яблоко_снаряд.png")
        self.hits = 0
        self.range = 100
        self.enemyz = []

    def find_target(self, enemies, enemy):
        ans = None
        steps = -1

        for i in enemies:
            d = math.hypot(i.center_x - self.center_x, i.center_y - self.center_y)
            if d <= self.range and steps <= i.way and i not in enemy:
                steps = i.way
                ans = i
        return ans

    def shot(self, gb):
        hit = arcade.check_for_collision(self, self.enemy)
        if hit:
            enemy = self.enemy
            enemy.hp -= self.damage
            self.enemyz.append(self.enemy)
            self.hits += 1
            if enemy.hp <= 0:
                gb.money += enemy.money
                if enemy in gb.enemies:
                    gb.emitters.append(gb.make_explosion(enemy.center_x, enemy.center_y, enemy.SPARK_TEX))
                    gb.kills += 1
                enemy.remove_from_sprite_lists()
            self.enemy = self.find_target(gb.enemies, self.enemyz)
            if not self.enemy:
                self.remove_from_sprite_lists()
            if self.hits == 3:
                self.remove_from_sprite_lists()


class Projectile_Cherry(Projectile):
    def __init__(self, start_x, start_y, enemy, speed, damage):
        super().__init__(start_x, start_y, enemy, speed, damage)
        self.texture = arcade.load_texture("imgs/яблоко_снаряд.png")




class NutsTower(AppleTower):
    def __init__(self, x, y, scale=2.0, img='imgs/Ореховое_дерево.png', dmg=75):
        super().__init__(x, y, scale, img, dmg)
        self.range = 400
        self.upg_cost = 70
        self.fire_rate = 0.6

    def update_tower(self, delta_time, enemies, projectiles):
        self.cooldown -= delta_time
        if self.cooldown > 0:
            return
        target = self.find_target(enemies)
        if not target:
            return

        projectile = Projectile_Nut(self.center_x, self.center_y, target, speed=self.projectile_speed, damage=self.damage)
        projectiles.append(projectile)
        self.cooldown = 1.0 / self.fire_rate

class CherryTower(AppleTower):
    def __init__(self, x, y, scale=2.0, img='imgs/Грушевое_дерево.png', dmg=34):
        super().__init__(x, y, scale, img, dmg)
        self.range = 300
        self.upg_cost = 80
        self.fire_rate = 0.7

    def find_target(self, enemies):
        ans = []
        steps = -1

        for i in enemies:
            d = math.hypot(i.center_x - self.center_x, i.center_y - self.center_y)
            if d <= self.range:
                ans.append(i)
        return ans

    def update_tower(self, delta_time, enemies, projectiles):
        self.cooldown -= delta_time
        if self.cooldown > 0:
            return
        targets = self.find_target(enemies)
        if len(targets) == 0:
            return

        for target in targets:
            projectile = Projectile_Cherry(self.center_x, self.center_y, target, speed=self.projectile_speed, damage=self.damage)
            projectiles.append(projectile)
        self.cooldown = 1.0 / self.fire_rate





window = arcade.Window(
    width=WIDHT,
    height=HEIGHT,
    title="Tower Defense",
    fullscreen=False,
    resizable=False,
    style=arcade.Window.WINDOW_STYLE_BORDERLESS
)
menu_view = MenuView()
window.show_view(menu_view)
arcade.run()

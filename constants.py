import pygame as pg
import csv
from button import Button

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Number of levels
MAX_LEVELS = 3

# Screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Clock
clock = pg.time.Clock()
FPS = 60

# Dimensions
ROWS, COLS = 16, 150

# Game Variables
GRAVITY = 0.85
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21

# When we want the background to start scrolling
SCROLLING_THRESH = 200

# Defining colors
BG = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# Some constants you can play around with
SOLDIER_HEALTH = 100
SOLDIER_SCALE = 1.65
PLAYER_MOVEMENT_SPEED = 5
ENEMY_MOVEMENT_SPEED = 3
PLAYER_STARTING_AMMO = 20
PLAYER_STARTING_GRENADES = 5
ENEMY_STARTING_AMMO = 15
PLAYER_ENEMY_HEALTH_DECREASE_PER_GRENADE = 50
ENEMY_HEALTH_DECREASE_PER_BULLET = 25
HEALTH_BAR_WIDTH = 150
HEALTH_BAR_HEIGHT = 20
AMMO_INCREASE_PER_PICKUP = 10
GRENADE_INCREASE_PER_PICKUP = 3
HEALTH_INCREASE_PER_PICKUP = 25
WIDTH_OF_ENEMY_VISION = 200

# Bullet
bullet_img = pg.image.load('img/icons/bullet.png').convert_alpha()
BULLET_SPEED = 10
BULLET_RELOAD_SPEED = 20  # How fast you want to shoot the bullets , the lower --> the faster

# Grenade
grenade_img = pg.image.load('img/icons/grenade.png').convert_alpha()
GRENADE_EXPLOSION_SPEED = 4
GRENADE_TIMER = 100
GRENADE_Y_VELOCITY = -11
GRENADE_SPEED = 10

# Pick-up Items
health_box_img = pg.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pg.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pg.image.load("img/icons/grenade_box.png").convert_alpha()
item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img
}
# Load Start and Exit button images

start_btn_img = pg.image.load('img/start_btn.png').convert_alpha()
restart_btn_img = pg.image.load('img/restart_btn.png').convert_alpha()
exit_btn_img = pg.image.load('img/exit_btn.png').convert_alpha()

# Load Start and Exit buttons
start_btn = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_btn_img, 1)
restart_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_btn_img, 2)
exit_btn = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_btn_img, 1)

# Load Background Images
pine1_img = pg.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pg.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pg.image.load('img/background/mountain.png').convert_alpha()
sky_img = pg.image.load('img/background/sky_cloud.png').convert_alpha()

# Sprite groups are basically python lists
# So whenever we are going to create multiple bullets we are going to sort them in a group
# Even though , we don't have an update or draw method in the Bullet class , we can still call them (built-in).
enemy_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
grenade_group = pg.sprite.Group()
explosion_group = pg.sprite.Group()
item_box_group = pg.sprite.Group()
decoration_group = pg.sprite.Group()
water_group = pg.sprite.Group()
exit_group = pg.sprite.Group()

# Tile Images
tile_images = []
for file_name in range(TILE_TYPES):
    img_file = pg.image.load(f"img/tile/{file_name}.png").convert_alpha()
    img_file = pg.transform.scale(img_file, (TILE_SIZE, TILE_SIZE))
    tile_images.append(img_file)

# Create Empty World Data
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# Load level data
level = 1
with open(f"level{level}_data.csv", newline='') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    for y_position, row in enumerate(reader):
        for x_position, tile in enumerate(row):
            world_data[y_position][x_position] = int(tile)


def draw_text(text, text_font, text_color, x, y):
    img = text_font.render(text, True, text_color)
    screen.blit(img, (x, y))


def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    item_box_group.empty()
    grenade_group.empty()
    exit_group.empty()
    explosion_group.empty()
    water_group.empty()
    decoration_group.empty()

    # Create New Level Empty Tile List
    data = []
    for _ in range(ROWS):
        data_row = [-1] * COLS
        data.append(data_row)
    return data

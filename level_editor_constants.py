import pygame as pg
from button import Button

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
LOWER_MARGIN, SIDE_MARGIN = 100, 300

# Clock
clock = pg.time.Clock()
FPS = 60

# Colors
LIGHT_RED = (200, 25, 25)
LIGHT_GREEN = (144, 201, 120)
WHITE = (255, 255, 255)

# Grid Dimensions
ROWS, MAX_COLS = 16, 150

# Tile
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21  # 21 Different Images related to tiles

# Level Screen
lvl_screen = pg.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))

# Load Background Images
pine1_img = pg.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pg.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pg.image.load('img/background/mountain.png').convert_alpha()
sky_img = pg.image.load('img/background/sky_cloud.png').convert_alpha()

# More Images
save_image = pg.image.load("img/save_btn.png").convert_alpha()
load_image = pg.image.load("img/load_btn.png").convert_alpha()

# Store Tile Images
tile_images = []
for x in range(TILE_TYPES):
    img = pg.image.load(f'img/tile/{x}.png').convert_alpha()
    img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    tile_images.append(img)

# Buttons List
buttons = []
button_col, button_row = 0, 0
for x in range(len(tile_images)):
    tile_button = Button(SCREEN_WIDTH + 75 * button_col + 50, 75 * button_row + 50, tile_images[x], 1)
    buttons.append(tile_button)
    button_col += 1

    if button_col == 3:
        button_row += 1
        button_col = 0

# Creating Save and Load Buttons
save_button = Button(x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT + LOWER_MARGIN - 50, image=save_image, scale=1)
load_button = Button(x=SCREEN_WIDTH // 2 + 200, y=SCREEN_HEIGHT + LOWER_MARGIN - 50, image=load_image, scale=1)

# Empty Tile List # 2D List
world_data = []
for _ in range(ROWS):
    row = [-1] * MAX_COLS  # -1 is the indication of an empty tile
    world_data.append(row)

# Creating ground
for tile in range(MAX_COLS):
    # Accessing the last row of the world map
    world_data[-1][tile] = 0

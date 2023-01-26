from level_editor_constants import *
import csv

# import pickle
pg.init()
pg.display.set_caption("Level Editor")

# Game Variables
scroll_left, scroll_right, scroll, scroll_speed, current_tile, level = False, False, 0, 1, 0, 0

# Defining font
font = pg.font.SysFont("Futura", 30)


# Helper Function
def draw_bg():
    lvl_screen.fill(LIGHT_GREEN)
    width = sky_img.get_width()  # Same width of all images
    for image_count in range(4):
        lvl_screen.blit(sky_img, ((image_count * width) - scroll * 0.5, 0))
        lvl_screen.blit(mountain_img,
                        ((image_count * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        lvl_screen.blit(pine1_img, ((image_count * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        lvl_screen.blit(pine2_img, ((image_count * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


def draw_grid():
    # Vertical Lines
    for col_num in range(MAX_COLS + 1):
        pg.draw.line(lvl_screen, WHITE, (col_num * TILE_SIZE - scroll, 0),
                     (col_num * TILE_SIZE - scroll, SCREEN_HEIGHT))
    # Horizontal Lines
    for row_num in range(ROWS + 1):
        pg.draw.line(lvl_screen, WHITE, (0, row_num * TILE_SIZE), (SCREEN_WIDTH, row_num * TILE_SIZE))


def draw_world():
    for y_position, row_world_data in enumerate(world_data):
        for x_position, tile_world_data in enumerate(row_world_data):
            if tile_world_data >= 0:
                lvl_screen.blit(tile_images[tile_world_data],
                                dest=(x_position * TILE_SIZE - scroll, y_position * TILE_SIZE))


def draw_text(text, text_font, text_color, text_x, text_y):
    image = text_font.render(text, True, text_color)
    lvl_screen.blit(image, (text_x, text_y))


# Main game loop
run = True
while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()
    draw_text(f"Level: {level}", font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP or DOWN to change the level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

    # Save and Load Buttons

    """ Done with the csv module"""

    if save_button.draw(lvl_screen):
        # Save Level Data
        # If this file doesn't exist , it will be created
        # If it is already there , then it is going to be over-ridden
        with open(f"level{level}_data.csv", "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            for row in world_data:
                writer.writerow(row)

    if load_button.draw(lvl_screen):
        # Load Level Data
        with open(f"level{level}_data.csv", newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    world_data[y][x] = int(tile)

    """Done with the pickle module"""

    # if save_button.draw(lvl_screen):
    #     # Save Level Data
    #     pickle_out = open(f"level{level}_data", "wb")
    #     pickle.dump(world_data, pickle_out)
    #     pickle_out.close()
    #
    # if load_button.draw(lvl_screen):
    #     scroll = 0
    #     world_data = []
    #     pickle_in = open(f"level{level}_data", "rb")
    #     world_data = pickle.load(pickle_in)

    # Draw Tile Panel
    pg.draw.rect(lvl_screen, LIGHT_GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    # Draw Buttons
    for button_count, i in enumerate(buttons):
        if i.draw(lvl_screen):
            current_tile = button_count

    # Highlight the selected tile
    pg.draw.rect(surface=lvl_screen, color=LIGHT_RED, rect=buttons[current_tile].rect, width=3)

    # Scroll the map
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    # Add new tiles to the screen
    mouse_position = pg.mouse.get_pos()
    x = (mouse_position[0] + scroll) // TILE_SIZE
    y = mouse_position[1] // TILE_SIZE

    # We only want to record mouse clicks which are inside the working area
    if mouse_position[0] < SCREEN_WIDTH and mouse_position[1] < SCREEN_HEIGHT:
        # Left Mouse Button Clicked
        if pg.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile

        # Right Mouse Button Clicked
        if pg.mouse.get_pressed()[2] == 1:
            if world_data[y][x] != -1:
                world_data[y][x] = -1
    # Events
    for event in pg.event.get():

        # Quit Game
        if event.type == pg.QUIT:
            run = False

        # Keyboard Presses
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                run = False
            if event.key == pg.K_UP:
                level += 1
            if event.key == pg.K_DOWN and level > 0:
                level -= 1
            if event.key == pg.K_LEFT:
                scroll_left = True
            if event.key == pg.K_RIGHT:
                scroll_right = True
            if event.key == pg.K_RSHIFT:
                scroll_speed = 5

        # Keyboard Releases
        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                scroll_left = False
            if event.key == pg.K_RIGHT:
                scroll_right = False
            if event.key == pg.K_RSHIFT:
                scroll_speed = 1

    pg.display.update()

pg.quit()

import os, random
from constants import *
from button import Button

# Initialization
pg.mixer.init()
pg.init()

# Load Music
# pg.mixer.music.load("audio/music2.mp3")
# pg.mixer.music.set_volume(0.1)
# pg.mixer.music.play(loops=-1, start=0.0)
jump_fx, shot_fx, grenade_fx = pg.mixer.Sound("audio/jump.wav"), pg.mixer.Sound("audio/shot.wav"), pg.mixer.Sound(
    "audio/grenade.wav")
jump_fx.set_volume(0.90)
shot_fx.set_volume(0.91)
grenade_fx.set_volume(0.915)

# Setting the caption
pg.display.set_caption("Shooter Game - Anique")

# Defining player action variables
moving_left = moving_right = shoot = grenade = grenade_thrown = start_game = start_intro = False

# Define Font
font = pg.font.SysFont("Futura", 30)

screen_scroll, bg_scroll = 0, 0


# Helper Functions
def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()  # Same width of all the images
    for image_counter in range(5):
        screen.blit(sky_img, ((image_counter * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img,
                    ((image_counter * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img,
                    ((image_counter * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((image_counter * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


""" All the classes"""


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, direction):
        # Every bullet instance is going to be added automatically to the group
        self.group = bullet_group
        pg.sprite.Sprite.__init__(self, self.group)

        self.speed = BULLET_SPEED
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    # Over-riding the built-in update method
    def update(self):
        # Move bullets
        self.rect.x += (self.direction * self.speed) + screen_scroll

        # Check if the bullet has gone off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Check collisions with map obstacles
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # Check collision with soldiers
        if pg.sprite.spritecollide(sprite=player, group=bullet_group, dokill=False):
            if player.alive:
                player.health -= 5
                self.kill()
        for danger in enemy_group:
            if pg.sprite.spritecollide(sprite=danger, group=bullet_group, dokill=False):
                if danger.alive:
                    danger.health -= ENEMY_HEALTH_DECREASE_PER_BULLET
                    self.kill()


class Soldier(pg.sprite.Sprite):
    def __init__(self, character_type, x, y, speed, ammo, grenades=0):
        if character_type == "enemy":
            self.group = enemy_group
            pg.sprite.Sprite.__init__(self, self.group)
        else:
            pg.sprite.Sprite.__init__(self)
        self.character_type = character_type
        self.speed = speed
        self.alive = True

        # Starting off when positive direction
        self.direction = 1
        self.flip = False

        """Jump will only be possible when the player is on the ground. So you can not spam the jump key"""
        self.jump = False
        self.y_velocity = 0
        # Assuming the player is starting in air but as soon as he hits the ground , we can set this to False
        self.in_air = True

        """  Animation : If we quickly skim all the pictures of the player , you can observe an animation 
        which is what we are going to use """

        self.animation_list = []
        self.action = 0
        self.frame_index = 0
        self.update_time = pg.time.get_ticks()

        # Load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # Reset temporary list of images
            temporary_list = []

            # Count number of files in the folder
            number_of_frames = len(os.listdir(f'img/{self.character_type}/{animation}'))
            for i in range(number_of_frames):
                img = pg.image.load(f'img/{self.character_type}/{animation}/{i}.png').convert_alpha()
                img = pg.transform.scale(img,
                                         (int(img.get_width() * SOLDIER_SCALE), int(img.get_height() * SOLDIER_SCALE)))
                temporary_list.append(img)
            self.animation_list.append(temporary_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.grenades = grenades
        # Shoot
        self.shoot_cooldown = 0
        self.ammo = ammo
        self.start_ammo = ammo
        self.health = SOLDIER_HEALTH
        self.max_health = self.health

        # AI
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.vision = pg.Rect(0, 0, WIDTH_OF_ENEMY_VISION, 20)

    def draw(self):
        screen.blit(pg.transform.flip(self.image, self.flip, False), self.rect)
        # pg.draw.line(screen, (255, 255, 255), (0, 400), (SCREEN_WIDTH, 400))
        # pg.draw.rect(surface=screen, color=RED, rect=self.rect, width=1)

    def update(self):
        self.update_animation()
        self.check_alive()

        # Checking shoot_cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, move_left, move_right):
        screen_scroll = 0

        # reset movement variables
        dx, dy = 0, 0

        # assign movement variables if moving left or right
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        # must check if the player is currently not in air
        if self.jump and not self.in_air:
            self.y_velocity = -13

            # jump completed
            self.jump = False
            self.in_air = True

        # applying gravity
        self.y_velocity += GRAVITY

        if self.y_velocity > 12:
            self.y_velocity = 12

        dy += self.y_velocity

        # check collision
        for tile in world.obstacle_list:
            # Check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.image.get_width(), self.image.get_height()):
                dx = 0

                # If the ai has hit a wall , make it turn around
                if self.character_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0

            # Check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.image.get_width(), self.image.get_height()):
                # Check if the player is below the groud , i.e jumping
                if self.y_velocity < 0:
                    self.y_velocity = 0
                    dy = tile[1].bottom - self.rect.top

                # Check if the player is above the ground, i.e falling
                elif self.y_velocity >= 0:
                    self.y_velocity = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Check if the player has collided with water
        # Allows us to check collision of a sprite with a sprite group
        if pg.sprite.spritecollide(player, water_group, dokill=False):
            self.health = 0

        # Check if the player has collided with exit
        level_complete = False
        if pg.sprite.spritecollide(player, exit_group, dokill=False):
            level_complete = True

        # Check if the player has fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Check if the player is going off the screen
        if self.character_type == "player":
            if self.rect.left + dx < 0 or self.rect.right > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player's position
        if self.character_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLLING_THRESH and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (
                    self.rect.left < SCROLLING_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0
            self.update_action(3)

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = BULLET_RELOAD_SPEED
            # Basically creating a bullet instance
            Bullet(self.rect.centerx + (0.75 * self.direction * self.rect.size[0]), self.rect.centery,
                   self.direction)
            # Reduce ammo
            self.ammo -= 1

            # Play shoot sound
            shot_fx.play()

    def update_animation(self):
        # Update animation
        ANIMATION_COOLDOWN = 100  # 100 milliseconds

        # Need to call this here else it is going to remain stuck with the first one
        self.image = self.animation_list[self.action][self.frame_index]

        if pg.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            # Have to reset the update time to the current time
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1

        # If the animation has run out , reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            # If the animation is the death animation , then we want to stop the animation at the last image
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action

            # Update the animation settings
            self.frame_index = 0
            self.update_time = pg.time.get_ticks()

    def ai(self):
        # Check if the enemy and player both are alive
        if self.alive and player.alive:
            """We do not want every enemy to move in sink with each other. 
            So we introduce an idling state for the enemies. Randomly, every now and then , the enemies will stop moving
            and be in the idle state."""
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)  # 0 : Idle
                self.idling = True
                self.idling_counter = 50
            # If the AI is near the player
            if self.vision.colliderect(player.rect):
                # Stop running
                self.update_action(0)  # 0 : Idle
                # Start shooting
                self.shoot()
            else:
                if not self.idling:
                    ai_moving_right = True if self.direction == 1 else False
                    ai_moving_left = not ai_moving_right
                    self.move(move_left=ai_moving_left, move_right=ai_moving_right)
                    self.update_action(1)  # 1: Running
                    self.move_counter += 1

                    # Update AI Vision
                    self.vision.center = (
                        self.rect.centerx + WIDTH_OF_ENEMY_VISION / 2 * self.direction, self.rect.centery)
                    # pg.draw.rect(surface=screen, color=RED, rect=self.vision)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # Scrolling Effect
        self.rect.x += screen_scroll


class ItemBox(pg.sprite.Sprite):
    def __init__(self, item_type, x, y):
        self.group = item_box_group
        pg.sprite.Sprite.__init__(self, self.group)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

        """ Note that here we are not using sprite collide but collide_rect because we don't want the enemy to pick up
        the item boxes, only the player can pick up boxes """
        # Check if the player has picked up a box
        if pg.sprite.collide_rect(left=self, right=player):
            # Check what kind of box it was
            if self.item_type == "Health":
                player.health += HEALTH_INCREASE_PER_PICKUP
                # We don't want to increase the health if it is already maximum
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += AMMO_INCREASE_PER_PICKUP
            else:
                player.grenades += GRENADE_INCREASE_PER_PICKUP

            # Delete the item box because it is picked up now
            self.kill()


class Grenade(pg.sprite.Sprite):
    def __init__(self, x, y, direction):
        # Every grenade instance is going to be added automatically to the group
        self.group = grenade_group
        pg.sprite.Sprite.__init__(self, self.group)
        self.timer = GRENADE_TIMER
        self.y_velocity = GRENADE_Y_VELOCITY
        self.speed = GRENADE_SPEED
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.y_velocity += GRAVITY
        dx = self.direction * self.speed
        dy = self.y_velocity

        # Check collision with level obstacles
        for tile in world.obstacle_list:
            # Check in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.image.get_width(), self.image.get_height()):
                self.direction *= -1
                dx = self.direction * self.speed
            # Check in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.image.get_width(), self.image.get_height()):
                self.speed = 0
                if self.y_velocity < 0:
                    self.y_velocity = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.y_velocity >= 0:
                    self.y_velocity = 0
                    dy = tile[1].top - self.rect.bottom
        # Check collision with the walls
        if self.rect.left + dx < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        # Change grenade's position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # Countdown Timer
        self.timer -= 1
        if self.timer <= 0:
            # Grenade will explode meaning it should disappear
            self.kill()

            # Play grenade sound
            grenade_fx.play()
            Explosion(self.rect.x, self.rect.y, 0.7)

            # Do damage to anyone nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and abs(
                    self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= PLAYER_ENEMY_HEALTH_DECREASE_PER_GRENADE

            for danger in enemy_group:
                if abs(self.rect.centerx - danger.rect.centerx) < TILE_SIZE * 2 and abs(
                        self.rect.centery - danger.rect.centery):
                    danger.health -= PLAYER_ENEMY_HEALTH_DECREASE_PER_GRENADE


class Explosion(pg.sprite.Sprite):
    def __init__(self, x, y, scale):
        # Every explosion instance is going to be added automatically to the group
        self.group = explosion_group
        pg.sprite.Sprite.__init__(self, self.group)

        self.images = []
        for num in range(1, 6):
            img = pg.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pg.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # Scroll
        self.rect.x += screen_scroll

        # Update explosion animation
        self.counter += 1
        if self.counter >= GRENADE_EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1

            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, new_health):
        self.health = new_health
        # Calculate ratio for health
        ratio = self.health / self.max_health
        # Draw a border for the health bar
        pg.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, HEALTH_BAR_WIDTH + 4, HEALTH_BAR_HEIGHT + 4))
        # Draw red bar
        pg.draw.rect(screen, RED, (self.x, self.y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        # Drawing a green box on top of the red bar
        pg.draw.rect(screen, GREEN, (self.x, self.y, HEALTH_BAR_WIDTH * ratio, HEALTH_BAR_HEIGHT))


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])  # We want to know how many columns does a level have
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = tile_images[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)

                    # If the tile is a ground , we append the information in the obstacles list

                    # Ground
                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)

                    # Water
                    elif tile == 9 or tile == 10:
                        Water(image=img, x=x * TILE_SIZE, y=y * TILE_SIZE)


                    # Decorations
                    elif 11 <= tile <= 14:
                        Decoration(image=img, x=x * TILE_SIZE, y=y * TILE_SIZE)

                    # Player
                    elif tile == 15:
                        player = Soldier(character_type='player', x=x * TILE_SIZE, y=y * TILE_SIZE,
                                         speed=PLAYER_MOVEMENT_SPEED, ammo=PLAYER_STARTING_AMMO,
                                         grenades=PLAYER_STARTING_GRENADES)
                        health_bar = HealthBar(x=10, y=10, health=player.health, max_health=player.health)

                    # Enemies
                    elif tile == 16:
                        enemy = Soldier(character_type='enemy', x=x * TILE_SIZE, y=y * TILE_SIZE,
                                        speed=ENEMY_MOVEMENT_SPEED, ammo=ENEMY_STARTING_AMMO)

                    # Boxes
                    elif tile == 17:
                        ammo_box = ItemBox("Ammo", x=x * TILE_SIZE, y=y * TILE_SIZE)
                    elif tile == 18:
                        grenade_box = ItemBox("Grenade", x=x * TILE_SIZE, y=y * TILE_SIZE)
                    elif tile == 19:
                        health_box = ItemBox("Health", x=x * TILE_SIZE, y=y * TILE_SIZE)

                    # Complete/Exit Level
                    elif tile == 20:
                        Exit(image=img, x=x * TILE_SIZE, y=y * TILE_SIZE)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            # tile[1] --> gives the rectangle
            # tile[1][0] --> gives the x value of the rectangle
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pg.sprite.Sprite):
    def __init__(self, image, x, y):
        self.group = decoration_group
        pg.sprite.Sprite.__init__(self, self.group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pg.sprite.Sprite):
    def __init__(self, image, x, y):
        self.group = water_group
        pg.sprite.Sprite.__init__(self, self.group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pg.sprite.Sprite):
    def __init__(self, image, x, y):
        self.group = exit_group
        pg.sprite.Sprite.__init__(self, self.group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ScreenFade:
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.speed = speed
        self.color = color
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # Whole Screen Fade
            pg.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pg.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pg.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pg.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # Vertical Screen Fade
            pg.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        return fade_complete


# Create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

world = World()
player, health_bar = world.process_data(world_data)

# Main While Loop
run = True
while run:
    clock.tick(FPS)

    if not start_game:
        # Draw Menu
        screen.fill(BG)

        # Draw buttons
        if start_btn.draw(screen):
            start_game, start_intro = True, True
        if exit_btn.draw(screen):
            run = False
    else:

        # The order of the below operations is vital
        draw_bg()

        # Draw world map
        world.draw()

        # Show health bar
        health_bar.draw(player.health)
        # Show ammo
        draw_text(f"Ammo: ", font, WHITE, 10, 35)
        for ammo_count in range(player.ammo):
            screen.blit(bullet_img, (90 + (ammo_count * 10), 40))

        # Show grenades
        draw_text(f"Grenades: ", font, WHITE, 10, 60)
        for grenade_count in range(player.grenades):
            screen.blit(grenade_img, (135 + (grenade_count * 15), 60))
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # Update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # Show Intro
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # Update player action
        if player.alive:
            if shoot:
                # Here we wanted both the enemy and player to shoot that is why we created a method inside the Player class
                player.shoot()
            elif grenade and not grenade_thrown and player.grenades > 0:
                # Only the player can throw grenades so coding it here
                grenade = Grenade(player.rect.centerx + (0.5 * player.direction * player.rect.size[0]),
                                  player.rect.top,
                                  player.direction)
                grenade_thrown = True

                # Reduce grenades
                player.grenades -= 1

            if player.in_air:
                # Animation for jumping is 1
                player.update_action(2)

            elif moving_left or moving_right:
                # Animation for running is 1
                player.update_action(1)

            else:
                # Animation for idle is 1
                player.update_action(0)

            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            # Check to see if the level is completed
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # Load in level data
                    with open(f'level{level}_data.csv', newline='') as csv_file:
                        reader = csv.reader(csv_file, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_btn.draw(screen):
                    death_fade.fade_counter, bg_scroll = 0, 0
                    start_intro = True
                    world_data = reset_level()

                    # Load in level data
                    with open(f'level{level}_data.csv', newline='') as csv_file:
                        reader = csv.reader(csv_file, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pg.event.get():

        # quit game
        if event.type == pg.QUIT:
            run = False

        # keyboard presses
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                moving_left = True
            if event.key == pg.K_d:
                moving_right = True
            if event.key == pg.K_SPACE:
                shoot = True
            if event.key == pg.K_q:
                grenade = True
            if event.key == pg.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pg.K_ESCAPE:
                run = False

        # keyboard button released
        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                moving_left = False
            if event.key == pg.K_d:
                moving_right = False
            if event.key == pg.K_SPACE:
                shoot = False
            if event.key == pg.K_q:
                grenade = grenade_thrown = False

    pg.display.update()
pg.quit()

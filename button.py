import pygame as pg


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pg.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # Get Mouse Position
        position = pg.mouse.get_pos()

        # Check Mouseover and Clicked Conditions
        if self.rect.collidepoint(position):
            if pg.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw Button
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

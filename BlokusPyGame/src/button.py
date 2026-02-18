import pygame
from pygame.surface import Surface


class Button:
    def __init__(self, screen: Surface, text: str, x: int, y: int, size: int, padding=10):
        self.screen = screen
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.padding = padding

        self.font = pygame.font.Font(pygame.font.get_default_font(), size)
        self.font_surface = self.font.render(text, False, 0)
        self.text_rect = self.font_surface.get_rect(center=(x, y)).inflate(padding, padding)

    def is_selected(self) -> bool:
        x, y, width, height = self.text_rect
        mouse_x, mouse_y = pygame.mouse.get_pos()

        return x <= mouse_x < x + width and y <= mouse_y < y + height

    def render(self):
        pygame.draw.rect(self.screen, 0xC8C8C8 if self.is_selected() else 0xDFDFDF, self.text_rect)
        self.screen.blit(self.font_surface, self.text_rect)

import pygame

from ui import UI


class Game:
    def __init__(self, width: int, height: int):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Blokus')

        self.clock = pygame.time.Clock()
        self.running = True

        self.ui = UI(pygame.display.set_mode((width, height)))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

                self.ui.handle_input(event)

            self.ui.render()
            self.clock.tick(60)

        pygame.quit()

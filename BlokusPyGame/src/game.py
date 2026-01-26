import pygame

from board import Board

class Game:
    def __init__(self, window):
        """
        Intialize Game Window and set basic params
        """
        self.window = window

        pygame.init()
        self.screen = pygame.display.set_mode(window)

        self.clock = pygame.time.Clock()
        self.running = True

        self.board = Board()

    def render_board(self):
        """
        Draw the Blokus board grid to the screen. Each cell is rendered as a 
        colored rectangle with a black border. Cell colors reflect the owner 
        (player ID) stored in the board's grid.
        """
        cell_size = 20

        pos = (self.window[0]//4, self.window[1]//4)

        for row in range(self.board.size):
            for col in range(self.board.size):
                x = col * cell_size + pos[0]
                y = row * cell_size + pos[1]

                color = (200, 200, 200) #light gray for now, will be based by owner of tile later 

                pygame.draw.rect(self.screen, color, (x, y, cell_size, cell_size))

                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, cell_size, cell_size), 1)

    def run(self):
        # Main game loop
        while self.running:
            keys = pygame.key.get_pressed() #might need this
            for event in pygame.event.get(): #waiting for user events
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: #For easy kill of the window
                        self.running = False

            self.screen.fill("white")

            #Game Rendering Here
            self.render_board()

            
            pygame.display.flip()

            self.clock.tick(60) 

        pygame.quit()

    

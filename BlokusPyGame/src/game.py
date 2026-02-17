import pygame
import math

from board import Board
from turn import Turn
from ui import UI
from piece import PIECES
from color import Color



class Game:
    def __init__(self, width: int, height: int):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Blokus')
        self.clock = pygame.time.Clock()
        self.running = True
        self.board = Board()
        self.turn = Turn(self.board)
        self.ui = UI(pygame.display.set_mode((width, height)), self.board, self.turn)
        
        self.score_dict = {}

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
            blue_score, yellow_score, red_score, green_score = self.count_score(self.ui.game_over)
            self.set_score_dict((blue_score, yellow_score, red_score, green_score ))
            self.clock.tick(60)
            # print(f"Blue Score: {blue_score}, Yellow Score: {yellow_score}, Red Score: {red_score}, Green Score: {green_score}")
            
            if (self.ui.game_over):
                winners = self.determine_winner()
                if len(winners) == 1:
                    print(f"Winner: {winners[0]}")
                elif len(winners) > 1:
                    print(f"Tie between: {', '.join([str(color) for color in winners])}")
                else:
                    print("No winner determined")

        pygame.quit()

    def count_score(self, game_over: bool):

        blue_count = 0; yellow_count = 0; red_count = 0; green_count = 0
        if (game_over): 
            for player, _ in self.ui.piece_regions.items():
                    for piece in player.remaining_pieces: 
                        shape = PIECES[piece]
                        for _ in shape:
                            if player.color == Color.BLUE: 
                                blue_count += 1 
                            if player.color == Color.YELLOW:
                                yellow_count += 1
                            if player.color == Color.RED: 
                                red_count += 1
                            if player.color == Color.GREEN:
                                green_count += 1

        return -1 * blue_count, -1 * yellow_count, -1 * red_count, -1 * green_count
    
    def set_score_dict(self, score_tuple: tuple[int, int, int, int]):

        for player, _ in self.ui.piece_regions.items():
            if player.color == Color.BLUE: 
                self.score_dict[player.color] = score_tuple[0]
            if player.color == Color.YELLOW:
                self.score_dict[player.color] = score_tuple[1]
            if player.color == Color.RED: 
                self.score_dict[player.color] = score_tuple[2]
            if player.color == Color.GREEN:
                self.score_dict[player.color] = score_tuple[3]
        
    def determine_winner(self): 
        score_desc = {k: v for k, v in sorted(self.score_dict.items(), key=lambda item: item[1], reverse= True)} #might be used
        max_score = max(self.score_dict.values())
        winner = [color for color, score in self.score_dict.items() if score == max_score]
        return winner


             

import pygame
from pygame.event import Event
from pygame.surface import Surface

from board import Board
from button import Button
from game_ui import GameUI
from turn import Turn

BACKGROUND = 0x222222


class UI:
    def __init__(self, screen: Surface):
        self.screen: Surface = screen
        self.two_player_button = Button(self.screen, "Two Players", self.screen.get_width() // 2 - 100, self.screen.get_height() // 2, 24)
        self.four_player_button = Button(self.screen, "Four Players", self.screen.get_width() // 2 + 100, self.screen.get_height() // 2, 24)
        self.ui: GameUI | None = None

    def handle_input(self, event: Event):
        if self.ui:
            self.ui.handle_input(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.two_player_button.is_selected():
                    board = Board(True)
                    turn = Turn(board)
                    self.ui = GameUI(self.screen, board, turn)
                elif self.four_player_button.is_selected():
                    board = Board(False)
                    turn = Turn(board)
                    self.ui = GameUI(self.screen, board, turn)

    def render(self):
        if self.ui:
            self.ui.render()
            return

        self.screen.fill(BACKGROUND)
        self.two_player_button.render()
        self.four_player_button.render()
        pygame.display.flip()

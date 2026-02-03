import pygame
from pygame.surface import Surface

from board import Board

CELL_SIZE = 20


class UI:
    def __init__(self, screen: Surface, board: Board):
        self.screen: Surface = screen
        self.board: Board = board

    def render(self):
        self.screen.fill("white")
        self._render_board()
        self._render_piece_selection()
        self._render_piece_hover()
        pygame.display.flip()

    def _render_board(self):
        """
        Render the grid and the tiles that have been played on the grid.
        """
        for x in range(self.board.size):
            for y in range(self.board.size):
                screen_x = x * CELL_SIZE + self.screen.width // 4
                screen_y = y * CELL_SIZE + self.screen.height // 4

                pygame.draw.rect(self.screen, self.board.grid[x][y].value, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, (0, 0, 0), (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)

    def _render_piece_selection(self):
        """
        Render each of the players' remaining pieces on their respective side of the board.
        """
        pass

    def _render_piece_hover(self):
        """
        Render the currently selected piece that hovers over the grid to preview its placement.
        """
        pass

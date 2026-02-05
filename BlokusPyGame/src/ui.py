from dataclasses import dataclass

import pygame
from pygame.surface import Surface

from board import Board
from color import Color
from piece import PIECES
from player import Player

CELL_SIZE = 20


@dataclass
class PanelRegion:
    x: int
    y: int
    width: int
    height: int


class UI:
    def __init__(self, screen: Surface, board: Board):
        self.screen: Surface = screen
        self.board: Board = board

        # Calculate Board Boundaries ---- (board_start_x, board_end_x) = (200, 600) = (board_start_y, board_end_y)
        board_start_x = self.screen.get_width() // 4  # 800 // 4 = 200
        board_end_x = board_start_x + (self.board.size * CELL_SIZE)  # 200 + (20 * 20) = 600
        board_start_y = self.screen.get_height() // 4  # 200
        board_end_y = board_start_y + (self.board.size * CELL_SIZE)  # 600

        self.piece_regions: dict[Color, PanelRegion] = {
            Color.RED: PanelRegion(0, board_start_y, board_start_x, board_end_y - board_start_y),  # Red region - (0, 200, 200, 400) = Left
            Color.YELLOW: PanelRegion(board_start_x, board_end_y, board_end_x - board_start_x, board_start_y),  # yellow region - (200, 600, 400, 200) = bottom
            Color.GREEN: PanelRegion(board_end_x, board_start_y, board_start_x, board_end_y - board_start_y),  # green region - (600, 200, 200, 400) = right
            Color.BLUE: PanelRegion(board_start_x, 0, board_end_x - board_start_x, board_start_y)  # blue region - (200, 0, 400, 200) = top
        }
        self.piece_sections: list[Color] = list(self.piece_regions)

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
                screen_x = x * CELL_SIZE + self.screen.get_width() // 4
                screen_y = y * CELL_SIZE + self.screen.get_height() // 4

                pygame.draw.rect(self.screen, self.board.grid[x][y].value, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, (0, 0, 0), (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)

    def _render_piece_selection(self):
        """
        Render each of the players' remaining pieces on their respective side of the board.
        """
        # this needs work
        piece_spacing = 40
        panel_tile_size = 12
        padding = 5
        pieces_per_row = 5

        left = self.piece_sections[0]  # red
        right = self.piece_sections[2]  # green
        bottom = self.piece_sections[1]  # yellow
        top = self.piece_sections[3]  # blue

        for color, sections in self.piece_regions.items():
            # pygame.draw.rect(self.screen, color.value, (sections.x, sections.y, sections.width, sections.height))

            if color.value == left.value:
                print(color.value)

            y_offset = sections.y + padding
            player = Player(color)
            for idx, piece in enumerate(player.remaining_pieces):
                piece_shape = PIECES[piece]

                row = idx // pieces_per_row
                col = idx % pieces_per_row

                x_offset = sections.x + padding + col * piece_spacing
                y_offset = sections.y + padding + row * piece_spacing

                for dx, dy in piece_shape:
                    x = x_offset + (dx * panel_tile_size)
                    y = y_offset + (dy * panel_tile_size)
                    pygame.draw.rect(self.screen, color.value, (x, y, panel_tile_size, panel_tile_size))
                    pygame.draw.rect(self.screen, (0, 0, 0), (x, y, panel_tile_size, panel_tile_size), 1)

    def _render_piece_hover(self):
        """
        Render the currently selected piece that hovers over the grid to preview its placement.
        """
        pass

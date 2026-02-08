import math
from dataclasses import dataclass

import pygame
from pygame.event import Event
from pygame.surface import Surface

from board import Board
from piece import PIECES, Piece
from player import Player
from turn import Turn

# CONSTANTS
CELL_SIZE = 20
PANEL_TILE_SIZE = 12
PADDING = 3
PIECES_PER_ROW = 3
PIECES_PER_COL = 7
BORDER_COLOR = (0, 0, 0)
CAN_PLAY_BORDER_COLOR = (0, 223, 0)
CANNOT_PLAY_BORDER_COLOR = (223, 0, 0)


# STRUCTS
@dataclass
class PanelRegion:
    x: int
    y: int
    width: int
    height: int
    pieces_per_n: int


class UI:
    def __init__(self, screen: Surface, board: Board, turn: Turn):
        self.screen: Surface = screen
        self.board: Board = board
        self.turn = turn

        # Calculate Board Boundaries ---- (board_start_x, board_end_x) = (200, 600) = (board_start_y, board_end_y)
        board_start_x = self.screen.get_width() // 4  # 800 // 4 = 200
        board_end_x = board_start_x + (self.board.size * CELL_SIZE)  # 200 + (20 * 20) = 600
        board_start_y = self.screen.get_height() // 4  # 200
        board_end_y = board_start_y + (self.board.size * CELL_SIZE)  # 600

        self.piece_regions: dict[Player, PanelRegion] = {
            self.turn.players[0]: PanelRegion(0, board_start_y, board_start_x, board_end_y - board_start_y, PIECES_PER_ROW),  # Red region - (0, 200, 200, 400) = Left
            self.turn.players[1]: PanelRegion(board_start_x, board_end_y, board_end_x - board_start_x, board_start_y, PIECES_PER_COL),  # yellow region - (200, 600, 400, 200) = bottom
            self.turn.players[2]: PanelRegion(board_end_x, board_start_y, board_start_x, board_end_y - board_start_y, PIECES_PER_ROW),  # green region - (600, 200, 200, 400) = right
            self.turn.players[3]: PanelRegion(board_start_x, 0, board_end_x - board_start_x, board_start_y, PIECES_PER_COL)  # blue region - (200, 0, 400, 200) = top
        }
        self.piece_bounds = {}

    def handle_input(self, event: Event):
        """
        Handles changing piece orientation, choosing piece, and placing piece with keybinds.
        """
        player = self.turn.current_player

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                piece_clicked = self._select_piece()

                if piece_clicked:
                    player.piece = Piece(piece_clicked, player.color)

                elif player.piece and self.board.can_place_piece(player.piece):
                    self.turn.place_piece(player.piece)
            elif event.button == 3 and player.piece:
                if player.piece:
                    player.piece.flip()
        elif event.type == pygame.MOUSEWHEEL and player.piece:
            if event.y > 0:
                player.piece.rotate_cw()
            else:
                player.piece.rotate_ccw()

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
                pygame.draw.rect(self.screen, BORDER_COLOR, (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)

    def _render_piece_selection(self):
        """
        Render each of the players' remaining pieces on their respective side of the board.
        """
        self.piece_bounds = {}

        for player, region in self.piece_regions.items():
            for idx, piece in enumerate(player.remaining_pieces):
                piece_shape = PIECES[piece]

                # Calculate grid positions
                row = idx // region.pieces_per_n
                col = idx % region.pieces_per_n

                x_offset = region.x + PADDING + col * 63.5
                y_offset = region.y + PADDING + row * 50

                min_x = math.inf
                min_y = math.inf
                max_x = -math.inf
                max_y = -math.inf

                for dx, dy in piece_shape:
                    x = x_offset + dx * PANEL_TILE_SIZE
                    y = y_offset + dy * PANEL_TILE_SIZE

                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

                    pygame.draw.rect(self.screen, player.color.value, (x, y, PANEL_TILE_SIZE, PANEL_TILE_SIZE))
                    border_color = CAN_PLAY_BORDER_COLOR if player == self.turn.current_player and type(player.piece) is Piece and piece == player.piece.shape else BORDER_COLOR
                    pygame.draw.rect(self.screen, border_color, (x, y, PANEL_TILE_SIZE, PANEL_TILE_SIZE), 1)

                x = min_x
                y = min_y

                width = (max_x - min_x) + PANEL_TILE_SIZE
                height = (max_y - min_y) + PANEL_TILE_SIZE

                if player == self.turn.current_player:
                    self.piece_bounds[piece] = (x, y, width, height)

    def _select_piece(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for piece_key, bounds in self.piece_bounds.items():
            x, y, width, height = bounds

            if (x <= mouse_x <= x + width) and (y <= mouse_y <= y + height):
                return piece_key

        return None

    def _render_piece_hover(self):
        """
        Render the currently selected piece that hovers over the grid to preview its placement.
        """
        player = self.turn.current_player

        if not player.piece:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        pos_x = (mouse_x - self.screen.get_width() // 4) // CELL_SIZE
        pos_y = (mouse_y - self.screen.get_height() // 4) // CELL_SIZE
        player.piece.set_pos(pos_x, pos_y)

        for x, y in player.piece.tiles():
            if x < 0 or y < 0 or x >= self.board.size or y >= self.board.size:
                return

        can_place_piece = self.board.can_place_piece(player.piece)
        border_color = CAN_PLAY_BORDER_COLOR if can_place_piece else CANNOT_PLAY_BORDER_COLOR

        for pos in player.piece.tiles():
            x = CELL_SIZE * pos[0] + self.screen.get_width() // 4
            y = CELL_SIZE * pos[1] + self.screen.get_height() // 4

            pygame.draw.rect(self.screen, player.color.value, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, border_color, (x, y, CELL_SIZE, CELL_SIZE), 2)

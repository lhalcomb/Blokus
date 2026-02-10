import math
from dataclasses import dataclass

import pygame
from pygame.event import Event
from pygame.surface import Surface

from board import Board
from color import Color
from piece import PIECES, Piece
from player import Player
from turn import Turn

# CONSTANTS
CELL_SIZE = 20
PANEL_TILE_SIZE = 12
PADDING = 3
PIECES_PER_ROW = 3
PIECES_PER_COL = 7
BORDER_COLOR = 0
CAN_PLAY_BORDER_COLOR = 0x00DF00
CANNOT_PLAY_BORDER_COLOR = 0xDF0000


# STRUCTS
@dataclass
class Bounds:
    x: int
    y: int
    width: int
    height: int

    def __iter__(self):
        return iter((self.x, self.y, self.width, self.height))


@dataclass
class PanelRegion:
    bounds: Bounds
    pieces_per_n: int


class UI:
    def __init__(self, screen: Surface, board: Board, turn: Turn):
        self.screen: Surface = screen
        self.font = pygame.Font(pygame.font.get_default_font())
        self.board: Board = board
        self.turn: Turn = turn
        self.piece_regions: dict[Player, PanelRegion] = self._get_piece_regions()
        self.piece_bounds: dict[str, Bounds] = {}
        self.forfeit_button_bounds = Bounds(10, self.screen.get_height() - 50, 105, 40)

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

                elif self._is_forfeit_button_selected():
                    self.turn.current_player.forfeit = True
                    self.turn.next_turn()

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
        self.screen.fill(0xFFFFFF)
        self._render_board()
        self._render_piece_selection()
        self._render_piece_hover()
        self._render_forfeit_button()
        pygame.display.flip()

    def _get_piece_regions(self):
        x_start = self.screen.get_width() // 4
        x_end = x_start + (self.board.size * CELL_SIZE)
        y_start = self.screen.get_height() // 4
        y_end = y_start + (self.board.size * CELL_SIZE)

        return {
            self.turn.players[0]: PanelRegion(Bounds(0x000, y_start, x_start, y_end - y_start), PIECES_PER_ROW),
            self.turn.players[1]: PanelRegion(Bounds(x_start, y_end, x_end - x_start, y_start), PIECES_PER_COL),
            self.turn.players[2]: PanelRegion(Bounds(x_end, y_start, x_start, y_end - y_start), PIECES_PER_ROW),
            self.turn.players[3]: PanelRegion(Bounds(x_start, 0x000, x_end - x_start, y_start), PIECES_PER_COL),
        }

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
            bounds = region.bounds

            if player == self.turn.current_player:
                if player.color == Color.RED or player.color == Color.GREEN:
                    pygame.draw.rect(self.screen, 0, (bounds.x, bounds.y, bounds.width, bounds.height), 1)
                else:
                    pygame.draw.rect(self.screen, 0, (bounds.x, bounds.y, bounds.width + 23, bounds.height), 1)

            for idx, piece in enumerate(player.remaining_pieces):
                piece_shape = PIECES[piece]

                row = idx // region.pieces_per_n
                col = idx % region.pieces_per_n

                x_offset = bounds.x + PADDING + col * 63.5
                y_offset = bounds.y + PADDING + row * 50

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
                    self.piece_bounds[piece] = Bounds(x, y, width, height)

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

        width, height = player.piece.size()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        pos_x = (mouse_x - self.screen.get_width() // 4 - width * CELL_SIZE // 2) // CELL_SIZE
        pos_y = (mouse_y - self.screen.get_height() // 4 - height * CELL_SIZE // 2) // CELL_SIZE

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

    def _is_forfeit_button_selected(self) -> bool:
        x, y, width, height = self.forfeit_button_bounds
        mouse_x, mouse_y = pygame.mouse.get_pos()

        return x <= mouse_x < x + width and y <= mouse_y < y + height

    def _render_forfeit_button(self):
        color = 0xC8C8C8 if self._is_forfeit_button_selected() else 0xDFDFDF
        x, y, width, height = self.forfeit_button_bounds

        pygame.draw.rect(self.screen, color, (x, y, width, height))
        self.screen.blit(self.font.render("Forfeit", True, 0), (x + 20, y + 10))

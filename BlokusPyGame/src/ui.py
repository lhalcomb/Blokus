from dataclasses import dataclass

import math
import pygame
from pygame.event import Event
from pygame.surface import Surface

from board import Board
from color import Color
from piece import PIECES, Piece
from player import Player
from turn import Turn

#CONSTANTS
CELL_SIZE = 20
PANEL_TILE_SIZE = 12
PADDING = 3
PIECES_PER_ROW = 3
PIECES_PER_COL = 7


#STRUCTS
@dataclass
class PanelRegion:
    x: int
    y: int
    width: int
    height: int



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

        self.piece_regions: dict[Color, PanelRegion] = {
            Color.RED: PanelRegion(0, board_start_y, board_start_x, board_end_y - board_start_y),  # Red region - (0, 200, 200, 400) = Left
            Color.YELLOW: PanelRegion(board_start_x, board_end_y, board_end_x - board_start_x, board_start_y),  # yellow region - (200, 600, 400, 200) = bottom
            Color.GREEN: PanelRegion(board_end_x, board_start_y, board_start_x, board_end_y - board_start_y),  # green region - (600, 200, 200, 400) = right
            Color.BLUE: PanelRegion(board_start_x, 0, board_end_x - board_start_x, board_start_y)  # blue region - (200, 0, 400, 200) = top
        }
        self.piece_sections: list[Color] = list(self.piece_regions)
        self.piece_bounds = {}

    def handle_input(self, event: Event):
        """
        Handles changing piece orientation, choosing piece, and placing piece with keybinds.
        """
        player = self.turn.current_player

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.board.can_place_piece(player.piece):
                    self.turn.place_piece(player.piece)
                
            elif event.button == 3:
                player.piece.flip()
        elif event.type == pygame.MOUSEWHEEL:
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
                pygame.draw.rect(self.screen, (0, 0, 0), (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)

    def _render_piece_selection(self):
        """
        Render each of the players' remaining pieces on their respective side of the board.
        """
        left = self.piece_sections[0]  # red
        right = self.piece_sections[2]  # green
        bottom = self.piece_sections[1]  # yellow
        top = self.piece_sections[3]  # blue

        player_t = self.turn.current_player

        for color, sections in self.piece_regions.items():
            # pygame.draw.rect(self.screen, color.value, (sections.x, sections.y, sections.width, sections.height))
            
            if (color.value == left.value) or (color.value == right.value):
                self._render_section(player_t, color, sections, PIECES_PER_ROW)
                piece_clicked = self._select_piece()
                
                if piece_clicked != None:
                    player_t.piece = Piece(piece_clicked[0], player_t.color)
                
            elif (color.value == top.value) or (color.value == bottom.value):
                self._render_section(player_t, color, sections, PIECES_PER_COL)
                piece_clicked = self._select_piece()
    
                if piece_clicked != None:
                    player_t.piece = Piece(piece_clicked[0], player_t.color)
                

    def _select_piece(self):

        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for piece_bound in self.piece_bounds.items():
            x, y, width, height, color = piece_bound[1]
            if (x <= mouse_x <= x + width) and (y <= mouse_y <= y + height) :
                return piece_bound
                
            

        
    def _render_section(self, player: Player, color: Color, sections: PanelRegion, pieces_per_n: int):
        """ Helper to render pieces into the sections with a given layout"""
    
        for idx, piece in enumerate(player.remaining_pieces):
            piece_shape = PIECES[piece]

            # Calculate grid positions
            row = idx // pieces_per_n
            col = idx % pieces_per_n
            
            x_offset = sections.x + PADDING + col * 63.5 
            y_offset = sections.y + PADDING + row * 50

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
            
                pygame.draw.rect(self.screen, color.value, (x, y, PANEL_TILE_SIZE, PANEL_TILE_SIZE))
                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, PANEL_TILE_SIZE, PANEL_TILE_SIZE), 1)
            x = min_x
            y = min_y 
            width = (max_x - min_x) + PANEL_TILE_SIZE
            height = (max_y - min_y) + PANEL_TILE_SIZE

            if color == self.turn.current_player.color:
                self.piece_bounds[piece] = (x, y, width, height, color.value)
        
        

    def _render_piece_hover(self):
        """
        Render the currently selected piece that hovers over the grid to preview its placement.
        """
        player = self.turn.current_player

        mouse_x, mouse_y = pygame.mouse.get_pos()
        pos_x = (mouse_x - self.screen.get_width() // 4) // 20 - 1
        pos_y = (mouse_y - self.screen.get_height() // 4) // 20 - 1
        player.piece.set_pos(pos_x, pos_y)

        can_place_piece = self.board.can_place_piece(player.piece)
        border_color = (0, 223, 0) if can_place_piece else (223, 0, 0)

        for pos in player.piece.tiles():
            x = CELL_SIZE * pos[0] + self.screen.get_width() // 4
            y = CELL_SIZE * pos[1] + self.screen.get_height() // 4

            pygame.draw.rect(self.screen, player.color.value, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, border_color, (x, y, CELL_SIZE, CELL_SIZE), 2)




   
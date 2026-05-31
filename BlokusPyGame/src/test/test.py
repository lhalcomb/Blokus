import math
from dataclasses import dataclass

import pygame
from pygame.event import Event
from pygame.surface import Surface

import numpy as np 
from enum import Enum


class Color(Enum):
    EMPTY = 0x444444
    PURPLE = 0xA13CE0
    ORANGE = 0xE08C3C
    BLUE = 0x3953ED
    YELLOW = 0xEFD93E
    RED = 0xEF593E
    GREEN = 0x59D741
    
    
PIECES = {
    'I1': [(0, 0)],
    'I2': [(0, 0), (1, 0)],
    'I3': [(0, 0), (1, 0), (2, 0)],
    'L3': [(0, 0), (1, 0), (0, 1)],
    'I4': [(0, 0), (1, 0), (2, 0), (3, 0)],
    'L4': [(0, 0), (1, 0), (0, 1), (0, 2)],
    'N4': [(0, 0), (0, 1), (1, 1), (1, 2)],
    'O4': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'T4': [(0, 0), (1, 0), (2, 0), (1, 1)],
    'F5': [(0, 0), (1, 0), (1, 1), (2, 1), (1, 2)],
    'I5': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    'L5': [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1)],
    'N5': [(0, 0), (1, 0), (2, 0), (2, 1), (3, 1)],
    'P5': [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)],
    'T5': [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
    'U5': [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1)],
    'V5': [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)],
    'W5': [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
    'X5': [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    'Y5': [(0, 0), (1, 0), (2, 0), (3, 0), (1, 1)],
    'Z5': [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)],
}


def normalize(shape):
    min_x = min(x for x, y in shape)
    min_y = min(y for x, y in shape)

    shape = [(x - min_x, y - min_y) for x, y in shape]

    return shape


class Piece:
    def __init__(self, shape: str, color: Color):
        self.shape: str = shape
        self.color: Color = color
        self.x: int = 0
        self.y: int = 0
        self.rotations: int = 0  # 0-3
        self.flipped: bool = False

    def set_pos(self, x: int, y: int):
        self.x = x
        self.y = y

    def rotate_cw(self):
        self.rotations = (self.rotations + 1) % 4

    def rotate_ccw(self):
        self.rotations = (self.rotations - 1) % 4

    def flip(self):
        self.flipped = not self.flipped

    def tiles(self):
        shape = PIECES[self.shape]

        for _ in range(self.rotations):
            shape = [(-y, x) for x, y in shape]

        if self.flipped:
            shape = [(-x, y) for x, y in shape]

        return [(x + self.x, y + self.y) for x, y in normalize(shape)]

    def size(self) -> tuple[int, int]:
        tiles = self.tiles()
        min_x = min(x for x, _ in tiles)
        min_y = min(y for _, y in tiles)

        return max(x for x, _ in tiles) - min_x, max(y for _, y in tiles) - min_y



class Player:
    def __init__(self, color: Color):
        self.color: Color = color
        self.remaining_pieces: list[str] = list(PIECES.keys())
        self.piece: Piece | None = None
        self.forfeit = False

    def remove_piece(self, shape: str):
        self.remaining_pieces.remove(shape)

colorIntMap = {color: i for i, color in enumerate(Color)}

from numpy.typing import NDArray
class Board:
    def __init__(self, version: bool):
        self.version = version
        self.size: int = 20 if version else 14

        self.board: list[Color] = [Color.EMPTY] * (self.size * self.size)
        self.grid: NDArray[np.object_] = np.array(self.board, dtype=object)
        
        self.starting_corners: dict[Color, int] = {
            Color.BLUE: 0,
            Color.YELLOW: self.size - 1,
            Color.RED: (self.size ** 2) - 1,
            Color.GREEN: (self.size ** 2) - (self.size),
        } if version else {
            Color.PURPLE: (4 * self.size) + 4,
            Color.ORANGE: ((self.size * self.size) - (4 * self.size)) - 5,
        }

        self.last_move_map = {}
        self.piece_orientations = {}

    def can_place_piece(self, piece: Piece) -> bool:
        touches_player_corner = False

        for pos in piece.tiles():
            x, y = pos
            # Check for bounds
            if x < 0 or x >= self.size or y < 0 or y >= self.size:
                return False

            # Check for overlap
            if self.grid[self._get_index(x,y)] != Color.EMPTY:
                return False

            # Check for edge-to-edge
            if (x > 0 and self.grid[self._get_index(x - 1, y)] == piece.color) or \
                    (x < self.size - 1 and self.grid[self._get_index(x + 1, y)] == piece.color) or \
                    (y > 0 and self.grid[self._get_index(x, y - 1)] == piece.color) or \
                    (y < self.size - 1 and self.grid[self._get_index(x, y + 1)] == piece.color):
                return False

            # Check for corner-to-corner
            if touches_player_corner:
                continue

            if (x > 0 and y > 0 and self.grid[self._get_index(x - 1, y - 1)] == piece.color) or \
                    (x > 0 and y < self.size - 1 and self.grid[self._get_index(x - 1, y + 1)] == piece.color) or \
                    (x < self.size - 1 and y > 0 and self.grid[self._get_index(x + 1, y - 1)] == piece.color) or \
                    (x < self.size - 1 and y < self.size - 1 and self.grid[self._get_index(x + 1, y + 1)] == piece.color):
                touches_player_corner = True

            # Check for starting piece
            elif self._get_index(x, y) == self.starting_corners[piece.color]:
                touches_player_corner = True

        return touches_player_corner

    def place_piece(self, piece: Piece):
        for pos in piece.tiles():
            idx = self._get_index(pos[0], pos[1])
            self.grid[idx] = piece.color
        
        self.last_move_map[piece.color] = {
            "shape": piece.shape,
            "tiles": piece.tiles(),
        }

    def unplace_piece(self, piece: Piece):
        for pos in piece.tiles():
            self.grid[self._get_index(pos[0], pos[1])] = Color.EMPTY
        
        self.last_move_map.pop(piece.color, None)

    def last_move(self, player: Color): 
        """Used for mirroring the opponents moves """
        return self.last_move_map.get(player)
    
    def _get_index(self, x: int, y: int) -> int:
        return x + y * self.size
    
    def _compute_orientations(self, shape):
        if shape in self.piece_orientations:
            return self.piece_orientations[shape]
        
        piece = Piece(shape, Color.EMPTY) #temp place holder
        orientations = []
        seen = set()

        for flipped in [False, True]:
            for rotations in range(4):
                piece.rotations = rotations
                piece.flipped = flipped

                tiles = tuple(sorted(piece.tiles()))

                if tiles not in seen:
                    orientations.append((rotations, flipped))
                    seen.add(tiles)
                              
        self.piece_orientations[shape] = orientations
        return orientations
    
    def _get_orientations(self, shape): 
        if shape not in self.piece_orientations:
            self.piece_orientations[shape] = self._compute_orientations(shape)
        return self.piece_orientations[shape]
    
    def player_can_play(self, player: Player) -> bool: # There has got to be a better way to do this

        """
        Whether the player has any available moves left.
        Checks every remaining piece at every position and orientation.
        """
        if player.forfeit:
            return False

        for shape in player.remaining_pieces:
            piece = Piece(shape, player.color)
            for x in range(self.size):
                for y in range(self.size):
                    piece.set_pos(x, y)
                    
                    for rotations, flipped in self._get_orientations(shape):
                        piece.rotations = rotations
                        piece.flipped = flipped
                        
                        if self.can_place_piece(piece):
                            return True

        return False

    def print_grid(self):
        arr = np.array([[colorIntMap[color] for color in self.grid]])
        return arr.reshape(self.size, self.size)
        

# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=false
#             
class Turn:
    def __init__(self, board: Board):
        self.board = board
        self.players = [
            Player(Color.BLUE),
            Player(Color.YELLOW),
            Player(Color.RED),
            Player(Color.GREEN),
        ] if board.version else [
            Player(Color.PURPLE),
            Player(Color.ORANGE),
        ] 
        self.active_players = self.players.copy()
        self.current_player = self.active_players[0]
        self.game_over = False
        self.scores: dict[Color, int] = self.get_scores()

    def place_piece(self, piece: Piece):
        if self.current_player is None: 
            raise ValueError("No current player - game is over")
        
        self.current_player.remove_piece(piece.shape)
        self.board.place_piece(piece)
        self.scores = self.get_scores()
        self.next_turn()

    def next_turn(self):
        """
        Sets current_player to the next player. Ends the game when no players are left.
        """
        player = self.current_player
        player.piece = None

        if len(self.active_players) > 1:
            current_index = self.active_players.index(player)
            self.current_player = self.active_players[(current_index + 1) % len(self.active_players)]

        if not self.board.player_can_play(player):
            self.active_players.remove(player)

        if len(self.active_players) == 0:
            print("Game Over")
            self._get_extra_scores()
            self.game_over = True
            self.current_player = None

    def get_scores(self):
        
        return {player.color: (-sum(len(PIECES[piece]) for piece in player.remaining_pieces)) for player in self.players}

    def _get_extra_scores(self): 
        monomino_last_score = 5; no_remaining_pieces_left = 15

        for last_move_color, last_move_info in self.board.last_move_map.items():
            if last_move_info['shape'] == 'I1' and last_move_color == Color.PURPLE:
                self.scores[Color.PURPLE] += monomino_last_score
            elif last_move_info['shape'] == 'I1' and last_move_color == Color.ORANGE:
                self.scores[Color.ORANGE] += monomino_last_score
        
        for player in self.players:
            if len(player.remaining_pieces) == 0: 
                self.scores[player.color] += no_remaining_pieces_left        

class Game:
    def __init__(self, width: int, height: int, version: bool):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Blokus')
        

        self.clock = pygame.time.Clock()
        self.running = True
        self.board = Board(version)
        self.turn = Turn(self.board)
        self.ui = UI(pygame.display.set_mode((width, height)), self.board, self.turn)
        

    def run(self):
    
        self._run_interactive()
    
    def _run_interactive(self):
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
    

# pyright: reportOptionalMemberAccess=false


# CONSTANTS
CELL_SIZE = 20
PANEL_TILE_SIZE = 12
PADDING = 3
PIECES_PER_ROW = 3
PIECES_PER_COL = 7
BACKGROUND = 0x222222
BORDER_COLOR = 0x222222
HIGHLIGHT = 0xFFFFFF


# STRUCTS
@dataclass
class Bounds:
    x: int | float
    y: int | float
    width: int | float
    height: int | float

    def __iter__(self):
        return iter((self.x, self.y, self.width, self.height))


@dataclass
class PanelRegion:
    bounds: Bounds
    pieces_per_n: int


class UI:
    def __init__(self, screen: Surface, board: Board, turn: Turn):
        self.screen: Surface = screen
        self.font = pygame.font.Font(pygame.font.get_default_font(), 24)
        self.board: Board = board
        self.turn: Turn = turn
        self.version = board.version
        self.piece_regions: dict[Player, PanelRegion] = self._get_piece_regions()
        self.piece_bounds: dict[str, Bounds] = {}
        self.forfeit_button_bounds = Bounds(10, self.screen.get_height() - 50, 105, 40)

    def handle_input(self, event: Event):
        """
        Handles changing piece orientation, choosing piece, and placing piece with keybinds.
        """
        if self.turn.game_over:
            return

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
                    self.turn.place_piece(player.piece); print(self.board.print_grid())
                    

            elif event.button == 3 and player.piece:
                if player.piece:
                    player.piece.flip()
        elif event.type == pygame.MOUSEWHEEL and player.piece:
            if event.y > 0:
                player.piece.rotate_cw()
            else:
                player.piece.rotate_ccw()

    def render(self):
        self.screen.fill(BACKGROUND)

        self._render_board()
        self._render_piece_selection()
        self._render_piece_hover()
        self._render_forfeit_button()
        self._render_game_over_text()
        self._render_scores()
        self._render_starting_corners()

        pygame.display.flip()

    def _get_board_start(self) -> tuple[int, int]:
        half_board = self.board.size * CELL_SIZE // 2
        return self.screen.get_width() // 2 - half_board, self.screen.get_height() // 2 - half_board
    
    def _get_piece_regions(self):
        x_start, y_start = self._get_board_start()

        x_end = x_start + (self.board.size * CELL_SIZE)
        y_end = y_start + (self.board.size * CELL_SIZE)

        return {
            self.turn.players[0]: PanelRegion(Bounds(0x000, y_start, x_start, y_end - y_start), PIECES_PER_ROW),
            self.turn.players[1]: PanelRegion(Bounds(x_start, y_end, x_end - x_start, y_start), PIECES_PER_COL),
            self.turn.players[2]: PanelRegion(Bounds(x_end, y_start, x_start, y_end - y_start), PIECES_PER_ROW),
            self.turn.players[3]: PanelRegion(Bounds(x_start, 0x000, x_end - x_start, y_start), PIECES_PER_COL),
        } if self.version else { 
            self.turn.players[0]: PanelRegion(Bounds(0x000, y_start, x_start, y_end - y_start), PIECES_PER_ROW),
            self.turn.players[1]: PanelRegion(Bounds(x_end, y_start, x_start, y_end - y_start), PIECES_PER_ROW),
        }

    def _render_board(self):
        """
        Render the grid and the tiles that have been played on the grid.
        """
        for x in range(self.board.size):
            for y in range(self.board.size):
                x_start, y_start = self._get_board_start()

                screen_x = x * CELL_SIZE + x_start
                screen_y = y * CELL_SIZE + y_start

                pygame.draw.rect(self.screen, self.board.grid[x + y * self.board.size].value, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, BACKGROUND, (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)

    def _render_piece_selection(self):
        """
        Render each of the players' remaining pieces on their respective side of the board.
        """
        self.piece_bounds = {}

        for index, (player, region) in enumerate(self.piece_regions.items()):
            bounds = region.bounds

            if player == self.turn.current_player and not self.turn.game_over:
                
                width = bounds.width + (index % 2 != 0 ) * 23 #clever trick to have good width for top and bottom piece regions (avoids ugly borders)
                height = bounds.height + (not self.version) * 64
                
                pygame.draw.rect(self.screen, HIGHLIGHT, (bounds.x, bounds.y, width, height), 2)

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
                    border = HIGHLIGHT if player == self.turn.current_player and type(player.piece) is Piece and piece == player.piece.shape else BACKGROUND
                    pygame.draw.rect(self.screen, border, (x, y, PANEL_TILE_SIZE, PANEL_TILE_SIZE), 1)

                x = min_x
                y = min_y

                width = (max_x - min_x) + PANEL_TILE_SIZE
                height = (max_y - min_y) + PANEL_TILE_SIZE

                if player == self.turn.current_player:
                    self.piece_bounds[piece] = Bounds(x, y, width, height)

    def _get_coords(self, index: int) -> tuple[int, int]:
        """Convert 1D array index back to 2D coordinates"""
        return index % self.board.size, index // self.board.size
    
    def _render_starting_corners(self):
        for color, index in self.board.starting_corners.items():
            x, y = self._get_coords(index)
            x_start, y_start = self._get_board_start()
            
            screen_x = x * CELL_SIZE + x_start + CELL_SIZE // 2
            screen_y = y * CELL_SIZE + y_start + CELL_SIZE // 2

            pygame.draw.circle(self.screen, color.value, (screen_x, screen_y), CELL_SIZE // 2 * 0.75)

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

        if self.turn.game_over or not player.piece:
            return

        width, height = player.piece.size()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        x_start, y_start = self._get_board_start()

        pos_x = (mouse_x - x_start - width * CELL_SIZE // 2) // CELL_SIZE
        pos_y = (mouse_y - y_start - height * CELL_SIZE // 2) // CELL_SIZE

        player.piece.set_pos(pos_x, pos_y)

        for x, y in player.piece.tiles():
            if x < 0 or y < 0 or x >= self.board.size or y >= self.board.size:
                return

        can_place_piece = self.board.can_place_piece(player.piece)
        border = HIGHLIGHT if can_place_piece else BACKGROUND

        for pos in player.piece.tiles():
            x = CELL_SIZE * pos[0] + x_start
            y = CELL_SIZE * pos[1] + y_start

            pygame.draw.rect(self.screen, player.color.value, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, border, (x, y, CELL_SIZE, CELL_SIZE), 1)

    def _is_forfeit_button_selected(self) -> bool:
        x, y, width, height = self.forfeit_button_bounds
        mouse_x, mouse_y = pygame.mouse.get_pos()

        return x <= mouse_x < x + width and y <= mouse_y < y + height

    def _render_forfeit_button(self):
        if self.turn.game_over:
            return

        color = 0xC8C8C8 if self._is_forfeit_button_selected() else 0xDFDFDF
        x, y, width, height = self.forfeit_button_bounds

        pygame.draw.rect(self.screen, color, (x, y, width, height))
        self.screen.blit(self.font.render("Forfeit", False, 0), (x + 20, y + 10))

    def _render_game_over_text(self):
        if not self.turn.game_over:
            return

        x = self.screen.get_width() // 2
        y = self.screen.get_height() // 2
        color = 0xC8C8C8

        font = pygame.font.Font(pygame.font.get_default_font(), 36)
        font_surface = font.render("Game Over", False, 0)
        text_rect = font_surface.get_rect(center=(x, y))

        padding = 20
        pygame.draw.rect(self.screen, color, text_rect.inflate(padding * 2, padding * 2))

        self.screen.blit(font_surface, text_rect)

    def _render_scores(self):
        scores = self.turn.scores
        font = pygame.font.Font(pygame.font.get_default_font(), 18)

        for index, (color, score) in enumerate(scores.items()):
            text = f"{color.name.title()}: {score}"

            if self.turn.game_over and score == max(scores.values()):
                text += " Winner!"

            font_surface = font.render(text, False, f"#{color.value:X}")
            self.screen.blit(font_surface, (4, 4 + index * 24))

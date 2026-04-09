from color import Color
from piece import Piece
from player import Player

import numpy as np

colorIntMap = {color: i for i, color in enumerate(Color)}


class Board:
    def __init__(self, version: bool):
        self.version = version
        self.size: int = 20 if version else 14
        self.grid: list[list[Color]] = [[Color.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.starting_corners: dict[Color, tuple[int, int]] = {
            Color.BLUE: (0, 0),
            Color.YELLOW: (0, self.size - 1),
            Color.RED: (self.size - 1, self.size - 1),
            Color.GREEN: (self.size - 1, 0),
        } if version else {
            Color.PURPLE: (4, 4),
            Color.ORANGE: (self.size - 5, self.size - 5),
        }

        self.last_move_map = {}
        self.piece_orientations = {}

    def can_place_piece(self, piece: Piece) -> bool:
        touches_player_corner = False

        for pos in piece.tiles():
            # Check for bounds
            if pos[0] < 0 or pos[0] >= self.size or pos[1] < 0 or pos[1] >= self.size:
                return False

            # Check for overlap
            if self.grid[pos[0]][pos[1]] != Color.EMPTY:
                return False

            # Check for edge-to-edge
            if (pos[0] > 0 and self.grid[pos[0] - 1][pos[1]] == piece.color) or \
                    (pos[0] < self.size - 1 and self.grid[pos[0] + 1][pos[1]] == piece.color) or \
                    (pos[1] > 0 and self.grid[pos[0]][pos[1] - 1] == piece.color) or \
                    (pos[1] < self.size - 1 and self.grid[pos[0]][pos[1] + 1] == piece.color):
                return False

            # Check for corner-to-corner
            if touches_player_corner:
                continue

            if (pos[0] > 0 and pos[1] > 0 and self.grid[pos[0] - 1][pos[1] - 1] == piece.color) or \
                    (pos[0] > 0 and pos[1] < self.size - 1 and self.grid[pos[0] - 1][pos[1] + 1] == piece.color) or \
                    (pos[0] < self.size - 1 and pos[1] > 0 and self.grid[pos[0] + 1][pos[1] - 1] == piece.color) or \
                    (pos[0] < self.size - 1 and pos[1] < self.size - 1 and self.grid[pos[0] + 1][pos[1] + 1] == piece.color):
                touches_player_corner = True

            # Check for starting piece
            elif pos == self.starting_corners[piece.color]:
                touches_player_corner = True

        return touches_player_corner

    def place_piece(self, piece: Piece):
        for pos in piece.tiles():
            self.grid[pos[0]][pos[1]] = piece.color
        
        self.last_move_map[piece.color] = {
            "color": piece.color,
            "shape": piece.shape,
            "tiles": piece.tiles(),
        }

    def unplace_piece(self, piece: Piece):
        for pos in piece.tiles():
            self.grid[pos[0]][pos[1]] = Color.EMPTY
        
        self.last_move_map.pop(piece.color, None)

    def last_move(self, player: Color): 
        """Used for mirroring the opponents moves"""
        return self.last_move_map.get(player)
    
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
    
    def player_can_play(self, player: Player) -> bool:
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
        arr = np.array([[colorIntMap[color] for color in col] for col in self.grid], dtype=np.int64)
        return arr.T

    def print_board(self):
        
        color_map = {
            Color.EMPTY: " . ", 
            Color.BLUE: " B ",
            Color.YELLOW: " Y ",
            Color.RED: " R ",
            Color.GREEN: " G ",
            Color.PURPLE: " P ",
            Color.ORANGE: " O ",
        }

        print("   ", end="")
        for col in range(self.size):
            print(f"{col: 3d}", end="") # add two spaces in front
        print()

        for row in range(self.size):
            if (row < 10): 
                print(f"{row: 3d}", end="") 
            else: 
                print(f"{row: 3d}", end=" ")
            for col in range(self.size):
                cell = self.grid[col][row]
                print(color_map.get(cell, "  ?  "), end="")
            print()
        

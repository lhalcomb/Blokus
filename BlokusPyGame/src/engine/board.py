from utils.color import Color
from engine.piece import Piece
from agents.player import Player

import numpy as np
from numpy.typing import NDArray

colorIntMap = {color: i for i, color in enumerate(Color)}



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

        self.last_move_map: dict[Color, dict[str, str | list[tuple[int, int]]]] = {}
        self.piece_orientations: dict[str, list[tuple[int, bool]]] = {}

        self.valid_diagonals: dict[Color, set[int]] = {
            Color.PURPLE: {self.starting_corners[Color.PURPLE]}, 
            Color.ORANGE: {self.starting_corners[Color.ORANGE]}
        }
        self._store_prev_diag = {} # Will store a prev snapshot of the diagonal indices for unplace_pieces' redo when traversing the mct

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
        self._store_prev_diag[piece.color] = frozenset(self.valid_diagonals[piece.color]) #hold the current unoccupied diagonals 
        for pos in piece.tiles():
            idx = self._get_index(pos[0], pos[1])
            self.grid[idx] = piece.color
            self._compute_diagonals(pos, piece)

        self.last_move_map[piece.color] = {
            "shape": piece.shape,
            "tiles": piece.tiles(),
        }

    def unplace_piece(self, piece: Piece):
        for pos in piece.tiles():
            self.grid[self._get_index(pos[0], pos[1])] = Color.EMPTY
        self.last_move_map.pop(piece.color, None)
        
        #Restore the snapshot after unplacing the piece
        self.valid_diagonals[piece.color] = set(self._store_prev_diag.pop(piece.color))

    def last_move(self, player: Color): 
        """Used for mirroring the opponents moves """
        return self.last_move_map.get(player)
    
    def get_orientations(self, shape): 
        if shape not in self.piece_orientations:
            self.piece_orientations[shape] = self._compute_orientations(shape)
        return self.piece_orientations[shape]
    
    def get_valid_diagonals(self, color: Color): 
        return self.valid_diagonals[color]
    
    def player_can_play(self, player: Player) -> bool: 

        """
        Whether the player has any available moves left.
        Checks every remaining piece at every position and orientation.
        """
        if player.forfeit:
            return False

        for shape in player.remaining_pieces: #loop through the remaining pieces for that player
            piece = Piece(shape, player.color)
            for rotations, flipped in self.get_orientations(shape): #try the orientations
                piece.rotations = rotations
                piece.flipped = flipped

                offsets = piece.tiles() # get that pieces tiles at that orientation
                for val_diag in self.get_valid_diagonals(player.color): #get the valid diagonals at that piece
                    fx, fy = val_diag % self.size, val_diag // self.size
                    for ox, oy in offsets: #for that specific pieces tiles...
                        piece.set_pos(fx - ox, fy - oy) # attempt its diagonal
                        if self.can_place_piece(piece): #can it place? 
                            return True 
        return False

    def print_grid(self):
        arr = np.array([[colorIntMap[color] for color in self.grid]])
        return arr.reshape(self.size, self.size)
    
    """ Private methods (only used in this file)"""
    def _get_index(self, x: int, y: int) -> int:
        return x + y * self.size
    
    def _compute_orientations(self, shape):
        if shape in self.piece_orientations:
            return self.piece_orientations[shape]
        
        piece = Piece(shape, Color.EMPTY) #temp place holder
        orientations: list[tuple[int, bool]] = []
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

    
    def _compute_diagonals(self, pos: tuple[int, int], piece: Piece):
        x, y = pos 
        idx = self._get_index(x, y)

        for diag_set in self.valid_diagonals.values(): # when we added the last piece the valid diagonals changed, discard that previous diagonal idx
            diag_set.discard(idx)

        diagonals = [(x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)]

        for dx, dy in diagonals:
            if 0 <= dx < self.size and 0 <= dy < self.size:
                idx = self._get_index(dx, dy)
                if self.grid[idx] == Color.EMPTY:
                    self.valid_diagonals[piece.color].add(idx)
    
    
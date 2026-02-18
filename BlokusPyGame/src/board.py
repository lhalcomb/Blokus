from color import Color
from piece import Piece
from player import Player


class Board:
    def __init__(self, two_players: bool):
        self.two_players = two_players
        self.size: int = 14 if two_players else 20
        self.grid: list[list[Color]] = [[Color.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.starting_corners: dict[Color, tuple[int, int]] = {
            Color.PURPLE: (4, 4),
            Color.ORANGE: (self.size - 5, self.size - 5),
        } if two_players else {
            Color.BLUE: (0, 0),
            Color.YELLOW: (0, self.size - 1),
            Color.RED: (self.size - 1, self.size - 1),
            Color.GREEN: (self.size - 1, 0),
        }

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

                    for _ in range(4):
                        piece.rotate_cw()

                        if self.can_place_piece(piece):
                            return True

                    piece.flip()

                    for _ in range(4):
                        piece.rotate_cw()

                        if self.can_place_piece(piece):
                            return True

        return False

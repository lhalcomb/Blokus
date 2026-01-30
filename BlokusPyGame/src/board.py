from piece import Piece

class Board:
    def __init__(self, size=20, num_players=4):
        self.size = size
        self.num_players = num_players
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.starting_corners = self._get_starting_corners()

    def _get_starting_corners(self):
        # For 4 players: all 4 corners
        # For 2 players: opposite corners
        if self.num_players == 4:
            return [(0, 0), (0, self.size-1), 
                    (self.size-1, 0), (self.size-1, self.size-1)]
        else:  # 2 players
            return [(0, 0), (self.size-1, self.size-1)]

    def _within_bounds(self, piece: Piece) -> bool:
        for pos in piece.cells():
            if pos[0] < 0 or pos[0] >= self.size or pos[1] < 0 or pos[1] >= self.size:
                return False

        return True

    def can_place_piece(self, piece: Piece):
        if not self._within_bounds(piece):
            return False

        touches_player_corner = False

        for pos in piece.cells():
            # Check for overlap
            if self.grid[pos[0]][pos[1]] != 0:
                return False

            # Check for edge-to-edge
            if (pos[0] > 0 and self.grid[pos[0] - 1][pos[1]] == piece.color) or \
               (pos[0] < self.size-1 and self.grid[pos[0] + 1][pos[1]] == piece.color) or \
               (pos[1] > 0 and self.grid[pos[0]][pos[1] - 1] == piece.color) or \
               (pos[1] < self.size-1 and self.grid[pos[0]][pos[1] + 1] == piece.color):
                return False

            # Check for corner-to-corner
            if touches_player_corner:
                continue

            if (pos[0] > 0 and pos[1] > 0 and self.grid[pos[0] - 1][pos[1] - 1] == piece.color) or \
               (pos[0] > 0 and pos[1] < self.size-1 and self.grid[pos[0] - 1][pos[1] + 1] == piece.color) or \
               (pos[0] < self.size-1 and pos[1] > 0 and self.grid[pos[0] + 1][pos[1] - 1] == piece.color) or \
               (pos[0] < self.size-1 and pos[1] < self.size-1 and self.grid[pos[0] + 1][pos[1] + 1] == piece.color):
                touches_player_corner = True

            # Check for starting piece
            if pos == self.starting_corners[piece.color - 1]:
                touches_player_corner = True

        return touches_player_corner

    def place_piece(self, piece: Piece):
        for pos in piece.cells():
            self.grid[pos[0]][pos[1]] = piece.color

    def all_valid_placements(self, piece: Piece):
        valid_placements: list[tuple[int, int]] = []

        for row in range(self.size):
            for col in range(self.size):
                piece.set_pos(row, col)

                if self.can_place_piece(piece):
                    valid_placements.append((row, col))

        return valid_placements

if __name__ == "__main__":
    board = Board()

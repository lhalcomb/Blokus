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

    def _within_bounds(self, piece) -> bool:
        for pos in piece:
            if pos[0] < 0 or pos[0] >= self.size or pos[1] < 0 or pos[1] >= self.size:
                return False

        return True

    def can_place_starting_piece(self, piece, player):
        # piece: [(0,0), (0,1)...] already transformed to its position
        # player: int 1-4
        if not self._within_bounds(piece):
            return False

        corner = self.starting_corners[player - 1]
        touches_corner = False

        for pos in piece:
            if pos == corner:
                touches_corner = True
                break

        return touches_corner

    def can_place_piece(self, piece, player):
        # piece: [(0,0), (0,1)...] already transformed to its position
        # player: int 1-4
        if not self._within_bounds(piece):
            return False

        touches_player_corner = False

        for pos in piece:
            # Check for overlap
            if self.grid[pos[0]][pos[1]] != 0:
                return False

            # Check for edge-to-edge
            if pos[0] > 0 and self.grid[pos[0] - 1][pos[1]] == player:
                return False

            if pos[0] < self.size-1 and self.grid[pos[0] + 1][pos[1]] == player:
                return False

            if pos[1] > 0 and self.grid[pos[0]][pos[1] - 1] == player:
                return False

            if pos[1] < self.size-1 and self.grid[pos[0]][pos[1] + 1] == player:
                return False

            # Check for corner-to-corner
            if pos[0] > 0 and pos[1] > 0 and self.grid[pos[0] - 1][pos[1] - 1] == player:
                touches_player_corner = True

            elif pos[0] > 0 and pos[1] < self.size-1 and self.grid[pos[0] - 1][pos[1] + 1] == player:
                touches_player_corner = True

            elif pos[0] < self.size-1 and pos[1] > 0 and self.grid[pos[0] + 1][pos[1] - 1] == player:
                touches_player_corner = True

            elif pos[0] < self.size-1 and pos[1] < self.size-1 and self.grid[pos[0] + 1][pos[1] + 1] == player:
                touches_player_corner = True

        return touches_player_corner

    def place_piece(self, piece, player):
        # piece: [(0,0), (0,1)...] already transformed to its position
        # player: int 1-4
        for pos in piece:
            self.grid[pos[0]][pos[1]] = player

if __name__ == "__main__":
    board = Board()

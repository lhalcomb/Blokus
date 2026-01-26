

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
    
    def can_place(self, piece, position, player):
        # Check:
        # 1. All piece squares fit on board
        # 2. No overlap with existing pieces
        # 3. First piece touches starting corner
        # 4. Subsequent pieces: corner-to-corner, no edge-to-edge
        pass
            
        
if __name__ == "__main__":

    board = Board()
    
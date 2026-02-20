from board import Board
from color import Color
from piece import Piece, PIECES
from player import Player

# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=false


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
            self.game_over = True
            self.current_player = None

    def get_scores(self):
        return {player.color: -sum(len(PIECES[piece]) for piece in player.remaining_pieces) for player in self.players}

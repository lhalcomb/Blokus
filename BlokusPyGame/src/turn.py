from board import Board
from color import Color
from piece import Piece
from player import Player


class Turn:
    def __init__(self, board: Board):
        self.board = board
        self.players = [
            Player(Color.RED),
            Player(Color.YELLOW),
            Player(Color.GREEN),
            Player(Color.BLUE),
        ]
        self.active_players = [
            self.players[0],
            self.players[1],
            self.players[2],
            self.players[3],
        ]
        self.current_player = self.active_players[0]

    def place_piece(self, piece: Piece):
        self.current_player.remove_piece(piece.shape)
        self.board.place_piece(piece)
        self._next_turn()  # TODO: End game if this returns false
        self.current_player.piece = Piece(self.current_player.remaining_pieces[0], self.current_player.color)

    def _next_turn(self) -> bool:
        """
        Sets current_player to the next player. Returns false if the game is over.
        """
        player_can_play = self.board.player_can_play(self.current_player)

        if len(self.active_players) > 1:
            current_index = self.active_players.index(self.current_player)
            self.current_player = self.active_players[(current_index + 1) % len(self.active_players)]

        if not player_can_play:
            current_index = self.active_players.index(self.current_player)
            self.current_player = self.active_players[(current_index + 1) % len(self.active_players)]
            self.active_players.remove(self.current_player)

        return len(self.active_players) > 0

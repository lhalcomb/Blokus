from board import Board
from color import Color
from piece import Piece, PIECES
from player import Player


class Turn:
    def __init__(self, board: Board):
        self.board = board
        self.players = [
            Player(Color.PURPLE),
            Player(Color.ORANGE),
        ] if board.two_players else [
            Player(Color.BLUE),
            Player(Color.YELLOW),
            Player(Color.RED),
            Player(Color.GREEN),
        ]
        self.active_players = self.players.copy()
        self.current_player = self.active_players[0]
        self.game_over = False
        self.scores = {player.color: -sum(len(PIECES[piece]) for piece in player.remaining_pieces) for player in self.players}

    def place_piece(self, piece: Piece):
        self.current_player.remove_piece(piece.shape)
        self.board.place_piece(piece)
        self.add_score(piece)
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

    def add_score(self, piece: Piece):
        self.scores[piece.color] += len(PIECES[piece.shape]) + (len(self.current_player.remaining_pieces) == 0) * (15 + (piece.shape == "I1") * 5)

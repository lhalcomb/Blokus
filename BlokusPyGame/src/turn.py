from board import Board
from color import Color
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
        self.current_player = self.players[0]

    def next_turn(self) -> bool:
        """
        Sets current_player to the next player. Returns false if the game is over.
        """
        if not self.board.player_can_play(self.current_player):
            self.players.remove(self.current_player)

        if len(self.players) > 1:
            current_index = self.players.index(self.current_player)
            self.current_player = self.players[(current_index + 1) % len(self.players)]

        return len(self.players) > 0

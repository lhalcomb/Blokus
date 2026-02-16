from board import Board
from color import Color
from piece import Piece
from player import Player


class Turn:
    def __init__(self, board: Board):
        self.board = board
        self.players = [
            Player(Color.BLUE),
            Player(Color.YELLOW),
            Player(Color.RED),
            Player(Color.GREEN),
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
        self.next_turn()

    def next_turn(self):
        """
        Sets current_player to the next player. Returns false if the game is over.
        """
        player = self.current_player
        player.piece = None

        if len(self.active_players) > 1:
            current_index = self.active_players.index(player)
            self.current_player = self.active_players[(current_index + 1) % len(self.active_players)]

        if not self.board.player_can_play(player):
            self.active_players.remove(player)

        if len(self.active_players) == 0:
            #exit()
            print("Game Over")
            #later change this so game over screen pops up and not exit

                 


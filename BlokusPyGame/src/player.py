from color import Color
from piece import Piece, PIECES


class Player:
    def __init__(self, color: Color):
        self.color: Color = color
        self.remaining_pieces: list[str] = list(PIECES.keys())
        self.piece = Piece(self.remaining_pieces[-1], self.color)  # TODO: Choose piece from selection

    def remove_piece(self, shape: str):
        self.remaining_pieces.remove(shape)

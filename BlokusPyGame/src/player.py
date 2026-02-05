from color import Color
from piece import PIECES


class Player:
    def __init__(self, color: Color):
        self.color: Color = color
        self.remaining_pieces: list[str] = list(PIECES.keys())

    def remove_piece(self, shape: str):
        self.remaining_pieces.remove(shape)

    def choose_color(self):
        pass
